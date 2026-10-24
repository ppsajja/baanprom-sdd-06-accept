"""ขั้น 3 ของ MD-SEQ-14-01: ค้นข้อมูลจริง จุดเดียวที่ข้อมูลเข้าผู้ช่วย REQ-DAT-010 ทุกบรรทัดถูกบังคับที่นี่
1 ข้อมูลงานมาจากตาราง jobs ผ่านฟังก์ชันเดิมของ booking และ refund ไม่มีแหล่งอื่น นโยบายมาจากคลัง policies/ ที่ทำจาก rules.md (Q-63)
2 ยอดคืนมาจาก refund/service.quote ตัวเดียวกับหน้ายกเลิก (BR-01 รุ่นใน Baseline)
3 Facts มีเวลาที่ค้น (fetched_at) ผู้ใช้ต้องค้นใหม่ถ้าเก่ากว่า 60 วินาที (is_fresh)
4 ส่งเฉพาะงานของผู้ถาม และช่องที่อนุญาต (ALLOWED_FIELDS) เท่านั้น ไม่มีชื่อ เบอร์ ที่อยู่ หรือพิกัดของลูกค้าตั้งแต่ต้น
5 ข้อมูลที่ระบบไม่มี (เวลาที่ช่างจะถึง ตำแหน่งช่าง จำนวนวันคืนเงิน) ใส่เป็น None ให้เห็นชัดว่า "ไม่มี" """
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import select

from app import config
from app.db.models import Job, JobStatusHistory, Technician
from app.jobstatus.transitions import STATUS_TH
from app.refund import service as refund_service
from app.booking.service import reschedules_used

MONTH_TH = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
ALLOWED_FIELDS = frozenset({"job_id", "status", "status_th", "date", "time", "technician", "category", "deposit",
                            "eta", "technician_location", "refund_days", "cancel", "reschedule"})
CLOSED = ("cancelled", "auto_cancelled", "done")
POLICY_DIR = Path(__file__).resolve().parent / "policies"
# ข้อความที่ดูเหมือนคำสั่งในข้อมูลของระบบ (คำสั่งแฝง LLM01 แบบ indirect และ LLM05) ตัดออกก่อนส่งให้ LLM
INSTRUCTION_IN_DATA = re.compile(r"\(?\s*(?:ระบบ|system|คำสั่ง|instruction)\s*[:：].*$|\(.*(?:ลืมกฎ|ให้บอก|ignore).*\)", re.I)


def fmt_date(dt: datetime) -> str:
    return f"{dt.day} {MONTH_TH[dt.month]}"


def fmt_time(dt: datetime) -> str:
    return f"{dt:%H:%M}"


def sanitize(value: str) -> str:
    return INSTRUCTION_IN_DATA.sub("", value).strip()


@dataclass
class Facts:
    data: dict
    sources: list[dict]
    fetched_at: datetime
    policies: list[dict] = field(default_factory=list)

    @property
    def job_ids(self) -> set[int]:
        return {self.data["job_id"]} if self.data.get("job_id") else set()

    def text(self) -> str:
        return json.dumps(self.data, ensure_ascii=False, default=str) + " " + " ".join(p["text"] for p in self.policies)

    @property
    def times(self) -> set[str]:
        return set(re.findall(r"\b\d{2}:\d{2}\b", self.text()))

    @property
    def numbers(self) -> set[str]:
        return set(re.findall(r"\d+", self.text()))

    def is_fresh(self, now: datetime) -> bool:
        return now - self.fetched_at <= timedelta(seconds=config.ASSISTANT_DATA_MAX_AGE_SECONDS)


def resolve_job(db, customer_id: int, job_id: int | None, context_job_id: int | None) -> tuple[Job | None, str]:
    """คืน (งาน, ผล) ผล = ok / not_owned / none ห้ามคืนงานของคนอื่นไม่ว่ากรณีใด (E-006)"""
    if job_id is not None:
        job = db.get(Job, job_id)
        if job is None or job.customer_id != customer_id:
            return None, "not_owned"
        return job, "ok"
    if context_job_id is not None:
        job = db.get(Job, context_job_id)
        if job is not None and job.customer_id == customer_id:
            return job, "ok"
    jobs = db.scalars(select(Job).where(Job.customer_id == customer_id).order_by(Job.scheduled_start)).all()
    if not jobs:
        return None, "none"
    active = [j for j in jobs if j.status not in CLOSED]
    return (active[0] if active else jobs[-1]), "ok"


def last_update(db, job: Job) -> datetime:
    row = db.scalars(select(JobStatusHistory).where(JobStatusHistory.job_id == job.id)
                     .order_by(JobStatusHistory.id.desc())).first()
    return row.at if row else job.created_at


def job_facts(db, job: Job, intent: str, now: datetime, normalized: str = "") -> Facts:
    tech = db.get(Technician, job.technician_id)
    data = {"job_id": job.id, "status": job.status, "status_th": STATUS_TH.get(job.status, job.status),
            "date": fmt_date(job.scheduled_start), "time": fmt_time(job.scheduled_start),
            "technician": sanitize(tech.name) if tech else None, "category": job.category,
            "deposit": job.deposit_amount, "eta": None, "technician_location": None}
    if intent == "cancel":
        closed = job.status in ("cancelled", "auto_cancelled")
        d = refund_service.quote(job, "customer", now)
        allowed = (not closed) and d.outcome in ("cancelled", "auto_cancelled")
        msg = "" if allowed else (refund_service.MSG_R3_PENDING if d.outcome == "pending_question"
                                  else refund_service.MSG_R6_NOT_ALLOWED)
        data["cancel"] = {"already_closed": closed, "allowed": allowed, "rule": d.rule,
                          "refund_amount": (d.refund_amount or 0) if allowed else None, "message": msg}
    if intent in ("reschedule_policy", "reschedule"):
        data["reschedule"] = {"max": config.RESCHEDULE_MAX_PER_JOB, "min_hours": config.RESCHEDULE_MIN_HOURS_BEFORE,
                              "used": reschedules_used(db, job)}
    if intent == "refund_timing":
        data["refund_days"] = None  # Q-35
    assert set(data) <= ALLOWED_FIELDS, set(data) - ALLOWED_FIELDS
    sources = [{"label": f"สถานะงาน #{job.id}", "updated_at": last_update(db, job).isoformat()}]
    facts = Facts(data, sources, now, policies_for(intent, normalized))
    for p in facts.policies:
        sources.append({"label": f"{p['title']} ({p['source']})", "updated_at": p["updated"]})
    return facts


# ---- คลังนโยบาย (ค้นด้วยคำ ไม่ใช้ดัชนีเวกเตอร์) ----

def load_policies(directory: Path = POLICY_DIR) -> list[dict]:
    docs = []
    for path in sorted(directory.glob("*.md")):
        if path.name == "README.md":
            continue
        raw = path.read_text(encoding="utf-8")
        _, head, body = raw.split("---", 2)
        meta = dict(line.split(":", 1) for line in head.strip().splitlines())
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        meta["intents"] = meta["intents"].split()
        meta["keywords"] = meta["keywords"].split()
        meta["text"] = body.strip()
        meta["file"] = path.name
        docs.append(meta)
    return docs


def policies_for(intent: str, normalized: str) -> list[dict]:
    """เฉพาะเอกสาร status: current คะแนน = ตรงความตั้งใจ 2 คะแนน + คำที่พบในคำถามคำละ 1 คะแนน เอา 1 เอกสารที่ได้คะแนนสูงสุด"""
    scored = []
    for d in load_policies():
        if d["status"] != "current":
            continue
        score = (2 if intent in d["intents"] else 0) + sum(1 for k in d["keywords"] if k in normalized)
        if intent in d["intents"]:
            scored.append((score, d["id"], d))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [scored[0][2]] if scored else []


def rules_section_hash(rules_path: Path, br: str) -> str:
    """sha256 ของส่วน "## BR-xx" ใน rules.md ใช้ตรวจว่าคลังนโยบายเปลี่ยนพร้อม BR (REQ-DAT-010 บรรทัดที่ 2)"""
    text = rules_path.read_text(encoding="utf-8")
    m = re.search(rf"^## {br}\b.*?(?=^## |\Z)", text, re.S | re.M)
    return hashlib.sha256(m.group(0).strip().encode("utf-8")).hexdigest()
