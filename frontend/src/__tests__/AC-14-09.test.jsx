// AC-14-09 (REQ-AI-011) ส่วนหน้าจอ: สรุปเลื่อนนัดแสดงค่าจากระบบ 4 ช่อง และไม่เรียกการเลื่อนนัดก่อนลูกค้ากดยืนยัน
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import AssistantChat from '../pages/AssistantChat.jsx'
import { fakeApi, PROPOSAL_REPLY } from './_assistantFake.js'
import { fmtDateTime } from '../statusNames.js'

async function askReschedule(api) {
  render(<AssistantChat api={api} customerId={1} />)
  await screen.findByTestId('greeting')
  fireEvent.change(screen.getByLabelText('พิมพ์คำถาม'), { target: { value: 'ขอเลื่อนเป็น 7 ต.ค. 09:00' } })
  fireEvent.click(screen.getByRole('button', { name: 'ส่ง' }))
  return screen.findByTestId('proposal')
}

test('AC-14-09 สรุปตรงกับค่าที่ระบบส่ง และกดยืนยันแล้วเรียก confirm ครั้งเดียว', async () => {
  const api = fakeApi({ send: vi.fn().mockResolvedValue({ status: 200, body: PROPOSAL_REPLY }) })
  const box = await askReschedule(api)
  expect(box).toHaveTextContent('#1024')
  expect(screen.getByTestId('old-start')).toHaveTextContent(fmtDateTime('2026-10-06T14:00:00'))
  expect(screen.getByTestId('new-start')).toHaveTextContent(fmtDateTime('2026-10-07T09:00:00'))
  expect(box).toHaveTextContent('ประสิทธิ์ (คนเดิม)')
  expect(api.confirm).not.toHaveBeenCalled()
  fireEvent.click(screen.getByRole('button', { name: 'ยืนยันเลื่อนนัด' }))
  await waitFor(() => expect(api.confirm).toHaveBeenCalledTimes(1))
  expect(api.confirm).toHaveBeenCalledWith({ proposalId: 5, customerId: 1 })
  expect(screen.queryByRole('button', { name: 'ยืนยันเลื่อนนัด' })).toBeNull()
})

test('AC-14-09 กด "ไม่ใช่" ไม่เรียกการเลื่อนนัด', async () => {
  const api = fakeApi({ send: vi.fn().mockResolvedValue({ status: 200, body: PROPOSAL_REPLY }) })
  await askReschedule(api)
  fireEvent.click(screen.getByRole('button', { name: 'ไม่ใช่' }))
  await waitFor(() => expect(api.decline).toHaveBeenCalledTimes(1))
  expect(api.confirm).not.toHaveBeenCalled()
  expect(await screen.findByText(/นัดเดิมยังอยู่/)).toBeInTheDocument()
})
