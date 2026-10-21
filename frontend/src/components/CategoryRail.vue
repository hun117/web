<script setup>
defineProps({
  items: { type: Array, default: () => [] },
  modelValue: { type: String, default: '전체' },
})

defineEmits(['update:modelValue', 'select'])
</script>

<template>
  <nav class="category-rail" aria-label="강의 분야">
    <button
      v-for="item in items"
      :key="item.label || item"
      type="button"
      class="category-item"
      :class="{ selected: modelValue === (item.label || item) }"
      :aria-pressed="modelValue === (item.label || item)"
      @click="$emit('update:modelValue', item.label || item); $emit('select', item.label || item)"
    >
      <span class="category-icon" aria-hidden="true">{{ item.icon || '✦' }}</span>
      <span>{{ item.label || item }}</span>
    </button>
  </nav>
</template>

<style scoped>
.category-rail {
  display: flex;
  gap: 24px;
  overflow-x: auto;
  padding: 4px 1px 11px;
  scrollbar-width: thin;
  scrollbar-color: #d5dfed transparent;
}

.category-item {
  position: relative;
  display: inline-flex;
  min-width: max-content;
  flex-direction: column;
  align-items: center;
  gap: 9px;
  padding: 5px 1px 10px;
  border: 0;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: #687384;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: color 150ms ease, border-color 150ms ease;
}

.category-icon { font-size: 21px; line-height: 1; filter: grayscale(1); opacity: .8; }
.category-item:hover { color: #1d2735; border-bottom-color: #c9d7ec; }
.category-item.selected { color: #1b2635; border-bottom-color: #4285F4; }
.category-item.selected .category-icon { filter: none; opacity: 1; }

@media (max-width: 600px) { .category-rail { gap: 19px; } }
@media (prefers-reduced-motion: reduce) { .category-item { transition: none; } }
</style>
