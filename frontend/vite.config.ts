import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    // 禁止浏览器缓存任何模块，杜绝改代码后页面仍跑旧逻辑的问题
    headers: {
      'Cache-Control': 'no-store',
    },
    // Windows 下偶尔丢失文件事件导致旧缓存（曾出现改了代码页面不变），用轮询兜底
    watch: {
      usePolling: true,
      interval: 300,
    },
    proxy: {
      // 本地开发转发到后端
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    chunkSizeWarningLimit: 1500,
  },
})