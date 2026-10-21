import { apiRequest } from './client'

export function createPaymentOrder(courseId) {
  return apiRequest('/payments/orders', {
    method: 'POST',
    body: JSON.stringify({ course_id: courseId }),
  })
}

export function confirmPayment(paymentId) {
  return apiRequest('/payments/complete', {
    method: 'POST',
    body: JSON.stringify({ payment_id: paymentId }),
  })
}
