"""agent เลื่อนนัด (UC-14 A4, MD-SEQ-14-02) สี่เรื่องของหน้าบทเรียนหัวข้อ 6.3
เครื่องมือ (tools.py REQ-AI-010) จุดอนุมัติ (ข้อเสนอรอยืนยัน REQ-AI-011) หยุดปลอดภัย (REQ-AI-012) บันทึก (records.py REQ-AI-013)
ค่าที่จะส่ง API มาจากโค้ดที่อ่านข้อความลูกค้าและช่วงเวลาจริง ไม่ได้มาจากข้อความของ LLM (D-14-03, LLM10:2026)"""
import re
from datetime import datetime, timedelta

from sqlalchemy import select

from app import config
from app.db.models import AssistantProposal, Job, TimeSlot, Technician
from app.booking.service import RescheduleRejected, check_reschedule
from app.assistant import tools
from app.assistant.retrieval import fmt_date, fmt_time, MONTH_TH

WEEKDAYS = {"จันทร์": 0, "อังคาร": 1, "พุธ": 2, "พฤหัส": 3, "ศุกร์": 4, "เสาร์": 5, "อาทิตย์": 6}
MONTHS = {"ต.ค.": 10, "ตุลาคม": 10, "ตุลา": 10, "พ.ย.": 11, "พฤศจิกายน": 11, "พฤศจิกา": 11}
OTHER_TECH = ("เปลี่ยนช่าง", "ช่างคนอื่น", "ช่างใหม่", "คนอื่นมาแทน", "ไม่เอาช่างคนนี้")


def parse_datetime(text: str, now: datetime) -> datetime | None:
    """ด่านตรวจของ agent: ลูกค้าขอวันและเวลาชัดเจนไหม ถ้าขาดวันหรือเวลา คืน None (ผู้ช่วยเสนอช่วงว่างแทน ไม่เดา)"""
    t = text.replace("บ่าย", " บ่าย ")
    day = None
    if "มะรืน" in t:
        day = now.date() + timedelta(days=2)
    elif "พรุ่งนี้" in t:
        day = now.date() + timedelta(days=1)
    m = re.search(r"วันที่\s*(\d{1,2})|(\d{1,2})\s*(ต\.ค\.|ตุลาคม|ตุลา|พ\.ย\.|พฤศจิกายน|พฤศจิกา)|(\d{1,2})/(\d{1,2})", t)
    if day is None and m:
        if m.group(1):
            d, mon = int(m.group(1)), now.month
        elif m.group(2):
            d, mon = int(m.group(2)), MONTHS[m.group(3)]
        else:
            d, mon = int(m.group(4)), int(m.group(5))
        try:
            cand = datetime(now.year, mon, d).date()
        except ValueError:
            return None
        if cand < now.date() and m.group(1):   # "วันที่ 3" ที่ผ่านไปแล้ว คือเดือนหน้า
            try:
                cand = datetime(now.year + (1 if mon == 12 else 0), mon % 12 + 1, d).date()
            except ValueError:
                return None
        day = cand
    if day is None:
        for name, wd in WEEKDAYS.items():
            if "วัน" + name in t:
                ahead = (wd - now.weekday()) % 7 or 7
                day = now.date() + timedelta(days=ahead)
                break
    hour = minute = None
    m = re.search(r"(?<!\d)(\d{1,2})[:.](\d{2})(?!\d)", t)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
    else:
        m = re.search(r"บ่าย\s*(\d)\s*โมง", t)
        if m:
            hour, minute = 12 + int(m.group(1)), 0
        else:
            m = re.search(r"(?<!\d)(\d{1,2})\s*(?:โมง|นาฬิกา)", t)
            if m:
                hour, minute = int(m.group(1)), 0
                if hour < 7:   # "2 โมง" แบบพูดหมายถึงบ่ายสอง
                    hour += 12
    if day is None or hour is None or not (0 <= hour < 24):
        return None
    return datetime(day.year, day.month, day.day, hour, minute)


def fmt(dt: datetime) -> str:
    return f"{fmt_date(dt)} {fmt_time(dt)}"


def slot_list(slots: list[TimeSlot], n: int = 3) -> str:
    return " | ".join(fmt(s.start) for s in slots[:n])


def plan_reschedule(db, conv, job: Job, text: str, now: datetime) -> dict:
    """คืน dict ผลของข้อความขอเลื่อน: outcome = beyond_rule / clarify / proposal / tool_error พร้อมข้อความถึงลูกค้า"""
    try:
        status = tools.call("read_job_status", db, conv.customer_id, now, job_id=job.id)
    except tools.ToolError:
        return {"outcome": "tool_error", "reply": "ขออภัย ระบบอ่านข้อมูลงานไม่ได้ ขอส่งต่อเจ้าหน้าที่นะคะ"}
    if any(w in text for w in OTHER_TECH):
        e = RescheduleRejected("other_technician")
        return {"outcome": "beyond_rule", "reason": e.reason, "reply": beyond_reply(e)}
    try:
        check_reschedule(db, job, None, now)   # BR-06 ข้อ 1 ถึง 3 ก่อนเสนออะไรทั้งนั้น
    except RescheduleRejected as e:
        return {"outcome": "beyond_rule", "reason": e.reason, "reply": beyond_reply(e)}
    free = tools.call("read_free_slots", db, conv.customer_id, now, job_id=job.id)
    wanted = parse_datetime(text, now)
    if wanted is None:
        return {"outcome": "clarify", "slots": free,
                "reply": f"ช่วงที่ว่างของช่างคนเดิม: {slot_list(free)} พิมพ์วันและเวลาที่ต้องการได้เลยค่ะ"
                if free else "ขออภัย ตอนนี้ช่างคนเดิมไม่มีช่วงว่างในกรอบการเลื่อน ขอส่งต่อเจ้าหน้าที่นะคะ"}
    slot = db.scalars(select(TimeSlot).where(TimeSlot.technician_id == job.technician_id,
                                             TimeSlot.start == wanted)).first()
    if slot is None:
        return {"outcome": "clarify", "slots": free,
                "reply": f"ช่างคนเดิมไม่มีช่วงเวลา {fmt(wanted)} ช่วงที่ว่าง: {slot_list(free)}"}
    try:
        check_reschedule(db, job, slot, now)
    except RescheduleRejected as e:
        if e.beyond_rule:
            return {"outcome": "beyond_rule", "reason": e.reason, "reply": beyond_reply(e)}
        return {"outcome": "clarify", "slots": free, "reply": f"{e.message} ช่วงที่ว่าง: {slot_list(free)}"}
    p = AssistantProposal(conversation_id=conv.id, customer_id=conv.customer_id, job_id=job.id,
                          technician_id=job.technician_id, old_slot_id=job.slot_id, new_slot_id=slot.id,
                          old_start=job.scheduled_start, new_start=slot.start, status="pending", created_at=now,
                          expires_at=now + timedelta(minutes=config.ASSISTANT_PROPOSAL_MINUTES))
    db.add(p)
    db.flush()
    return {"outcome": "proposal", "proposal": p, "reply": summary_text(db, p)}


def beyond_reply(e: RescheduleRejected) -> str:
    return f"ขออภัย เลื่อนนัดนี้ให้ไม่ได้ค่ะ {e.message} ขอส่งต่อเจ้าหน้าที่นะคะ"


def proposal_out(db, p: AssistantProposal) -> dict:
    """ค่าในสรุปคือค่าที่จะส่ง API ทุกตัว (D-14-03 ASI09)"""
    tech = db.get(Technician, p.technician_id)
    return {"proposal_id": p.id, "job_id": p.job_id, "old_start": p.old_start.isoformat(),
            "new_start": p.new_start.isoformat(), "new_slot_id": p.new_slot_id,
            "technician": tech.name if tech else None, "same_technician": True, "status": p.status,
            "expires_at": p.expires_at.isoformat()}


def summary_text(db, p: AssistantProposal) -> str:
    tech = db.get(Technician, p.technician_id)
    return (f"สรุปการเลื่อนนัด งาน #{p.job_id} วันเวลาเดิม {fmt(p.old_start)} วันเวลาใหม่ {fmt(p.new_start)} "
            f"ช่าง {tech.name if tech else ''} (คนเดิม) กด ยืนยันเลื่อนนัด หรือ ไม่ใช่")
