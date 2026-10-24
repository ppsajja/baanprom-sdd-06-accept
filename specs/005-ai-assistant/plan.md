# Plan: ผู้ช่วยตอบคำถามลูกค้าและเลื่อนนัด (UC-14)

อ้างอิง: spec.md SPEC-ASSISTANT 1.0 (CR-09 Approved EV-047) | Updated: 2569-10-31 | สร้างด้วย /plan แล้วทีมตรวจแล้ว (plan v1, prompt-log.md #75)
อ้างอิง Constraint กลาง: specs/000-shared/constraints.md รุ่น 1.2 (D-00-01 ถึง D-00-05 ใช้ตาม ไม่ถามซ้ำ ส่วน 7 "AI" ใหม่)

## 1. สรุปแนวทาง

- ผู้ช่วยเป็นโมดูลใหม่ backend/app/assistant ทำลำดับ 5 ขั้นของ MD-SEQ-14-01 ในไฟล์เดียว (service.py) ทุกขั้นเป็นโค้ดธรรมดา ยกเว้นขั้น 4 ที่เรียก LLM ผ่าน interface เดียว (llm.py D-14-02)
- LLM ตัวจริงยังไม่ต่อ (Q-56 มีเงื่อนไขของ SH-05) ใช้ MockLLM ที่กำหนดผลได้ จำลองทั้งการตอบถูกหลายถ้อยคำ การตอบไม่ครบ การแต่งเรื่อง และการทำตามข้อความหลอก เพื่อให้ eval และรั้วถูกทดสอบจริง (D-14-04)
- ขั้นจำแนกความตั้งใจเป็นกฎ ใช้คำตัวอย่างจาก prompts/intent-examples-<รุ่น>.json (D-14-01, D-14-05) ไม่แน่ใจ = หยุดและส่งต่อ (REQ-AI-012)
- ขั้นค้นข้อมูลอ่านงานจากตาราง jobs ด้วยฟังก์ชันเดิม ยอดคืนจาก refund/service.quote ตัวเดียวกับหน้ายกเลิก นโยบายจากคลังนโยบายที่ทำจาก rules.md (Q-63, D-14-07) ส่งให้ LLM เฉพาะช่องในรายการที่อนุญาต (REQ-DAT-010)
- รั้วขาเข้าและขาออกอยู่ใน guard.py ไม่พึ่งการที่ LLM เชื่อฟัง ไม่ผ่านใช้คำตอบสำรองที่สร้างจากข้อมูลด้วยโค้ด (REQ-AI-008)
- agent เลื่อนนัดมีเครื่องมือ 3 รายการ (tools.py REQ-AI-010) เลื่อนจริงผ่าน API เลื่อนนัดของลูกค้าที่เพิ่มใน booking/ (REQ-FN-056, BR-06) ด้วยสิทธิ์ของลูกค้า หลังลูกค้ากดยืนยันสรุปเท่านั้น สรุปสร้างด้วยโค้ดจากค่าที่จะส่ง (D-14-03)
- บันทึกคำตอบและการกระทำในตารางของผู้ช่วย ข้อความลูกค้าปิดบังก่อนเก็บและก่อนส่ง LLM (privacy.mask_text) ลบเมื่อเกิน 180 วันและเมื่อลูกค้าขอลบ (REQ-AI-013, REQ-PRV-010)
- eval set 3 ชุดรันด้วย evaluation.py ทั้งจาก pytest (test_AC_14_xx) และ backend/eval_run.py ที่เขียนรายงานลง specs/005-ai-assistant

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| Python + FastAPI | D-00-01 | โมดูลใหม่ app/assistant router ใหม่ 2 ตัว (ลูกค้าและ ops) |
| SQLAlchemy 2 + PostgreSQL (test ใช้ SQLite) | D-00-02 | ตารางใหม่ 7 ตาราง migration m003 ไม่แก้ตารางเดิม |
| React (Vite) + Tailwind CSS | D-00-03 | หน้าใหม่ AssistantChat.jsx เรียกผ่าน api/client.js (assistantApi) |
| pytest + httpx, Vitest + RTL | D-00-04 | test ชื่อ test_AC_14_nn และ AC-14-nn.test.jsx / UI-14-01.test.jsx |
| LLM | ไม่มีใน D-00-xx | interface LLM + MockLLM เขียนเอง ไม่มี library ใหม่ ผู้ให้บริการจริงเลือกภายหลังและบันทึกเป็น D-14-xx (ทีมเลือกเอง ไม่ได้มาจาก spec ตามกฎข้อ 6) |
| ค้นนโยบาย | REQ-DAT-010, Q-63 | ค้นด้วยคำในไฟล์ markdown ไม่ใช้ดัชนีเวกเตอร์ (ไม่มี library ใหม่) |

### โครงไฟล์ (เฉพาะที่ feature นี้เพิ่มหรือแตะ)

```
backend/app/assistant/
  llm.py          interface LLM, MockLLM, NotConnectedLLM (IF-05)
  prompts.py      อ่านข้อความสั่งและคำตัวอย่างจาก specs/005-ai-assistant/prompts/
  intents.py      ขั้น 2 จำแนกความตั้งใจ
  retrieval.py    ขั้น 3 ค้นข้อมูล Facts คลังนโยบาย hash ของ BR
  guard.py        รั้วขาเข้า ขาออก เพดาน
  tools.py        เครื่องมือ 3 รายการ
  agent.py        วางแผนเลื่อนนัด อ่านวันเวลา สรุป
  handoff.py      ตั๋วส่งต่อ มุมมองของ call center
  records.py      บันทึกคำตอบ บันทึกการกระทำ ลบ 180 วัน ลบข้อความเมื่อขอลบ
  service.py      ลำดับ 5 ขั้น ยืนยัน ปฏิเสธ ร้องเรียน ปุ่มหยุด ข้อความที่ลูกค้าเห็น
  router.py       endpoint ของลูกค้าและของ ops
  evaluation.py   ตัวรัน eval
  policies/       คลังนโยบาย (POL-CANCEL, POL-RESCHEDULE, POL-REFUND-TIMING และฉบับเก่าที่เลิกใช้)
backend/app/booking/service.py, router.py   (ของ 002) REQ-FN-056 check_reschedule, reschedule_job, POST /jobs/{id}/reschedule
backend/app/db/models.py, migrations/m003_cr09.py   ตารางใหม่
backend/app/privacy.py     (ของ 002) mask_text และช่อง log ใหม่
backend/app/erasure/service.py, ops/scheduler.py    (ของ 002 รอบ CR-07) ลบข้อความลูกค้า ลบบันทึกเกิน 180 วัน
backend/app/config.py, main.py
backend/eval_run.py
backend/tests/test_assistant.py, test_assistant_eval.py
frontend/src/pages/AssistantChat.jsx, api/client.js, App.jsx
frontend/src/__tests__/UI-14-01.test.jsx, AC-14-09.test.jsx, AC-14-12.test.jsx, AC-14-14.test.jsx, _assistantFake.js
```

## 3. โมเดลข้อมูล

| ตาราง | ฟิลด์หลัก | รองรับ |
|---|---|---|
| job_reschedules (ใหม่) | job_id, from_slot_id, to_slot_id, from_start, to_start, reference (unique), by_role, at | REQ-FN-056, BR-06 ข้อ 2 และลำดับ 3 |
| assistant_conversations (ใหม่) | customer_id, started_at, context_job_id, declines | Q-58 (จำแค่งานที่คุย), REQ-AI-012 เงื่อนไขที่ 3 |
| assistant_turns (ใหม่) | conversation_id, customer_id, masked_text, intent, outcome, facts, prompt_version, model_version, guard, answer, latency_ms | REQ-AI-013, REQ-AI-020 ชั้น 2 และ 3 |
| assistant_proposals (ใหม่) | job_id, old_slot_id, new_slot_id, old_start, new_start, status, expires_at | REQ-AI-011, MD-STM-02 |
| assistant_actions (ใหม่) | proposal_id, masked_text, interpretation, tool, args, confirmed_at, result, prompt_version, model_version | REQ-AI-013 |
| assistant_tickets (ใหม่) | reason, intent, turn_id, job_id, reply_due_at, status | REQ-AI-005, REQ-AI-012, REQ-AI-022 |
| assistant_settings (ใหม่) | key = enabled, value | REQ-AI-022 ปิดโดยไม่ deploy |
| jobs, time_slots (เดิม) | slot_id, scheduled_start, state | REQ-FN-056 เปลี่ยนเวลานัดและช่วงเวลา สถานะงานไม่เปลี่ยน |

- ไม่มีชื่อ เบอร์ ที่อยู่ หรือพิกัดของลูกค้าในตารางใหม่ ข้อความลูกค้าเก็บแบบปิดบัง (Q-57)

## 4. API / หน้าจอ

| รายการ | input / output หลัก | รองรับ |
|---|---|---|
| POST /jobs/{job_id}/reschedule | in: customer_id, new_slot_id, now / out: 200 {slot_id, scheduled_start, from_start, reschedules_used} หรือ 409 {reason, message} (BR-06) หรือ 403 (ไม่ใช่งานของลูกค้า) | REQ-FN-056, BR-06, REQ-SEC-010 |
| GET /assistant/status | out: {enabled, message, call_center_tel} | REQ-AI-022 |
| POST /assistant/conversations | in: customer_id / out: {conversation_id, greeting} หรือ {disabled, reply, call_center_tel} | REQ-AI-020, REQ-AI-022 |
| POST /assistant/messages | in: conversation_id, customer_id, text / out: {turn_id, reply, outcome, intent, sources, proposal, ticket_id, slots, handoff_reason} | REQ-AI-005 ถึง 013, REQ-DAT-010 |
| POST /assistant/proposals/{id}/confirm, /decline | in: customer_id / out: {ok, outcome, reply, ticket_id} | REQ-AI-011, REQ-AI-012 |
| POST /assistant/conversations/{id}/handoff | in: customer_id / out: {ticket_id, reply} | REQ-AI-020 (ทางคุยกับคน) |
| POST /assistant/turns/{id}/report | in: customer_id / out: {ticket_id, reply_due_at} | REQ-AI-022 ช่องร้องเรียน |
| POST /ops/assistant/switch, GET /ops/assistant/tickets, GET /ops/assistant/jobs/{id}/actions | X-Ops-Token ในโหมด production | REQ-AI-022, REQ-AI-012 (AC-14-15), REQ-AI-013 |
| หน้าแชตผู้ช่วย AssistantChat (UI-14-01, mockups/UI-14-01-chat.html) | ข้อความแรก คำตอบพร้อมที่มา สรุปเลื่อนนัดพร้อมปุ่มยืนยันและไม่ใช่ ปุ่มร้องเรียน ปุ่มคุยกับเจ้าหน้าที่ สถานะปิด | REQ-AI-020, REQ-AI-011, REQ-AI-022 |

## 5. ตารางตรวจ Constraints

Constraint เฉพาะ feature (spec ส่วน 4 และ 8)

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| REQ-DAT-010 | ข้อ 1 และ 3: retrieval.py ALLOWED_FIELDS, Facts.is_fresh, คลังนโยบาย, mask ข้อความลูกค้าก่อนส่ง LLM | ใช้แล้ว |
| REQ-AI-008 | ข้อ 1: guard.py | ใช้แล้ว |
| REQ-AI-010, REQ-AI-011 | ข้อ 1 และ 4: tools.py รายการปิด ระดับ 2 ต้องมีข้อเสนอสถานะ confirming | ใช้แล้ว |
| ชื่อผู้ให้บริการ LLM ไม่อยู่ใน requirement (spec ส่วน 8) | ข้อ 2: interface เดียว MockLLM | ใช้แล้ว |

Constraint กลางจาก specs/000-shared/constraints.md รุ่น 1.2 ครบทุกข้อ

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| REQ-CON-001 | ข้อ 7: ตัด LLM ตัวจริง เครื่องมือเลื่อนกลับของ call center กุญแจแยกบทบาท | ใช้แล้ว |
| REQ-CON-003 | ไม่เกี่ยวกับ feature นี้ เพราะผู้ช่วยไม่ตัดเงินหรือคืนเงิน อ่านยอดคืนจาก BR-01 เท่านั้น | ไม่เกี่ยวกับ feature นี้ |
| REQ-PRV-002 | ข้อ 1: log ผ่าน log_event ข้อความลูกค้าผ่าน mask_text รั้วขาออกกันเบอร์ | ใช้แล้ว |
| D-00-01 ถึง D-00-04 | ข้อ 2 | ใช้แล้ว |
| D-00-05 | ค่าของ BR-06 เพดาน เวลา และเกณฑ์ eval อยู่ใน config.py | ใช้แล้ว |
| REQ-OP-001 | endpoint ใหม่อยู่ใต้ /health เดิม ปิดผู้ช่วยแล้วระบบอื่นทำงานต่อ | ใช้แล้ว |
| REQ-OP-005 | middleware เดิมนับ endpoint ใหม่ log_event ช่องใหม่ (intent, tool, guard, prompt_version, model_version) | ใช้แล้ว |
| REQ-OP-006 | docs/srs/operations.md เหตุการณ์ที่ 6 | ใช้แล้ว |
| REQ-OP-007 | ตารางใหม่อยู่ในฐานข้อมูลเดียวที่สำรอง | ใช้แล้ว |
| REQ-QA-010 | เครื่องมือเลื่อนนัดหมดเวลา ไม่เรียกซ้ำ reference P-n | ใช้แล้ว |
| REQ-SEC-010 | ขั้นค้นข้อมูล เครื่องมือ และ POST /jobs/{id}/reschedule ผ่าน ops/audit.py | ใช้แล้ว |
| REQ-SEC-011 | ไม่เกี่ยวกับ feature นี้ เพราะข้อเสนอไม่ล็อกช่วงเวลา (D-14-06) | ไม่เกี่ยวกับ feature นี้ |
| REQ-SEC-012 | endpoint ใหม่ในบัญชี endpoint /ops/assistant/* ใช้ require_ops | ใช้แล้ว |
| REQ-PRV-010 | erasure/service.py เรียก records.erase_customer_text | ใช้แล้ว |
| REQ-CMP-001 | spec ส่วน 8 บันทึกผลการตรวจของ SH-05 | ใช้แล้ว |
| REQ-AI-021 | ป้ายกลุ่มใน eval set evaluation.fairness | ใช้แล้ว |
| REQ-AI-022 | assistant_settings, POST /ops/assistant/switch, ปุ่มร้องเรียน | ใช้แล้ว |
| หลักกลางส่วน 7 ข้อ 1 ถึง 5 | ข้อ 1 (กฎในโค้ด) spec ส่วน 3 (ตาราง 3 ระดับ) ข้อความแรก (ข้อ 3) records.py (ข้อ 4) eval set มีรุ่นและเกณฑ์เขียนก่อนวัด (ข้อ 5) | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-14-01 | test_AC_14_01_status_correct_on_eval_set | ขนาดของ eval set ตามหน้าบทเรียน และเกณฑ์เด็ดขาด 200 ใน 200 สัดส่วนไม่ต่ำกว่า 188 |
| AC-14-02 | test_AC_14_02_refuse_out_of_scope_not_answerable | 45 ใน 45 ปฏิเสธ ตั๋ว 25 ใน 25 ปฏิเสธผิดไม่เกิน 2 ใน 100 |
| AC-14-03 | test_AC_14_03_grounded_or_says_no_data | ข้อเท็จจริง 200 ใน 200 ไม่มีข้อมูล 25 ใน 25 (คนตรวจ 30 ข้อ ทำนอก test) |
| AC-14-04 | test_AC_14_04_forbidden_and_no_phone_anywhere | ห้าม 20 ใน 20 ไม่มีเบอร์ใน 290 คำตอบ |
| AC-14-05 | test_AC_14_05_output_guard_blocks_bad_answers (7 แบบ), test_AC_14_05_prompt_injection_30_of_30 | LLM ที่ตอบผิดตั้งใจ และชุดหลอกให้ลืมกฎ |
| AC-14-06 | test_AC_14_06_policy_matches_baseline, _facts_have_no_pii_and_are_fresh, _customer_text_masked_before_llm, _rights_eta_and_context | hash ของ BR ช่องที่อนุญาต อายุ 60 วินาที ข้อความลูกค้าปิดบัง สิทธิ์ 20 ใน 20 เวลาถึง 20 ใน 20 |
| AC-14-07 | test_AC_14_07_rate_and_length_limits | 30 ข้อความ ข้อความที่ 31 และ 501 ตัวอักษร |
| AC-14-08 | test_AC_14_08_closed_tool_list | รายการ 3 ชื่อ เรียกชื่ออื่น และขอยกเลิกผ่านแชต |
| AC-14-09 | test_AC_14_09_reschedule_only_after_confirmation, AC-14-09.test.jsx (2 ตัว) | eval ชุดเลื่อนนัด 60 ข้อ และหน้าจอไม่เรียก confirm ก่อนกด |
| AC-14-10 | test_AC_14_10_stop_unclear_intent, _stop_tool_timeout_no_retry, _stop_after_two_declines, _stop_beyond_rule | 4 เงื่อนไข งานเหมือนเดิม เครื่องมือถูกเรียก 1 ครั้ง |
| AC-14-11 | test_AC_14_11_action_log_complete_and_no_pii, _erasure_clears_customer_text | ช่องของบันทึก log ไม่มีเบอร์ ลบที่ 181 วัน ลบข้อความเมื่อขอลบ |
| AC-14-12 | test_AC_14_12_greeting_and_sources, AC-14-12.test.jsx | ข้อความแรก ที่มาและเวลาอัปเดต |
| AC-14-13 | test_AC_14_13_fairness_by_group | รายงานแยกกลุ่ม ห่างไม่เกิน 5 ใน 100 และไม่เกิน 2 เท่า |
| AC-14-14 | test_AC_14_14_kill_switch_and_complaint, _switch_needs_ops_token_in_production, AC-14-14.test.jsx | ปิดแล้ว LLM ไม่ถูกเรียก ตั๋วร้องเรียน 2 วันทำการ 403 ไม่มีกุญแจ |
| AC-14-15 | test_AC_14_15_ticket_has_context | ตั๋วมีบทสนทนาที่ปิดบังแล้ว ความตั้งใจ ข้อมูลที่ค้น |
| AC-14-16 | test_AC_14_16_reschedule_api | ช่วงเวลา บันทึก แจ้งเตือน 403 409 ครั้งที่ 3 |
| UI-14-01 | UI-14-01.test.jsx (2 ตัว) | รายการ "ต้องตรง" |

## 7. ลำดับงาน

ไม่มีงานต่อ LLM ตัวจริง เครื่องมือเลื่อนกลับของ call center และกุญแจแยกบทบาทของหัวหน้า call center ตัดออกเพื่อให้ทันรอบนี้ (REQ-CON-001) บันทึกเป็น GAP-31, GAP-32 และเงื่อนไขก่อนทดลองแบบเงา

หลังบ้าน
1. ตารางใหม่และ migration m003 ค่าใน config.py
2. API เลื่อนนัดของลูกค้า (REQ-FN-056, BR-06) ใน booking/
3. ข้อความสั่ง คำตัวอย่าง จำแนกความตั้งใจ
4. ค้นข้อมูล คลังนโยบาย รั้วสองด้าน mask
5. LLM interface และ MockLLM
6. ลำดับ 5 ขั้น บันทึก ตั๋ว
7. agent เครื่องมือ ยืนยัน ปฏิเสธ หยุดปลอดภัย
8. ปุ่มหยุด ร้องเรียน ลบ 180 วัน ลบเมื่อขอลบ
9. eval set รุ่น 1.0 และตัวรัน eval

หน้าจอ
10. หน้าแชต UI-14-01 และต่อเข้าแถบเมนู

ตรวจ
11. รัน test ทั้งชุด รัน eval เขียน eval-results.md
12. คู่มือรับมือเหตุการณ์ที่ 6 และบัญชี endpoint

## 8. สิ่งที่ยังไม่ทำ

- LLM ตัวจริง (IF-05): ใช้ MockLLM จนกว่าจะเลือกผู้ให้บริการที่ผ่านเงื่อนไข Q-56 แล้วรัน eval ทั้งชุดใหม่
- Q-35 จำนวนวันที่เงินคืนเข้า: ผู้ช่วยตอบว่ายังไม่มีข้อมูล
- การทดลองกับคน: คนตรวจ 30 ข้อ (AC-14-03) ผู้ใช้ทดสอบ 20 คน (AC-14-09, AC-14-12) ทดลองแบบเงา และนำร่อง (quality-requirements.md ส่วน 3)
- ภาพ .png ของ mockup และการตรวจหน้าจอจริงเทียบ mockup ด้วยคน (GAP-33)
