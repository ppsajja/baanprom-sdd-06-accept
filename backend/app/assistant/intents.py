"""ขั้น 2 ของ MD-SEQ-14-01: จำแนกความตั้งใจด้วยกฎและคำตัวอย่าง (D-14-01 กล่องนี้เป็นโค้ด ไม่ใช่ LLM)
รองรับ REQ-AI-005 (5 เรื่องที่รับ นอกนั้นส่งต่อ) REQ-AI-007 (เรื่องที่ห้าม) REQ-AI-012 เงื่อนไขที่ 1 (ไม่แน่ใจ = หยุดและส่งต่อ)
คำตัวอย่างอยู่ใน specs/005-ai-assistant/prompts/intent-examples-<รุ่น>.json รุ่นเดียวกับข้อความสั่ง"""
import re
from dataclasses import dataclass

from app.assistant import prompts

# ลำดับสำคัญ: เรื่องที่ห้ามและนอกขอบเขตมาก่อน (ถ้าข้อความมีทั้งสถานะและขอเบอร์ ต้องปฏิเสธ)
PRIORITY = ("forbidden_phone", "forbidden_refund_deal", "forbidden_promise", "out_of_scope", "handoff_request",
            "reschedule", "reschedule_policy", "refund_timing", "cancel", "eta", "technician_name", "status")
FORBIDDEN = ("forbidden_phone", "forbidden_refund_deal", "forbidden_promise")
ANSWERABLE = ("status", "eta", "technician_name", "cancel", "reschedule_policy", "refund_timing", "reschedule")

JOB_ID = re.compile(r"(?:#|งาน\s*(?:หมายเลข|เลขที่|เลข|ที่)?\s*#?)\s*(\d{1,6})")
TIME_LIKE = re.compile(r"\d{1,2}[:.]\d{2}|\d{1,2}\s*โมง|โมง|บ่าย|เช้า|พรุ่งนี้|มะรืน|วันที่|วัน(?:จันทร์|อังคาร|พุธ|พฤหัส|ศุกร์|เสาร์|อาทิตย์)")


@dataclass
class Intent:
    name: str              # ชื่อใน PRIORITY หรือ unclear
    confidence: float
    job_id: int | None
    matched: list[str]
    normalized: str


def classify(text: str, version: str | None = None) -> Intent:
    norm = prompts.normalize(text, version)
    squeezed = norm.replace(" ", "")
    words = prompts.lexicon(version)["intents"]
    hits = {name: [w for w in words[name] if w.lower().replace(" ", "") in squeezed] for name in PRIORITY}
    found = [n for n in PRIORITY if hits[n]]
    m = JOB_ID.search(norm)
    job_id = int(m.group(1)) if m else None
    if not found:
        return Intent("unclear", 0.0, job_id, [], norm)
    name = found[0]
    # "เลื่อน" พร้อมวันเวลา = ขอเลื่อนจริง ไม่ใช่ถามเงื่อนไข
    if name == "reschedule_policy" and TIME_LIKE.search(norm) and "กี่" not in norm:
        name = "reschedule"
    # "เงื่อนไขการเลื่อนนัดเป็นยังไง" ไม่มีวันเวลา = ถามเงื่อนไข
    if name == "reschedule" and hits["reschedule_policy"] and not TIME_LIKE.search(norm):
        name = "reschedule_policy"
    # "ยกเลิกแล้วเงินเข้ากี่วัน" คือถามเวลาคืนเงิน "ยกเลิก" อย่างเดียวคือถามเงื่อนไขยกเลิก
    confidence = 0.9 if len(found) == 1 else 0.75
    return Intent(name, confidence, job_id, hits[name], norm)
