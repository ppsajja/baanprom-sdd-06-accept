"""REQ-PRV-002 เบอร์โทรลูกค้าห้ามปรากฏใน log ของระบบ
ทุกโมดูลต้องขอ logger จากที่นี่ ตัวกรองจะแทนเบอร์โทรที่หลุดมาด้วย [phone]"""
import logging
import re

PHONE_PATTERN = re.compile(r"0\d{1,2}[- ]?\d{3}[- ]?\d{4}")


class PhoneFilter(logging.Filter):
    # รองรับ REQ-PRV-002: กรองข้อความ log ก่อนเขียน
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = PHONE_PATTERN.sub("[phone]", str(record.msg))
        if isinstance(record.args, dict):
            # logging เก็บ arg เดี่ยวที่เป็น dict ไว้ทั้งก้อน ให้แปลงเป็นข้อความแล้วกรอง
            record.args = (PHONE_PATTERN.sub("[phone]", str(record.args)),)
        elif record.args:
            record.args = tuple(PHONE_PATTERN.sub("[phone]", str(a)) for a in record.args)
        return True


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(f, PhoneFilter) for f in logger.filters):
        logger.addFilter(PhoneFilter())
    return logger


# ---- CR-07 REQ-OP-005 บรรทัดที่ 3: log แบบมีโครงสร้าง ห้ามมีเบอร์โทร ที่อยู่ และพิกัดของลูกค้า ----
# ใช้รายการช่องที่อนุญาต (allowlist) แทนการไล่กรองทีหลัง ช่องที่ไม่อยู่ในรายการถูกทิ้งและนับไว้ใน dropped
# เหตุผล: ที่อยู่และพิกัดไม่มีรูปแบบตายตัวแบบเบอร์โทร จึงกรองด้วย regex ไม่ได้ (GAP-22)
import json

ALLOWED_LOG_FIELDS = frozenset({
    "event", "endpoint", "method", "status", "ms", "job_id", "customer_id", "technician_id",
    "slot_id", "rule", "amount", "result", "count", "attempt", "reason", "actor_role", "actor_id",
    # CR-09 (REQ-AI-013): รหัสและรุ่นของผู้ช่วย ไม่มีข้อความที่ลูกค้าพิมพ์และไม่มีคำตอบ (ข้อความเหล่านั้นอยู่ในบันทึกคำตอบที่ปิดบังแล้ว)
    "conversation_id", "turn_id", "proposal_id", "ticket_id", "intent", "tool", "guard", "prompt_version", "model_version",
})


def log_event(logger: logging.Logger, event: str, **fields) -> dict:
    """เขียน log 1 บรรทัดเป็น JSON มีเฉพาะช่องใน ALLOWED_LOG_FIELDS คืน dict ที่เขียนจริง (ให้ test ตรวจได้)"""
    record = {"event": event}
    dropped = []
    for key, value in fields.items():
        if key in ALLOWED_LOG_FIELDS:
            record[key] = value
        else:
            dropped.append(key)
    if dropped:
        record["dropped"] = sorted(dropped)
    line = PHONE_PATTERN.sub("[phone]", json.dumps(record, ensure_ascii=False, default=str))
    logger.info(line)
    return record


# ---- CR-09 REQ-AI-013 (Q-57): ปิดบังข้อมูลส่วนบุคคลในข้อความที่ลูกค้าพิมพ์ ก่อนเก็บในบันทึกคำตอบและบันทึกการกระทำ ----
# ลูกค้าพิมพ์เบอร์โทร อีเมล หรือเลขบัตรประชาชนของตัวเองมาได้ ระบบไม่เก็บค่าเหล่านั้น (SH-05 ใน EV-047)
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
THAI_ID_PATTERN = re.compile(r"\b\d[- ]?\d{4}[- ]?\d{5}[- ]?\d{2}[- ]?\d\b")
LONG_DIGITS_PATTERN = re.compile(r"\d{9,}")


def mask_text(text: str) -> str:
    text = EMAIL_PATTERN.sub("[email]", text)
    text = THAI_ID_PATTERN.sub("[id]", text)
    text = PHONE_PATTERN.sub("[phone]", text)
    return LONG_DIGITS_PATTERN.sub("[number]", text)
