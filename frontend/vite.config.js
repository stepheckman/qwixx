import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js',
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['qwixx.penguin2751.net'],
    proxy: {
      '/api': {
        target: 'http://backend:7004',
        changeOrigin: true,
      }
    }
  }
})
