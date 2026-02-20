/**
 * DPIS — API Service Layer (v3.2)
 *
 * - Uses relative paths only (/api)
 * - Works with Vite proxy in dev (no path rewrite, /api prefix forwarded as-is)
 * - Works with Vercel serverless in prod (api/index.py mounts at /api)
 * - Safe JSON parsing — never throws "Unexpected token T"
 */

const BASE = '/api'

// ──────────────────────────────────────────────────────────────────────────────
// Safe fetch wrapper
// ──────────────────────────────────────────────────────────────────────────────
async function safeFetch(url, options = {}) {
    let response

    try {
        response = await fetch(url, options)
    } catch (networkErr) {
        throw new Error(`Network error — is the backend running? (${networkErr.message})`)
    }

    const contentType = response.headers.get('content-type') ?? ''

    if (!contentType.includes('application/json')) {
        const text = await response.text()
        throw new Error(
            response.ok
                ? `Unexpected response format (expected JSON, got ${contentType})`
                : `Server ${response.status}: ${text.slice(0, 300)}`
        )
    }

    const body = await response.json()

    if (!response.ok) {
        throw new Error(body?.detail ?? body?.message ?? `HTTP ${response.status}`)
    }

    return body
}


// ──────────────────────────────────────────────────────────────────────────────
// Text / transcript analysis   →  POST /api/analyze
// ──────────────────────────────────────────────────────────────────────────────
export async function analyzeText(text, inputType = 'text', deepfakeScore = 0.72) {
    return safeFetch(`${BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text,
            input_type: inputType,
            simulated_deepfake_score: deepfakeScore,
        }),
    })
}


// ──────────────────────────────────────────────────────────────────────────────
// Multi-modal media analysis   →  POST /api/analyze/media
//
// Accepts a pre-built FormData object so callers retain full control
// over which file slots (video / audio / image) and text are included.
//
// Usage:
//   const form = new FormData()
//   form.append('video', videoFile)       // optional File object
//   form.append('media_url', 'https://…') // or a public URL
//   form.append('text', 'caption…')       // optional caption
//   const result = await analyzeMedia(form)
// ──────────────────────────────────────────────────────────────────────────────
export async function analyzeMedia(formData) {
    if (!(formData instanceof FormData)) {
        throw new TypeError('analyzeMedia expects a FormData instance')
    }
    return safeFetch(`${BASE}/analyze/media`, {
        method: 'POST',
        body: formData,
        // Do NOT set Content-Type header — browser must set multipart boundary automatically
    })
}