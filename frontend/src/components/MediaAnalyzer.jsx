import { useState, useRef, useCallback } from 'react'
import ResultDisplay from './ResultDisplay.jsx'
import { analyzeMedia } from '../services/api.js'

// ─── Constants ───────────────────────────────────────────────────────────────
const MODES = ['IMAGE', 'AUDIO', 'VIDEO']

const ACCEPT = {
    IMAGE: 'image/*',
    AUDIO: 'audio/*',
    VIDEO: 'video/*',
}

const FORM_KEY = {
    IMAGE: 'image',
    AUDIO: 'audio',
    VIDEO: 'video',
}

const MIME = {
    AUDIO: 'audio/webm;codecs=opus',
    VIDEO: 'video/webm;codecs=vp8,opus',
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
function StatusBadge({ mode, recording }) {
    const color = recording ? '#ef4444' : 'var(--text-muted)'
    return (
        <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 5,
            fontSize: '0.75rem', color,
        }}>
            <span style={{
                width: 7, height: 7, borderRadius: '50%',
                background: color,
                animation: recording ? 'pulse 1.2s infinite' : 'none',
            }} />
            {recording ? 'RECORDING' : 'READY'}
        </span>
    )
}

// ─── Component ────────────────────────────────────────────────────────────────
export default function MediaAnalyzer() {
    const [mode, setMode] = useState('IMAGE')
    const [file, setFile] = useState(null)
    const [mediaUrl, setMediaUrl] = useState('')
    const [caption, setCaption] = useState('')
    const [recording, setRecording] = useState(false)
    const [recordedBlob, setRecordedBlob] = useState(null)
    const [recordedMime, setRecordedMime] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')
    const [status, setStatus] = useState('')

    const mediaRecRef = useRef(null)
    const chunksRef = useRef([])
    const streamRef = useRef(null)
    const videoPreview = useRef(null)
    const fileInput = useRef(null)

    // ── Mode switch ────────────────────────────────────────────────────────────
    function switchMode(m) {
        stopRecording()
        setMode(m)
        setFile(null)
        setRecordedBlob(null)
        setRecordedMime('')
        setMediaUrl('')
        setResult(null)
        setError('')
        setStatus('')
        if (fileInput.current) fileInput.current.value = ''
    }

    // ── File select ────────────────────────────────────────────────────────────
    function onFileChange(e) {
        const f = e.target.files?.[0] ?? null
        setFile(f)
        setRecordedBlob(null)
        setError('')
        if (f) setStatus(`File selected: ${f.name}`)
    }

    // ── MediaRecorder ──────────────────────────────────────────────────────────
    async function startRecording() {
        setError('')
        setRecordedBlob(null)
        chunksRef.current = []

        const constraints = mode === 'AUDIO'
            ? { audio: true }
            : { audio: true, video: { facingMode: 'user' } }

        let stream
        try {
            stream = await navigator.mediaDevices.getUserMedia(constraints)
        } catch {
            setError('Camera/microphone permission denied.')
            return
        }

        streamRef.current = stream

        if (mode === 'VIDEO' && videoPreview.current) {
            videoPreview.current.srcObject = stream
            videoPreview.current.play()
        }

        const mime = mode === 'AUDIO' ? MIME.AUDIO : MIME.VIDEO
        const mr = new MediaRecorder(stream, { mimeType: mime })

        mr.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data) }
        mr.onstop = () => {
            const blob = new Blob(chunksRef.current, { type: mime })
            setRecordedBlob(blob)
            setRecordedMime(mime)
            setStatus(`Recording complete — ${(blob.size / 1024).toFixed(1)} KB`)
            if (videoPreview.current) {
                videoPreview.current.srcObject = null
                videoPreview.current.src = URL.createObjectURL(blob)
            }
        }

        mediaRecRef.current = mr
        mr.start(250)
        setRecording(true)
        setStatus('Recording…')
    }

    const stopRecording = useCallback(() => {
        if (mediaRecRef.current && mediaRecRef.current.state !== 'inactive') {
            mediaRecRef.current.stop()
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(t => t.stop())
            streamRef.current = null
        }
        setRecording(false)
    }, [])

    // ── Camera capture (image) ─────────────────────────────────────────────────
    async function captureImage() {
        setError('')
        if (!navigator.mediaDevices?.getUserMedia) {
            setError('Camera not supported in this browser.')
            return
        }
        let stream
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true })
        } catch {
            setError('Camera permission denied.')
            return
        }

        // Create off-screen video + canvas to grab frame
        const video = document.createElement('video')
        video.srcObject = stream
        await new Promise(res => { video.onloadedmetadata = () => { video.play(); res() } })

        await new Promise(res => setTimeout(res, 300)) // let sensor settle

        const canvas = document.createElement('canvas')
        canvas.width = video.videoWidth || 640
        canvas.height = video.videoHeight || 480
        canvas.getContext('2d').drawImage(video, 0, 0)

        stream.getTracks().forEach(t => t.stop())

        canvas.toBlob(blob => {
            if (!blob) { setError('Failed to capture frame.'); return }
            setRecordedBlob(blob)
            setRecordedMime('image/jpeg')
            setFile(null)
            setStatus(`Frame captured — ${(blob.size / 1024).toFixed(1)} KB`)
        }, 'image/jpeg', 0.88)
    }

    // ── Validation ─────────────────────────────────────────────────────────────
    function validate() {
        if (!file && !recordedBlob && !mediaUrl.trim()) {
            setError('Provide a file, recording, or URL to analyze.')
            return false
        }
        if (mediaUrl.trim()) {
            try { new URL(mediaUrl.trim()) }
            catch { setError('Enter a valid URL (https://…)'); return false }
        }
        return true
    }

    // ── Run Analysis ───────────────────────────────────────────────────────────
    async function runAnalysis() {
        if (!validate()) return
        setError('')
        setResult(null)
        setLoading(true)
        setStatus('Submitting to intelligence engine…')

        try {
            const form = new FormData()
            const key = FORM_KEY[mode]

            if (file) {
                form.append(key, file)
            } else if (recordedBlob) {
                const ext = recordedMime.includes('audio') ? 'webm' : (mode === 'IMAGE' ? 'jpg' : 'webm')
                form.append(key, recordedBlob, `recorded.${ext}`)
            } else if (mediaUrl.trim()) {
                form.append('media_url', mediaUrl.trim())
            }

            if (caption.trim()) form.append('text', caption.trim())

            const data = await analyzeMedia(form)
            setResult(data)
            setStatus('Analysis complete.')
        } catch (e) {
            setError(e.message || 'Analysis failed — check server logs.')
            setStatus('')
        } finally {
            setLoading(false)
        }
    }

    // ── Derived state ──────────────────────────────────────────────────────────
    const hasInput = file || recordedBlob || mediaUrl.trim()
    const canRecord = mode === 'AUDIO' || mode === 'VIDEO'

    // ─── Render ────────────────────────────────────────────────────────────────
    return (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.4rem' }}>

            {/* ── Header ── */}
            <div>
                <h2 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Multi-Modal Media Intelligence
                </h2>
                <p style={{ margin: '0.3rem 0 0', fontSize: '0.81rem', color: 'var(--text-muted)' }}>
                    Upload, record, capture, or provide a public URL. All analysis is server-side.
                </p>
            </div>

            {/* ── Mode Selector ── */}
            <div style={{ display: 'flex', gap: '0.5rem' }}>
                {MODES.map(m => (
                    <button
                        key={m}
                        onClick={() => switchMode(m)}
                        style={{
                            padding: '0.35rem 1rem',
                            borderRadius: 6,
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            letterSpacing: '0.05em',
                            border: mode === m ? 'none' : '1px solid var(--border)',
                            background: mode === m ? 'var(--accent)' : 'var(--surface-2)',
                            color: mode === m ? '#fff' : 'var(--text-secondary)',
                            cursor: 'pointer',
                            transition: 'all 0.15s',
                        }}
                    >
                        {m}
                    </button>
                ))}
            </div>

            {/* ── File Upload ── */}
            <div className="form-group">
                <label className="form-label" htmlFor="media-file">
                    {mode === 'IMAGE' ? 'Image File' : mode === 'AUDIO' ? 'Audio File' : 'Video File'}
                </label>
                <input
                    ref={fileInput}
                    id="media-file"
                    type="file"
                    accept={ACCEPT[mode]}
                    className="form-input"
                    onChange={onFileChange}
                    style={{ paddingTop: '0.4rem' }}
                />
            </div>

            {/* ── Recorder Controls ── */}
            {canRecord && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                    <button
                        className="btn-primary"
                        onClick={recording ? stopRecording : startRecording}
                        disabled={loading}
                        style={{
                            background: recording ? '#ef4444' : undefined,
                            padding: '0.45rem 1.1rem',
                            fontSize: '0.82rem',
                        }}
                    >
                        {recording ? 'Stop Recording' : `Record ${mode === 'AUDIO' ? 'Audio' : 'Video'}`}
                    </button>
                    <StatusBadge mode={mode} recording={recording} />
                    {recordedBlob && !recording && (
                        <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                            Recording ready — {(recordedBlob.size / 1024).toFixed(1)} KB
                        </span>
                    )}
                </div>
            )}

            {/* ── Image Capture ── */}
            {mode === 'IMAGE' && (
                <button
                    className="btn-secondary"
                    onClick={captureImage}
                    disabled={loading}
                    style={{ alignSelf: 'flex-start', padding: '0.45rem 1.1rem', fontSize: '0.82rem' }}
                >
                    Capture from Camera
                </button>
            )}

            {/* ── Video Preview (recording) ── */}
            {mode === 'VIDEO' && (
                <video
                    ref={videoPreview}
                    muted
                    playsInline
                    style={{
                        width: '100%', maxHeight: 220, borderRadius: 8, objectFit: 'cover',
                        background: 'var(--surface-2)',
                        display: recording || recordedBlob ? 'block' : 'none',
                        border: '1px solid var(--border)',
                    }}
                />
            )}

            {/* ── URL Input ── */}
            <div className="form-group">
                <label className="form-label" htmlFor="media-url">
                    Public Media URL <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional — no file needed)</span>
                </label>
                <input
                    id="media-url"
                    className="form-input"
                    type="url"
                    placeholder="https://…"
                    value={mediaUrl}
                    onChange={e => { setMediaUrl(e.target.value); setError('') }}
                />
                {mediaUrl.trim() && (
                    <p style={{ margin: '0.35rem 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Remote media will be processed server-side.
                    </p>
                )}
            </div>

            {/* ── Caption ── */}
            <div className="form-group">
                <label className="form-label" htmlFor="caption">
                    Caption / Context <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span>
                </label>
                <textarea
                    id="caption"
                    className="form-input"
                    placeholder="Describe what this media is about — improves psychological layer accuracy."
                    value={caption}
                    onChange={e => setCaption(e.target.value)}
                    maxLength={500}
                    rows={2}
                    style={{ resize: 'vertical', fontFamily: 'inherit' }}
                />
            </div>

            {/* ── Status / Error ── */}
            {status && !error && (
                <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-muted)' }}>{status}</p>
            )}
            {error && (
                <div className="error-alert" role="alert" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span>&#9888;</span> {error}
                </div>
            )}

            {/* ── Submit ── */}
            <button
                className={`btn-primary${loading ? ' loading' : ''}`}
                onClick={runAnalysis}
                disabled={loading || !hasInput}
            >
                {loading ? (
                    <>
                        <span className="spinner" aria-hidden="true" />
                        Analyzing&hellip;
                    </>
                ) : (
                    'Run Analysis'
                )}
            </button>

            {/* ── Result ── */}
            {result && <ResultDisplay result={result} showForensic={true} />}
        </div>
    )
}