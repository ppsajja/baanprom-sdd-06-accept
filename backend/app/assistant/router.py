"""endpoint ของผู้ช่วย UC-14 (specs/005-ai-assistant/plan.md ข้อ 4) ทุกตัวอยู่ในบัญชี endpoint ของ operations.md (REQ-SEC-012)
R1 ยังไม่มีการเข้าสู่ระบบ (UC-02) ลูกค้าบอกตัวเองด้วย customer_id ที่ส่งมา (TH-01, AS-14) เหมือนทุก feature ของ R1"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.db.session import get_db
from app.db.models import AssistantConversation, AssistantTicket
from app.clock import get_now
from app.ops.guard import require_ops
from app.privacy import get_logger, log_event
from app.assistant import service, handoff, records

router = APIRouter()
ops_router = APIRouter(dependencies=[Depends(require_ops)])
log = get_logger(__name__)


class CustomerIn(BaseModel):
    customer_id: int


class MessageIn(BaseModel):
    conversation_id: int
    customer_id: int
    text: str


class SwitchIn(BaseModel):
    enabled: bool


def _conv(db, conversation_id: int, customer_id: int) -> AssistantConversation:
    conv = db.get(AssistantConversation, conversation_id)
    if conv is None or conv.customer_id != customer_id:
        raise HTTPException(404, "ไม่พบบทสนทนา")
    return conv


@router.get("/assistant/status")
def status(db: Session = Depends(get_db)):
    # REQ-AI-022: หน้าจอถามก่อนเปิดแชต ถ้าปิดอยู่ แสดงข้อความและปุ่มโทร
    return {"enabled": service.is_enabled(db), "message": None if service.is_enabled(db) else service.MSG_DISABLED,
            "call_center_tel": config.call_center_tel()}


@router.post("/assistant/conversations")
def start(body: CustomerIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-AI-020 (ข้อความแรก) และ REQ-AI-022 (ปิดอยู่ไม่เริ่มบทสนทนา)
    return service.start(db, body.customer_id, now)


@router.post("/assistant/messages")
def message(body: MessageIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-AI-005 ถึง 013, REQ-DAT-010 (ลำดับ 5 ขั้นใน service.handle_message)
    if not service.is_enabled(db):
        return service.disabled_out()
    conv = _conv(db, body.conversation_id, body.customer_id)
    out = service.handle_message(db, conv, body.text, now)
    out.pop("raw_answer", None)
    out.pop("facts", None)  # ข้อมูลที่ส่งให้ LLM ไม่ส่งกลับหน้าจอ อยู่ในบันทึกคำตอบสำหรับ call center
    return out


@router.post("/assistant/proposals/{proposal_id}/confirm")
def confirm(proposal_id: int, body: CustomerIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-AI-011 (ระดับ 2 ยืนยันก่อน) REQ-FN-056
    return service.confirm(db, proposal_id, body.customer_id, now)


@router.post("/assistant/proposals/{proposal_id}/decline")
def decline(proposal_id: int, body: CustomerIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-AI-012 เงื่อนไขที่ 3
    return service.decline(db, proposal_id, body.customer_id, now)


@router.post("/assistant/conversations/{conversation_id}/handoff")
def ask_human(conversation_id: int, body: CustomerIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-AI-020 (ทางคุยกับเจ้าหน้าที่ทุกจอ)
    return service.request_handoff(db, _conv(db, conversation_id, body.customer_id), now)


@router.post("/assistant/turns/{turn_id}/report")
def report(turn_id: int, body: CustomerIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-AI-022 ช่องร้องเรียน
    out = service.report(db, turn_id, body.customer_id, now)
    if out is None:
        raise HTTPException(404, "ไม่พบคำตอบ")
    return out


@ops_router.post("/ops/assistant/switch")
def switch(body: SwitchIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # REQ-AI-022: หัวหน้า call center ปิดหรือเปิดผู้ช่วยผ่านกุญแจของ Ops (Q-60) มีผลกับคำขอถัดไปทันที ไม่ต้อง deploy
    service.set_enabled(db, body.enabled, now)
    log_event(log, "assistant_switched", result="enabled" if body.enabled else "disabled")
    return {"enabled": body.enabled, "at": now.isoformat()}


@ops_router.get("/ops/assistant/tickets")
def tickets(db: Session = Depends(get_db)):
    # REQ-AI-012 / AC-14-15: มุมมองตั๋วของ call center (ชั้นที่ 2 ของความโปร่งใส)
    rows = db.scalars(select(AssistantTicket).order_by(AssistantTicket.id)).all()
    return [handoff.ticket_view(db, t) for t in rows]


@ops_router.get("/ops/assistant/jobs/{job_id}/actions")
def actions(job_id: int, db: Session = Depends(get_db)):
    # REQ-AI-013: ตอบ "ทำไมนัดฉันถูกเลื่อน" จากบันทึกการกระทำ
    return records.reason_for_reschedule(db, job_id)
