"""ส่งต่อ call center (REQ-AI-005 นอกขอบเขต, REQ-AI-012 หยุดปลอดภัย, REQ-AI-022 ช่องร้องเรียน)
ตั๋วมีบริบทพอให้เจ้าหน้าที่รับต่อโดยลูกค้าไม่ต้องเล่าใหม่ (AC-14-15, REQ-AI-020 ชั้นที่ 2)"""
import json
from datetime import datetime, timedelta

from sqlalchemy import select

from app import config
from app.db.models import AssistantTicket, AssistantTurn
from app.privacy import get_logger, log_event

log = get_logger(__name__)

REASONS = ("out_of_scope", "unclear_intent", "tool_error", "declined_twice", "beyond_rule", "customer_request", "complaint")


def add_business_days(start: datetime, days: int) -> datetime:
    d = start
    while days > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            days -= 1
    return d


def create_ticket(db, conv, reason: str, intent: str, now: datetime, turn_id: int | None = None,
                  job_id: int | None = None) -> AssistantTicket:
    assert reason in REASONS, reason
    due = add_business_days(now, config.ASSISTANT_COMPLAINT_REPLY_BUSINESS_DAYS) if reason == "complaint" else None
    t = AssistantTicket(conversation_id=conv.id, customer_id=conv.customer_id, reason=reason, intent=intent,
                        turn_id=turn_id, job_id=job_id, created_at=now, reply_due_at=due)
    db.add(t)
    db.flush()
    log_event(log, "assistant_handoff", conversation_id=conv.id, customer_id=conv.customer_id, ticket_id=t.id,
              reason=reason, intent=intent)
    return t


def ticket_view(db, t: AssistantTicket) -> dict:
    """มุมมองของ call center: บทสนทนาเต็ม (ปิดบังแล้ว) ความตั้งใจที่ตีความ ข้อมูลที่ค้นมา และเหตุที่ส่งต่อ"""
    turns = db.scalars(select(AssistantTurn).where(AssistantTurn.conversation_id == t.conversation_id)
                       .order_by(AssistantTurn.id)).all()
    return {"ticket_id": t.id, "reason": t.reason, "intent": t.intent, "job_id": t.job_id, "status": t.status,
            "created_at": t.created_at.isoformat(), "reply_due_at": t.reply_due_at.isoformat() if t.reply_due_at else None,
            "conversation": [{"turn_id": r.id, "at": r.at.isoformat(), "customer_text": r.masked_text, "intent": r.intent,
                              "facts": json.loads(r.facts), "answer": r.answer, "outcome": r.outcome, "guard": r.guard}
                             for r in turns]}
