<script setup>
import { computed, ref } from 'vue'
import { courseArtwork } from '../assets/courseArtwork'

const props = defineProps({
  course: { type: Object, required: true },
  href: { type: String, default: '' },
})

const saved = ref(false)
const courseHref = computed(() => props.href || `/course/${props.course.id}`)
const coverStyle = computed(() => props.course.thumbnail
  ? { backgroundImage: `linear-gradient(180deg,transparent 42%,rgb(14 30 53 / 38%)),url('${courseArtwork(props.course.thumbnail)}')` }
  : {})

function toggleSaved() {
  saved.value = !saved.value
}
</script>

<template>
  <article class="course-card">
    <a class="course-card-main" :data-course="course.id" :href="courseHref" data-route>
      <div class="course-cover" :style="coverStyle" :aria-label="`${course.title} 강의 이미지`" role="img">
        <span class="course-cover-category">{{ course.category || '강의' }}</span>
        <span class="course-cover-level">{{ course.level || '온라인 강의' }}</span>
      </div>
      <div class="course-card-copy">
        <div class="course-card-heading">
          <h3>{{ course.title }}</h3>
          <span class="course-rating" :aria-label="`평점 ${course.rating || '신규'}`">★ {{ course.rating || '신규' }}</span>
        </div>
        <p class="course-instructor">{{ course.instructor }} 강사</p>
        <p class="course-meta">{{ course.duration || '온라인 수강' }} <span aria-hidden="true">·</span> 내 속도로 학습</p>
        <div class="course-price"><strong>{{ Number(course.price || 0).toLocaleString('ko-KR') }}원</strong><span>한 번 구매로 평생 수강</span></div>
      </div>
    </a>
    <button
      class="course-save"
      type="button"
      :aria-pressed="saved"
      :aria-label="saved ? `${course.title} 저장 취소` : `${course.title} 저장하기`"
      @click="toggleSaved"
    ><span aria-hidden="true">{{ saved ? '♥' : '♡' }}</span></button>
  </article>
</template>

<style scoped>
.course-card {
  position: relative;
  min-width: 0;
  border-radius: 17px;
  color: #202a38;
}

.course-card-main { display: block; color: inherit; text-decoration: none; }
.course-cover {
  position: relative;
  display: flex;
  min-height: 0;
  aspect-ratio: 1.32;
  align-items: flex-start;
  justify-content: space-between;
  overflow: hidden;
  padding: 14px;
  border-radius: 17px;
  background-color: #dce9fb;
  background-image: linear-gradient(140deg, #b8d2fb, #f0f5ff 48%, #d8e8ff);
  background-position: center;
  background-size: cover;
  transition: transform 220ms ease;
}

.course-card:hover .course-cover { transform: scale(1.012); }
.course-cover-category, .course-cover-level {
  padding: 6px 9px;
  border: 1px solid rgb(255 255 255 / 55%);
  border-radius: 999px;
  background: rgb(255 255 255 / 88%);
  color: #263247;
  font-size: 11px;
  font-weight: 700;
  backdrop-filter: blur(8px);
}

.course-cover-level { align-self: flex-end; background: rgb(20 31 48 / 62%); color: #fff; }
.course-card-copy { padding: 13px 2px 1px; }
.course-card-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.course-card-heading h3 { margin: 0; color: #202a38; font-size: 16px; font-weight: 700; letter-spacing: -.025em; line-height: 1.45; }
.course-rating { flex: 0 0 auto; color: #283142; font-size: 12px; white-space: nowrap; }
.course-instructor, .course-meta { margin: 5px 0 0; color: #6c7686; font-size: 12px; line-height: 1.5; }
.course-meta span { margin: 0 4px; }
.course-price { display: flex; align-items: baseline; flex-wrap: wrap; gap: 7px; margin-top: 10px; }
.course-price strong { color: #202a38; font-size: 14px; }
.course-price span { color: #6c7686; font-size: 11px; }
.course-save {
  position: absolute;
  z-index: 1;
  top: 10px;
  right: 10px;
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  border: 1px solid rgb(28 38 54 / 12%);
  border-radius: 50%;
  background: rgb(255 255 255 / 90%);
  color: #263247;
  cursor: pointer;
  font-size: 23px;
  line-height: 1;
  transition: color 150ms ease, transform 150ms ease, background 150ms ease;
}

.course-save:hover { transform: scale(1.07); }
.course-save[aria-pressed="true"] { color: #4285F4; }
.course-save:focus-visible { outline: 3px solid #4285F4; outline-offset: 3px; }

@media (max-width: 600px) {
  .course-cover { aspect-ratio: 1.48; }
  .course-card-copy { padding-top: 11px; }
}

@media (prefers-reduced-motion: reduce) { .course-cover, .course-save { transition: none; } }
</style>
