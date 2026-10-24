// API จำลองของผู้ช่วย ใช้ร่วมใน test ของ UI-14-01, AC-14-09, AC-14-12, AC-14-14 (ค่าตอบเหมือนหลังบ้านจริง)
export const GREETING = 'สวัสดีค่ะ ฉันคือผู้ช่วยอัตโนมัติของบ้านพร้อม ไม่ใช่เจ้าหน้าที่ ตอบได้ 5 เรื่อง'
export function fakeApi(over = {}) {
  return {
    start: vi.fn().mockResolvedValue({ status: 200, body: { disabled: false, conversation_id: 7, greeting: GREETING } }),
    send: vi.fn().mockResolvedValue({ status: 200, body: { disabled: false, turn_id: 11, reply: 'งาน #1024 สถานะ "ช่างกำลังเดินทาง" นัดไว้ 4 ต.ค. 14:00 น.',
      outcome: 'answered', sources: [{ label: 'สถานะงาน #1024', updated_at: '2026-10-04T09:52:00' }], proposal: null } }),
    confirm: vi.fn().mockResolvedValue({ status: 200, body: { ok: true, reply: 'เลื่อนนัดแล้วค่ะ' } }),
    decline: vi.fn().mockResolvedValue({ status: 200, body: { ok: true, reply: 'ยกเลิกคำขอเลื่อนนัดแล้วค่ะ นัดเดิมยังอยู่' } }),
    handoff: vi.fn().mockResolvedValue({ status: 200, body: { ticket_id: 3, reply: 'ส่งต่อเจ้าหน้าที่แล้วค่ะ' } }),
    report: vi.fn().mockResolvedValue({ status: 200, body: { ticket_id: 4, reply: 'รับเรื่องแล้วค่ะ เจ้าหน้าที่จะตอบกลับภายใน 2 วันทำการ' } }),
    ...over,
  }
}
export const PROPOSAL_REPLY = { disabled: false, turn_id: 12, reply: 'สรุปการเลื่อนนัด งาน #1024', outcome: 'proposal', sources: [],
  proposal: { proposal_id: 5, job_id: 1024, old_start: '2026-10-06T14:00:00', new_start: '2026-10-07T09:00:00', technician: 'ประสิทธิ์' } }
