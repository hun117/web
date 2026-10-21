<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { completeKakaoLogin, createKakaoLoginState, login, register } from '../api/auth'
import { currentUser, setCurrentUser } from '../stores/session'
import { notify } from '../stores/notifications'
import { navigate } from '../router'
import AuthForm from '../components/AuthForm.vue'

const props = defineProps({ route: { type: Object, required: true } })
const kakaoJavascriptKey = inject('kakaoJavascriptKey', '')
const auth = ref({ name: '', email: '', password: '' })
const submitting = ref(false)
const error = ref('')
const isRegister = computed(() => props.route.mode === 'register')

function initializeKakao() {
  if (kakaoJavascriptKey && window.Kakao && !window.Kakao.isInitialized?.()) window.Kakao.init(kakaoJavascriptKey)
}

async function submitAuth() {
  submitting.value = true
  error.value = ''
  try {
    if (isRegister.value) {
      await register(auth.value)
      auth.value = { name: '', email: '', password: '' }
      notify('가입이 완료됐어요. 로그인해 주세요.')
      navigate('/login')
    } else {
      const user = await login({ email: auth.value.email, password: auth.value.password })
      setCurrentUser(user || { email: auth.value.email })
      notify('로그인했어요.')
      auth.value = { name: '', email: '', password: '' }
      navigate('/')
    }
  } catch (cause) {
    error.value = cause.message
  } finally {
    submitting.value = false
  }
}

async function startKakaoLogin() {
  error.value = ''
  try {
    initializeKakao()
    if (!kakaoJavascriptKey || !window.Kakao?.Auth?.authorize) throw new Error('카카오 로그인을 사용할 수 없습니다.')
    const result = await createKakaoLoginState()
    window.sessionStorage.setItem('kakaoOAuthState', result.state)
    window.Kakao.Auth.authorize({ redirectUri: `${window.location.origin}/login/kakao/callback`, state: result.state, scope: 'profile_nickname' })
  } catch (cause) {
    error.value = cause.message
  }
}

async function completeKakaoCallback() {
  const params = new URLSearchParams(window.location.search)
  const code = params.get('code')
  const state = params.get('state')
  const providerError = params.get('error')
  window.history.replaceState({}, '', window.location.pathname)
  const expectedState = window.sessionStorage.getItem('kakaoOAuthState')
  window.sessionStorage.removeItem('kakaoOAuthState')
  if (!expectedState || !state || state !== expectedState) {
    error.value = '카카오 로그인 확인 정보가 유효하지 않습니다. 다시 시도해 주세요.'
    return
  }

  try {
    const user = await completeKakaoLogin(providerError ? { state, error: providerError } : { code, state })
    setCurrentUser(user)
    notify('카카오 계정으로 로그인했어요.')
    navigate('/')
  } catch (cause) {
    error.value = cause.message === 'cancelled' ? '카카오 로그인을 취소했어요.' : cause.message
  }
}

onMounted(() => {
  initializeKakao()
  if (props.route.kakaoCallback) void completeKakaoCallback()
})
</script>

<template>
  <AuthForm
    v-model:name.trim="auth.name"
    v-model:email.trim="auth.email"
    v-model:password="auth.password"
    :mode="isRegister ? 'register' : 'login'"
    :submitting="submitting"
    :error="error"
    @submit="submitAuth"
    @kakao="startKakaoLogin"
  />
</template>
