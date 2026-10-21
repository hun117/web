function getApiBaseUrl() {
  const configuredUrl = typeof __API_BASE_URL__ === 'undefined' ? '' : __API_BASE_URL__.trim()
  if (configuredUrl) return configuredUrl.replace(/\/+$/, '')

  throw new Error('The backend API origin is missing from the Vite configuration.')
}

export async function apiRequest(path, options = {}) {
  const apiBaseUrl = getApiBaseUrl()
  const apiPath = path.startsWith('/') ? path : `/${path}`
  const response = await fetch(`${apiBaseUrl}${apiPath}`, {
    ...options,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  const payload = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = payload?.detail ?? payload?.message
    const messages = {
      400: '이미 가입된 이메일입니다. 다른 주소를 사용해 주세요.',
      401: '이메일 또는 비밀번호를 확인해 주세요.',
      404: '요청한 내용을 찾을 수 없습니다. 목록에서 다시 선택해 주세요.',
      422: '입력한 내용을 확인해 주세요.',
    }
    const error = new Error(
      typeof detail === 'string' && ![400, 401, 404].includes(response.status)
        ? detail
        : messages[response.status] || '요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.',
    )
    error.status = response.status
    throw error
  }

  return payload?.result
}
