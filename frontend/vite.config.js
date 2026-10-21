import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

const API_BASE_URLS = {
  development: 'http://localhost:8000',
  production: 'https://api.pepepe.p-e.kr',
}

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  define: {
    __VITE_SERVE__: JSON.stringify(command === 'serve'),
    __API_BASE_URL__: JSON.stringify(command === 'serve' ? API_BASE_URLS.development : API_BASE_URLS.production),
  },
  base: '/',
  root: fileURLToPath(new URL('.', import.meta.url)),
  build: {
    outDir: fileURLToPath(new URL('./dist', import.meta.url)),
    emptyOutDir: true,
  },
}))
