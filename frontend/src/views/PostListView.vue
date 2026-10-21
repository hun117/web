<script setup>
import { onMounted, ref } from 'vue'
import { getPosts } from '../api/board'

const posts = ref([])
const loading = ref(true)
const error = ref('')

async function loadPosts() {
  loading.value = true
  error.value = ''
  try {
    const result = await getPosts()
    posts.value = result?.items ?? []
  } catch (cause) {
    error.value = cause.message
  } finally {
    loading.value = false
  }
}

onMounted(loadPosts)
</script>

<template>
  <section>
    <div class="welcome"><div class="welcome-copy"><p class="welcome-kicker">오늘의 모음</p><h1>생각을 모으고<br>마음을 나누는 곳</h1><p class="welcome-text">읽고 싶은 이야기를 만나고, 나의 생각도 편하게 꺼내 보세요.</p></div><div class="sun-art" aria-hidden="true"><span></span><i></i></div></div>
    <div class="list-heading"><div><h2>게시글</h2><p>{{ loading ? '이야기를 불러오고 있어요' : `${posts.length}개의 이야기` }}</p></div><a class="compose-button" href="/posts/new" data-route><span aria-hidden="true">＋</span> 글쓰기</a></div>
    <div v-if="error" class="inline-alert" role="alert">{{ error }} <button type="button" @click="loadPosts">다시 불러오기</button></div>
    <ul v-if="loading" class="post-list skeleton-list" aria-label="게시글 불러오는 중"><li v-for="n in 4" :key="n" class="skeleton-row"><span class="skeleton skeleton-icon"></span><span class="skeleton-copy"><span class="skeleton skeleton-title"></span><span class="skeleton skeleton-line"></span></span></li></ul>
    <div v-else-if="!error && !posts.length" class="empty-state"><span class="empty-icon" aria-hidden="true">✳</span><h3>아직 나눈 이야기가 없어요</h3><p>첫 번째 이야기를 꺼내 보세요.</p><a href="/posts/new" class="compose-button" data-route>첫 글 쓰기</a></div>
    <ul v-else-if="!error" class="post-list" aria-label="게시글 목록"><li v-for="item in posts" :key="item.idx"><a class="post-row" :href="`/posts/${item.idx}`" data-route><span class="post-symbol" aria-hidden="true">✳</span><span class="post-copy"><span class="post-title">{{ item.title }}</span><span class="post-excerpt">{{ item.contents }}</span></span><span class="post-number">{{ String(item.idx).padStart(2, '0') }}</span></a></li></ul>
  </section>
</template>
