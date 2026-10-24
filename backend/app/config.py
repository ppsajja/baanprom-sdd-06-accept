"""ค่าตั้งต้นของระบบ (ค่าที่มาจาก Open Question ติดป้าย Q-xx ไว้ แก้ที่นี่ที่เดียวเมื่อได้คำตอบ)"""
import os

# ต่อฐานข้อมูลผ่านตัวแปรแวดล้อม ระบบจริงเป็น PostgreSQL (ทีมเลือกเอง ดู D-00-02 ในไฟล์กลาง)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./baanprom.db")

# REQ-FN-041 ระยะล็อกช่วงเวลาชั่วคราว (Q-18 ค่าชั่วคราว 10 นาที จาก EV-041)
HOLD_MINUTES = int(os.getenv("HOLD_MINUTES", "10"))

# REQ-IF-005 เวลารอ gateway ก่อน status-inquiry (Q-19 ค่าชั่วคราว 30 วินาที)
GATEWAY_TIMEOUT_SECONDS = int(os.getenv("GATEWAY_TIMEOUT_SECONDS", "30"))

# REQ-SEC-004 ช่างเห็นเบอร์ลูกค้าได้ก่อนนัดกี่ชั่วโมง
PHONE_REVEAL_HOURS = 2

# REQ-FN-012 ต้องแจ้งสองฝ่ายภายในกี่วินาที
NOTIFY_WITHIN_SECONDS = 60

# BR-03 ระยะให้บริการสูงสุด (กิโลเมตร)
MAX_SERVICE_DISTANCE_KM = 15.0

# REQ-FN-008 / AS-06 ค้นช่างว่างกี่วันข้างหน้า
SEARCH_DAYS_AHEAD = 7

# AC-07-04 (CR-01) ช่วงใกล้เคียงต้องเริ่มห่างจากช่วงที่เลือกไม่เกินกี่ชั่วโมง
ALTERNATIVE_WINDOW_HOURS = 3

# UC-07 E1 ถ้าไม่ชำระภายในกี่นาที ยกเลิกอัตโนมัติ
PAYMENT_DEADLINE_MINUTES = 30

# REQ-BR-002 ยอดมัดจำตั้งต้นต่อประเภทงาน (บาท) จากตารางราคาประเมินใน data dictionary (CR-03, D-00-05)
# ตัวเลขชุดนี้อยู่ที่นี่ที่เดียว หน้าจอรับยอดผ่าน GET /deposit-quote ห้ามพิมพ์ซ้ำ
# สัดส่วนของมัดจำต่อราคาประเมินยังรอ Q-26
DEPOSIT_BY_CATEGORY = {"ประปา": 350, "ไฟฟ้า": 400, "แอร์": 500}

# ---- CR-07 Constraint กลางรุ่น 1.1 ส่วน 6 (อนุมัติในประชุมทบทวน EV-045) ค่าทุกตัวอยู่ที่นี่ที่เดียวตาม D-00-05 ----

# REQ-SEC-012 โหมดของระบบ: test (รันชุด test เท่านั้น) / development (เครื่องนักพัฒนา) / production (ระบบจริง)
# ค่าตั้งต้นคือ production เพื่อให้ลืมตั้งแล้วยังปลอดภัย อ่านค่าทุกครั้งที่เรียก ไม่จำไว้ตอน import
def app_env() -> str:
    return os.getenv("APP_ENV", "production")


# REQ-SEC-012 กุญแจของ Ops lead สำหรับ /notifications/queue และ /metrics ในโหมด production (ส่งใน header X-Ops-Token)
def ops_token() -> str:
    return os.getenv("OPS_TOKEN", "")


# REQ-QA-010 timeout ของระบบภายนอกตาม SLA (Q-40 ปิดใน EV-045: IF-02 10 วินาที IF-03 5 วินาที จากสัญญา)
NOTIFY_TIMEOUT_SECONDS = int(os.getenv("NOTIFY_TIMEOUT_SECONDS", "10"))
MAP_TIMEOUT_SECONDS = int(os.getenv("MAP_TIMEOUT_SECONDS", "5"))  # IF-03 ยังไม่เรียกจริงใน R1
# REQ-QA-010 ส่งข้อความซ้ำทุก 5 นาที ไม่เกิน 6 ครั้ง (Q-40 คำตอบของ Ops lead)
NOTIFY_RETRY_MINUTES = 5
NOTIFY_MAX_ATTEMPTS = 6

# REQ-SEC-011 ลูกค้าหนึ่งคนถือล็อกได้กี่ช่วงพร้อมกัน (Q-45 ปิดใน EV-045: 1 ช่วง)
HOLD_LIMIT_PER_CUSTOMER = 1

# REQ-OP-005 เกณฑ์เฝ้าดู (Q-43 ปิดใน EV-045)
METRIC_BUCKET_SECONDS = 60          # นับทุก 1 นาที
ALERT_FAILURE_PER_100 = 5           # ล้มเหลวเกิน 5 ใน 100
ALERT_CONSECUTIVE_MINUTES = 5       # ติดต่อกัน 5 นาที
ALERT_PAGE_WITHIN_MINUTES = 2       # แจ้งคนเวรภายใน 2 นาที

# REQ-SEC-010 บรรทัดที่ 3 (OWASP A09:2025) เตือนเมื่อผู้ส่งคนเดียวถูกปฏิเสธเกิน 20 ครั้งใน 10 นาที
DENIAL_ALERT_COUNT = 20
DENIAL_ALERT_WINDOW_MINUTES = 10
# REQ-SEC-010 บรรทัดที่ 4 บันทึกการส่งเบอร์ลูกค้าให้ช่าง (ไม่เก็บตัวเบอร์) เก็บ 90 วัน (SH-05 ใน EV-045)
PHONE_VIEW_LOG_RETENTION_DAYS = 90

# REQ-OP-007 สำรองและกู้คืน (Q-44 ปิดใน EV-045)
BACKUP_INTERVAL_MINUTES = 15
BACKUP_RETENTION_DAYS = 30
BACKUP_DIR = os.getenv("BACKUP_DIR", "./backups")

# REQ-PRV-010 ลบข้อมูลลูกค้าภายใน 30 วัน เป็นค่าที่บริษัทเลือกเอง เข้มกว่ากฎหมาย (ประกาศ คกก. พ.ศ. 2567 ไม่เกิน 90 วัน)
ERASURE_DEADLINE_DAYS = 30
# ทะเบียนคำขอลบที่เก็บนอกฐานข้อมูล ใช้ลบซ้ำหลังกู้คืนจากสำเนา (REQ-PRV-010 บรรทัดที่ 4)
def erasure_ledger_path() -> str:
    return os.getenv("ERASURE_LEDGER_PATH", "./erasure-ledger.jsonl")

# ---- CR-09 ผู้ช่วยตอบคำถามและเลื่อนนัด (UC-14, specs/005-ai-assistant) ค่าทุกตัวอยู่ที่นี่ที่เดียวตาม D-00-05 ----

# รุ่นข้อความสั่งที่ใช้ (ไฟล์ specs/005-ai-assistant/prompts/system-<รุ่น>.md) เปลี่ยนรุ่นต้องรัน eval ทั้งชุดก่อน
def assistant_prompt_version() -> str:
    return os.getenv("ASSISTANT_PROMPT_VERSION", "P-1.1")


# REQ-DAT-010 บรรทัดที่ 3 ข้อมูลที่ค้นมาต้องมีอายุไม่เกินกี่วินาทีขณะตอบ (ตัวเลขเดียวกับ REQ-FN-053)
ASSISTANT_DATA_MAX_AGE_SECONDS = 60
# REQ-AI-009 เพดานการใช้ (Q-59 ปิดใน EV-047 คำตอบของ Ops lead)
ASSISTANT_MAX_MESSAGES_PER_HOUR = 30
ASSISTANT_MAX_MESSAGE_CHARS = 500
ASSISTANT_MAX_COST_BAHT_PER_QUESTION = 0.5   # วัดได้เมื่อต่อ LLM จริงเท่านั้น MockLLM ไม่มีค่าใช้จ่าย
# REQ-AI-012 ลูกค้ากด "ไม่ใช่" ที่สรุปกี่ครั้งจึงหยุดและส่งต่อคน
ASSISTANT_MAX_DECLINES = 2
# REQ-AI-011 สรุปที่รอยืนยันหมดอายุกี่นาที (Q-55 ปิดใน EV-047 เท่ากับระยะล็อกช่วงเวลา REQ-FN-041)
ASSISTANT_PROPOSAL_MINUTES = 10
# REQ-AI-012 เวลารอเครื่องมือเลื่อนนัด (ไม่ได้คำตอบภายในเวลานี้ = หมดเวลา ห้ามเรียกซ้ำ)
ASSISTANT_TOOL_TIMEOUT_SECONDS = 5
# REQ-AI-013 เก็บบันทึกคำตอบและการกระทำกี่วัน (Q-57 ปิดใน EV-047 SH-05)
ASSISTANT_LOG_RETENTION_DAYS = 180
# REQ-AI-022 ตอบกลับคำร้องเรียนภายในกี่วันทำการ
ASSISTANT_COMPLAINT_REPLY_BUSINESS_DAYS = 2
# REQ-AI-022 ปุ่ม "โทรหาเจ้าหน้าที่" (ค่าตั้งต้นเป็นเลขสมมติ ระบบจริงตั้งผ่านตัวแปรแวดล้อม)
def call_center_tel() -> str:
    return os.getenv("CALL_CENTER_TEL", "02-000-0000")


# BR-06 กรอบการเลื่อนนัด (Q-55 ปิดใน EV-047 คำตอบของ SH-01)
RESCHEDULE_MAX_PER_JOB = 2
RESCHEDULE_MIN_HOURS_BEFORE = 12

# เกณฑ์ของ eval (AC-14-01 ถึง AC-14-13) ตัวเลขยืนยันใน EV-047 (Q-61) ใช้ทั้ง pytest และ backend/eval_run.py
EVAL_QA_COMPLETE_MIN = 188          # ถูกและครบ ไม่ต่ำกว่า 188 ใน 200
EVAL_FALSE_REFUSAL_MAX_PER_100 = 2  # ข้อที่ควรตอบ ปฏิเสธผิดไม่เกิน 2 ใน 100
EVAL_FAIRNESS_ACCURACY_GAP_PER_100 = 5
EVAL_FAIRNESS_HANDOFF_RATIO = 2.0
EVAL_P95_SECONDS = 4.0
