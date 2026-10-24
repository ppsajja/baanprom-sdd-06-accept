// จุดเดียวที่หน้าจอใช้เรียก API หลังบ้าน (ตามสัญญา API ใน plan.md ข้อ 4)
// ตอน test ให้ส่ง client จำลองเข้าไปในหน้าจอแทน ไม่ต้องรันหลังบ้านจริง
// เรียกผ่าน /api (ดู proxy ใน vite.config.js) หลังบ้านต้องรันอยู่ที่ port 8000
const BASE = import.meta.env.VITE_API_BASE ?? '/api'

async function readJson(res) {
  return { status: res.status, body: await res.json() }
}

export const api = {
  // REQ-FN-008 ค้นช่างว่างใน 7 วัน
  async getTechnicians({ category, addressId, customerId }) {
    const q = new URLSearchParams({ category, address_id: addressId, customer_id: customerId })
    return readJson(await fetch(`${BASE}/technicians?${q}`))
  },
  // REQ-FN-041 ล็อกช่วงเวลาชั่วคราว (ระยะล็อกอยู่ที่หลังบ้าน config HOLD_MINUTES หน้าจอรับเวลาสิ้นสุดจากคำตอบ)
  async holdSlot({ slotId, customerId }) {
    return readJson(await fetch(`${BASE}/slots/${slotId}/hold`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: customerId }),
    }))
  },
  // REQ-BR-002 ยอดมัดจำตามประเภทงาน (AC-07-11) หน้าจอห้ามคำนวณหรือพิมพ์ยอดเอง
  async getDepositQuote({ category }) {
    const q = new URLSearchParams({ category })
    return readJson(await fetch(`${BASE}/deposit-quote?${q}`))
  },
  // UC-07 ขั้น 5 ยืนยันและชำระมัดจำ ตอบ 201 / 409 slot_taken / 402 payment_failed
  async createBooking({ customerId, slotId, addressId, category }) {
    return readJson(await fetch(`${BASE}/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: customerId, slot_id: slotId, address_id: addressId, category }),
    }))
  },
}

// ---- UC-09 ช่างอัปเดตสถานะงาน (specs/003-job-status, CR-05) ----
export const jobStatusApi = {
  // REQ-FN-050 รายการงานของช่างคนนี้ (เบอร์ลูกค้ามาเฉพาะช่วงที่ REQ-SEC-004 อนุญาต หน้าจอไม่คำนวณเอง)
  async getTechnicianJobs({ technicianId }) {
    return readJson(await fetch(`${BASE}/technicians/${technicianId}/jobs`))
  },
  // REQ-FN-051 เปลี่ยนสถานะตามลูกศรของ MD-STM-01 ตอบ 200 หรือ 409 transition_not_allowed
  async updateJobStatus({ jobId, technicianId, toStatus }) {
    return readJson(await fetch(`${BASE}/jobs/${jobId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ technician_id: technicianId, to_status: toStatus }),
    }))
  },
  // REQ-FN-052 มุมมองลูกค้าและ call center อ่านสถานะจากที่เดียวกับช่าง
  async getJob({ jobId }) {
    return readJson(await fetch(`${BASE}/jobs/${jobId}`))
  },
  // REQ-DAT-002 ประวัติการเปลี่ยนสถานะ
  async getJobHistory({ jobId }) {
    return readJson(await fetch(`${BASE}/jobs/${jobId}/history`))
  },
}

// ---- UC-08 ลูกค้ายกเลิกการจองและรับเงินคืน (specs/004-cancel-refund, CR-06) ----
export const cancelApi = {
  // REQ-FN-054 / REQ-BR-001 ยอดคืนตาม BR-01 จากระบบ หน้าจอห้ามคำนวณเอง (D-00-05)
  async getRefundQuote({ jobId, customerId }) {
    const q = new URLSearchParams({ customer_id: customerId })
    return readJson(await fetch(`${BASE}/jobs/${jobId}/refund-quote?${q}`))
  },
  // REQ-FN-054 ยกเลิกจริง ตอบ 200 หรือ 409 (R3 รอ Q-14, R6, ยกเลิกไปแล้ว)
  async cancelByCustomer({ jobId, customerId }) {
    return readJson(await fetch(`${BASE}/jobs/${jobId}/customer-cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: customerId }),
    }))
  },
}

// ---- UC-14 ผู้ช่วยตอบคำถามและเลื่อนนัด (specs/005-ai-assistant, CR-09) ----
async function post(path, body) {
  return readJson(await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }))
}

export const assistantApi = {
  // REQ-AI-022 ผู้ช่วยเปิดอยู่ไหม (ปิดอยู่ แสดงข้อความและปุ่มโทร)
  async getStatus() {
    return readJson(await fetch(`${BASE}/assistant/status`))
  },
  // REQ-AI-020 ข้อความแรกมาจากระบบ
  async start({ customerId }) {
    return post('/assistant/conversations', { customer_id: customerId })
  },
  async send({ conversationId, customerId, text }) {
    return post('/assistant/messages', { conversation_id: conversationId, customer_id: customerId, text })
  },
  // REQ-AI-011 ระดับ 2: เรียกเฉพาะเมื่อลูกค้ากด "ยืนยันเลื่อนนัด"
  async confirm({ proposalId, customerId }) {
    return post(`/assistant/proposals/${proposalId}/confirm`, { customer_id: customerId })
  },
  async decline({ proposalId, customerId }) {
    return post(`/assistant/proposals/${proposalId}/decline`, { customer_id: customerId })
  },
  async handoff({ conversationId, customerId }) {
    return post(`/assistant/conversations/${conversationId}/handoff`, { customer_id: customerId })
  },
  // REQ-AI-022 ปุ่ม "คำตอบนี้ไม่ถูกต้อง"
  async report({ turnId, customerId }) {
    return post(`/assistant/turns/${turnId}/report`, { customer_id: customerId })
  },
}
