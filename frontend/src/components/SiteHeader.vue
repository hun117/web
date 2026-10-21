<script setup>
defineProps({ user: { type: Object, default: null } })
</script>

<template>
  <header class="topbar">
    <a class="brand" href="/" data-route><span class="brand-mark" aria-hidden="true">✦</span><span>배움상점</span></a>
    <p class="topline">배움이 실력이 되는 온라인 강의</p>
    <nav class="account-actions" aria-label="계정 메뉴">
      <span v-if="user" class="account-email" :aria-label="user.displayKind === 'nickname' ? '카카오 닉네임' : '로그인한 계정'">{{ user.displayName }}</span>
      <template v-else>
        <a class="text-link" href="/login" data-route>로그인</a>
        <a class="join-button" href="/register" data-route>가입하기</a>
      </template>
    </nav>
  </header>
</template>

<style scoped>
.account-actions {
  gap: 10px;
  font-family: inherit;
}

.account-actions a {
  display: inline-flex;
  min-height: 42px;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: 0 15px;
  border-radius: 999px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  line-height: 1;
  text-decoration: none;
  vertical-align: middle;
  white-space: nowrap;
  transition: color 160ms ease, background-color 160ms ease, border-color 160ms ease;
}

.account-actions .text-link {
  border: 1px solid transparent;
  background: transparent;
  color: #222;
}

.account-actions .text-link:hover {
  background: #f2f7ff;
  color: #2f73df;
}

.account-actions .join-button {
  border: 1px solid #d9dee8;
  background: #fff;
  color: #222;
}

.account-actions .join-button:hover {
  border-color: #4285F4;
  background: #f7faff;
  color: #202a38;
}

@media (max-width: 600px) {
  .account-actions { gap: 5px; }
  .account-actions a { min-height: 38px; padding-right: 10px; padding-left: 10px; font-size: 12px; }
}

@media (prefers-reduced-motion: reduce) {
  .account-actions a { transition: none; }
}
</style>
