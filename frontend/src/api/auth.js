import { apiRequest } from './client'

export function getCurrentUser() {
  return apiRequest('/user/me')
}

export function login(credentials) {
  return apiRequest('/user/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

export function register(account) {
  return apiRequest('/user/signup', {
    method: 'POST',
    body: JSON.stringify(account),
  })
}

export function createKakaoLoginState() {
  return apiRequest('/user/oauth/kakao/state')
}

export function completeKakaoLogin(payload) {
  return apiRequest('/user/oauth/kakao/callback', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
