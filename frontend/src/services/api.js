/**
 * DPIS — API Service
 * Centralized fetch wrapper for all backend calls.
 * All paths are relative — routed through Vite proxy in dev.
 */

const BASE = ''   // empty = relative path, works via Vite proxy

/**
 * Send transcribed text to the DPIS analysis pipeline.
 * @param {string} text        - transcribed content
 * @param {string} inputType   - "text" | "audio" | "video"
 * @param {number} deepfakeScore - 0–1 simulated deepfake confidence
 * @returns {Promise<object>}  - full AnalysisResult JSON
 */
export async function analyzeText(text, inputType = 'text', deepfakeScore = 0.72) {
    const response = await fetch(`${BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text,
            input_type: inputType,
            simulated_deepfake_score: deepfakeScore,
        }),
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data?.detail ?? `HTTP ${response.status}`)
    }

    return data
}

/**
 * Send media files + optional text to multi-modal forensic analysis pipeline.
 * @param {object} options
 * @param {File|null} options.video   - video file (optional)
 * @param {File|null} options.audio   - audio file (optional)
 * @param {File|null} options.image   - image file (optional)
 * @param {string}    options.text    - transcript / caption text (optional)
 * @returns {Promise<object>}  - full forensic result JSON
 */
export async function analyzeMedia({ video = null, audio = null, image = null, text = '' } = {}) {
    const form = new FormData()
    if (video) form.append('video', video)
    if (audio) form.append('audio', audio)
    if (image) form.append('image', image)
    form.append('text', text)

    const response = await fetch(`${BASE}/api/analyze/media`, {
        method: 'POST',
        body: form,
        // Do NOT set Content-Type — browser sets it with correct boundary
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data?.detail ?? `HTTP ${response.status}`)
    }

    return data
}

