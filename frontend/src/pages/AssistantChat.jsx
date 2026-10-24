// หน้าแชตผู้ช่วย (UC-14) ตามแบบ UI-14-01 (CR-09) รองรับ REQ-AI-020, REQ-AI-011, REQ-AI-022, REQ-AI-012
// ทุกข้อความของผู้ช่วยมาจากระบบ หน้าจอไม่แต่งข้อความเอง สรุปเลื่อนนัดแสดงค่าจากระบบ (ค่าที่จะส่ง API D-14-03)
// ก่อนลูกค้ากด "ยืนยันเลื่อนนัด" หน้าจอไม่เรียกการเลื่อนนัด กล่อง "รอ Q-55" (ค่าธรรมเนียม) ใน mockup ไม่สร้าง (SH-01 ตอบว่าไม่มีค่าธรรมเนียม)
import { useEffect, useState } from 'react'
import { fmtDateTime } from '../statusNames.js'

function fmtTime(iso) {
  return new Date(iso).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
}

export default function AssistantChat({ api, customerId }) {
  const [conv, setConv] = useState(null)
  const [disabled, setDisabled] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let alive = true
    api.start({ customerId }).then(({ body }) => {
      if (!alive) return
      if (body.disabled) return setDisabled(body)
      setConv(body.conversation_id)
      setMessages([{ from: 'bot', reply: body.greeting, greeting: true }])
    })
    return () => { alive = false }
  }, [api, customerId])

  function push(m) { setMessages((ms) => [...ms, m]) }

  async function send(e) {
    e?.preventDefault()
    if (!text.trim()) return
    const mine = text
    setText('')
    push({ from: 'me', reply: mine })
    setBusy(true)
    const { body } = await api.send({ conversationId: conv, customerId, text: mine })
    setBusy(false)
    if (body.disabled) return setDisabled(body)
    push({ from: 'bot', ...body })
  }

  async function decide(m, yes) {
    const call = yes ? api.confirm : api.decline
    const { body } = await call({ proposalId: m.proposal.proposal_id, customerId })
    setMessages((ms) => ms.map((x) => (x === m ? { ...x, decided: true } : x)))
    push({ from: 'bot', reply: body.reply })
  }

  async function report(m) {
    const { body } = await api.report({ turnId: m.turn_id, customerId })
    setMessages((ms) => ms.map((x) => (x === m ? { ...x, reported: true } : x)))
    push({ from: 'bot', reply: body.reply })
  }

  async function human() {
    if (!conv) return
    const { body } = await api.handoff({ conversationId: conv, customerId })
    push({ from: 'bot', reply: body.reply })
  }

  if (disabled) {
    return (
      <section className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-800">ผู้ช่วย</h2>
        <p role="alert" className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">{disabled.reply}</p>
        <a href={`tel:${disabled.call_center_tel}`} className="mt-3 inline-block rounded-lg bg-teal-700 px-4 py-2 text-sm font-medium text-white">โทรหาเจ้าหน้าที่</a>
      </section>
    )
  }

  return (
    <section className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-800">ผู้ช่วย</h2>
      <ol aria-label="บทสนทนา" className="mt-3 space-y-2">
        {messages.map((m, i) => (
          <li key={i} className={m.from === 'me' ? 'ml-10 rounded-lg bg-slate-100 p-2 text-sm' : 'rounded-lg border border-teal-200 bg-teal-50 p-2 text-sm'}>
            <p data-testid={m.greeting ? 'greeting' : undefined}>{m.reply}</p>
            {m.from === 'bot' && m.sources?.length > 0 && (
              <p className="mt-1 text-xs text-slate-500" data-testid="source">
                ที่มา: {m.sources.map((s) => `${s.label} อัปเดต ${fmtTime(s.updated_at)}`).join(', ')}
              </p>
            )}
            {m.proposal && (
              <div className="mt-2" data-testid="proposal">
                <table className="text-sm"><tbody>
                  <tr><td className="pr-3">งาน</td><td>#{m.proposal.job_id}</td></tr>
                  <tr><td className="pr-3">วันเวลาเดิม</td><td data-testid="old-start">{fmtDateTime(m.proposal.old_start)}</td></tr>
                  <tr><td className="pr-3">วันเวลาใหม่</td><td data-testid="new-start">{fmtDateTime(m.proposal.new_start)}</td></tr>
                  <tr><td className="pr-3">ช่าง</td><td>{m.proposal.technician} (คนเดิม)</td></tr>
                </tbody></table>
                {!m.decided && (
                  <div className="mt-2 flex gap-2">
                    <button type="button" onClick={() => decide(m, true)} className="rounded-lg bg-teal-700 px-3 py-1 text-white">ยืนยันเลื่อนนัด</button>
                    <button type="button" onClick={() => decide(m, false)} className="rounded-lg px-3 py-1 text-teal-800 ring-1 ring-teal-700">ไม่ใช่</button>
                  </div>
                )}
              </div>
            )}
            {m.from === 'bot' && m.turn_id && !m.reported && (
              <button type="button" onClick={() => report(m)} className="mt-1 text-xs text-slate-500 underline">คำตอบนี้ไม่ถูกต้อง</button>
            )}
          </li>
        ))}
      </ol>
      <form onSubmit={send} className="mt-3 flex gap-2">
        <label className="flex-1 text-sm text-slate-600">
          พิมพ์คำถาม
          <input value={text} onChange={(e) => setText(e.target.value)} maxLength={500}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900" />
        </label>
        <button type="submit" disabled={busy || !conv} className="self-end rounded-lg bg-teal-700 px-4 py-2 text-sm font-medium text-white">ส่ง</button>
      </form>
      <button type="button" onClick={human} className="mt-3 rounded-lg px-3 py-1 text-sm text-teal-800 ring-1 ring-teal-700">คุยกับเจ้าหน้าที่</button>
    </section>
  )
}
