/**
 * DPIS — API Service Layer
 *
 * All paths are RELATIVE — no localhost, no hardcoded domains.
 * Development: Vite proxy forwards /api/* to uvicorn api.index:app (port 8000).
 * Production:  Vercel serverless function handles /api/* directly.
 *
 * Safe JSON parsing on every call — never throws on non-JSON responses.
 */

const BASE = '/api'

/**
 * Safe fetch wrapper — always returns parsed JSON or throws an Error
 * with a human-readable message, even if server returns HTML or plain text.
 */
async function safeFetch(url, options = {}) {
    let response
    try {
        response = await fetch(url, options)
    } catch (networkErr) {
        throw new Error(`Network error — is the backend running? (${networkErr.message})`)
    }

    const contentType = response.headers.get('content-type') ?? ''
    let body

    if (contentType.includes('application/json')) {
        body = await response.json()
    } else {
        // Server returned non-JSON (HTML error page, plain text, etc.)
        const text = await response.text()
        if (!response.ok) {
            throw new Error(`Server error ${response.status}: ${text.slice(0, 200)}`)
        }
        // Unexpected non-JSON success — surface as error
        throw new Error(`Unexpected response format (expected JSON, got ${contentType})`)
    }

    if (!response.ok) {
        throw new Error(body?.detail ?? body?.message ?? `HTTP ${response.status}`)
    }

    return body
}

/**
 * Analyze text / transcript.
 * @param {string} text          - Content to analyze
 * @param {string} inputType     - "text" | "audio" | "video"
 * @param {number} deepfakeScore - Simulated 0–1 deepfake confidence (demo)
 */
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

/**
 * Multi-modal forensic file analysis.
 * @param {object} options
 * @param {File|null} options.video
 * @param {File|null} options.audio
 * @param {File|null} options.image
 * @param {string}    options.text   - Optional accompanying transcript
 */
export async function analyzeMedia({ video = null, audio = null, image = null, text = '' } = {}) {
    const form = new FormData()
    if (video) form.append('video', video)
    if (audio) form.append('audio', audio)
    if (image) form.append('image', image)
    form.append('text', text)
    // Do NOT set Content-Type — browser must set multipart boundary automatically

    return safeFetch(`${BASE}/analyze/media`, {
        method: 'POST',
        body: form,
    })
}
