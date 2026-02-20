import { useState } from 'react'
import ResultDisplay from './ResultDisplay.jsx'
import { analyzeMedia } from '../services/api.js'

const PLATFORM_HINTS = [
    { icon: '▶', label: 'YouTube', ex: 'https://youtube.com/watch?v=...' },
    { icon: '𝕏', label: 'Twitter/X', ex: 'https://x.com/...' },
    { icon: '📸', label: 'Instagram', ex: 'https://instagram.com/p/...' },
    { icon: '🎬', label: 'Facebook', ex: 'https://fb.watch/...' },
    { icon: '🔗', label: 'Google Drive', ex: 'https://drive.google.com/file/...' },
    { icon: '🌐', label: 'Direct URL', ex: 'https://cdn.example.com/video.mp4' },
]

export default function MediaAnalyzer() {
    const [url, setUrl] = useState('')
    const [caption, setCaption] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')

    async function handleAnalyze() {
        if (!url.trim()) {
            setError('Please enter a media URL')
            return
        }
        setError('')
        setResult(null)
        setLoading(true)

        try {
            const form = new FormData()
            form.append('media_url', url.trim())
            if (caption.trim()) form.append('text', caption.trim())

            const data = await analyzeMedia(form)
            setResult(data)
        } catch (e) {
            setError(e.message || 'Analysis failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Header */}
            <div>
                <h2 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Public Media URL Analyzer
                </h2>
                <p style={{ margin: '0.35rem 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    Analyze video, audio, or image content from public URLs — no download required.
                </p>
            </div>

            {/* Platform chips */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {PLATFORM_HINTS.map(p => (
                    <span key={p.label} title={p.ex} style={{
                        display: 'inline-flex', alignItems: 'center', gap: '0.35rem',
                        padding: '0.25rem 0.65rem', borderRadius: '999px',
                        background: 'var(--surface-2)', fontSize: '0.78rem',
                        color: 'var(--text-secondary)', cursor: 'default',
                        border: '1px solid var(--border)',
                    }}>
                        <span>{p.icon}</span> {p.label}
                    </span>
                ))}
            </div>

            {/* URL input */}
            <div className="form-group">
                <label className="form-label" htmlFor="media-url">Media URL</label>
                <input
                    id="media-url"
                    className="form-input"
                    type="url"
                    placeholder="https://youtube.com/watch?v=... or any public media URL"
                    value={url}
                    onChange={e => { setUrl(e.target.value); setError('') }}
                    onKeyDown={e => e.key === 'Enter' && handleAnalyze()}
                />
            </div>

            {/* Optional caption */}
            <div className="form-group">
                <label className="form-label" htmlFor="caption">
                    Caption / Context <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional — improves psychological layer)</span>
                </label>
                <input
                    id="caption"
                    className="form-input"
                    type="text"
                    placeholder="Describe what this media is about…"
                    value={caption}
                    onChange={e => setCaption(e.target.value)}
                    maxLength={300}
                />
            </div>

            {/* Error */}
            {error && (
                <div className="error-alert" role="alert" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span>⚠</span> {error}
                </div>
            )}

            {/* Submit */}
            <button
                className={`btn-primary${loading ? ' loading' : ''}`}
                onClick={handleAnalyze}
                disabled={loading || !url.trim()}
            >
                {loading ? (
                    <>
                        <span className="spinner" aria-hidden="true" />
                        Fetching &amp; Analyzing…
                    </>
                ) : (
                    '🔍 Analyze URL'
                )}
            </button>

            {/* Result */}
            {result && <ResultDisplay result={result} />}
        </div>
    )
}