<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '강의명, 강사명, 주제를 검색하세요' },
})

defineEmits(['update:modelValue', 'search'])
</script>

<template>
  <form class="course-search" role="search" @submit.prevent="$emit('search')">
    <label class="course-search-field">
      <span>무엇을 배우고 싶으세요?</span>
      <input
        :value="modelValue"
        type="search"
        aria-label="강의 검색"
        :placeholder="placeholder"
        @input="$emit('update:modelValue', $event.target.value)"
      >
    </label>
    <button class="course-search-submit" type="submit" aria-label="강의 검색">
      <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10.8" cy="10.8" r="6.3"/><path d="m15.5 15.5 4.2 4.2"/></svg>
      <span>검색</span>
    </button>
  </form>
</template>

<style scoped>
.course-search {
  display: flex;
  width: min(100%, 690px);
  min-height: 68px;
  align-items: center;
  gap: 8px;
  padding: 7px 8px 7px 23px;
  border: 1px solid #e2e6ec;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 5px 18px rgb(17 24 39 / 7%);
  transition: box-shadow 160ms ease, border-color 160ms ease;
}

.course-search:focus-within {
  border-color: #b8cff8;
  box-shadow: 0 8px 24px rgb(66 133 244 / 15%);
}

.course-search-field {
  display: grid;
  min-width: 0;
  flex: 1;
  gap: 3px;
}

.course-search-field span {
  color: #232a35;
  font-size: 12px;
  font-weight: 700;
}

.course-search-field input {
  width: 100%;
  min-width: 0;
  padding: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: #222b38;
  font-size: 14px;
}

.course-search-field input::placeholder { color: #7b8491; }

.course-search-submit {
  display: inline-flex;
  min-width: 48px;
  height: 48px;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 0 15px;
  border: 0;
  border-radius: 999px;
  background: #4285F4;
  color: #fff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  transition: background-color 160ms ease, transform 160ms ease;
}

.course-search-submit:hover { background: #2f73df; }
.course-search-submit:active { transform: scale(.97); }
.course-search-submit svg { width: 19px; height: 19px; fill: none; stroke: currentColor; stroke-width: 2; }

@media (max-width: 540px) {
  .course-search { min-height: 60px; padding-left: 17px; }
  .course-search-submit { width: 45px; min-width: 45px; height: 45px; padding: 0; }
  .course-search-submit span { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .course-search, .course-search-submit { transition: none; }
}
</style>
