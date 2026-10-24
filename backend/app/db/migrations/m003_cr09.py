"""CR-09 (T-01 ของ 005): ตาราง job_reschedules และตารางของผู้ช่วย (assistant_*) ทุกตารางเป็นตารางใหม่
ไม่มีคอลัมน์ใหม่ในตารางเดิม จึงไม่มี ALTER TABLE เรียก m002 ก่อนเพื่อให้ฐานข้อมูลเก่าได้ครบทุกขั้น"""
from app.db.migrations import m002_cr07


def upgrade(engine) -> None:
    m002_cr07.upgrade(engine)  # create_all ใน m002 สร้างตารางใหม่ของ CR-09 ให้ด้วย เพราะ models.py มีครบแล้ว
