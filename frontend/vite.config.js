import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// DPIS Frontend — Vite Dev Config
//
// Dev proxy:  /api/*  →  http://127.0.0.1:8000/*  (strips /api prefix)
//   browser:  POST /api/analyze/media
//   proxy:    POST http://127.0.0.1:8000/analyze/media   ✓ matches FastAPI route
//
// Works with EITHER backend entry point:
//   python -m uvicorn backend.main:app --reload   (routes at /analyze, /analyze/media)
//   python -m uvicorn api.index:app   --reload    (same — api/index.py re-exports backend app)
//
// Prod (Vercel): vercel.json rewrites /api/* → api/index.py (Vercel strips /api itself)

export default defineConfig({
    plugins: [react()],
    server: {
        port: 5174,
        strictPort: false,
        proxy: {
            "/api": {
                target: "http://127.0.0.1:8000",
                changeOrigin: true,
                secure: false,
                // Rewrite: strip /api prefix before forwarding to FastAPI
                // /api/analyze        → /analyze
                // /api/analyze/media  → /analyze/media
                // /api/health         → /health
                rewrite: (path) => path.replace(/^\/api/, ""),
            },
        },
    },
});