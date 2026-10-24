"""POST /slots/{id}/hold, GET /deposit-quote, POST /bookings, GET /jobs/{id}, GET /jobs/{id}/technician-view (plan.md ข้อ 4)
CR-09: POST /jobs/{id}/reschedule (REQ-FN-056, BR-06) API เลื่อนนัดของลูกค้า ผู้ช่วยของ UC-14 ใช้ฟังก์ชันเดียวกัน
CR-07: REQ-SEC-011 (409 hold_limit), REQ-QA-010 (202 payment_pending), REQ-SEC-010 (technician-view 403 และบันทึก)
log ผ่าน log_event เท่านั้น (REQ-OP-005 บรรทัดที่ 3)"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import TimeSlot, Customer, ServiceAddress, Job
from app.booking import service
from app.payments.gateway import get_gateway
from app.clock import get_now
from app.privacy import get_logger, log_event
from app.ops import audit

router = APIRouter()
log = get_logger(__name__)


class HoldIn(BaseModel):
    customer_id: int


class BookingIn(BaseModel):
    customer_id: int
    slot_id: int
    address_id: int
    category: str


def job_out(job: Job) -> dict:
    return {"job_id": job.id, "status": job.status, "technician_id": job.technician_id,
            "slot_id": job.slot_id, "deposit_amount": job.deposit_amount,
            "scheduled_start": job.scheduled_start.isoformat()}


@router.post("/slots/{slot_id}/hold")
def hold(slot_id: int, body: HoldIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-FN-041
    slot = db.get(TimeSlot, slot_id)
    if not slot:
        raise HTTPException(404, "ไม่พบช่วงเวลา")
    try:
        slot = service.hold_slot(db, slot, body.customer_id, now)
    except service.SlotTaken as e:
        return JSONResponse({"reason": "slot_taken", "alternatives": e.alternatives}, status_code=409)
    except service.HoldLimitReached as e:
        return hold_limit_response(e)
    return {"slot_id": slot.id, "hold_expires_at": slot.hold_expires_at.isoformat()}


# ข้อความที่หน้าจอแสดงเมื่อถือล็อกครบเพดาน (UI-07-01 รายการ "ต้องตรง" ที่เพิ่มโดย CR-07) อยู่ที่นี่ที่เดียว
MSG_HOLD_LIMIT = "คุณล็อกช่วงเวลาอื่นไว้อยู่ กรุณายืนยันช่วงนั้นหรือรอให้หมดอายุก่อน"
# ข้อความเมื่อ gateway ไม่ตอบ (UI-07-02 รายการ "ต้องตรง" ที่เพิ่มโดย CR-07) เวลาสิ้นสุดของล็อกส่งแยกใน hold_expires_at
MSG_PAYMENT_PENDING = "ระบบชำระเงินขัดข้อง เราล็อกช่วงเวลาไว้ให้ถึง {until} น. กดยืนยันอีกครั้งได้ ระบบจะไม่ตัดเงินซ้ำ"


def hold_limit_response(e: "service.HoldLimitReached") -> JSONResponse:
    # รองรับ REQ-SEC-011 (AC-07-14): ปฏิเสธ 409 และบอกว่าช่วงใดที่ยังถืออยู่
    return JSONResponse({"reason": "hold_limit", "message": MSG_HOLD_LIMIT,
                         "held": [{"slot_id": s.id, "start": s.start.isoformat(),
                                   "hold_expires_at": s.hold_expires_at.isoformat()} for s in e.held]},
                        status_code=409)


@router.get("/deposit-quote")
def deposit_quote(category: str):
    # รองรับ REQ-BR-002 (AC-07-11): ยอดที่หน้าจอแสดงก่อนยืนยัน มาจากฟังก์ชันเดียวกับที่ใช้ตัดมัดจำ
    try:
        amount = service.deposit_for(category)
    except service.UnknownCategory:
        raise HTTPException(422, "ไม่รู้จักประเภทงาน")
    return {"category": category, "deposit_amount": amount}


@router.post("/bookings", status_code=201)
def create(body: BookingIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-FN-008, REQ-IF-001, REQ-IF-005
    customer, slot, address = db.get(Customer, body.customer_id), db.get(TimeSlot, body.slot_id), db.get(ServiceAddress, body.address_id)
    if not (customer and slot and address):
        raise HTTPException(404, "ไม่พบลูกค้า ช่วงเวลา หรือที่อยู่")
    try:
        service.deposit_for(body.category)  # REQ-BR-002: ประเภทงานต้องอยู่ในตารางราคาประเมิน (AS-10)
    except service.UnknownCategory:
        raise HTTPException(422, "ไม่รู้จักประเภทงาน")
    try:
        job = service.create_booking(db, customer, slot, address, body.category, get_gateway(), now)
    except service.SlotTaken as e:
        return JSONResponse({"reason": "slot_taken", "alternatives": e.alternatives}, status_code=409)
    except service.HoldLimitReached as e:
        return hold_limit_response(e)
    except service.PaymentPending as e:
        # รองรับ REQ-QA-010 บรรทัดที่ 3 (AC-07-12): 202 = รับคำขอแล้วแต่ยังไม่รู้ผลเงิน
        log_event(log, "booking_pending_payment", job_id=e.job.id, customer_id=customer.id)
        until = e.slot.hold_expires_at
        return JSONResponse({"reason": "payment_pending", "job_id": e.job.id, "status": e.job.status,
                             "hold_expires_at": until.isoformat() if until else None,
                             "message": MSG_PAYMENT_PENDING.format(until=f"{until:%H:%M}" if until else "")},
                            status_code=202)
    except service.PaymentFailed as e:
        return JSONResponse({"reason": "payment_failed", "detail": e.reason, "job_id": e.job_id}, status_code=402)
    log_event(log, "booking_created", job_id=job.id, customer_id=customer.id)  # ไม่มีเบอร์โทร (REQ-PRV-002)
    return job_out(job)


@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    # CR-07 EV-045: R1 ยังไม่รู้ตัวผู้ขอ (ไม่มีการเข้าสู่ระบบ) endpoint นี้ไม่มีข้อมูลส่วนบุคคล
    # SH-01 ยอมรับความเสี่ยงจนกว่า UC-02 มาใน R2 (GAP-24) ไม่ใช่การยกเว้น REQ-SEC-010 ถาวร
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "ไม่พบงาน")
    return job_out(job)


@router.get("/jobs/{job_id}/technician-view")
def technician_view(job_id: int, technician_id: int, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-SEC-004 และ REQ-SEC-010 (CR-07, AC-07-15): ไม่ใช่งานของช่างคนนี้หรือไม่มีงาน ตอบ 403 เหมือนกัน และบันทึก
    job = audit.job_of_technician(db, job_id, technician_id, "GET /jobs/{job_id}/technician-view", now)
    data = service.technician_view(job, now)
    if "customer_phone" in data:
        audit.record_phone_revealed(db, technician_id, job.id, "GET /jobs/{job_id}/technician-view", now)
        db.commit()
    # GAP-22: เดิม log ทั้ง dict (ชื่อลูกค้าหลุดลง log ได้ เบอร์ถูกกรอง) ตอนนี้ log เฉพาะรหัส
    log_event(log, "technician_view", technician_id=technician_id, job_id=job.id)
    return data


class RescheduleIn(BaseModel):
    customer_id: int
    new_slot_id: int


@router.post("/jobs/{job_id}/reschedule")
def reschedule(job_id: int, body: RescheduleIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-FN-056, BR-06 (CR-09, AC-14-16) และ REQ-SEC-010: ไม่ใช่งานของลูกค้าคนนี้ ตอบ 403 และบันทึก
    job = audit.job_of_customer(db, job_id, body.customer_id, "POST /jobs/{job_id}/reschedule", now)
    slot = db.get(TimeSlot, body.new_slot_id)
    if not slot:
        raise HTTPException(404, "ไม่พบช่วงเวลา")
    try:
        record = service.reschedule_job(db, job, slot, now)
    except service.RescheduleRejected as e:
        return JSONResponse({"reason": e.reason, "message": e.message}, status_code=409)
    log_event(log, "job_rescheduled", job_id=job.id, customer_id=body.customer_id, slot_id=slot.id)
    return {"job_id": job.id, "slot_id": job.slot_id, "scheduled_start": job.scheduled_start.isoformat(),
            "from_start": record.from_start.isoformat(), "reschedules_used": service.reschedules_used(db, job)}
