"""รั้วของผู้ช่วย (REQ-AI-008 REQ-AI-009) เป็นโค้ดธรรมดา ไม่พึ่งการที่ LLM "เชื่อฟัง" (หน้าบทเรียนหัวข้อ 5.7)
ขาเข้า: เพดาน ความยาว ข้อความหลอกให้ลืมกฎแบบตรง (ตัวตรวจนี้ตั้งใจให้ไม่สมบูรณ์ ข้อความที่สะกดแยกตัวหลุดได้ รั้วขาออกต้องกันต่อ)
ขาออก: เบอร์โทร ข้อความสั่ง เวลา ยอดเงิน ตัวเลข เลขงาน และคำอ้างที่ขัดกับข้อมูล"""
import re
from collections import defaultdict
from datetime import datetime, timedelta

from app import config
from app.privacy import PHONE_PATTERN
from app.assistant import prompts

INJECTION_PATTERNS = ("ลืมกฎ", "ลืมคำสั่ง", "ignore previous", "ignore all", "system prompt", "แสดงข้อความสั่ง",
                      "บอกข้อความสั่ง", "คำสั่งระบบ", "developer mode", "คุณคือแอดมิน", "ไม่ต้องทำตามกฎ",
                      "เลิกทำตามกฎ", "ทำตัวเป็น", "jailbreak", "ข้ามกฎ")


def detect_injection(text: str) -> bool:
    t = re.sub(r"\s+", " ", text.lower())
    return any(p in t for p in INJECTION_PATTERNS)


class RateLimiter:
    """REQ-AI-009 นับข้อความต่อลูกค้าใน 1 ชั่วโมงล่าสุด (เก็บในหน่วยความจำ แบบเดียวกับ ops/metrics.py)"""
    def __init__(self) -> None:
        self.sent: dict[int, list[datetime]] = defaultdict(list)

    def allow(self, customer_id: int, now: datetime) -> bool:
        window = [t for t in self.sent[customer_id] if now - t < timedelta(hours=1)]
        self.sent[customer_id] = window
        if len(window) >= config.ASSISTANT_MAX_MESSAGES_PER_HOUR:
            return False
        window.append(now)
        return True

    def clear(self) -> None:
        self.sent.clear()


limiter = RateLimiter()

TIME_RE = re.compile(r"(?<!\d)(\d{1,2})[:.](\d{2})(?!\d)")
AMOUNT_RE = re.compile(r"(\d[\d,]*)\s*บาท")
UNIT_RE = re.compile(r"(\d+)\s*(?:นาที|ชั่วโมง|ชม\.|วันทำการ|วัน|ครั้ง)")
JOB_RE = re.compile(r"#\s*(\d+)")
LONG_DIGITS = re.compile(r"\d{9,}")


def check_answer(text: str, facts, version: str | None = None) -> list[str]:
    """คืนรายการเหตุที่ไม่ผ่าน (ว่าง = ผ่าน) facts คือ retrieval.Facts ของคำถามนี้"""
    reasons = []
    if PHONE_PATTERN.search(text) or LONG_DIGITS.search(text.replace("-", "").replace(" ", "")):
        reasons.append("phone")
    system = prompts.system_prompt(version)
    if prompts.canary(version) in text or "BP-SYS" in text or any(
            len(line) > 20 and line in text for line in system.splitlines()):
        reasons.append("hidden_context")
    times = {f"{int(h):02d}:{m}" for h, m in TIME_RE.findall(text)}
    if times - facts.times:
        reasons.append("ungrounded_time")
    amounts = {a.replace(",", "") for a in AMOUNT_RE.findall(text)}
    if amounts - facts.numbers:
        reasons.append("ungrounded_amount")
    if set(UNIT_RE.findall(text)) - facts.numbers:
        reasons.append("ungrounded_number")
    if {int(j) for j in JOB_RE.findall(text)} - facts.job_ids:
        reasons.append("other_job")
    c = facts.data.get("cancel") or {}
    full = c.get("allowed") and c.get("refund_amount") == facts.data.get("deposit")
    if ("เต็มจำนวน" in text or "คืนเต็ม" in text) and not full:
        reasons.append("false_claim")
    if re.search(r"(ยกเลิก|คืนเงิน|เลื่อน)\S*\s*(งาน\s*#?\d+\s*)?ให้แล้ว", text):
        reasons.append("false_claim")
    return sorted(set(reasons))
