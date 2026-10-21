<script setup>
import { computed, onBeforeMount, onMounted, onUnmounted } from 'vue'
import SiteFooter from './components/SiteFooter.vue'
import SiteHeader from './components/SiteHeader.vue'
import ToastMessage from './components/ToastMessage.vue'
import ReadingSidebar from './components/ReadingSidebar.vue'
import { currentPath, handlePopState, handleRouteLinkClick, resolveRoute, syncRoute } from './router'
import { currentUser, restoreCurrentUser } from './stores/session'
import { clearNotice, notice } from './stores/notifications'
import AuthView from './views/AuthView.vue'
import CourseCatalogView from './views/CourseCatalogView.vue'
import CourseDetailView from './views/CourseDetailView.vue'
import NotFoundView from './views/NotFoundView.vue'
import PaymentCompleteView from './views/PaymentCompleteView.vue'
import PostComposeView from './views/PostComposeView.vue'
import PostDetailView from './views/PostDetailView.vue'
import PostListView from './views/PostListView.vue'

const views = {
  auth: AuthView,
  courseCatalog: CourseCatalogView,
  courseDetail: CourseDetailView,
  notFound: NotFoundView,
  paymentComplete: PaymentCompleteView,
  postCompose: PostComposeView,
  postDetail: PostDetailView,
  postList: PostListView,
}
const activeRoute = computed(() => resolveRoute(currentPath.value))
const currentView = computed(() => views[activeRoute.value.name] || NotFoundView)
const viewProps = computed(() => ['auth', 'courseDetail', 'postDetail'].includes(activeRoute.value.name)
  ? { route: activeRoute.value }
  : {})

onMounted(() => {
  window.addEventListener('popstate', handlePopState)
  if (!activeRoute.value.kakaoCallback) void restoreCurrentUser()
})

onBeforeMount(() => {
  syncRoute()
  clearNotice()
})

onUnmounted(() => window.removeEventListener('popstate', handlePopState))
</script>

<template>
  <div class="site-shell" @click="handleRouteLinkClick">
    <a class="skip-link" href="#main">본문으로 건너뛰기</a>
    <SiteHeader :user="currentUser" />
    <main id="main" class="main-layout">
      <Transition name="page" mode="out-in">
        <component :is="currentView" :key="currentPath" v-bind="viewProps" class="page-content" />
      </Transition>
      <ReadingSidebar v-if="activeRoute.name === 'postList'" />
    </main>
    <SiteFooter />
    <ToastMessage :message="notice" />
  </div>
</template>
