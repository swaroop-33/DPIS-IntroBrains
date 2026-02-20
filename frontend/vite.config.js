import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// DPIS Frontend — Vite config
// /api/* → http://127.0.0.1:8000/* (strips /api prefix)
// /health → http://127.0.0.1:8000/health
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5174,
        proxy: {
            // /api/analyze → /analyze on backend
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ''),
            },
            // direct health check
            '/health': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
})