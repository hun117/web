import { flushPromises, mount } from '@vue/test-utils'
import App from '../src/App.vue'

const response = (result) => ({ ok: true, json: async () => ({ result }) })

describe('모음 게시판', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/posts')
    window.matchMedia = jest.fn().mockReturnValue({ matches: false })
    window.scrollTo = jest.fn()
    global.fetch = jest.fn((path) => path === '/board/list'
      ? Promise.resolve(response({ items: [{ idx: 4, title: '작은 생각의 기록', contents: '오늘 발견한 이야기를 나눠요.' }], total: 1 }))
      : Promise.resolve(response({ idx: 4, title: '작은 생각의 기록', contents: '오늘 발견한 이야기를 나눠요.' })))
  })
  afterEach(() => jest.restoreAllMocks())

  test('게시글 목록을 불러오고 상세 페이지로 이동한다', async () => {
    const wrapper = mount(App)
    await flushPromises()
    expect(global.fetch).toHaveBeenCalledWith('/board/list', expect.objectContaining({ credentials: 'same-origin' }))
    expect(wrapper.text()).toContain('작은 생각의 기록')
    await wrapper.get('.post-row').trigger('click')
    await flushPromises()
    expect(window.location.pathname).toBe('/posts/4')
    expect(wrapper.text()).toContain('작은 생각의 기록')
    wrapper.unmount()
  })

  test('회원가입 페이지에 이름, 이메일, 비밀번호 입력을 제공한다', async () => {
    window.history.replaceState({}, '', '/register')
    const wrapper = mount(App)
    expect(wrapper.get('h1').text()).toBe('함께하기')
    expect(wrapper.find('label[for="auth-name"]').exists()).toBe(true)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    wrapper.unmount()
  })

  test('게시글 작성 페이지에 제목과 내용 입력을 제공한다', async () => {
    window.history.replaceState({}, '', '/posts/new')
    const wrapper = mount(App)
    expect(wrapper.get('h1').text()).toBe('글쓰기')
    expect(wrapper.find('label[for="post-title"]').exists()).toBe(true)
    expect(wrapper.find('label[for="post-contents"]').exists()).toBe(true)
    wrapper.unmount()
  })
})
