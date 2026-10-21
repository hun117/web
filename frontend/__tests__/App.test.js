import { flushPromises, mount } from '@vue/test-utils'
import App from '../src/App.vue'

const response = (result) => ({ ok: true, json: async () => ({ result }) })
const course = { id: 7, title: 'Vue로 만드는 첫 서비스', description: '실전 프로젝트로 배우는 Vue', instructor: '김강사', category: '개발', price: 59000, thumbnail: '', level: '입문', duration: '8시간', rating: 4.9 }

describe('배움상점', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
    window.matchMedia = jest.fn().mockReturnValue({ matches: false })
    window.scrollTo = jest.fn()
    sessionStorage.clear()
    global.fetch = jest.fn((path) => Promise.resolve(response(path === '/courses'
      ? { items: [course], total: 1 }
      : path === '/user/me' ? null : course)))
  })
  afterEach(() => jest.restoreAllMocks())

  test('기본 경로에서 강의 목록을 보여주고 상세 페이지로 이동한다', async () => {
    const wrapper = mount(App)
    await flushPromises()
    expect(global.fetch).toHaveBeenCalledWith('/courses', expect.objectContaining({ credentials: 'same-origin' }))
    expect(wrapper.text()).toContain(course.title)
    await wrapper.get('[data-course="7"]').trigger('click')
    await flushPromises()
    expect(window.location.pathname).toBe('/course/7')
    expect(global.fetch).toHaveBeenLastCalledWith('/courses/7', expect.objectContaining({ credentials: 'same-origin' }))
    expect(wrapper.text()).toContain(course.instructor)
    expect(wrapper.text()).toContain('구매하기')
    wrapper.unmount()
  })

  test('/learn 경로에서도 강의 목록을 제공한다', async () => {
    window.history.replaceState({}, '', '/learn')
    const wrapper = mount(App)
    await flushPromises()
    expect(global.fetch).toHaveBeenCalledWith('/courses', expect.objectContaining({ credentials: 'same-origin' }))
    expect(wrapper.text()).toContain(course.title)
    wrapper.unmount()
  })

  test('unauthenticated purchase redirects to login with readable guidance', async () => {
    window.history.replaceState({}, '', '/course/7')
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('.enroll-panel button').trigger('click')
    await flushPromises()

    expect(window.location.pathname).toBe('/login')
    expect(wrapper.text()).toContain('\uac15\uc758\u0020\uad6c\ub9e4\ub294\u0020\ub85c\uadf8\uc778\u0020\ud6c4\u0020\uc774\uc6a9\ud560\u0020\uc218\u0020\uc788\uc5b4\uc694\u002e\u0020\ub85c\uadf8\uc778\ud574\u0020\uc8fc\uc138\uc694\u002e')
    wrapper.unmount()
  })

  test('강의 구매 버튼이 서버 주문을 만든 뒤 PortOne Toss 결제창을 연다', async () => {
    window.history.replaceState({}, '', '/course/7')
    global.PortOne = { requestPayment: jest.fn().mockResolvedValue({}) }
    global.fetch = jest.fn((path) => Promise.resolve(response(path === '/user/me'
      ? { email: 'learner@example.com', display_name: 'Learner' }
      : path === '/payments/orders'
        ? { payment_id: 'course-order-123456', order_name: course.title, amount: 59000, currency: 'KRW', store_id: 'store-test', channel_key: 'channel-test' }
        : course)))
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('.enroll-panel button').trigger('click')
    await flushPromises()

    expect(global.fetch).toHaveBeenCalledWith('/payments/orders', expect.objectContaining({
      method: 'POST', body: JSON.stringify({ course_id: course.id }),
    }))
    expect(global.PortOne.requestPayment).toHaveBeenCalledWith(expect.objectContaining({
      storeId: 'store-test', channelKey: 'channel-test', paymentId: 'course-order-123456',
      totalAmount: 59000, currency: 'KRW', payMethod: 'CARD', forceRedirect: true,
    }))
    wrapper.unmount()
    delete global.PortOne
  })

  test('switches to enrolled state when the order API reports an existing enrollment', async () => {
    window.history.replaceState({}, '', '/course/7')
    global.PortOne = { requestPayment: jest.fn() }
    global.fetch = jest.fn((path) => {
      if (path === '/user/me') return Promise.resolve(response({ email: 'learner@example.com' }))
      if (path === '/courses/7') return Promise.resolve(response({ ...course, is_enrolled: false }))
      if (path === '/payments/orders') return Promise.resolve({
        ok: false,
        status: 409,
        json: async () => ({ detail: '\uC774\uBBF8 \uC218\uAC15 \uC911\uC778 \uAC15\uC758\uC785\uB2C8\uB2E4.' }),
      })
      return Promise.resolve(response(course))
    })
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('.enroll-panel button').trigger('click')
    await flushPromises()

    expect(wrapper.get('.enroll-panel button').text()).toBe('\uAC15\uC758 \uB4E3\uAE30')
    expect(wrapper.text()).not.toContain('\uAD6C\uB9E4\uD558\uAE30')
    expect(wrapper.find('.toast').text()).toContain('\uC774\uBBF8 \uC218\uAC15 \uC911\uC778 \uAC15\uC758')
    wrapper.unmount()
    delete global.PortOne
  })

  test('redirects to enrolled course after payment confirmation', async () => {
    window.history.replaceState({}, '', '/payment/complete?paymentId=course-order-123456')
    global.fetch = jest.fn((path) => Promise.resolve(response(path === '/user/me'
      ? { email: 'learner@example.com' }
      : path === '/payments/complete'
        ? { payment_id: 'course-order-123456', course_id: course.id, course_title: course.title, status: 'PAID' }
        : { ...course, is_enrolled: true })))
    const wrapper = mount(App)
    await flushPromises()

    expect(global.fetch).toHaveBeenCalledWith('/payments/complete', expect.objectContaining({
      method: 'POST', body: JSON.stringify({ payment_id: 'course-order-123456' }),
    }))
    expect(window.location.pathname).toBe(`/course/${course.id}`)
    expect(global.fetch).toHaveBeenCalledWith(`/courses/${course.id}`, expect.objectContaining({ credentials: 'same-origin' }))
    expect(wrapper.text()).toContain('\uac15\uc758 \ub4e3\uae30')
    expect(wrapper.text()).not.toContain('\uad6c\ub9e4\ud558\uae30')
    wrapper.unmount()
  })

  test('세션 사용자를 복원해 계정 메뉴에 표시한다', async () => {
    global.fetch = jest.fn((path) => Promise.resolve(response(path === '/user/me'
      ? { email: 'learner@example.com', display_name: '학습자', display_kind: 'nickname' }
      : { items: [course], total: 1 })))
    const wrapper = mount(App)
    await flushPromises()
    expect(global.fetch).toHaveBeenCalledWith('/user/me', expect.objectContaining({ credentials: 'same-origin' }))
    expect(wrapper.find('.account-email').text()).toBe('학습자')
    wrapper.unmount()
  })

  test('로그인 양식을 기존 API로 제출하고 강의 화면으로 돌아온다', async () => {
    window.history.replaceState({}, '', '/login')
    global.fetch = jest.fn((path) => Promise.resolve(response(path === '/user/me' ? null : path === '/user/login'
      ? { email: 'learner@example.com' }
      : { items: [course], total: 1 })))
    const wrapper = mount(App)
    await wrapper.get('input[type="email"]').setValue('learner@example.com')
    await wrapper.get('input[type="password"]').setValue('secret')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(global.fetch).toHaveBeenCalledWith('/user/login', expect.objectContaining({ method: 'POST' }))
    expect(window.location.pathname).toBe('/')
    expect(wrapper.find('.account-email').text()).toBe('learner@example.com')
    wrapper.unmount()
  })

  test('카카오 인증 state를 저장하고 OAuth 콜백을 교환한다', async () => {
    window.history.replaceState({}, '', '/login')
    window.Kakao = { isInitialized: () => false, init: jest.fn(), Auth: { authorize: jest.fn() } }
    global.fetch = jest.fn((path) => Promise.resolve(response(path === '/user/oauth/kakao/state'
      ? { state: 'state-123' }
      : path === '/user/me' ? null : path === '/user/oauth/kakao/callback'
        ? { display_name: '카카오 학습자', display_kind: 'nickname' }
        : { items: [course], total: 1 })))
    const wrapper = mount(App, { global: { provide: { kakaoJavascriptKey: 'javascript-key' } } })
    await flushPromises()
    await wrapper.get('.kakao-action').trigger('click')
    await flushPromises()
    expect(sessionStorage.getItem('kakaoOAuthState')).toBe('state-123')
    expect(window.Kakao.Auth.authorize).toHaveBeenCalledWith(expect.objectContaining({ state: 'state-123' }))

    window.history.replaceState({}, '', '/login/kakao/callback?code=oauth-code&state=state-123')
    sessionStorage.setItem('kakaoOAuthState', 'state-123')
    wrapper.unmount()
    const callback = mount(App, { global: { provide: { kakaoJavascriptKey: 'javascript-key' } } })
    await flushPromises()
    expect(global.fetch).toHaveBeenCalledWith('/user/oauth/kakao/callback', expect.objectContaining({ method: 'POST' }))
    expect(window.location.pathname).toBe('/')
    expect(callback.find('.account-email').text()).toBe('카카오 학습자')
    callback.unmount()
    delete window.Kakao
  })
})
