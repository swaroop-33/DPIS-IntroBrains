/**
 * DPIS — File Forensics Panel
 *
 * Upload UI for the new "🔬 Forensic Analysis" tab.
 * Accepts optional video, audio, and image files plus an optional text transcript.
 * Submits via analyzeMedia() → renders ForensicDashboard with results.
 */

import { useState, useRef } from 'react'
import { analyzeMedia } from '../services/api.js'
import ForensicDashboard from './ForensicDashboard.jsx'

// ─── File drop-zone card ────────────────────────────────────────────────────
function FileCard({ label, icon, accept, file, onChange, color = '#6366f1' }) {
    const ref = useRef(null)
    const [dragging, setDragging] = useState(false)

    const handleDrop = (e) => {
        e.preventDefault()
        setDragging(false)
        const f = e.dataTransfer.files[0]
        if (f) onChange(f)
    }

    return (
        <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => ref.current?.click()}
            style={{
                border: `2px dashed ${dragging ? color : file ? color + '88' : '#2a2a3a'}`,
                borderRadius: 10,
                padding: '18px 14px',
                cursor: 'pointer',
                background: dragging ? color + '11' : file ? color + '08' : '#0e0e1a',
                transition: 'all 0.2s',
                textAlign: 'center',
                flex: 1,
                minWidth: 140,
            }}
        >
            <input
                ref={ref}
                type="file"
                accept={accept}
                style={{ display: 'none' }}
                onChange={(e) => { const f = e.target.files[0]; if (f) onChange(f) }}
            />
            <div style={{ fontSize: 28, marginBottom: 6 }}>{icon}</div>
            <div style={{ color: file ? color : '#666', fontSize: 13, fontWeight: 'bold' }}>
                {label}
            </div>
            {file ? (
                <div style={{ color: '#888', fontSize: 11, marginTop: 4, wordBreak: 'break-all' }}>
                    ✅ {file.name}<br />
                    <span style={{ color: '#555' }}>({(file.size / 1024).toFixed(0)} KB)</span>
                </div>
            ) : (
                <div style={{ color: '#444', fontSize: 11, marginTop: 4 }}>
                    Click or drag & drop
                </div>
            )}
        </div>
    )
}

// ─── Progress state indicator ───────────────────────────────────────────────
function ProgressStep({ label, done, active }) {
    return (
        <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            color: done ? '#22c55e' : active ? '#6366f1' : '#444',
            fontSize: 13,
            transition: 'color 0.3s',
        }}>
            <span>{done ? '✅' : active ? '⏳' : '○'}</span>
            <span>{label}</span>
        </div>
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// ── Main FileForensicsPanel ────────────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════════════
export default function FileForensicsPanel() {
    const [videoFile, setVideoFile] = useState(null)
    const [audioFile, setAudioFile] = useState(null)
    const [imageFile, setImageFile] = useState(null)
    const [text, setText] = useState('')
    const [loading, setLoading] = useState(false)
    const [step, setStep] = useState(null)   // 'reading' | 'analyzing' | 'done'
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)

    const hasInput = videoFile || audioFile || imageFile || text.trim().length > 4

    const handleReset = () => {
        setVideoFile(null); setAudioFile(null); setImageFile(null)
        setText(''); setResult(null); setError(null); setStep(null)
    }

    const handleAnalyze = async () => {
        if (!hasInput) return
        setLoading(true)
        setError(null)
        setResult(null)
        setStep('reading')

        try {
            setTimeout(() => setStep('analyzing'), 400)
            const data = await analyzeMedia({
                video: videoFile,
                audio: audioFile,
                image: imageFile,
                text,
            })
            setResult(data)
            setStep('done')
        } catch (e) {
            setError(e.message)
            setStep(null)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ color: '#e2e8f0', fontFamily: "'Inter', 'Segoe UI', monospace" }}>

            {/* ── Description ─────────────────────────────────────────────── */}
            <p style={{ color: '#64748b', fontSize: 13, margin: '0 0 20px' }}>
                Upload media files for heuristic multi-modal forensic analysis.{' '}
                All files are processed in-memory — nothing is stored.{' '}
                Provide any combination (video + audio + image + text) or just one.
            </p>

            {/* ── File Inputs ──────────────────────────────────────────────── */}
            <div style={{ marginBottom: 20 }}>
                <Label>🗂 Upload Files (all optional)</Label>
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    <FileCard
                        label="Video File"
                        icon="🎬"
                        accept="video/*"
                        file={videoFile}
                        onChange={setVideoFile}
                        color="#ef4444"
                    />
                    <FileCard
                        label="Audio File"
                        icon="🎙️"
                        accept="audio/*"
                        file={audioFile}
                        onChange={setAudioFile}
                        color="#6366f1"
                    />
                    <FileCard
                        label="Image File"
                        icon="🖼️"
                        accept="image/*"
                        file={imageFile}
                        onChange={setImageFile}
                        color="#22c55e"
                    />
                </div>
            </div>

            {/* ── Text Field ──────────────────────────────────────────────── */}
            <div style={{ marginBottom: 20 }}>
                <Label>📝 Text / Transcript (optional — enhances text scores)</Label>
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    rows={5}
                    placeholder="Paste related text, transcript, caption, or description for manipulation & emotion analysis…"
                    style={{
                        width: '100%',
                        padding: 12,
                        background: '#0e0e1a',
                        border: '1px solid #1e1e2e',
                        borderRadius: 8,
                        color: '#e2e8f0',
                        fontFamily: 'inherit',
                        fontSize: 13,
                        resize: 'vertical',
                        boxSizing: 'border-box',
                        outline: 'none',
                    }}
                />
            </div>

            {/* ── Action Row ───────────────────────────────────────────────── */}
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 20 }}>
                <button
                    onClick={handleAnalyze}
                    disabled={loading || !hasInput}
                    style={{
                        padding: '11px 28px',
                        fontSize: 14,
                        fontWeight: 'bold',
                        cursor: loading || !hasInput ? 'not-allowed' : 'pointer',
                        background: loading || !hasInput
                            ? '#1e1e2e'
                            : 'linear-gradient(135deg, #4f46e5, #7c3aed)',
                        color: loading || !hasInput ? '#444' : '#fff',
                        border: 'none',
                        borderRadius: 8,
                        transition: 'all 0.2s',
                        boxShadow: loading || !hasInput ? 'none' : '0 4px 14px #6366f133',
                    }}
                >
                    {loading ? '⏳ Analyzing…' : '🔬 Run Forensic Analysis'}
                </button>

                {(result || error || videoFile || audioFile || imageFile || text) && (
                    <button
                        onClick={handleReset}
                        disabled={loading}
                        style={{
                            padding: '11px 18px',
                            fontSize: 13,
                            cursor: 'pointer',
                            background: '#1e1e2e',
                            color: '#94a3b8',
                            border: '1px solid #2a2a3a',
                            borderRadius: 8,
                        }}
                    >
                        🔄 Reset
                    </button>
                )}
            </div>

            {/* ── Progress ─────────────────────────────────────────────────── */}
            {loading && (
                <div style={{
                    background: '#0e0e1a',
                    border: '1px solid #1e1e2e',
                    borderRadius: 8,
                    padding: '12px 16px',
                    marginBottom: 16,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 6,
                }}>
                    <ProgressStep label="Reading file buffers" done={step === 'analyzing' || step === 'done'} active={step === 'reading'} />
                    <ProgressStep label="Running forensic analysis" done={step === 'done'} active={step === 'analyzing'} />
                    <ProgressStep label="Generating PPS breakdown" done={step === 'done'} active={false} />
                </div>
            )}

            {/* ── Error ────────────────────────────────────────────────────── */}
            {error && (
                <div style={{
                    background: '#2a0a0a',
                    border: '1px solid #ef444466',
                    borderRadius: 8,
                    padding: '12px 16px',
                    color: '#fca5a5',
                    fontSize: 13,
                    marginBottom: 16,
                }}>
                    ❌ <strong>Error:</strong> {error}
                </div>
            )}

            {/* ── Result ───────────────────────────────────────────────────── */}
            <ForensicDashboard result={result} />

            {/* ── Footer disclaimer ─────────────────────────────────────────── */}
            <div style={{
                marginTop: 24,
                padding: '10px 16px',
                border: '1px solid #1e1e2e',
                borderRadius: 8,
                fontSize: 11,
                color: '#475569',
                lineHeight: 1.7,
            }}>
                <strong style={{ color: '#64748b' }}>ℹ️ Technical Notes:</strong>{' '}
                Video analysis samples 1 frame per second using OpenCV Haar cascades (no model download).{' '}
                Audio analysis uses librosa FFT/pyin for spectral heuristics.{' '}
                Image analysis uses Pillow EXIF + numpy pixel statistics.{' '}
                No PyTorch, TensorFlow, or external API calls are made.{' '}
                All processing is local and temporary.
            </div>
        </div>
    )
}

// ─── Micro ─────────────────────────────────────────────────────────────────
function Label({ children }) {
    return (
        <div style={{
            color: '#94a3b8',
            fontSize: 12,
            fontWeight: 'bold',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: 10,
        }}>
            {children}
        </div>
    )
}
