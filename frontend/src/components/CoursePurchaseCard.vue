<script setup>
defineProps({
  price: { type: [Number, String], required: true },
  actionLabel: { type: String, default: '구매하기' },
  busy: { type: Boolean, default: false },
  error: { type: String, default: '' },
  enrolled: { type: Boolean, default: false },
})

defineEmits(['action'])
</script>

<template>
  <aside class="enroll-panel" :aria-label="enrolled ? '수강 중인 강의' : '강의 구매 정보'">
    <p v-if="!enrolled" class="purchase-label">강의 구매</p>
    <div v-if="!enrolled" class="purchase-price"><strong>{{ Number(price).toLocaleString('ko-KR') }}원</strong><span>일회 결제</span></div>
    <button type="button" class="primary-action" :disabled="busy" @click="$emit('action')">
      {{ busy ? '결제 연결 중…' : actionLabel }}
    </button>
    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="!enrolled" class="purchase-note"><span aria-hidden="true">✓</span> 구매 후 언제든지 편하게 학습하세요</p>
    <slot />
  </aside>
</template>

<style scoped>
.enroll-panel {
  align-self: start;
  position: sticky;
  top: 24px;
  padding: 21px;
  border: 1px solid #e4e8ef;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 32px rgb(24 42 67 / 8%);
}

.purchase-label { margin: 0 0 11px; color: #697588; font-size: 12px; font-weight: 600; }
.purchase-price { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; margin-bottom: 17px; }
.purchase-price strong { color: #202a38; font-size: 22px; letter-spacing: -.035em; }
.purchase-price span { color: #788394; font-size: 11px; }
.enroll-panel .primary-action { width: 100%; min-height: 48px; margin: 0; border: 0; border-radius: 10px; background: #4285F4; color: #fff; font-size: 14px; font-weight: 700; cursor: pointer; }
.enroll-panel .primary-action:hover { background: #2f73df; }
.enroll-panel .primary-action:disabled { cursor: wait; opacity: .68; }
.purchase-note { display: flex; align-items: flex-start; gap: 7px; margin: 13px 0 0; color: #6c7686; font-size: 11px; line-height: 1.55; }
.purchase-note span { color: #4285F4; font-weight: 800; }
.enroll-panel .form-error { margin: 12px 0 0; }

@media (max-width: 760px) { .enroll-panel { position: static; } }
</style>
