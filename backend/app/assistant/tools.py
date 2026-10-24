"""REQ-AI-010 เครื่องมือของผู้ช่วยเป็นรายการปิด 3 รายการ เรียกชื่ออื่นได้ ToolNotAllowed เสมอ
ทุกเครื่องมือทำด้วยสิทธิ์ของลูกค้าที่ถาม ผ่านฟังก์ชันเดิมของ booking (REQ-AI-011 บรรทัดที่ 3, ASI03) ผู้ช่วยไม่มีสิทธิ์ของตัวเอง
เครื่องมือระดับ 2 (เลื่อนนัด) เรียกได้เฉพาะเมื่อข้อเสนออยู่ในสถานะ confirming คือหลังลูกค้ากดยืนยันแล้วเท่านั้น"""
from datetime import datetime

from fastapi import HTTPException

from app.db.models import TimeSlot
from app.booking import service as booking
from app.ops import audit

LEVEL = {"read_job_status": 1, "read_free_slots": 1, "reschedule_job": 2}
NAMES_TH = {"read_job_status": "อ่านสถานะงาน", "read_free_slots": "อ่านช่วงเวลาว่างของช่างคนเดิม",
            "reschedule_job": "เลื่อนนัด"}
ENDPOINT = "assistant tool"


class ToolNotAllowed(Exception):
    pass


class ApprovalRequired(Exception):
    pass


class ToolTimeout(Exception):
    """เครื่องมือไม่ตอบภายใน ASSISTANT_TOOL_TIMEOUT_SECONDS ผลไม่ทราบ ห้ามเรียกซ้ำ (REQ-AI-012)"""


class ToolError(Exception):
    pass


# ช่องสำหรับ test เท่านั้น: ทำให้เครื่องมือ "หมดเวลา" ก่อนทำ (before) หรือหลังทำแล้ว (after) และนับการเรียก
FAULTS: dict[str, str] = {}
CALLS: list[str] = []


def _own_job(db, customer_id: int, job_id: int, now: datetime):
    try:
        return audit.job_of_customer(db, job_id, customer_id, ENDPOINT, now)
    except HTTPException as e:
        raise ToolError("not_owner") from e


def call(name: str, db, customer_id: int, now: datetime, **kw):
    if name not in LEVEL:
        raise ToolNotAllowed(name)
    CALLS.append(name)
    if name == "read_job_status":
        job = _own_job(db, customer_id, kw["job_id"], now)
        return {"job_id": job.id, "status": job.status, "scheduled_start": job.scheduled_start,
                "technician_id": job.technician_id, "used": booking.reschedules_used(db, job)}
    if name == "read_free_slots":
        job = _own_job(db, customer_id, kw["job_id"], now)
        return booking.free_slots_for_reschedule(db, job, now)
    # reschedule_job ระดับ 2
    proposal = kw["proposal"]
    if proposal.status != "confirming" or proposal.customer_id != customer_id:
        raise ApprovalRequired(proposal.id)
    if FAULTS.get(name) == "before":
        raise ToolTimeout(name)
    job = _own_job(db, customer_id, proposal.job_id, now)
    slot = db.get(TimeSlot, proposal.new_slot_id)
    record = booking.reschedule_job(db, job, slot, now, reference=f"P-{proposal.id}")
    if FAULTS.get(name) == "after":
        raise ToolTimeout(name)
    return record
