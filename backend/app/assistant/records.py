"""REQ-AI-013 บันทึกคำตอบและบันทึกการกระทำ (ชั้นที่ 3 ของความโปร่งใส REQ-AI-020) ไม่มีเบอร์โทร (REQ-PRV-002)
ข้อความของลูกค้าเก็บแบบปิดบังแล้ว (privacy.mask_text Q-57) เก็บ 180 วัน และลบข้อความเมื่อลูกค้าขอลบข้อมูล (REQ-PRV-010)"""
import json
from datetime import datetime, timedelta

from sqlalchemy import delete, select

from app import config
from app.db.models import AssistantTurn, AssistantAction, AssistantTicket
from app.privacy import get_logger, log_event, mask_text

log = get_logger(__name__)


def write_turn(db, conv, text: str, intent: str, outcome: str, facts_data: dict | None, prompt_version: str,
               model_version: str, guard: str, answer: str, now: datetime, latency_ms: float = 0.0) -> AssistantTurn:
    turn = AssistantTurn(conversation_id=conv.id, customer_id=conv.customer_id, at=now, masked_text=mask_text(text)[:600],
                         intent=intent, outcome=outcome,
                         facts=json.dumps(facts_data or {}, ensure_ascii=False, default=str)[:4000],
                         prompt_version=prompt_version, model_version=model_version, guard=guard[:200],
                         answer=mask_text(answer)[:2000], latency_ms=latency_ms)
    db.add(turn)
    db.flush()
    log_event(log, "assistant_turn", conversation_id=conv.id, customer_id=conv.customer_id, turn_id=turn.id,
              intent=intent, result=outcome, guard=guard, prompt_version=prompt_version, model_version=model_version)
    return turn


def write_action(db, proposal, text: str, interpretation: str, tool: str, args: dict, result: str,
                 prompt_version: str, model_version: str, now: datetime) -> AssistantAction:
    action = AssistantAction(proposal_id=proposal.id, conversation_id=proposal.conversation_id,
                             customer_id=proposal.customer_id, masked_text=mask_text(text)[:600],
                             interpretation=interpretation[:300], tool=tool,
                             args=json.dumps(args, ensure_ascii=False, default=str)[:300], confirmed_at=now,
                             result=result, prompt_version=prompt_version, model_version=model_version, at=now)
    db.add(action)
    db.flush()
    log_event(log, "assistant_action", conversation_id=proposal.conversation_id, customer_id=proposal.customer_id,
              proposal_id=proposal.id, tool=tool, job_id=proposal.job_id, result=result)
    return action


def purge(db, now: datetime) -> int:
    """ลบบันทึกที่อายุเกิน 180 วัน (scheduler เรียกทุก 1 นาที) คืนจำนวนแถวที่ลบ"""
    cutoff = now - timedelta(days=config.ASSISTANT_LOG_RETENTION_DAYS)
    n = db.execute(delete(AssistantTurn).where(AssistantTurn.at < cutoff)).rowcount
    n += db.execute(delete(AssistantAction).where(AssistantAction.at < cutoff)).rowcount
    db.commit()
    return n


def erase_customer_text(db, customer_id: int) -> int:
    """REQ-PRV-010 (Q-57 SH-05): เมื่อลูกค้าขอลบข้อมูล ลบข้อความที่ลูกค้าพิมพ์ในบันทึกทั้งหมด คงรหัส ความตั้งใจ และผลไว้"""
    rows = db.scalars(select(AssistantTurn).where(AssistantTurn.customer_id == customer_id)).all()
    actions = db.scalars(select(AssistantAction).where(AssistantAction.customer_id == customer_id)).all()
    for r in rows + actions:
        r.masked_text = ""
    return len(rows) + len(actions)


def reason_for_reschedule(db, job_id: int) -> list[dict]:
    """ตอบ "ทำไมนัดฉันถูกเลื่อน" จากบันทึกการกระทำ (REQ-AI-013 ข้อตรวจ 1 นาที) ใช้ในหน้าตั๋วของ call center"""
    from app.db.models import AssistantProposal
    out = []
    for a in db.scalars(select(AssistantAction).order_by(AssistantAction.id)).all():
        p = db.get(AssistantProposal, a.proposal_id)
        if p is not None and p.job_id == job_id:
            out.append({"at": a.at.isoformat(), "customer_id": a.customer_id, "text": a.masked_text,
                        "interpretation": a.interpretation, "tool": a.tool, "args": json.loads(a.args),
                        "result": a.result, "prompt_version": a.prompt_version, "model_version": a.model_version})
    return out
