import { useRef, useState } from 'react'
import ResultDisplay from './ResultDisplay.jsx'
import { analyzeMedia } from '../services/api.js'

const SLOTS = [
    { key: 'video', label: 'Video', icon: '🎬', accept: 'video/*', maxMB: 50 },
    { key: 'audio', label: 'Audio', icon: '🎙', accept: 'audio/*', maxMB: 20 },
    { key: 'image', label: 'Image', icon: '🖼', accept: 'image/*', maxMB: 10 },
]

function DropZone({ slot, file, onFile }) {
    const inputRef = useRef()
    const [drag, setDrag] = useState(false)

    function handleDrop(e) {
        e.preventDefault()
        setDrag(false)
        const f = e.dataTransfer.files[0]
        if (f) onFile(slot.key, f)
    }

    function handleChange(e) {
        const f = e.target.files[0]
        if (f) onFile(slot.key, f)
    }

    const sizeMB = file ? (file.size / 1_048_576).toFixed(2) : null
    const tooLarge = file && file.size > slot.maxMB * 1_048_576

    return (
        <div
            className={`drop-zone${drag ? ' drag-over' : ''}${file ? ' has-file' : ''}`}
            onDragOver={e => { e.preventDefault(); setDrag(true) }}
            onDragLeave={() => setDrag(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && inputRef.current?.click()}
            aria-label={`Upload ${slot.label}`}
        >
            <input
                ref={inputRef}
                type="file"
                accept={slot.accept}
                style={{ display: 'none' }}
                onChange={handleChange}
            />

            {file ? (
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5rem', marginBottom: '0.35rem' }}>{slot.icon}</div>
                    <div style={{ fontSize: '0.83rem', fontWeight: 600, color: tooLarge ? 'var(--danger)' : 'var(--accent-cyan)', wordBreak: 'break-all' }}>
                        {file.name}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: tooLarge ? 'var(--danger)' : 'var(--text-muted)', marginTop: '0.2rem' }}>
                        {sizeMB} MB {tooLarge && `— exceeds ${slot.maxMB} MB limit`}
                    </div>
                    <button
                        className="btn-ghost"
                        style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}
                        onClick={e => { e.stopPropagation(); onFile(slot.key, null) }}
                    >
                        Remove
                    </button>
                </div>
            ) : (
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '0.4rem', opacity: 0.7 }}>{slot.icon}</div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                        {slot.label}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                        Drop or click · max {slot.maxMB} MB
                    </div>
                </div>
            )}
        </div>
    )
}

export default function FileForensicsPanel() {
    const [files, setFiles] = useState({ video: null, audio: null, image: null })
    const [caption, setCaption] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')

    function handleFile(key, file) {
        setFiles(prev => ({ ...prev, [key]: file }))
        setError('')
    }

    const hasFile = Object.values(files).some(Boolean)

    async function handleSubmit() {
        if (!hasFile) {
            setError('Upload at least one media file (video, audio, or image)')
            return
        }

        const oversized = SLOTS.find(
            s => files[s.key] && files[s.key].size > s.maxMB * 1_048_576
        )
        if (oversized) {
            setError(`${oversized.label} exceeds the ${oversized.maxMB} MB limit`)
            return
        }

        setError('')
        setResult(null)
        setLoading(true)

        try {
            const form = new FormData()
            if (files.video) form.append('video', files.video)
            if (files.audio) form.append('audio', files.audio)
            if (files.image) form.append('image', files.image)
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
                    File Forensics — Upload &amp; Analyze
                </h2>
                <p style={{ margin: '0.35rem 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    Upload video, audio, or image files for deepfake and AI artifact detection.
                    Mix and match — all slots are optional.
                </p>
            </div>

            {/* Drop zones */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem' }}>
                {SLOTS.map(slot => (
                    <DropZone key={slot.key} slot={slot} file={files[slot.key]} onFile={handleFile} />
                ))}
            </div>

            {/* Caption */}
            <div className="form-group">
                <label className="form-label" htmlFor="file-caption">
                    Caption / Context <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span>
                </label>
                <input
                    id="file-caption"
                    className="form-input"
                    type="text"
                    placeholder="Briefly describe the media content…"
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
                onClick={handleSubmit}
                disabled={loading || !hasFile}
            >
                {loading ? (
                    <>
                        <span className="spinner" aria-hidden="true" />
                        Processing Media…
                    </>
                ) : (
                    '🔬 Run Forensic Analysis'
                )}
            </button>

            {/* Result — includes forensic sub-scores */}
            {result && <ResultDisplay result={result} showForensic />}
        </div>
    )
}