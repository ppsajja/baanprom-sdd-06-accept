// AC-14-12 (REQ-AI-020): ข้อความแรกบอกว่าเป็นผู้ช่วยอัตโนมัติ และคำตอบแสดงที่มาและเวลาอัปเดตที่ระบบส่งมา
import { render, screen, fireEvent } from '@testing-library/react'
import AssistantChat from '../pages/AssistantChat.jsx'
import { fakeApi } from './_assistantFake.js'

test('AC-14-12 บอกว่าเป็นผู้ช่วยอัตโนมัติ และแสดงที่มาใต้คำตอบ', async () => {
  render(<AssistantChat api={fakeApi()} customerId={1} />)
  expect(await screen.findByTestId('greeting')).toHaveTextContent('ผู้ช่วยอัตโนมัติ')
  fireEvent.change(screen.getByLabelText('พิมพ์คำถาม'), { target: { value: 'ช่างมายัง' } })
  fireEvent.click(screen.getByRole('button', { name: 'ส่ง' }))
  const src = await screen.findByTestId('source')
  expect(src).toHaveTextContent('ที่มา: สถานะงาน #1024 อัปเดต')
  expect(src.textContent).toMatch(/09[:.]52/)
})
