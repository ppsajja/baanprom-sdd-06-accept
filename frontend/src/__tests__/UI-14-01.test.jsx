// ตรวจรายการ "ต้องตรง" ของ UI-14-01 แชตผู้ช่วย (spec ส่วน 12 ของ specs/005-ai-assistant)
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import AssistantChat from '../pages/AssistantChat.jsx'
import { fakeApi, GREETING } from './_assistantFake.js'

test('UI-14-01 ข้อความแรกมาจากระบบ ปุ่มคุยกับเจ้าหน้าที่ และปุ่มคำตอบนี้ไม่ถูกต้องใต้คำตอบ', async () => {
  const api = fakeApi()
  render(<AssistantChat api={api} customerId={1} />)
  await waitFor(() => expect(screen.getByTestId('greeting')).toHaveTextContent(GREETING))
  expect(screen.getByRole('button', { name: 'คุยกับเจ้าหน้าที่' })).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('พิมพ์คำถาม'), { target: { value: 'ช่างมายัง' } })
  fireEvent.click(screen.getByRole('button', { name: 'ส่ง' }))
  await waitFor(() => expect(screen.getByText(/ช่างกำลังเดินทาง/)).toBeInTheDocument())
  expect(screen.getByRole('button', { name: 'คุยกับเจ้าหน้าที่' })).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'คำตอบนี้ไม่ถูกต้อง' }))
  await waitFor(() => expect(api.report).toHaveBeenCalledWith({ turnId: 11, customerId: 1 }))
  expect(await screen.findByText(/2 วันทำการ/)).toBeInTheDocument()
})

test('UI-14-01 กดคุยกับเจ้าหน้าที่ สร้างตั๋วส่งต่อ', async () => {
  const api = fakeApi()
  render(<AssistantChat api={api} customerId={1} />)
  await screen.findByTestId('greeting')
  fireEvent.click(screen.getByRole('button', { name: 'คุยกับเจ้าหน้าที่' }))
  await waitFor(() => expect(api.handoff).toHaveBeenCalledWith({ conversationId: 7, customerId: 1 }))
})
