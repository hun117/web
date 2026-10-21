<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { getCourses } from '../api/courses'
import CourseCard from '../components/CourseCard.vue'
import CategoryRail from '../components/CategoryRail.vue'
import CourseSearchBar from '../components/CourseSearchBar.vue'

const courses = ref([])
const loading = ref(true)
const error = ref('')
const queryDraft = ref('')
const searchTerm = ref('')
const selectedCategory = ref('전체')
const displayedCourses = ref([])
const pendingCourses = ref([])
const cardsAreLeaving = ref(false)
let leavingCardCount = 0

const categoryIcons = { 개발: '⌘', 디자인: '✳', 비즈니스: '↗', 마케팅: '◉', 데이터: '▤', 취미: '✦' }
const categories = computed(() => [
  { label: '전체', icon: '✦' },
  ...[...new Set(courses.value.map((course) => course.category).filter(Boolean))]
    .map((label) => ({ label, icon: categoryIcons[label] || '◌' })),
])
const filteredCourses = computed(() => {
  const query = searchTerm.value.toLocaleLowerCase('ko-KR')
  return courses.value.filter((course) => {
    const matchesCategory = selectedCategory.value === '전체' || course.category === selectedCategory.value
    const searchable = [course.title, course.instructor, course.category, course.description].filter(Boolean).join(' ').toLocaleLowerCase('ko-KR')
    return matchesCategory && (!query || searchable.includes(query))
  })
})

function applySearch() {
  searchTerm.value = queryDraft.value.trim()
}

function stageFilteredCourses() {
  pendingCourses.value = [...filteredCourses.value]

  // Keep only the latest filter choice while the current cards finish leaving.
  if (cardsAreLeaving.value) return

  if (!displayedCourses.value.length) {
    displayedCourses.value = pendingCourses.value
    pendingCourses.value = []
    return
  }

  cardsAreLeaving.value = true
  leavingCardCount = displayedCourses.value.length
  displayedCourses.value = []
}

function onCourseCardAfterLeave() {
  if (!cardsAreLeaving.value) return

  leavingCardCount = Math.max(0, leavingCardCount - 1)
  if (leavingCardCount > 0) return

  cardsAreLeaving.value = false
  displayedCourses.value = pendingCourses.value
  pendingCourses.value = []
}

watch([selectedCategory, searchTerm], stageFilteredCourses)

async function loadCourses() {
  loading.value = true
  error.value = ''
  try {
    const result = await getCourses()
    courses.value = result?.items ?? []
    displayedCourses.value = [...filteredCourses.value]
  } catch (cause) {
    error.value = cause.message
  } finally {
    loading.value = false
  }
}

onMounted(loadCourses)
</script>

<template>
  <section>
    <section class="academy-hero">
      <div><p class="academy-kicker">배움이 쌓이는 곳</p><h1>배우고 싶은 마음을<br>오늘의 실력으로</h1><p>현업 강사의 노하우를 내 속도에 맞춰 배워보세요.</p></div>
      <div class="academy-orbit" aria-hidden="true"><span></span><b>배움<br>→ 성장</b></div>
    </section>
    <div class="catalog-tools">
      <CourseSearchBar v-model="queryDraft" @search="applySearch" />
      <CategoryRail v-if="!loading && categories.length > 1" v-model="selectedCategory" :items="categories" />
    </div>
    <div class="academy-heading"><div><h2>{{ selectedCategory === '전체' ? '모든 강의' : selectedCategory }}</h2><p>{{ loading ? '강의를 불러오고 있어요' : `${filteredCourses.length}개의 강의` }}</p></div></div>
    <div v-if="error" class="inline-alert" role="alert">{{ error }} <button type="button" @click="loadCourses">다시 불러오기</button></div>
    <div v-if="loading" class="course-grid" role="status" aria-label="강의 불러오는 중"><div v-for="n in 3" :key="n" class="course-skeleton"></div></div>
    <div v-else-if="!error && !courses.length" class="academy-empty"><h3>아직 등록된 강의가 없어요</h3><p>새로운 강의가 준비되면 이곳에서 만날 수 있어요.</p></div>
    <TransitionGroup
      v-else-if="!error && (displayedCourses.length || cardsAreLeaving || filteredCourses.length)"
      name="course-grid"
      tag="div"
      class="course-grid"
      :class="{ 'is-filtering': cardsAreLeaving }"
      @after-leave="onCourseCardAfterLeave"
    >
      <CourseCard
        v-for="(course, index) in displayedCourses"
        :key="course.id"
        :course="course"
        :style="{ '--course-index': Math.min(index, 5) }"
      />
    </TransitionGroup>
    <div v-else-if="!error" class="academy-empty"><h3>검색 결과가 없어요</h3><p>다른 강의명이나 분야로 찾아보세요.</p><button class="clear-search" type="button" @click="queryDraft = ''; searchTerm = ''; selectedCategory = '전체'">필터 초기화</button></div>
  </section>
</template>

<style scoped>
.catalog-tools { display: grid; justify-items: center; gap: 23px; margin: 29px 0 4px; }
.catalog-tools :deep(.category-rail) { width: 100%; }
.clear-search { margin-top: 8px; padding: 9px 14px; border: 1px solid #d9e2f1; border-radius: 999px; background: #fff; color: #336fc8; cursor: pointer; font-size: 13px; font-weight: 700; }
.clear-search:hover { background: #f2f7ff; }

.course-grid :deep(.course-grid-enter-active) {
  transition: opacity 220ms ease, transform 260ms cubic-bezier(.2, .75, .25, 1);
  transition-delay: calc(var(--course-index, 0) * 32ms);
  will-change: opacity, transform;
}

.course-grid :deep(.course-grid-leave-active) {
  transition: opacity 170ms ease, transform 190ms ease;
  will-change: opacity, transform;
}

.course-grid :deep(.course-grid-enter-from),
.course-grid :deep(.course-grid-leave-to) {
  opacity: 0;
  transform: translateY(12px) scale(.985);
}

.course-grid :deep(.course-grid-move) {
  transition: transform 280ms cubic-bezier(.2, .75, .25, 1);
}

.course-grid.is-filtering { min-height: 280px; }

@media (max-width: 600px) { .catalog-tools { gap: 17px; margin-top: 23px; } }

@media (prefers-reduced-motion: reduce) {
  .course-grid :deep(.course-grid-enter-active),
  .course-grid :deep(.course-grid-leave-active),
  .course-grid :deep(.course-grid-move) {
    transition-duration: .01ms;
    transition-delay: 0ms;
  }
}
</style>
