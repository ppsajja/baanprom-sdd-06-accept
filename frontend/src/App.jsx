// หน้าหลักของบ้านพร้อม R1: UC-07 จองงาน (เลือกช่าง ยืนยัน ผล), UC-08 ยกเลิกการจอง, UC-09 สถานะงานและงานของช่าง, UC-14 ผู้ช่วย (CR-09)
// ตัวอย่างใช้ลูกค้า ที่อยู่ และช่างคงที่ (การเข้าสู่ระบบของลูกค้า UC-02 และ sign-in ของแอปช่าง UC-01 เลื่อนไป R2 ดู README "R1 release scope"
// ส่วนการเลือกที่อยู่ให้บริการยังรอ Q-29) แถบเมนูด้านบนเป็นปุ่มนำทาง ไม่ต้องมี REQ รองรับ
import { useState } from 'react'
import { api as realApi, jobStatusApi as realJobStatusApi, cancelApi as realCancelApi, assistantApi as realAssistantApi } from './api/client.js'
import TechnicianPicker from './pages/TechnicianPicker.jsx'
import ConfirmBooking from './pages/ConfirmBooking.jsx'
import BookingResult from './pages/BookingResult.jsx'
import TechnicianJobs from './pages/TechnicianJobs.jsx'
import JobStatus from './pages/JobStatus.jsx'
import CancelBooking from './pages/CancelBooking.jsx'
import CancelResult from './pages/CancelResult.jsx'
import AssistantChat from './pages/AssistantChat.jsx'

const VIEWS = [
  ['book', 'จองงาน'], ['status', 'สถานะงาน'], ['cancel', 'ยกเลิกการจอง'], ['technician', 'งานของช่าง'], ['assistant', 'ผู้ช่วย'],
]

export default function App({ api = realApi, jobStatusApi = realJobStatusApi, cancelApi = realCancelApi, assistantApi = realAssistantApi,
  customerId = 1, addressId = 1, technicianId = 1, initialView = 'book' }) {
  const [view, setView] = useState(initialView)
  const [held, setHeld] = useState(null)
  const [job, setJob] = useState(null)
  const [cancelled, setCancelled] = useState(null)

  return (
    <main className="mx-auto max-w-2xl p-6">
      <header className="mb-4">
        <h1 className="text-2xl font-bold text-teal-800">บ้านพร้อม</h1>
        <p className="text-slate-600">จองช่างซ่อมบ้านที่ว่างจริง ไม่ต้องโทรถาม</p>
      </header>
      <nav aria-label="เมนู" className="mb-4 flex flex-wrap gap-2">
        {VIEWS.map(([key, label]) => (
          <button key={key} type="button" onClick={() => { setView(key); setCancelled(null) }} aria-current={view === key ? 'page' : undefined}
            className={`rounded-full px-3 py-1 text-sm ${view === key ? 'bg-teal-700 text-white' : 'bg-white text-teal-800 ring-1 ring-teal-700'}`}>
            {label}
          </button>
        ))}
      </nav>

      {view === 'book' && !held && !job && (
        <TechnicianPicker api={api} customerId={customerId} addressId={addressId} onHeld={setHeld} />
      )}
      {view === 'book' && held && !job && (
        <ConfirmBooking key={held.slot.slot_id} api={api} customerId={customerId} addressId={addressId} held={held}
          onConfirmed={setJob}
          onBack={() => setHeld(null)}
          onPickAlternative={(a) => setHeld({ ...held, slot: a, holdExpiresAt: null, technician: { technician_id: a.technician_id, name: a.technician_name } })} />
      )}
      {view === 'book' && job && <BookingResult job={job} technicianName={held?.technician?.name} onRestart={() => { setHeld(null); setJob(null) }} />}

      {view === 'status' && <JobStatus api={jobStatusApi} />}
      {view === 'cancel' && !cancelled && <CancelBooking api={cancelApi} customerId={customerId} onCancelled={setCancelled} />}
      {view === 'cancel' && cancelled && <CancelResult result={cancelled} onHome={() => { setCancelled(null); setView('book') }} />}
      {view === 'technician' && <TechnicianJobs api={jobStatusApi} technicianId={technicianId} />}
      {view === 'assistant' && <AssistantChat api={assistantApi} customerId={customerId} />}
    </main>
  )
}
