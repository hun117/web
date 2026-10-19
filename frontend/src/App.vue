<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const route = ref(window.location.pathname)
const posts = ref([])
const post = ref(null)
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const notice = ref('')
const auth = ref({ name: '', email: '', password: '' })
const draft = ref({ title: '', contents: '' })
const page = computed(() => route.value === '/register' ? 'register' : route.value === '/login' ? 'login' : route.value === '/posts/new' ? 'compose' : route.value.startsWith('/posts/') ? 'detail' : 'list')
const postId = computed(() => Number(route.value.split('/')[2]))

async function api(path, options = {}) {
  const response = await fetch(path, { credentials: 'same-origin', headers: { 'Content-Type': 'application/json', ...options.headers }, ...options })
  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = payload?.detail
    const messages = { 400: '이미 가입된 이메일입니다. 다른 주소를 사용해 주세요.', 401: '이메일 또는 비밀번호를 확인해 주세요.', 404: '게시글을 찾을 수 없습니다. 목록에서 다시 선택해 주세요.', 422: '입력한 내용을 확인해 주세요.' }
    throw new Error(typeof detail === 'string' && response.status !== 400 && response.status !== 401 && response.status !== 404 ? detail : messages[response.status] || '요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.')
  }
  return payload?.result
}

function navigate(path) {
  if (path === route.value) return
  history.pushState({}, '', path)
  route.value = path
  error.value = ''
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
  window.scrollTo?.({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' })
  void loadRoute()
}
function onPopState() { route.value = window.location.pathname; error.value = ''; void loadRoute() }
function onDocumentClick(event) {
  const link = event.target.closest('a[data-route]')
  if (!link || event.defaultPrevented || event.button > 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
  event.preventDefault(); navigate(link.getAttribute('href'))
}
async function loadRoute() {
  const currentPage = page.value
  loading.value = currentPage === 'list' || currentPage === 'detail'
  post.value = null
  if (!loading.value) return
  error.value = ''
  try {
    if (currentPage === 'list') {
      const result = await api('/board/list')
      posts.value = result?.items ?? []
    } else post.value = await api(`/board/read/${postId.value}`)
  } catch (cause) { error.value = cause.message }
  finally { loading.value = false }
}
async function submitAuth() {
  submitting.value = true; error.value = ''
  try {
    if (page.value === 'register') {
      await api('/user/signup', { method: 'POST', body: JSON.stringify(auth.value) })
      auth.value = { name: '', email: '', password: '' }
      notice.value = '가입이 완료됐어요. 로그인해 주세요.'
      navigate('/login')
    } else {
      await api('/user/login', { method: 'POST', body: JSON.stringify({ email: auth.value.email, password: auth.value.password }) })
      notice.value = '로그인했어요.'
      auth.value = { name: '', email: '', password: '' }
      navigate('/posts')
    }
  } catch (cause) { error.value = cause.message }
  finally { submitting.value = false }
}
async function publishPost() {
  submitting.value = true; error.value = ''
  try {
    const created = await api('/board/rergister', { method: 'POST', body: JSON.stringify(draft.value) })
    draft.value = { title: '', contents: '' }
    notice.value = '게시글을 등록했어요.'
    navigate(`/posts/${created.idx}`)
  } catch (cause) { error.value = cause.message }
  finally { submitting.value = false }
}
watch(notice, (message) => { if (message) window.setTimeout(() => { notice.value = '' }, 3500) })
onMounted(() => { window.addEventListener('popstate', onPopState); void loadRoute() })
onUnmounted(() => { window.removeEventListener('popstate', onPopState) })
</script>

<template>
  <div class="site-shell" @click="onDocumentClick">
    <a class="skip-link" href="#main">본문으로 건너뛰기</a>
    <header class="topbar">
      <a class="brand" href="/posts" data-route><span class="brand-mark" aria-hidden="true">ㅁ</span><span>모음</span></a>
      <p class="topline">천천히 읽고, 다정하게 나누는 곳</p>
      <nav class="account-actions" aria-label="계정 메뉴">
        <a class="text-link" href="/login" data-route>로그인</a>
        <a class="join-button" href="/register" data-route>가입하기</a>
      </nav>
    </header>

    <main id="main" class="main-layout">
      <Transition name="page" mode="out-in">
        <section :key="route" class="page-content" :aria-busy="loading" aria-live="polite">
          <template v-if="page === 'list'">
            <div class="welcome">
              <div class="welcome-copy"><p class="welcome-kicker">오늘의 모음</p><h1>생각을 모으고<br>마음을 나누는 곳</h1><p class="welcome-text">읽고 싶은 이야기를 만나고, 나의 생각도 편하게 꺼내 보세요.</p></div>
              <div class="sun-art" aria-hidden="true"><span></span><i></i></div>
            </div>
            <div class="list-heading"><div><h2>게시글</h2><p>{{ loading ? '이야기를 불러오고 있어요' : `${posts.length}개의 이야기` }}</p></div><a class="compose-button" href="/posts/new" data-route><span aria-hidden="true">＋</span> 글쓰기</a></div>
            <div v-if="error" class="inline-alert" role="alert">{{ error }} <button type="button" @click="loadRoute">다시 불러오기</button></div>
            <ul v-if="loading" class="post-list skeleton-list" aria-label="게시글 불러오는 중"><li v-for="n in 4" :key="n" class="skeleton-row"><span class="skeleton skeleton-icon"></span><span class="skeleton-copy"><span class="skeleton skeleton-title"></span><span class="skeleton skeleton-line"></span></span></li></ul>
            <div v-else-if="!error && posts.length === 0" class="empty-state"><span class="empty-icon" aria-hidden="true">✳</span><h3>아직 나눈 이야기가 없어요</h3><p>첫 번째 이야기를 꺼내 보세요.</p><a href="/posts/new" class="compose-button" data-route>첫 글 쓰기</a></div>
            <ul v-else-if="!error" class="post-list" aria-label="게시글 목록"><li v-for="item in posts" :key="item.idx"><a class="post-row" :href="`/posts/${item.idx}`" data-route><span class="post-symbol" aria-hidden="true">✳</span><span class="post-copy"><span class="post-title">{{ item.title }}</span><span class="post-excerpt">{{ item.contents }}</span></span><span class="post-number">{{ String(item.idx).padStart(2, '0') }}</span></a></li></ul>
          </template>

          <section v-else-if="page === 'detail'" class="form-page detail-page">
            <a class="back-link" href="/posts" data-route>← 게시글 목록</a>
            <div v-if="loading" class="detail-skeleton" role="status" aria-label="게시글을 불러오는 중"><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-title detail-title"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line half"></span></div>
            <div v-else-if="error" class="inline-alert" role="alert">{{ error }} <a href="/posts" data-route>게시글 목록으로 이동</a></div>
            <article v-else-if="post" class="article"><p class="reading-label">모음의 게시글</p><h1>{{ post.title }}</h1><div class="reading-rule"><span></span></div><p class="reading-body">{{ post.contents }}</p><p class="reading-end">읽어 주셔서 고맙습니다.</p></article>
          </section>

          <section v-else class="form-page">
            <a class="back-link" href="/posts" data-route>← 게시글 목록</a>
            <p class="form-kicker">{{ page === 'compose' ? '모음에 남기는 이야기' : page === 'register' ? '모음에서 만나요' : '다시 만나 반가워요' }}</p>
            <h1>{{ page === 'compose' ? '글쓰기' : page === 'register' ? '함께하기' : '로그인' }}</h1>
            <p class="form-intro">{{ page === 'compose' ? '지금 떠오른 생각을 천천히 적어 주세요.' : page === 'register' ? '이야기를 나눌 계정을 만들어 주세요.' : '계정에 로그인하고 이야기를 이어가세요.' }}</p>
            <form @submit.prevent="page === 'compose' ? publishPost() : submitAuth()">
              <template v-if="page === 'compose'">
                <label for="post-title">제목</label><input id="post-title" v-model.trim="draft.title" name="title" autocomplete="off" maxlength="120" required placeholder="어떤 이야기를 나눌까요?">
                <label for="post-contents">내용</label><textarea id="post-contents" v-model.trim="draft.contents" name="contents" autocomplete="off" rows="8" required placeholder="편안한 마음으로 적어 주세요."></textarea>
              </template>
              <template v-else>
                <template v-if="page === 'register'"><label for="auth-name">이름</label><input id="auth-name" v-model.trim="auth.name" name="name" autocomplete="name" required placeholder="이름을 입력해 주세요."></template>
                <label for="auth-email">이메일</label><input id="auth-email" v-model.trim="auth.email" name="email" type="email" autocomplete="email" required spellcheck="false" placeholder="name@example.com">
                <label for="auth-password">비밀번호</label><input id="auth-password" v-model="auth.password" name="password" type="password" :autocomplete="page === 'register' ? 'new-password' : 'current-password'" required placeholder="비밀번호를 입력해 주세요.">
              </template>
              <p v-if="error" class="form-error" role="alert">{{ error }}</p>
              <button class="primary-action" type="submit" :disabled="submitting">{{ submitting ? (page === 'compose' ? '등록 중…' : '처리 중…') : page === 'compose' ? '게시글 등록' : page === 'register' ? '가입하기' : '로그인' }}</button>
            </form>
            <p v-if="page === 'register'" class="switch-auth">이미 계정이 있나요? <a href="/login" data-route>로그인</a></p>
            <p v-if="page === 'login'" class="switch-auth">아직 계정이 없나요? <a href="/register" data-route>가입하기</a></p>
          </section>
        </section>
      </Transition>

      <aside v-if="page === 'list'" class="reading-column" aria-label="게시글 안내"><div class="reading-empty"><div class="paper-mark" aria-hidden="true"><span></span><span></span><span></span></div><p>마음이 머무는 글을<br>골라 읽어 보세요</p><span class="reading-caption">이야기는 서로를 잇는 작은 다리가 됩니다.</span></div><div class="side-note"><span class="note-dot"></span><p>모음은 누구나 편히<br>이야기를 나누는 공간입니다.</p></div></aside>
    </main>
    <footer class="footer"><span>모음</span><span>천천히 읽고, 다정하게 나누는 곳</span></footer>
    <div v-if="notice" class="toast" role="status" aria-live="polite">{{ notice }}</div>
  </div>
</template>
