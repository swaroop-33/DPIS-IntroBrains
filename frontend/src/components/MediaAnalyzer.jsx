/**
 * DPIS — MediaAnalyzer Component
 *
 * Provides 4 media input modes, all transcribed in-browser using
 * Web Speech API (no external libraries, no backend media endpoints):
 *
 *   1. Audio Upload   — upload an audio file, play + capture mic
 *   2. Video Upload   — upload a video file, play + capture mic
 *   3. Record Audio   — live microphone recording + transcription
 *   4. Record Video   — live camera + mic recording + transcription
 *
 * ⚠️ Browser note:
 *   SpeechRecognition listens to the MICROPHONE, not to audio playback.
 *   For file modes: play the file through speakers — the mic will pick it up.
 *   For live modes: speech is captured in real time.
 *   Chrome only (SpeechRecognition is a Chrome/Edge API).
 *
 * On transcription complete → calls analyzeText() from api.js → renders result.
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { analyzeText } from '../services/api.js'

// ─── SpeechRecognition feature detection ─────────────────────────────────────
const SR = window.SpeechRecognition || window.webkitSpeechRecognition || null

// ─── Utility: build a SpeechRecognition instance ─────────────────────────────
function buildRecognizer(onResult, onEnd, onError) {
    if (!SR) return null
    const rec = new SR()
    rec.lang = 'en-US'
    rec.continuous = true     // keep listening until we call .stop()
    rec.interimResults = true     // show live interim text
    rec.maxAlternatives = 1

    let finalText = ''
    rec.onresult = (e) => {
        let interim = ''
        for (let i = e.resultIndex; i < e.results.length; i++) {
            const t = e.results[i][0].transcript
            if (e.results[i].isFinal) finalText += t + ' '
            else interim += t
        }
        onResult(finalText.trim(), interim)
    }
    rec.onend = () => onEnd(finalText.trim())
    rec.onerror = (e) => onError(e.error)
    return rec
}

// ─── Score table row component ────────────────────────────────────────────────
function ScoreRow({ icon, label, score, detail, hl, bold }) {
    const cell = bold
        ? { border: '1px solid #444', padding: '6px 10px', fontWeight: 'bold' }
        : { border: '1px solid #444', padding: '6px 10px' }
    return (
        <tr style={hl ? { background: hl } : {}}>
            <td style={cell}>{icon} {label}</td>
            <td style={cell}>{score != null ? Number(score).toFixed(1) : '—'}</td>
            <td style={cell}>{detail}</td>
        </tr>
    )
}

// ─── Compact result panel ─────────────────────────────────────────────────────
function ResultPanel({ result }) {
    if (!result) return null
    const pps = result.pps
    const bgColor = pps?.score >= 81 ? '#3a0a0a'
        : pps?.score >= 61 ? '#3a1a00'
            : pps?.score >= 31 ? '#2a2a00'
                : '#0a2a0a'
    return (
        <div style={{ marginTop: 20, padding: 16, background: bgColor, borderRadius: 6, border: '1px solid #555' }}>
            <h3 style={{ color: '#fff', margin: '0 0 12px' }}>
                🧠 PPS: <strong>{pps?.score?.toFixed(1)}</strong>/100 &nbsp;·&nbsp; {pps?.threat_level}
                &nbsp;·&nbsp; 🌐 SDI: {result.sdi?.sdi_score?.toFixed(1)} ({result.sdi?.disruption_level})
            </h3>

            <table style={{ borderCollapse: 'collapse', width: '100%', color: '#ddd', fontSize: 13, marginBottom: 12 }}>
                <thead>
                    <tr>
                        {['Module', 'Score', 'Detail'].map(h => (
                            <th key={h} style={{ border: '1px solid #555', padding: '5px 10px', textAlign: 'left', background: '#222' }}>{h}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    <ScoreRow icon="🎭" label="Deepfake (DF)" score={result.deepfake?.final_deepfake_score} detail={result.deepfake?.method} />
                    <ScoreRow icon="😡" label="Emotion (EA)" score={result.emotion?.amplification_score} detail={`Dominant: ${result.emotion?.dominant_emotion}`} />
                    <ScoreRow icon="📢" label="Propaganda (MP)" score={result.propaganda?.manipulation_score} detail={`${result.propaganda?.trigger_phrases?.length ?? 0} triggers`} />
                    <ScoreRow icon="📈" label="Virality (VR)" score={result.virality?.virality_score} detail={`Spread: ${result.virality?.spread_probability}`} />
                    <ScoreRow icon="🧠" label="PPS" score={pps?.score} detail={pps?.threat_level} hl="#1a1a00" bold />
                    <ScoreRow icon="🌐" label="SDI" score={result.sdi?.sdi_score} detail={`Disruption: ${result.sdi?.disruption_level}`} hl="#1a0000" bold />
                </tbody>
            </table>

            <p style={{ color: '#bbb', fontSize: 13, margin: '0 0 8px' }}>
                {result.explanation?.summary}
            </p>
            {result.explanation?.counterfactual_analysis?.impact_statement && (
                <p style={{ color: '#999', fontSize: 12, margin: 0 }}>
                    🔀 {result.explanation.counterfactual_analysis.impact_statement}
                </p>
            )}
            {result.performance && (
                <p style={{ color: '#666', fontSize: 11, marginTop: 8, marginBottom: 0 }}>
                    ⚡ {result.performance.execution_time_ms} ms
                </p>
            )}
        </div>
    )
}

// ─── Shared transcript / status box ──────────────────────────────────────────
function TranscriptBox({ final, interim, placeholder }) {
    const text = final || interim || placeholder || ''
    return (
        <div style={{
            minHeight: 80, maxHeight: 160, overflow: 'auto',
            background: '#111', color: final ? '#0f0' : '#888',
            border: '1px solid #333', borderRadius: 4,
            padding: 10, fontSize: 13, fontFamily: 'monospace',
            whiteSpace: 'pre-wrap', marginTop: 8,
        }}>
            {text || <span style={{ color: '#444' }}>Transcript will appear here…</span>}
            {interim && <span style={{ color: '#555' }}> {interim}</span>}
        </div>
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// ── Section 1: Audio Upload ────────────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════════════
function AudioUpload({ onResult, onError }) {
    const [file, setFile] = useState(null)
    const [status, setStatus] = useState('')
    const [finalText, setFinalText] = useState('')
    const [interim, setInterim] = useState('')
    const [loading, setLoading] = useState(false)
    const audioRef = useRef(null)
    const recRef = useRef(null)

    const handleFile = (e) => {
        const f = e.target.files[0]
        if (!f) return
        setFile(f)
        setFinalText('')
        setInterim('')
        setStatus('File loaded. Click Transcribe to begin.')
    }

    const startTranscription = () => {
        if (!file) return
        if (!SR) { setStatus('❌ SpeechRecognition not supported in this browser. Use Chrome.'); return }

        setFinalText('')
        setInterim('')
        setStatus('🎙 Listening (play audio through speakers so mic can pick it up)…')

        recRef.current = buildRecognizer(
            (fin, int) => { setFinalText(fin); setInterim(int) },
            async (final) => {
                setStatus('✅ Transcription complete. Analyzing…')
                setLoading(true)
                try {
                    const r = await analyzeText(final || '[no speech detected]', 'audio')
                    onResult(r)
                    setStatus('✅ Analysis complete.')
                } catch (e) { onError(e.message); setStatus('❌ ' + e.message) }
                finally { setLoading(false) }
            },
            (err) => setStatus(`❌ Recognition error: ${err}`)
        )
        recRef.current.start()

        // Play the audio file
        const url = URL.createObjectURL(file)
        audioRef.current.src = url
        audioRef.current.onended = () => {
            setTimeout(() => { recRef.current?.stop(); URL.revokeObjectURL(url) }, 1500)
        }
        audioRef.current.play()
    }

    const stopAll = () => {
        recRef.current?.stop()
        audioRef.current?.pause()
        setStatus('Stopped.')
    }

    return (
        <div>
            <p style={hint}>
                Upload an audio file and click <em>Transcribe</em>. Play audio through speakers — the mic captures it.
            </p>
            <input type="file" accept="audio/*" onChange={handleFile} />
            <audio ref={audioRef} style={{ display: 'none' }} />

            {file && (
                <div style={{ marginTop: 10 }}>
                    <audio controls src={file ? URL.createObjectURL(file) : ''} style={{ width: '100%', marginBottom: 8 }} />
                    <div style={{ display: 'flex', gap: 8 }}>
                        <Btn onClick={startTranscription} disabled={loading}>🎙 Transcribe + Analyze</Btn>
                        <Btn onClick={stopAll} secondary>⏹ Stop</Btn>
                    </div>
                </div>
            )}

            {status && <p style={statusStyle}>{status}</p>}
            <TranscriptBox final={finalText} interim={interim} placeholder="Transcript appears here after transcription…" />
        </div>
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// ── Section 2: Video Upload ────────────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════════════
function VideoUpload({ onResult, onError }) {
    const [file, setFile] = useState(null)
    const [videoSrc, setVideoSrc] = useState(null)
    const [status, setStatus] = useState('')
    const [finalText, setFinalText] = useState('')
    const [interim, setInterim] = useState('')
    const [loading, setLoading] = useState(false)
    const videoRef = useRef(null)
    const recRef = useRef(null)

    const handleFile = (e) => {
        const f = e.target.files[0]
        if (!f) return
        setFile(f)
        const url = URL.createObjectURL(f)
        setVideoSrc(url)
        setFinalText('')
        setInterim('')
        setStatus('Video loaded. Click Transcribe to begin.')
    }

    const startTranscription = () => {
        if (!file) return
        if (!SR) { setStatus('❌ SpeechRecognition not supported. Use Chrome.'); return }

        setFinalText('')
        setInterim('')
        setStatus('🎙 Listening (play video through speakers)…')

        recRef.current = buildRecognizer(
            (fin, int) => { setFinalText(fin); setInterim(int) },
            async (final) => {
                setStatus('✅ Transcription complete. Analyzing…')
                setLoading(true)
                try {
                    const r = await analyzeText(final || '[no speech detected]', 'video')
                    onResult(r)
                    setStatus('✅ Analysis complete.')
                } catch (e) { onError(e.message); setStatus('❌ ' + e.message) }
                finally { setLoading(false) }
            },
            (err) => setStatus(`❌ Recognition error: ${err}`)
        )
        recRef.current.start()

        if (videoRef.current) {
            videoRef.current.onended = () => {
                setTimeout(() => recRef.current?.stop(), 1500)
            }
            videoRef.current.play()
        }
    }

    const stopAll = () => {
        recRef.current?.stop()
        videoRef.current?.pause()
        setStatus('Stopped.')
    }

    return (
        <div>
            <p style={hint}>
                Upload a video file. Click <em>Transcribe Video Audio</em> — play it through speakers and the mic will capture the speech.
            </p>
            <input type="file" accept="video/*" onChange={handleFile} />

            {videoSrc && (
                <div style={{ marginTop: 10 }}>
                    <video ref={videoRef} src={videoSrc} controls style={{ width: '100%', maxHeight: 260, borderRadius: 4, background: '#000', marginBottom: 8 }} />
                    <div style={{ display: 'flex', gap: 8 }}>
                        <Btn onClick={startTranscription} disabled={loading}>🎙 Transcribe Video Audio</Btn>
                        <Btn onClick={stopAll} secondary>⏹ Stop</Btn>
                    </div>
                </div>
            )}

            {status && <p style={statusStyle}>{status}</p>}
            <TranscriptBox final={finalText} interim={interim} placeholder="Transcript appears here after transcription…" />
        </div>
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// ── Section 3: Record Audio (Live Mic) ────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════════════
function RecordAudio({ onResult, onError }) {
    const [isRecording, setIsRecording] = useState(false)
    const [status, setStatus] = useState('')
    const [finalText, setFinalText] = useState('')
    const [interim, setInterim] = useState('')
    const [loading, setLoading] = useState(false)
    const recRef = useRef(null)
    const streamRef = useRef(null)

    const startRecording = async () => {
        if (!SR) { setStatus('❌ SpeechRecognition not supported. Use Chrome.'); return }

        try {
            // Get mic access (just to confirm permission — SR uses it internally)
            streamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true })
            setFinalText('')
            setInterim('')
            setIsRecording(true)
            setStatus('🔴 Recording… speak now.')

            recRef.current = buildRecognizer(
                (fin, int) => { setFinalText(fin); setInterim(int) },
                async (final) => {
                    setIsRecording(false)
                    setStatus('✅ Recording done. Analyzing…')
                    setLoading(true)
                    // Stop mic stream
                    streamRef.current?.getTracks().forEach(t => t.stop())
                    try {
                        const r = await analyzeText(final || '[no speech detected]', 'audio')
                        onResult(r)
                        setStatus('✅ Analysis complete.')
                    } catch (e) { onError(e.message); setStatus('❌ ' + e.message) }
                    finally { setLoading(false) }
                },
                (err) => { setIsRecording(false); setStatus(`❌ Mic error: ${err}`) }
            )
            recRef.current.start()
        } catch (e) {
            setStatus(`❌ Microphone access denied: ${e.message}`)
        }
    }

    const stopRecording = () => {
        recRef.current?.stop()
        streamRef.current?.getTracks().forEach(t => t.stop())
        setIsRecording(false)
        setStatus('Stopped — processing…')
    }

    return (
        <div>
            <p style={hint}>
                Click <em>Start Recording</em> and speak. Click <em>Stop</em> when done — transcript is sent for analysis automatically.
            </p>

            {/* Mic level indicator */}
            {isRecording && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#f00', display: 'inline-block', animation: 'pulse 1s infinite' }} />
                    <span style={{ color: '#f88', fontSize: 13 }}>Live recording active</span>
                </div>
            )}

            <div style={{ display: 'flex', gap: 8 }}>
                <Btn onClick={startRecording} disabled={isRecording || loading}>🎙 Start Recording</Btn>
                <Btn onClick={stopRecording} disabled={!isRecording} secondary>⏹ Stop</Btn>
            </div>

            {status && <p style={statusStyle}>{status}</p>}
            <TranscriptBox final={finalText} interim={interim} placeholder="Speak — live transcript appears here…" />
        </div>
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// ── Section 4: Record Video (Live Camera + Mic) ───────────────────────────────
// ═══════════════════════════════════════════════════════════════════════════════
function RecordVideo({ onResult, onError }) {
    const [isRecording, setIsRecording] = useState(false)
    const [hasCamera, setHasCamera] = useState(false)
    const [status, setStatus] = useState('')
    const [finalText, setFinalText] = useState('')
    const [interim, setInterim] = useState('')
    const [loading, setLoading] = useState(false)
    const videoRef = useRef(null)
    const recRef = useRef(null)
    const streamRef = useRef(null)

    const startCamera = async () => {
        try {
            streamRef.current = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            if (videoRef.current) {
                videoRef.current.srcObject = streamRef.current
                videoRef.current.play()
            }
            setHasCamera(true)
            setStatus('Camera active. Click Record when ready.')
        } catch (e) {
            setStatus(`❌ Camera/mic access denied: ${e.message}`)
        }
    }

    const startRecording = () => {
        if (!SR) { setStatus('❌ SpeechRecognition not supported. Use Chrome.'); return }
        if (!hasCamera) { setStatus('❌ Start camera first.'); return }

        setFinalText('')
        setInterim('')
        setIsRecording(true)
        setStatus('🔴 Recording… speak now.')

        recRef.current = buildRecognizer(
            (fin, int) => { setFinalText(fin); setInterim(int) },
            async (final) => {
                setIsRecording(false)
                setStatus('✅ Recording done. Analyzing…')
                setLoading(true)
                try {
                    const r = await analyzeText(final || '[no speech detected]', 'video')
                    onResult(r)
                    setStatus('✅ Analysis complete.')
                } catch (e) { onError(e.message); setStatus('❌ ' + e.message) }
                finally { setLoading(false) }
            },
            (err) => { setIsRecording(false); setStatus(`❌ Error: ${err}`) }
        )
        recRef.current.start()
    }

    const stopAll = () => {
        recRef.current?.stop()
        streamRef.current?.getTracks().forEach(t => t.stop())
        if (videoRef.current) videoRef.current.srcObject = null
        setIsRecording(false)
        setHasCamera(false)
        setStatus('Camera stopped — processing…')
    }

    // Clean up stream on unmount
    useEffect(() => () => { streamRef.current?.getTracks().forEach(t => t.stop()) }, [])

    return (
        <div>
            <p style={hint}>
                Start the camera, then click <em>Record</em> and speak. Click <em>Stop</em> to end and analyze.
            </p>

            {/* Live camera preview */}
            <video
                ref={videoRef}
                muted
                playsInline
                style={{
                    width: '100%', maxHeight: 260, background: '#000',
                    borderRadius: 4, marginBottom: 8, border: '1px solid #333',
                    display: 'block',
                }}
            />

            {isRecording && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#f00', display: 'inline-block', animation: 'pulse 1s infinite' }} />
                    <span style={{ color: '#f88', fontSize: 13 }}>Recording live video</span>
                </div>
            )}

            <div style={{ display: 'flex', gap: 8 }}>
                <Btn onClick={startCamera} disabled={hasCamera}>📷 Start Camera</Btn>
                <Btn onClick={startRecording} disabled={!hasCamera || isRecording || loading}>🔴 Record</Btn>
                <Btn onClick={stopAll} disabled={!hasCamera} secondary>⏹ Stop</Btn>
            </div>

            {status && <p style={statusStyle}>{status}</p>}
            <TranscriptBox final={finalText} interim={interim} placeholder="Speak — live transcript appears here…" />
        </div>
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// ── Main MediaAnalyzer export ──────────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════════════

const MODES = [
    { key: 'audio-upload', label: '🔊 Audio Upload' },
    { key: 'video-upload', label: '🎬 Video Upload' },
    { key: 'record-audio', label: '🎙 Record Audio' },
    { key: 'record-video', label: '📹 Record Video' },
]

export default function MediaAnalyzer() {
    const [mode, setMode] = useState('audio-upload')
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)

    const handleResult = useCallback((r) => { setResult(r); setError(null) }, [])
    const handleError = useCallback((e) => { setError(e); setResult(null) }, [])

    // Clear result when switching modes
    const switchMode = (m) => { setMode(m); setResult(null); setError(null) }

    const sharedProps = { onResult: handleResult, onError: handleError }

    if (!SR) {
        return (
            <div style={{ padding: 16, background: '#2a0a0a', borderRadius: 6, border: '1px solid #f66', color: '#f99' }}>
                ⚠️ <strong>Web Speech API not available.</strong><br />
                SpeechRecognition requires <strong>Google Chrome</strong> or <strong>Microsoft Edge</strong>.
                Please switch browsers to use media transcription.
            </div>
        )
    }

    return (
        <div style={{ marginTop: 8 }}>
            {/* ── Mode tabs ── */}
            <div style={{ display: 'flex', gap: 4, marginBottom: 16, flexWrap: 'wrap' }}>
                {MODES.map(m => (
                    <button
                        key={m.key}
                        onClick={() => switchMode(m.key)}
                        style={{
                            padding: '8px 14px',
                            fontSize: 13,
                            cursor: 'pointer',
                            borderRadius: 4,
                            border: mode === m.key ? '2px solid #4af' : '1px solid #555',
                            background: mode === m.key ? '#0d2a3a' : '#1a1a1a',
                            color: mode === m.key ? '#4af' : '#aaa',
                            fontWeight: mode === m.key ? 'bold' : 'normal',
                            transition: 'all 0.15s',
                        }}
                    >
                        {m.label}
                    </button>
                ))}
            </div>

            {/* ── Active section ── */}
            <div style={{ padding: 16, background: '#141414', borderRadius: 6, border: '1px solid #333' }}>
                {mode === 'audio-upload' && <AudioUpload {...sharedProps} />}
                {mode === 'video-upload' && <VideoUpload {...sharedProps} />}
                {mode === 'record-audio' && <RecordAudio {...sharedProps} />}
                {mode === 'record-video' && <RecordVideo {...sharedProps} />}
            </div>

            {/* ── Error ── */}
            {error && (
                <div style={{ marginTop: 12, padding: 12, background: '#2a0a0a', border: '1px solid #f66', borderRadius: 4, color: '#f99' }}>
                    ❌ {error}
                </div>
            )}

            {/* ── Result ── */}
            <ResultPanel result={result} />

            {/* Pulse keyframe */}
            <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(1.3); }
        }
      `}</style>
        </div>
    )
}

// ─── Shared micro-components ──────────────────────────────────────────────────
function Btn({ children, onClick, disabled, secondary }) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            style={{
                padding: '8px 16px',
                fontSize: 13,
                cursor: disabled ? 'not-allowed' : 'pointer',
                borderRadius: 4,
                border: 'none',
                background: disabled ? '#333' : secondary ? '#2a2a2a' : '#1a4a6a',
                color: disabled ? '#666' : secondary ? '#aaa' : '#fff',
                transition: 'background 0.15s',
            }}
        >
            {children}
        </button>
    )
}

const hint = { color: '#888', fontSize: 13, margin: '0 0 12px' }
const statusStyle = { color: '#aaa', fontSize: 13, marginTop: 8, fontStyle: 'italic' }
