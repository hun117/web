import { ref } from 'vue'

export const notice = ref('')
let clearTimer

export function notify(message) {
  notice.value = message
  window.clearTimeout(clearTimer)
  clearTimer = window.setTimeout(() => {
    notice.value = ''
  }, 3500)
}

export function clearNotice() {
  window.clearTimeout(clearTimer)
  notice.value = ''
}
