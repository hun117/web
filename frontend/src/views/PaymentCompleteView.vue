<script setup>
import { onMounted, ref } from 'vue'
import { confirmPayment } from '../api/payments'
import { notify } from '../stores/notifications'
import { navigate } from '../router'

const error = ref('')

async function completePayment() {
  const params = new URLSearchParams(window.location.search)
  const paymentId = params.get('paymentId')
  const providerError = params.get('code')
  window.history.replaceState({}, '', window.location.pathname)
  if (providerError || !paymentId) {
    error.value = '결제가 취소되었거나 결제 정보를 확인할 수 없습니다.'
    return
  }

  try {
    const result = await confirmPayment(paymentId)
    notify(`${result.course_title} 결제가 확인되었어요. 강의로 이동합니다.`)
    navigate(`/course/${result.course_id}`)
  } catch (cause) {
    error.value = cause.message || '결제 확인을 완료하지 못했어요. 잠시 후 다시 시도해 주세요.'
  }
}

onMounted(completePayment)
</script>

<template>
  <section class="form-page">
    <a class="back-link" href="/" data-route>강의 목록</a>
    <p class="form-kicker">PORTONE CHECKOUT</p>
    <h1>결제 확인</h1>
    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-else role="status">결제를 확인하고 있습니다.</p>
  </section>
</template>
