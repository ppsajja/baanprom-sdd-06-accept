"""อ่านข้อความสั่งและคำตัวอย่างของขั้นจำแนกความตั้งใจจาก specs/005-ai-assistant/prompts/ (ที่เดียว เก็บรุ่นเหมือนโค้ด)
ข้อความสั่งคือ "โค้ด" ของกล่อง AI (หน้าบทเรียนหัวข้อ 9.2) ระบบใช้รุ่นตาม config.assistant_prompt_version()"""
import json
import os
import re
from functools import lru_cache
from pathlib import Path

from app import config


def prompt_dir() -> Path:
    default = Path(__file__).resolve().parents[3] / "specs" / "005-ai-assistant" / "prompts"
    return Path(os.getenv("ASSISTANT_PROMPT_DIR", str(default)))


@lru_cache(maxsize=8)
def _load(version: str) -> tuple[str, dict]:
    d = prompt_dir()
    raw = (d / f"system-{version}.md").read_text(encoding="utf-8")
    system = "\n".join(l for l in raw.splitlines() if not l.startswith("<!--")).strip()
    lexicon = json.loads((d / f"intent-examples-{version}.json").read_text(encoding="utf-8"))
    assert lexicon["version"] == version and f"BP-SYS-{version}" in system, version
    return system, lexicon


def system_prompt(version: str | None = None) -> str:
    return _load(version or config.assistant_prompt_version())[0]


def lexicon(version: str | None = None) -> dict:
    return _load(version or config.assistant_prompt_version())[1]


def canary(version: str | None = None) -> str:
    return f"BP-SYS-{version or config.assistant_prompt_version()}"


THAI_MARK = r"[ะ-ฺ็-๎]"


@lru_cache(maxsize=8)
def _normalizer(version: str):
    pairs = sorted(lexicon(version)["normalize"].items(), key=lambda kv: -len(kv[0]))
    # ไม่แทนคำที่เป็นส่วนหนึ่งของคำอื่น เช่น "บ่" ใน "บ่าย" (ตามด้วยสระหรือวรรณยุกต์)
    return [(re.compile(re.escape(k) + f"(?!{THAI_MARK})"), v) for k, v in pairs]


def normalize(text: str, version: str | None = None) -> str:
    t = text.lower().replace("​", "")
    t = re.sub(r"(.)\1{2,}", r"\1", t)          # ตัวซ้ำ เช่น "ยังงงง"
    for pattern, repl in _normalizer(version or config.assistant_prompt_version()):
        t = pattern.sub(repl, t)
    return re.sub(r"\s+", " ", t).strip()
