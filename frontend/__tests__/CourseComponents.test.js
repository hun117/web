import { mount } from '@vue/test-utils'
import AuthForm from '../src/components/AuthForm.vue'
import CategoryRail from '../src/components/CategoryRail.vue'
import CourseCard from '../src/components/CourseCard.vue'
import CourseGallery from '../src/components/CourseGallery.vue'
import CoursePurchaseCard from '../src/components/CoursePurchaseCard.vue'
import CourseSearchBar from '../src/components/CourseSearchBar.vue'

const course = {
  id: 12,
  title: 'Vue 기초부터 실전까지',
  instructor: '김강사',
  category: '개발',
  price: 59000,
  rating: 4.9,
  level: '입문',
  duration: '8시간',
  thumbnail: '',
}

describe('강의 화면 공용 컴포넌트', () => {
  test('검색어와 제출 동작을 부모 화면에 전달한다', async () => {
    const wrapper = mount(CourseSearchBar)
    await wrapper.get('input').setValue('Vue')
    await wrapper.get('form').trigger('submit')

    expect(wrapper.emitted('update:modelValue')).toEqual([['Vue']])
    expect(wrapper.emitted('search')).toHaveLength(1)
  })

  test('선택한 분야를 버튼 상태와 이벤트로 알린다', async () => {
    const wrapper = mount(CategoryRail, {
      props: { items: [{ label: '전체', icon: '✦' }, { label: '개발', icon: '⌘' }], modelValue: '전체' },
    })
    await wrapper.get('button:nth-child(2)').trigger('click')

    expect(wrapper.emitted('update:modelValue')).toEqual([['개발']])
    expect(wrapper.emitted('select')).toEqual([['개발']])
  })

  test('강의 카드 저장 버튼을 키보드 접근 가능한 토글로 제공한다', async () => {
    const wrapper = mount(CourseCard, { props: { course } })
    const saveButton = wrapper.get('.course-save')
    expect(saveButton.attributes('aria-pressed')).toBe('false')
    await saveButton.trigger('click')

    expect(wrapper.get('.course-save').attributes('aria-pressed')).toBe('true')
    expect(wrapper.get('a[data-course="12"]').attributes('href')).toBe('/course/12')
  })

  test('상세 갤러리는 모든 사진 보기 동작을 부모 화면에 전달한다', async () => {
    const wrapper = mount(CourseGallery, { props: { title: course.title, images: ['/one.svg', '/two.svg'] } })
    await wrapper.get('.gallery-view-all').trigger('click')

    expect(wrapper.findAll('img')).toHaveLength(2)
    expect(wrapper.emitted('view-all')).toHaveLength(1)
  })

  test('구매 요약 카드는 액션을 부모 화면에 전달한다', async () => {
    const wrapper = mount(CoursePurchaseCard, { props: { price: course.price } })
    await wrapper.get('button').trigger('click')

    expect(wrapper.text()).toContain('59,000원')
    expect(wrapper.emitted('action')).toHaveLength(1)
  })

  test('이미 수강 중인 강의는 가격과 구매 안내를 숨기고 강의 듣기만 표시한다', () => {
    const wrapper = mount(CoursePurchaseCard, {
      props: { price: course.price, enrolled: true, actionLabel: '강의 듣기' },
    })

    expect(wrapper.text()).toContain('강의 듣기')
    expect(wrapper.text()).not.toContain('59,000원')
    expect(wrapper.text()).not.toContain('일회 결제')
    expect(wrapper.text()).not.toContain('구매 후 언제든지 편하게 학습하세요')
    expect(wrapper.find('.purchase-price').exists()).toBe(false)
    expect(wrapper.find('.purchase-note').exists()).toBe(false)
  })

  test('인증 폼은 가입 필드와 입력 변경 이벤트를 제공한다', async () => {
    const wrapper = mount(AuthForm, { props: { mode: 'register' } })
    await wrapper.get('#auth-name').setValue('학습자')
    await wrapper.get('#auth-email').setValue('learner@example.com')
    await wrapper.get('form').trigger('submit')

    expect(wrapper.emitted('update:name')).toEqual([['학습자']])
    expect(wrapper.emitted('update:email')).toEqual([['learner@example.com']])
    expect(wrapper.emitted('submit')).toHaveLength(1)
  })
})
