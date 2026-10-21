<script setup>
import { computed } from 'vue'

const props = defineProps({
  images: { type: Array, default: () => [] },
  title: { type: String, default: '강의 이미지' },
})

defineEmits(['view-all'])

const visibleImages = computed(() => props.images
  .filter(Boolean)
  .slice(0, 5)
  .map((image) => typeof image === 'string' ? { src: image, alt: props.title } : image))
</script>

<template>
  <section class="course-gallery" :class="{ 'has-multiple': visibleImages.length > 1 }" :aria-label="`${title} 이미지 갤러리`">
    <figure v-for="(image, index) in visibleImages" :key="`${image.src}-${index}`" class="gallery-image" :class="`gallery-image-${index + 1}`">
      <img :src="image.src" :alt="image.alt || `${title} 이미지 ${index + 1}`" :loading="index ? 'lazy' : 'eager'">
    </figure>
    <button v-if="visibleImages.length > 1" class="gallery-view-all" type="button" @click="$emit('view-all')">
      <span aria-hidden="true">▦</span> 사진 모두 보기
    </button>
  </section>
</template>

<style scoped>
.course-gallery {
  position: relative;
  display: grid;
  min-height: 310px;
  grid-template-columns: minmax(0, 1fr);
  overflow: hidden;
  border-radius: 20px;
  background: #e5eefb;
}

.gallery-image { min-width: 0; min-height: 0; margin: 0; overflow: hidden; background: #e8eef7; }
.gallery-image img { display: block; width: 100%; height: 100%; min-height: 310px; object-fit: cover; }
.has-multiple { grid-template-columns: 2fr 1fr 1fr; grid-template-rows: repeat(2, minmax(135px, 1fr)); gap: 8px; }
.has-multiple .gallery-image-1 { grid-column: 1; grid-row: 1 / span 2; }
.has-multiple .gallery-image-1 img { min-height: 100%; }
.has-multiple .gallery-image:nth-child(n + 2) img { min-height: 135px; }
.gallery-view-all {
  position: absolute;
  right: 16px;
  bottom: 16px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 37px;
  padding: 0 12px;
  border: 1px solid #263247;
  border-radius: 8px;
  background: #fff;
  color: #202a38;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}
.gallery-view-all:hover { background: #f3f7fd; }
.gallery-view-all:focus-visible { outline: 3px solid #4285F4; outline-offset: 3px; }

@media (max-width: 680px) {
  .course-gallery { min-height: 245px; border-radius: 16px; }
  .gallery-image img { min-height: 245px; }
  .has-multiple { min-height: 245px; grid-template-columns: 1fr 1fr; grid-template-rows: minmax(140px, 1fr) minmax(95px, .7fr); gap: 5px; }
  .has-multiple .gallery-image-1 { grid-column: 1 / span 2; grid-row: 1; }
  .has-multiple .gallery-image-1 img { min-height: 140px; }
  .has-multiple .gallery-image:nth-child(n + 2) img { min-height: 95px; }
  .gallery-view-all { right: 10px; bottom: 10px; }
}
</style>
