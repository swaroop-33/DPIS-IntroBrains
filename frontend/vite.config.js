import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// DPIS Frontend — Vite Dev Config
//
// Dev:  Proxy forwards /api/* → http://127.0.0.1:8000 (api/index.py via uvicorn)
//       api/index.py mounts backend at /api, so /api/analyze → backend /analyze
//
// Prod: vercel.json routes /api/* → api/index.py serverless function (same path)
//
// Backend must run from project ROOT (not inside backend/):
//   python -m uvicorn api.index:app --reload
//   OR:
//   python -m uvicorn backend.main:app --reload   ← if testing backend directly
//
// NO path rewrite — full /api/... path is forwarded, matching production exactly.

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
                // NO rewrite — /api/analyze stays as /api/analyze
                // api/index.py mounts backend at /api → backend sees /analyze ✓
            },
        },
    },
});