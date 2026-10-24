"""CR-07: งานที่ต้องทำทุก 1 นาทีในระบบจริง (main.py เรียกในงานเบื้องหลัง ยกเว้นโหมด test ที่ test เรียก tick เอง)
ลำดับ: ปิดล็อกที่หมดอายุ (REQ-QA-010) ส่งข้อความที่ค้าง (REQ-QA-010) ทำคำขอลบ (REQ-PRV-010)
ลบบันทึกการส่งเบอร์ที่เก่ากว่า 90 วัน (REQ-SEC-010) แล้วตรวจเกณฑ์เตือน (REQ-OP-005, REQ-SEC-010)
CR-09: ลบบันทึกคำตอบและบันทึกการกระทำของผู้ช่วยที่อายุเกิน 180 วัน (REQ-AI-013)"""
from datetime import datetime

from app.technicians.service import release_expired_holds
from app.notify.queue import queue, get_notifier
from app.erasure.service import process_due
from app.ops import audit, alerts
from app.ops.metrics import metrics
from app.assistant import records as assistant_records


def tick(db, now: datetime) -> None:
    release_expired_holds(db, now)
    db.commit()
    queue.deliver_due(get_notifier(), now)
    process_due(db, now, get_notifier())
    audit.purge_phone_view_log(db, now)
    assistant_records.purge(db, now)
    alerts.evaluate(db, metrics, now)
