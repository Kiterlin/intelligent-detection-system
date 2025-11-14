import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // 代码分割策略
    rollupOptions: {
      output: {
        // 手动分块策略
        manualChunks: {
          // Vue 核心库
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          // Element Plus UI 库
          'element-plus': ['element-plus'],
          // ECharts 图表库
          'echarts': ['echarts'],
          // Axios HTTP 库
          'axios': ['axios'],
        },
        // 分块文件命名
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    // 使用 esbuild 压缩（比 terser 快）
    minify: 'esbuild',
    // esbuild 压缩选项
    esbuild: {
      drop: ['console', 'debugger'], // 移除 console 和 debugger
    },
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // chunk 大小警告阈值（KB）
    chunkSizeWarningLimit: 1000,
    // 启用 gzip 压缩大小报告
    reportCompressedSize: true,
    // sourcemap（生产环境关闭以减小体积）
    sourcemap: false,
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'element-plus',
      'axios',
      'echarts',
    ],
  },
})
