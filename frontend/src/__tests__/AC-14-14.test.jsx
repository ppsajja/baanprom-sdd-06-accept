// AC-14-14 (REQ-AI-022) ส่วนหน้าจอ: ผู้ช่วยปิดอยู่ ลูกค้าเห็นข้อความจากระบบและปุ่มโทรหาเจ้าหน้าที่ ไม่มีช่องพิมพ์
import { render, screen } from '@testing-library/react'
import AssistantChat from '../pages/AssistantChat.jsx'
import { fakeApi } from './_assistantFake.js'

test('AC-14-14 ผู้ช่วยปิด แสดงข้อความและปุ่มโทร', async () => {
  const api = fakeApi({ start: vi.fn().mockResolvedValue({ status: 200, body: { disabled: true,
    reply: 'ผู้ช่วยปิดชั่วคราว กรุณาติดต่อเจ้าหน้าที่', call_center_tel: '02-000-0000' } }) })
  render(<AssistantChat api={api} customerId={1} />)
  expect(await screen.findByRole('alert')).toHaveTextContent('ผู้ช่วยปิดชั่วคราว กรุณาติดต่อเจ้าหน้าที่')
  expect(screen.getByRole('link', { name: 'โทรหาเจ้าหน้าที่' })).toHaveAttribute('href', 'tel:02-000-0000')
  expect(screen.queryByLabelText('พิมพ์คำถาม')).toBeNull()
  expect(api.send).not.toHaveBeenCalled()
})
