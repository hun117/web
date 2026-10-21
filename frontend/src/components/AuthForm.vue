<script setup>
defineProps({
  mode: { type: String, default: 'login' },
  name: { type: String, default: '' },
  email: { type: String, default: '' },
  password: { type: String, default: '' },
  submitting: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['update:name', 'update:email', 'update:password', 'submit', 'kakao'])
</script>

<template>
  <section class="form-page auth-panel">
    <a class="back-link" href="/" data-route>← 강의 목록</a>
    <p class="form-kicker">{{ mode === 'register' ? '배움상점에서 만나요' : '다시 만나 반가워요' }}</p>
    <h1>{{ mode === 'register' ? '함께 시작하기' : '로그인' }}</h1>
    <p class="form-intro">{{ mode === 'register' ? '강의를 수강할 계정을 만들어 주세요.' : '계정에 로그인하고 배움을 이어가세요.' }}</p>
    <form @submit.prevent="$emit('submit')">
      <template v-if="mode === 'register'">
        <label for="auth-name">이름</label>
        <input id="auth-name" :value="name" name="name" autocomplete="name" required placeholder="이름을 입력해 주세요." @input="$emit('update:name', $event.target.value)">
      </template>
      <label for="auth-email">이메일</label>
      <input id="auth-email" :value="email" name="email" type="email" autocomplete="email" required spellcheck="false" placeholder="name@example.com" @input="$emit('update:email', $event.target.value)">
      <label for="auth-password">비밀번호</label>
      <input id="auth-password" :value="password" name="password" type="password" :autocomplete="mode === 'register' ? 'new-password' : 'current-password'" required placeholder="비밀번호를 입력해 주세요." @input="$emit('update:password', $event.target.value)">
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <button class="primary-action" type="submit" :disabled="submitting">
        {{ submitting ? '처리 중…' : mode === 'register' ? '가입하기' : '로그인' }}
      </button>
    </form>
    <p v-if="mode === 'register'" class="switch-auth">이미 계정이 있나요? <a href="/login" data-route>로그인</a></p>
    <p v-else class="switch-auth">아직 계정이 없나요? <a href="/register" data-route>가입하기</a></p>
    <button class="kakao-action" type="button" @click="$emit('kakao')">카카오로 로그인</button>
  </section>
</template>

<style scoped>
.auth-panel { border-color: #e5eaf2; border-radius: 18px; box-shadow: 0 14px 42px rgb(27 47 76 / 8%); }
.auth-panel .form-kicker { color: #4285F4; font-weight: 700; }
.auth-panel .primary-action { background: #4285F4; font-weight: 700; }
.auth-panel .primary-action:hover { background: #2f73df; }
.auth-panel .switch-auth a { color: #4285F4; }
.auth-panel .kakao-action { width: 100%; }
.auth-panel input:focus { border-color: #4285F4; box-shadow: 0 0 0 3px rgb(66 133 244 / 14%); }
</style>
