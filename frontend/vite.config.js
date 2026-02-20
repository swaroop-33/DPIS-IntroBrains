import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// DPIS Frontend — Vite dev-server config
//
// In production (Vercel): /api/* is routed by vercel.json to the Python
// serverless function, which receives the FULL path including /api/.
//
// In local dev: this proxy forwards /api/* to uvicorn api.index:app
// which also receives the FULL path (no rewrite), keeping behaviour identical.
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5174,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                // NO rewrite — full path /api/analyze forwarded to backend.
                // api/index.py mounts backend at /api so it handles correctly.
            },
        },
    },
})