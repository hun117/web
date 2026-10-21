import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  define: { __VITE_SERVE__: JSON.stringify(command === 'serve') },
  base: command === 'serve' ? '/' : '/static/',
  root: fileURLToPath(new URL('.', import.meta.url)),
  build: {
    outDir: fileURLToPath(new URL('../static', import.meta.url)),
    emptyOutDir: true,
  },
  server: {
    proxy: { '/board': 'http://127.0.0.1:8000', '/user': 'http://127.0.0.1:8000', '^/courses(?:/\\d+)?$': 'http://127.0.0.1:8000', '/payments': 'http://127.0.0.1:8000' },
  },
}))
