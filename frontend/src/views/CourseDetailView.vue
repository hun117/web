<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { getCourse } from '../api/courses'
import { createPaymentOrder } from '../api/payments'
import { courseArtwork } from '../assets/courseArtwork'
import CourseGallery from '../components/CourseGallery.vue'
import CoursePurchaseCard from '../components/CoursePurchaseCard.vue'
import { currentUser } from '../stores/session'
import { notify } from '../stores/notifications'
import { navigate } from '../router'

const props = defineProps({ route: { type: Object, required: true } })
const course = ref(null)
const loading = ref(true)
const purchaseSubmitting = ref(false)
const error = ref('')
const portOne = window.PortOne
const kakaoJavascriptKey = inject('kakaoJavascriptKey', '')
const galleryImages = computed(() => {
  if (!course.value) return []
  const sourceImages = course.value.images || course.value.gallery || []
  if (sourceImages.length) {
    return sourceImages.map((image) => typeof image === 'string'
      ? courseArtwork(image)
      : { ...image, src: courseArtwork(image.src || image.url) })
  }
  return course.value.thumbnail ? [courseArtwork(course.value.thumbnail)] : []
})

async function loadCourse() {
  loading.value = true
  error.value = ''
  try {
    course.value = await getCourse(props.route.courseId)
  } catch (cause) {
    error.value = cause.message
  } finally {
    loading.value = false
  }
}

async function purchaseCourse() {
  error.value = ''
  if (!currentUser.value) {
    notify('강의 구매는 로그인 후 이용할 수 있어요. 로그인해 주세요.')
    navigate('/login')
    return
  }
  if (!course.value || purchaseSubmitting.value) return
  if (!portOne?.requestPayment) {
    error.value = '결제 모듈을 불러오는 중입니다. 잠시 후 다시 시도해 주세요.'
    return
  }

  purchaseSubmitting.value = true
  try {
    const order = await createPaymentOrder(course.value.id)
    await portOne.requestPayment({
      storeId: order.store_id,
      channelKey: order.channel_key,
      paymentId: order.payment_id,
      orderName: order.order_name,
      totalAmount: order.amount,
      currency: order.currency,
      payMethod: 'CARD',
      redirectUrl: `${window.location.origin}/payment/complete`,
      forceRedirect: true,
    })
  } catch (cause) {
    if (cause.status === 409) {
      course.value = { ...course.value, is_enrolled: true }
      notify('이미 수강 중인 강의예요. 강의 듣기로 이어서 학습하세요.')
      return
    }
    error.value = cause.message || '결제를 진행하지 못했어요. 잠시 후 다시 시도해 주세요.'
  } finally {
    purchaseSubmitting.value = false
  }
}

onMounted(loadCourse)

function handlePurchaseAction() {
  if (course.value?.is_enrolled) return
  return purchaseCourse()
}
</script>

<template>
  <section class="course-detail-page">
    <a class="back-link" href="/" data-route>← 강의 목록</a>
    <div v-if="loading" class="course-detail-loading" role="status">강의 정보를 불러오는 중이에요</div>
    <div v-else-if="error" class="inline-alert" role="alert">{{ error }} <a href="/" data-route>강의 목록으로 이동</a></div>
    <article v-else-if="course" class="course-detail">
      <CourseGallery :images="galleryImages" :title="course.title" />
      <header class="course-detail-heading">
        <div><p class="academy-kicker">{{ course.category }} 강의</p><h1>{{ course.title }}</h1><p class="course-instructor">{{ course.instructor }} 강사 <span>·</span> <b>★ {{ course.rating }}</b></p></div>
        <div class="course-detail-rating"><span aria-hidden="true">★</span><strong>{{ course.rating }}</strong><small>수강생 평점</small></div>
      </header>
      <div class="course-detail-columns">
        <div class="course-detail-copy"><p class="academy-kicker">강의 소개</p><h2>{{ course.description }}</h2><div class="course-facts"><span>난이도 <b>{{ course.level }}</b></span><span>강의 시간 <b>{{ course.duration }}</b></span><span>수강생 평점 <b>★ {{ course.rating }}</b></span></div></div>
        <CoursePurchaseCard :price="course.price" :action-label="course.is_enrolled ? '강의 듣기' : '구매하기'" :busy="purchaseSubmitting" :error="error" :enrolled="course.is_enrolled" @action="handlePurchaseAction" />
      </div>
    </article>
  </section>
</template>

<style scoped>
.course-detail { color: #202a38; }
.course-detail-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; padding: 23px 2px 0; }
.course-detail-heading h1 { margin: 4px 0 8px; font-size: clamp(27px, 3.3vw, 37px); font-weight: 700; letter-spacing: -.045em; line-height: 1.28; }
.course-detail-heading .academy-kicker { margin-bottom: 5px; }
.course-detail-heading .course-instructor { margin: 0; }
.course-detail-heading .course-instructor span { margin: 0 5px; color: #9ba4b1; }
.course-detail-heading .course-instructor b { color: #3b4554; }
.course-detail-rating { display: grid; min-width: 105px; grid-template-columns: auto 1fr; align-items: center; column-gap: 7px; padding-top: 12px; color: #202a38; }
.course-detail-rating > span { grid-row: span 2; color: #4285F4; font-size: 20px; }
.course-detail-rating strong { font-size: 15px; }
.course-detail-rating small { color: #707b8b; font-size: 10px; }
.course-detail-copy h2 { margin-top: 4px; line-height: 1.65; }
.course-detail-columns { align-items: start; }

@media (max-width: 600px) {
  .course-detail-heading { padding-top: 19px; }
  .course-detail-heading h1 { font-size: 27px; }
  .course-detail-rating { min-width: auto; }
  .course-detail-rating small { max-width: 55px; }
}
</style>
