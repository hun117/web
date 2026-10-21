<script setup>
import { onMounted, ref } from 'vue'
import { getPost } from '../api/board'

const props = defineProps({ route: { type: Object, required: true } })
const post = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    post.value = await getPost(props.route.postId)
  } catch (cause) {
    error.value = cause.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="form-page detail-page">
    <a class="back-link" href="/posts" data-route>← 게시글 목록</a>
    <div v-if="loading" class="detail-skeleton" role="status" aria-label="게시글을 불러오는 중"><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-title detail-title"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line half"></span></div>
    <div v-else-if="error" class="inline-alert" role="alert">{{ error }} <a href="/posts" data-route>게시글 목록으로 이동</a></div>
    <article v-else-if="post" class="article"><p class="reading-label">모음의 게시글</p><h1>{{ post.title }}</h1><div class="reading-rule"><span></span></div><p class="reading-body">{{ post.contents }}</p><p class="reading-end">읽어 주셔서 고맙습니다.</p></article>
  </section>
</template>
