import { createApp } from 'vue'
import App from './App.vue'
import './assets/style.css'
import './assets/airbnb-theme.css'

createApp(App)
  .provide('kakaoJavascriptKey', import.meta.env.VITE_KAKAO_JAVASCRIPT_KEY || '')
  .mount('#app')
