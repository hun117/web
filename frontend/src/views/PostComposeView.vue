<script setup>
import { ref } from 'vue'
import { createPost } from '../api/board'
import { notify } from '../stores/notifications'
import { navigate } from '../router'

const draft = ref({ title: '', contents: '' })
const submitting = ref(false)
const error = ref('')

async function publishPost() {
  submitting.value = true
  error.value = ''
  try {
    const created = await createPost(draft.value)
    draft.value = { title: '', contents: '' }
    notify('게시글을 등록했어요.')
    navigate(`/posts/${created.idx}`)
  } catch (cause) {
    error.value = cause.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-page">
    <a class="back-link" href="/posts" data-route>← 게시글 목록</a>
    <p class="form-kicker">모음에 남기는 이야기</p><h1>글쓰기</h1>
    <p class="form-intro">지금 떠오른 생각을 천천히 적어 주세요.</p>
    <form @submit.prevent="publishPost">
      <label for="post-title">제목</label><input id="post-title" v-model.trim="draft.title" name="title" autocomplete="off" maxlength="120" required placeholder="어떤 이야기를 나눌까요?">
      <label for="post-contents">내용</label><textarea id="post-contents" v-model.trim="draft.contents" name="contents" autocomplete="off" rows="8" required placeholder="편안한 마음으로 적어 주세요."></textarea>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <button class="primary-action" type="submit" :disabled="submitting">{{ submitting ? '등록 중…' : '게시글 등록' }}</button>
    </form>
  </section>
</template>
