# baanprom-sdd-06-accept

repo ตัวอย่างของรายวิชา 517511-266 Requirement Engineering (AI-Native RE)
ภาควิชาคอมพิวเตอร์ คณะวิทยาศาสตร์ มหาวิทยาลัยศิลปากร

เคส: บ้านพร้อม (แพลตฟอร์มจองช่างซ่อมบ้าน) มี 4 feature คือ UC-07 จองงานบริการซ่อมบำรุง UC-09 ช่างอัปเดตสถานะงาน UC-08 ลูกค้ายกเลิกการจองและรับเงินคืน และ UC-14 ผู้ช่วยตอบคำถามลูกค้าและเลื่อนนัด (ส่วนแรกของระบบที่มี AI อยู่ข้างใน)
ข้อมูลทั้งหมดในเคสนี้เป็นข้อมูลสมมติเพื่อการสอน

## repo นี้คืออะไร

repo นี้คือสภาพงานของกลุ่มตัวอย่าง (กลุ่ม X) หลังบทเรียน Data, AI และ Agent และหลังเจ้าของอนุมัติข้อกำหนดของผู้ช่วย
ต่อจาก baanprom-sdd-05-ai (ประวัติ commit ของ repo 05 อยู่ครบใน repo นี้) และเพิ่ม 2 commit ที่อ่านแยกกันได้

- commit ที่ 1 "Data, AI และ Agent: ข้อกำหนดผู้ช่วย AI บนกระดาษ (CR-09 Proposed)" คือสิ่งที่ Studio ของบทเรียนทำในห้อง: วาดเส้นแบ่งกฎกับ AI เขียน REQ-DAT-010 REQ-AI พฤติกรรม 5 กลุ่ม REQ-AI ของ agent 4 เรื่อง เป็นธรรม โปร่งใส กำกับ แผน V&V และ eval set 10 ข้อแรก แล้วเสนอเป็น CR-09 ยังไม่มีโค้ด
- commit ที่ 2 "CR-09 อนุมัติ: ผู้ช่วย AI (MockLLM) eval และ Baseline B4" คือสิ่งที่ทีม SDD จริงทำต่อหลังบทเรียน: ประชุมทบทวนกับเจ้าของเรื่อง (EV-047) ตอบคำถามเปิด 9 ข้อ /plan /tasks /implement ขยาย eval set เป็น 290 ข้อ รัน test และ eval จริง แล้วประกาศ Baseline B4

ในห้องเรียนบทนี้ไม่เปิดเครื่อง (หน้าบทเรียนบอกไว้) commit ที่ 2 จึงเป็นเฉลยแบบ "ทำจนจบจริง" ไว้ให้เทียบ
คำตอบของเจ้าของเรื่องในประชุม EV-047 เป็นข้อมูลสมมติ สร้างขึ้นเพื่อให้ชุด repo ต่อเนื่อง ตัวเลขทุกตัวตรงกับที่หน้าบทเรียนเสนอ
เลข CR ข้ามจาก CR-07 เป็น CR-09 เพราะหน้าบทเรียน RE in One Line และการตรวจรับ ใช้ CR-08 เป็นตัวอย่างสมมติ ("ลูกค้าเลือกช่างคนเดิมได้")

## ใช้เริ่มบทเรียนไหน และเป็นเฉลยของบทไหน

- ใช้เริ่มบทเรียน **RE in One Line และการตรวจรับ**
- เป็นเฉลยของบทเรียน **Data, AI และ Agent** (commit ที่ 1 คือเฉลยของ Studio commit ที่ 2 คือการทำต่อจนเข้า Baseline)

## ชุด repo ทั้ง 8

แต่ละ repo คือจุดเริ่มของบทหนึ่ง และเป็นเฉลยของบทก่อนหน้า repo ถัดไปจึงเป็นเฉลยของงานในบทนี้

| repo | ใช้เริ่มบท | ข้างในคือเฉลยของ |
|---|---|---|
| [baanprom-sdd-01-spec](https://github.com/ppsajja/baanprom-sdd-01-spec) | Modern Specification และ SDD | ชิ้นงานบท 1 ถึง 7 (Problem Framing ถึง Integrated Modelling) |
| [baanprom-sdd-02-build](https://github.com/ppsajja/baanprom-sdd-02-build) | AI Build from Spec | Modern Specification และ SDD: spec plan tasks ที่กลุ่มเขียนเอง และ Baseline B1 |
| [baanprom-sdd-03-vv](https://github.com/ppsajja/baanprom-sdd-03-vv) | Verification, Validation และ Change | AI Build from Spec: โค้ดและ test ที่ AI สร้าง ac-results gaps CR-01 CR-02 |
| [baanprom-sdd-04-ops](https://github.com/ppsajja/baanprom-sdd-04-ops) | Operational, Security และ Privacy | V&V และ Change: RTM mockup CR-03 ถึง CR-06 Baseline B2 และ R1 ครบ (003 004) |
| [baanprom-sdd-05-ai](https://github.com/ppsajja/baanprom-sdd-05-ai) | Data, AI และ Agent | Operational, Security และ Privacy: CR-07 อนุมัติ และ Baseline B3 |
| **baanprom-sdd-06-accept** (repo นี้) | RE in One Line และการตรวจรับ | Data, AI และ Agent: ผู้ช่วย AI UC-14 (CR-09) และ Baseline B4 |
| [baanprom-sdd-07-r1-done](https://github.com/ppsajja/baanprom-sdd-07-r1-done) | บทเสริม การตรวจรับและการส่งมอบ | RE in One Line และการตรวจรับ: ตรวจรับ R1 (CR-10) และ Baseline B5 |
| [baanprom-sdd-08-complete](https://github.com/ppsajja/baanprom-sdd-08-complete) | (ระบบสมบูรณ์ของวิชา) | บทเสริม การตรวจรับและการส่งมอบ: R2 ครบทุก UC ส่งมอบตาม TOR และ Baseline B7 |

## อะไรใหม่เมื่อเทียบกับ repo ก่อนหน้า (baanprom-sdd-05-ai)

commit ที่ 1 (งาน Studio บนกระดาษ AI จัดรูปเป็นไฟล์ prompt-log.md #73)

| ไฟล์ | สิ่งที่เพิ่มหรือแก้ | เพราะอะไร |
|---|---|---|
| specs/005-ai-assistant/ | feature ใหม่ ชุดไฟล์เดียวกับ 002 ถึง 004 (spec 0.1, ai-assistant.feature AC-14-01 ถึง 16, rules.md BR-06 ร่าง, models.md, quality-requirements.md แผน V&V, gaps.md GAP-29) เพิ่ม eval/ และ prompts/ ตามหน้าบทเรียนหัวข้อ 9.2 | ข้อกำหนด AI ใช้โครงสเปกเดิม เพิ่มแค่ eval set กับข้อความสั่งที่มีรุ่น |
| specs/005-ai-assistant/eval/qa.jsonl | 10 ข้อแรก E-001 ถึง E-010 (6 ข้อจากตารางในหน้าบทเรียน) | Studio ช่วงที่ 2 |
| specs/005-ai-assistant/changes/CR-09.md | ใหม่ สถานะ Proposed คำถาม Q-55 ถึง Q-63 ตาราง OWASP Top 10 for LLM Applications 2026 และ Agentic Applications 2026 | นำผู้ช่วยเข้าสู่การพิจารณา |
| docs/srs/UC-14.md | use case fully dressed ร่าง | UC ใหม่เลขถัดจาก UC-13 |
| specs/000-shared/constraints.md | รุ่น 1.2 ร่าง ส่วน 7 "AI" (หลักกลาง 5 ข้อ REQ-AI-021, REQ-AI-022) | ข้อที่ "ลบ feature ผู้ช่วยทิ้งแล้วยังต้องอยู่" ไปไฟล์กลาง |
| docs/srs/catalogue.md, baseline.md | แถว Proposed 14 ข้อ EV-046 แถว CR-09 | ให้ Impact Analysis มองเห็นก่อนอนุมัติ |

commit ที่ 2 (หลังอนุมัติ)

| ไฟล์ | สิ่งที่เพิ่มหรือแก้ | เพราะอะไร |
|---|---|---|
| specs/005-ai-assistant/changes/CR-09.md | Approved 31 ต.ค. 2569 บันทึกประชุม EV-047 คำตอบ Q-55 ถึง Q-63 การแก้ 3 เรื่อง (ค1 ถึง ค3) และเงื่อนไขก่อนทดลองแบบเงาและนำร่อง | การอนุมัติต้องมีเหตุผลและผู้ตัดสิน |
| specs/005-ai-assistant/ spec, feature, rules, models, quality-requirements, UC-14 | รุ่น 1.0 ส่วน 13 eval และข้อความสั่ง D-14-04 ถึง 07 | CR-09 อนุมัติ |
| specs/005-ai-assistant/plan.md, tasks.md | ใหม่ plan v1 tasks v1 (T-01 ถึง T-12) | /plan /tasks |
| specs/005-ai-assistant/eval/ | รุ่น 1.0: qa 200 ข้อ reschedule 60 ข้อ injection 30 ข้อ ใบให้คะแนนของคน CHANGELOG | ขนาดตามหน้าบทเรียน (200, 60 ข้อเกินกรอบ 20, 30) |
| specs/005-ai-assistant/prompts/ | P-1.0 (รอบที่ 1 ไม่ผ่าน) และ P-1.1 (ใช้ใน B4) ข้อความสั่งและคำตัวอย่าง | ข้อความสั่งคือ "โค้ด" ของกล่อง AI |
| specs/005-ai-assistant/eval-results.md, .json, eval-results-round1-P-1.0.md | ผล eval จริง 2 รอบ | รอบที่ 1 ไม่ผ่านเพราะภาษาถิ่น (GAP-30) |
| specs/005-ai-assistant/ac-results.md, rtm.md, gaps.md | ใหม่ F-15, F-16 GAP-30 ถึง GAP-34 | ผลตรวจของ feature ใหม่ |
| backend/app/assistant/ | ใหม่ 13 ไฟล์: llm.py (interface และ MockLLM) intents.py retrieval.py guard.py tools.py agent.py handoff.py records.py service.py router.py prompts.py evaluation.py และ policies/ (คลังนโยบาย) | REQ-AI-005 ถึง 013, 020, 022, REQ-DAT-010 |
| backend/app/booking/service.py, router.py | เพิ่ม check_reschedule, reschedule_job, POST /jobs/{id}/reschedule (ไม่แก้ฟังก์ชันเดิม) | REQ-FN-056, BR-06 (GAP-29) |
| backend/app/db/models.py, migrations/m003_cr09.py | ตารางใหม่ 7 ตาราง ไม่แก้ตารางเดิม | |
| backend/app/privacy.py, erasure/service.py, ops/scheduler.py, config.py, main.py | mask_text ช่อง log ใหม่ ลบข้อความลูกค้าเมื่อขอลบ ลบบันทึกเกิน 180 วัน ค่าใหม่ทุกตัว | REQ-AI-013, REQ-PRV-010, D-00-05 |
| backend/eval_run.py | ใหม่ ตัวรัน eval เขียนรายงานลง specs/005-ai-assistant | หน้าบทเรียนหัวข้อ 9.3 "รัน eval" แทน "รัน test" |
| backend/tests/test_assistant.py, test_assistant_eval.py | test ใหม่ 31 ตัว test เดิมไม่เปลี่ยน | |
| frontend/src/pages/AssistantChat.jsx, api/client.js, App.jsx, __tests__ 4 ไฟล์ | หน้าแชต UI-14-01 เมนู "ผู้ช่วย" test ใหม่ 6 ตัว | REQ-AI-020, REQ-AI-011, REQ-AI-022 |
| specs/000-shared/constraints.md | รุ่น 1.2 Approved ตารางของ 005 ในข้อ 3 | CR-09 |
| specs/000-shared/test-run.txt, ac-results.md | ผลรันจริงทั้งโครงการ รอบ CR-09 | |
| docs/srs/catalogue.md, baseline.md | catalogue v1.5 (14 ข้อ Approved EV-047) Baseline B4 ตาราง "B4 ต่างจาก B3 อย่างไร" กติกาข้อ 10 | ประกาศ Baseline ใหม่ |
| docs/srs/operations.md | รุ่น 1.1 เหตุการณ์ที่ 6 เครื่องมือของผู้ช่วย endpoint ใหม่ 11 ตัว | REQ-AI-022, REQ-SEC-012 |
| docs/srs/stakeholders.md | เพิ่มบทบาท หัวหน้า call center (ยังไม่มีรหัส SH) | เจ้าของผู้ช่วย (Q-60) |
| prompt-log.md | เพิ่ม #73 ถึง #78 | ทุกคำสั่งและการตัดสินของรอบนี้ |

ดู diff ทั้งหมดของรอบอนุมัติ: `git diff origin/checkpoint/cr09-proposed origin/checkpoint/b4 --stat` และของทั้งบท: `git diff origin/checkpoint/cr09-proposed~1 origin/checkpoint/b4 --stat`

> จุดในประวัติ (เช่น checkpoint/cr09-proposed, checkpoint/b4) เป็น branch ชื่อขึ้นต้น checkpoint/ เปิดได้ด้วย `git checkout checkpoint/ชื่อ` หลัง clone ถ้าสร้าง repo ของกลุ่มด้วยปุ่ม Use this template ให้ติ๊ก Include all branches


## งานของบทนี้ที่นักศึกษาต้องทำต่อ

บทเรียน RE in One Line และการตรวจรับ มองย้อนทั้งเทอมบนเส้น 7 ขั้น แล้ววางแผนตรวจรับ R1 กับเจ้าของ

1. วาดเส้น 7 ขั้นบน A3 วางชิ้นงานของ repo นี้ใต้ขั้นที่มันอยู่ พร้อมช่วงรหัส (EV-001 ถึง EV-047, CR-01 ถึง CR-09, B1 ถึง B4) ขั้นไหนไม่มีชิ้นงานให้เว้นว่าง
2. เดินย้อน 2 เส้น จากโค้ดถึงหลักฐาน เช่น guard.py ไปหา REQ-AI-008 ไปหา EV-046 และ booking/reschedule_job ไปหา REQ-FN-056 ไปหา GAP-29
3. เขียนแผนตรวจรับ R1 หนึ่งหน้า อ้างอิง Baseline B4 (ไม่ใช่ B2 อย่างตัวอย่างในหน้าบทเรียน) ผู้ลงนาม เกณฑ์เริ่ม เกณฑ์จบ ข้อที่ตรวจได้แค่ย่อส่วนให้เป็นเงื่อนไข (เช่น AC-07-08 ที่ 500 คน และผล eval ที่วัดกับ MockLLM)
4. แยกสิ่งที่พบระหว่างตรวจรับเป็น ข้อบกพร่อง คำขอเปลี่ยนแปลง และสเปกผิด ด้วยคำถามเดียวว่า "Baseline B4 เขียนไว้อย่างไร" ตัวอย่างในหน้าบทเรียนคือ DEF-01 และ CR-08 (เลือกช่างคนเดิม)
5. ตัดสินผู้ช่วย UC-14 แยกจาก 002 ถึง 004: ผู้ช่วยยังเป็น MockLLM และเกณฑ์ที่ต้องใช้คนยังไม่ทำ จะรับ รับแบบมีเงื่อนไข หรือไม่รับ ด้วยเหตุผลที่อ้างเกณฑ์จบ

ผลลัพธ์อยู่ใน repo ถัดไป (baanprom-sdd-07-r1-done): แผนตรวจรับ R1 บันทึกการตรวจรับ สิ่งที่พบ และ CR ที่เกิดจากการตรวจรับ
ใน repo นี้ยังไม่มีไฟล์เหล่านี้ ตั้งใจให้เป็นอย่างนั้น ทำของตัวเองก่อน แล้วค่อยเปิดเฉลย

## ถ้าทำของตัวเองพลาดหรือไม่ทัน

เอา repo นี้ไปทำต่อได้สองทาง

ทางที่ 1 บน GitHub

- เปิดหน้า repo นี้ กด Use this template แล้วเลือก Create a new repository
- ตั้งชื่อ repo ของกลุ่ม แล้วเปิดด้วย Codespaces

ทางที่ 2 clone แล้วเปลี่ยน remote

```
git clone https://github.com/ppsajja/baanprom-sdd-06-accept.git baanprom-group
cd baanprom-group
git remote set-url origin https://github.com/<บัญชีของกลุ่ม>/<ชื่อ repo ของกลุ่ม>.git
git push -u origin main
```

`git remote set-url origin` เปลี่ยนปลายทางของ push จาก repo ของผู้สอนเป็น repo ของกลุ่ม (ต้องสร้าง repo เปล่าบน GitHub ไว้ก่อน)
ถ้าอยากเริ่มจากสภาพหลัง Studio ที่ยังไม่อนุมัติ ใช้ `git checkout checkpoint/cr09-proposed` แล้วสร้าง branch ของกลุ่มจากจุดนั้น

## ทีม

- ชื่อทีม: กลุ่ม X (ตัวอย่างของรายวิชา)
- สมาชิก: สมาชิก A, สมาชิก B, สมาชิก C, สมาชิก D
- เครื่องมือ AI ที่ใช้: Copilot Chat โหมด Agent ใน GitHub Codespaces (รอบนี้ผู้สอนเดโมด้วย Claude Code)

## โครงของ repo

```
README.md                      ไฟล์นี้
AGENTS.md                      กติกาที่ AI ต้องทำตาม 10 ข้อ (agent-pack รุ่น 2)
CLAUDE.md                      ชี้ไป AGENTS.md (สำหรับ Claude Code)
prompt-log.md                  บันทึกทุกคำสั่ง (เพิ่มต่อท้ายเท่านั้น ล่าสุด #78)
docs/srs/                      catalogue v1.5, UC-07, UC-08, UC-09, UC-14, glossary, baseline (B4 ด้านบน), operations.md รุ่น 1.1
specs/000-shared/              Constraint กลางรุ่น 1.2 (ส่วน 7 "AI") AC ข้ามทุก feature test-run ของทั้งโครงการ
specs/002-booking/             UC-07 spec 1.5
specs/003-job-status/          UC-09 spec 1.1
specs/004-cancel-refund/       UC-08 spec 1.1
specs/005-ai-assistant/        UC-14 spec 1.0 eval/ (290 ข้อ) prompts/ (P-1.0, P-1.1) eval-results.md changes/CR-09.md
backend/                       Python FastAPI + SQLAlchemy app/assistant ใหม่ eval_run.py ตัวรัน eval
frontend/                      React (Vite) + Tailwind CSS + Vitest หน้าใหม่ "ผู้ช่วย"
```

อ่านรอบนี้ตามลำดับนี้

1. specs/005-ai-assistant/spec.md ส่วน 3 (เส้นแบ่งกฎกับ AI และตารางระดับการกระทำ) แล้วส่วน 4
2. specs/005-ai-assistant/changes/CR-09.md (ส่วนบนคือข้อเสนอเดิม ส่วน "บันทึกประชุมทบทวน" คือสิ่งที่เปลี่ยน)
3. specs/005-ai-assistant/ai-assistant.feature แล้ว eval/README.md และตัวอย่างใน eval/qa.jsonl
4. specs/005-ai-assistant/eval-results-round1-P-1.0.md (รอบที่ไม่ผ่าน) แล้ว eval-results.md
5. backend/app/assistant/service.py (ลำดับ 5 ขั้น) guard.py และ llm.py (MockLLM ทำผิดตรงไหนบ้าง)
6. ac-results.md, rtm.md, gaps.md แล้ว docs/srs/baseline.md (B4)

## วิธีรัน

หลังบ้าน

```
cd backend
pip install -r requirements.txt
python -m pytest -v -k "AC_"
python eval_run.py
APP_ENV=development uvicorn app.main:app --reload --port 8000
```

`python eval_run.py` รัน eval ทั้ง 3 ชุดกับ MockLLM เขียนผลลง specs/005-ai-assistant/eval-results.md และ .json คืนรหัส 0 เมื่อผ่านทุกเกณฑ์
ลองรุ่นข้อความสั่งเดิม: `python eval_run.py --prompt-version P-1.0 --out /tmp/round1.md` (ไม่ผ่าน 9 เกณฑ์ เหมือนรอบที่ 1)
ระบบตั้งค่าตั้งต้นเป็นโหมด production (REQ-SEC-012) ถ้ารัน uvicorn โดยไม่ตั้ง APP_ENV หน้า /docs จะปิด และ endpoint ของ ops ต้องมี header X-Ops-Token ที่ตรงกับตัวแปร OPS_TOKEN

หน้าจอ

```
cd frontend
npm install
npm test
npm run dev
```

ถ้าเปิดด้วย GitHub Codespaces คำสั่ง pip install และ npm install ถูกรันให้แล้วตอนสร้างเครื่อง

ผลที่ควรเห็น (รันจริงจาก repo นี้ ตรงกับ specs/000-shared/test-run.txt และ specs/005-ai-assistant/eval-results.md)

- Python 3.11 และ 3.12: บรรทัดสุดท้าย `97 passed, 1 skipped, 1 warning` (ข้าม 1 คือ AC-07-10 แถว R3 ที่รอ Q-14)
- หน้าจอ: `Test Files 21 passed (21)` และ `Tests 37 passed (37)`
- eval: `prompt P-1.1: 20/20 เกณฑ์ผ่าน`
- ถ้าเปิด commit ที่ 1 (`git checkout checkpoint/cr09-proposed`) จะได้ 66 passed, 1 skipped และ 31 passed เท่า repo 05 เพราะยังไม่มีโค้ดของผู้ช่วย

## สิ่งที่รู้อยู่แล้วว่ายังไม่ใช่ของจริง

- **LLM เป็น MockLLM** (backend/app/assistant/llm.py) ตัวจริงยังไม่ต่อ เพราะยังไม่เลือกผู้ให้บริการที่ผ่านเงื่อนไขของ SH-05 (Q-56) MockLLM กำหนดผลจากค่า crc32 ของคำถาม จำลองทั้งการตอบถูก การไม่บอกเวลานัด การแต่งเวลาที่ช่างจะถึงและจำนวนวันคืนเงิน การอ้างคืนเต็มจำนวน และการทำตามข้อความหลอก ผล eval 197 จาก 200 จึงบอกว่ารั้ว กฎ และวิธีวัดทำงาน **ไม่ได้บอกว่า LLM ตัวจริงจะผ่าน**
- ขั้นจำแนกความตั้งใจเป็นกฎกับคำตัวอย่าง ไม่ใช่โมเดล คำภาษาถิ่นมีเท่าที่ call center ให้มา (P-1.1)
- คำถามใน eval set สร้างขึ้นเพื่อการสอน ไม่ได้มาจากสายจริง ขยายจาก 10 ข้อแรกด้วยสคริปต์ที่อยู่นอก repo
- เกณฑ์ที่ต้องใช้คนยังไม่ได้วัด: คนตรวจ 30 ข้อ (AC-14-03) ลูกค้าจริง 20 คน (AC-14-09, AC-14-12) ซ้อมปิดผู้ช่วยจับเวลา (AC-14-14) ทดลองแบบเงาและนำร่องยังไม่เริ่ม
- เวลาตอบ p95 ที่วัดได้ (ราว 10 มิลลิวินาที) เป็นเวลาของโค้ดเรากับ MockLLM ค่าใช้จ่ายต่อคำถามวัดไม่ได้
- R1 ยังไม่มีการเข้าสู่ระบบ ผู้ช่วยทำในนามลูกค้าจาก customer_id ที่ส่งมาเอง ซึ่งยังปลอมได้ (TH-01) จึงห้ามนำร่องก่อนมี UC-02 (CR-09 ข้อ ค3)
- หัวหน้า call center ยังไม่มีกุญแจของตัวเอง ต้องสั่งคนเวรกดปิด (GAP-32) call center ยังไม่มีเครื่องมือเลื่อนกลับ (GAP-31)
- mockup UI-14-01 ยังไม่มีภาพ .png และยังไม่ได้ตรวจหน้าจอจริงเทียบ mockup ด้วยคน (GAP-33)
- เลขโทรของ call center บนปุ่มโทรเป็นเลขสมมติ 02-000-0000 (ตั้งจริงผ่าน CALL_CENTER_TEL)
- ของเดิมจาก repo 05 ที่ยังไม่ใช่ของจริง ยังอยู่ทั้งหมด: FakeGateway, FakeNotifier, คิวในหน่วยความจำ, Pager เขียน log อย่างเดียว (GAP-28), สำรองกู้คืนบน SQLite เท่านั้น, ผลย่อส่วนของ AC-07-08, AC-09-12, AC-08-09, ระยะทางจากสูตรแทนบริการแผนที่

## คำถามที่ยังเปิด และจะได้คำตอบใน repo ไหน

| คำถาม | เรื่อง | สถานะ |
|---|---|---|
| Q-55 ถึง Q-63 | ข้อกำหนดของผู้ช่วย UC-14 | ปิดแล้วใน repo นี้ (EV-047) |
| Q-35 | จำนวนวันที่เงินคืนเข้า | ยังเปิด ผู้ช่วยตอบว่ายังไม่มีข้อมูล |
| Q-26, Q-31, Q-34 | เงื่อนไขก่อนเปิด R1 ให้ลูกค้าจริง (CR-03, CR-05, CR-06) | ยังเปิด ใช้เป็นเกณฑ์ในบท RE in One Line และการตรวจรับ ผลอยู่ใน baanprom-sdd-07-r1-done |
| ข้อตกลงกับ IF-02 ซ้อมกู้คืนบนระบบจริง ช่องทางถึงคนเวร (GAP-28) | เงื่อนไขก่อนเปิด R1 จาก CR-07 | ยังเปิด เกณฑ์ตรวจรับด้านปฏิบัติการ (repo 07) |
| เลือกผู้ให้บริการ LLM (IF-05) และรัน eval กับตัวจริง | เงื่อนไขก่อนทดลองแบบเงา (CR-09) | ยังเปิด ตัดสินในการตรวจรับว่าผู้ช่วยอยู่ใน R1 หรือไม่ (repo 07) |
| F-15 คำว่า "ทุกจอ" ใน REQ-AI-020 | หน้าจอไหนต้องมีปุ่มคุยกับเจ้าหน้าที่ | ถาม SH-01 ในบท RE in One Line และการตรวจรับ (repo 07) |
| CR-02 | ทำให้ REQ-QA-003 วัดได้ (รอ SH-01) | ยังรอ SH-01 |
| Q-14, Q-18, Q-19, Q-22, Q-23, Q-27, Q-28, Q-29, Q-30, Q-32, Q-33, Q-36, Q-37 | ค้างจาก B1 ถึง R1 | ยังเปิด ทุกข้อมีเจ้าของและพฤติกรรมชั่วคราว |
| GAP-24, GAP-26, GAP-31, GAP-32, GAP-33, F-16 | สิทธิ์ของ GET /jobs/{id} mockup เครื่องมือของ call center กุญแจแยกบทบาท test กรณีหมดเวลาหลังทำ | ยังเปิด |

## Reflection ของกลุ่ม X รอบ Data, AI และ Agent (5 บรรทัด)

1. test ผ่านทั้งชุดตั้งแต่รอบแรก แต่ eval ไม่ผ่าน 9 เกณฑ์ ความผิดไม่ได้อยู่ในข้อใดข้อหนึ่ง แต่ตกกับคนที่พิมพ์ภาษาถิ่น เราเห็นได้เพราะติดป้ายกลุ่มให้ทุกข้อตั้งแต่สร้างชุด
2. สิ่งที่กันข้อความหลอกได้จริงคือรั้วที่เป็นโค้ด ปิดรั้วขาออกแล้วชุดหลอก 30 ข้อเหลือผ่าน 20 ข้อความสั่งที่ยาวขึ้นไม่ได้ช่วย
3. agent ไม่มีกฎของตัวเอง BR-06 อยู่ใน booking ที่เดียว ผู้ช่วยกับ API ของลูกค้าใช้ฟังก์ชันเดียวกัน
4. หน้าบทเรียนบอกให้เลื่อนนัด "ผ่าน API เดิม" แต่ API นั้นไม่มี ถ้าไม่ไล่ของเดิมก่อน agent จะได้สิทธิ์แก้ตาราง jobs เอง (GAP-29)
5. ผล eval กับ MockLLM เป็นหลักฐานของรั้วและวิธีวัด ไม่ใช่ของ AI ตัวจริง ต้องเขียนให้ชัดก่อนเจ้าของเอาตัวเลขไปใช้ตอนตรวจรับ
