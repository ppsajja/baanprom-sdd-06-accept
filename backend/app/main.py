"""FastAPI app ของบ้านพร้อม R1: UC-07 (specs/002-booking), UC-09 (specs/003-job-status), UC-08 (specs/004-cancel-refund)
CR-09: UC-14 ผู้ช่วยตอบคำถามและเลื่อนนัด (specs/005-ai-assistant) app/assistant และ POST /jobs/{id}/reschedule
CR-07 (Constraint กลางรุ่น 1.1 ส่วน 6):
- REQ-SEC-012 โหมด production ปิด /docs /redoc /openapi.json และให้ /notifications/queue /metrics /ops/* ใช้ X-Ops-Token
- REQ-OP-005 ตัวนับคำขอต่อ endpoint ต่อนาที (middleware) และงานเบื้องหลังทุก 1 นาที (ops/scheduler.py)
- REQ-OP-001 /health และ /ready อยู่ใน ops/router.py
- OWASP API9:2023 บัญชี endpoint อยู่ใน docs/srs/operations.md ส่วน "บัญชี endpoint" POST /jobs/{id}/cancel ถูกปิด
  (router เดิมใน app/refund/router.py ถูกลบ การยกเลิกโดยลูกค้ามีทางเดียวคือ customer-cancel ของ 004)"""
import asyncio
import time
from contextlib import asynccontextmanager, suppress
from datetime import datetime

from fastapi import Depends, FastAPI, Request

from app import config
from app.db.session import engine, SessionLocal
from app.db.migrations.m003_cr09 import upgrade
from app.technicians.router import router as technicians_router
from app.booking.router import router as booking_router
from app.jobstatus.router import router as jobstatus_router
from app.cancel.router import router as cancel_router
from app.erasure.router import router as erasure_router
from app.ops.router import router as ops_router
from app.assistant.router import router as assistant_router, ops_router as assistant_ops_router
from app.ops.guard import require_ops
from app.ops.metrics import metrics
from app.ops import scheduler
from app.notify.queue import queue


async def _every_minute() -> None:
    # งานเบื้องหลังของระบบจริง (ไม่รันในโหมด test เพราะ test เรียก scheduler.tick เองด้วยเวลาจำลอง)
    while True:
        await asyncio.sleep(60)
        db = SessionLocal()
        try:
            scheduler.tick(db, datetime.now())
        finally:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    upgrade(engine)  # T-01 สร้างตาราง m002 ของ CR-07 (T-17 ของ 002) และ m003 ของ CR-09 (T-01 ของ 005)
    task = None if config.app_env() == "test" else asyncio.create_task(_every_minute())
    yield
    if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


def create_app() -> FastAPI:
    production = config.app_env() == "production"
    app = FastAPI(title="บ้านพร้อม R1 - UC-07 จองงาน, UC-09 สถานะงาน, UC-08 ยกเลิกและคืนเงิน, UC-14 ผู้ช่วย", lifespan=lifespan,
                  # รองรับ REQ-SEC-012 (AC-00-06): หน้าเอกสารที่ FastAPI เปิดให้เอง ปิดในระบบจริง
                  docs_url=None if production else "/docs",
                  redoc_url=None if production else "/redoc",
                  openapi_url=None if production else "/openapi.json")

    @app.middleware("http")
    async def count_requests(request: Request, call_next):
        # รองรับ REQ-OP-005 บรรทัดที่ 1 (AC-00-01): นับตามแม่แบบของ path ไม่ใช่ path จริง
        t0 = time.perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        endpoint = f"{request.method} {route.path}" if route is not None else f"{request.method} (ไม่มี route)"
        empty = endpoint == "GET /technicians" and response.headers.get("x-result-count") == "0"
        metrics.record(endpoint, response.status_code, (time.perf_counter() - t0) * 1000, datetime.now(), empty)
        return response

    app.include_router(ops_router)
    app.include_router(technicians_router)
    app.include_router(booking_router)
    app.include_router(jobstatus_router)   # CR-05 (specs/003-job-status)
    app.include_router(cancel_router)      # CR-06 (specs/004-cancel-refund)
    app.include_router(erasure_router)     # CR-07 REQ-PRV-010
    app.include_router(assistant_router)   # CR-09 (specs/005-ai-assistant) UC-14 ผู้ช่วย
    app.include_router(assistant_ops_router)  # CR-09 REQ-AI-022 ปุ่มหยุด และตั๋วของ call center (X-Ops-Token)

    @app.get("/notifications/queue", dependencies=[Depends(require_ops)])
    def notifications():
        # รองรับ REQ-FN-012 ใช้ตรวจใน test และหน้าแอดมิน | CR-07 REQ-SEC-012 ในระบบจริงต้องมี X-Ops-Token
        return queue.as_dicts()

    return app


app = create_app()
