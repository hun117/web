import { ref } from 'vue'

export const currentPath = ref(window.location.pathname)

export function syncRoute() {
  currentPath.value = window.location.pathname
}

export function resolveRoute(path) {
  if (path === '/' || path === '/learn') return { name: 'courseCatalog', path }

  const course = path.match(/^\/course\/(\d+)$/)
  if (course) return { name: 'courseDetail', path, courseId: Number(course[1]) }
  if (path === '/payment/complete') return { name: 'paymentComplete', path }
  if (path === '/login') return { name: 'auth', path, mode: 'login' }
  if (path === '/register') return { name: 'auth', path, mode: 'register' }
  if (path === '/login/kakao/callback') return { name: 'auth', path, mode: 'login', kakaoCallback: true }
  if (path === '/posts') return { name: 'postList', path }
  if (path === '/posts/new') return { name: 'postCompose', path }

  const post = path.match(/^\/posts\/(\d+)$/)
  if (post) return { name: 'postDetail', path, postId: Number(post[1]) }
  return { name: 'notFound', path }
}

export function navigate(path) {
  if (path === currentPath.value) return
  window.history.pushState({}, '', path)
  currentPath.value = path
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
  window.scrollTo?.({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' })
}

export function handlePopState() {
  syncRoute()
}

export function handleRouteLinkClick(event) {
  const link = event.target.closest('a[data-route]')
  if (!link || event.defaultPrevented || event.button > 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
  event.preventDefault()
  navigate(link.getAttribute('href'))
}
