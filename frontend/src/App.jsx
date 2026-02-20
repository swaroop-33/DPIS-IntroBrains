import { useState } from 'react'
import UploadPanel from './UploadPanel.jsx'
import MediaAnalyzer from './components/MediaAnalyzer.jsx'
import FileForensicsPanel from './components/FileForensicsPanel.jsx'
import { analyzeText } from './services/api.js'

// ── Tab definitions ───────────────────────────────────────────────────────────
const TABS = [
    { key: 'text', label: '📝 Text Analysis' },
    { key: 'media', label: '🎬 Media Analysis' },
    { key: 'forensic', label: '🔬 Forensic Analysis' },
]

// ─── Score row helper ─────────────────────────────────────────────────────────
function Row({ icon, label, score, detail, hl, bold }) {
    const base = { border: '1px solid #ccc', padding: '8px 12px' }
    const cell = bold ? { ...base, fontWeight: 'bold' } : base
    return (
        <tr style={hl ? { background: hl } : {}}>
            <td style={cell}>{icon} {label}</td>
            <td style={cell}>{score != null ? Number(score).toFixed(1) : '—'}</td>
            <td style={cell}>{detail}</td>
        </tr>
    )
}

// ─── Result display (used by Text mode) ──────────────────────────────────────
function ResultDisplay({ result }) {
    if (!result) return null
    return (
        <div style={{ marginTop: 16 }}>
            <h2 style={{ marginBottom: 8 }}>Analysis Result</h2>

            <table style={{ borderCollapse: 'collapse', width: '100%', marginBottom: 24 }}>
                <thead>
                    <tr style={{ background: '#f0f0f0' }}>
                        <th style={TH}>Module</th>
                        <th style={TH}>Score / 100</th>
                        <th style={TH}>Level / Detail</th>
                    </tr>
                </thead>
                <tbody>
                    <Row icon="🎭" label="Deepfake (DF)" score={result.deepfake?.final_deepfake_score} detail={result.deepfake?.method} />
                    <Row icon="😡" label="Emotion (EA)" score={result.emotion?.amplification_score} detail={`Dominant: ${result.emotion?.dominant_emotion}`} />
                    <Row icon="📢" label="Propaganda (MP)" score={result.propaganda?.manipulation_score} detail={`${result.propaganda?.trigger_phrases?.length ?? 0} triggers`} />
                    <Row icon="📈" label="Virality (VR)" score={result.virality?.virality_score} detail={`Spread: ${result.virality?.spread_probability}`} />
                    <Row icon="🧠" label="PPS" score={result.pps?.score} detail={result.pps?.threat_level} hl="#fff8e7" bold />
                    <Row icon="🌐" label="SDI" score={result.sdi?.sdi_score} detail={`Disruption: ${result.sdi?.disruption_level}`} hl="#fde8e8" bold />
                </tbody>
            </table>

            <h3>📋 Explainability</h3>
            <p>{result.explanation?.summary}</p>

            <h3>🔀 Counterfactual Analysis</h3>
            <p>{result.explanation?.counterfactual_analysis?.impact_statement}</p>
            <table style={{ borderCollapse: 'collapse', marginBottom: 24 }}>
                <thead>
                    <tr style={{ background: '#f0f0f0' }}>
                        <th style={TH}>Scenario</th><th style={TH}>PPS</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td style={TD}>Original</td><td style={TD}><strong>{result.pps?.score?.toFixed(1)}</strong></td></tr>
                    <tr><td style={TD}>Without urgency triggers</td><td style={TD}>{result.explanation?.counterfactual_analysis?.pps_without_urgency?.toFixed(1)}</td></tr>
                    <tr><td style={TD}>With fear halved</td><td style={TD}>{result.explanation?.counterfactual_analysis?.pps_without_fear?.toFixed(1)}</td></tr>
                </tbody>
            </table>

            <h3>🔍 Top Signals</h3>
            <ul>
                {result.explanation?.top_signals?.map((s, i) => (
                    <li key={i} style={{ marginBottom: 4, whiteSpace: 'pre-wrap' }}>{s}</li>
                ))}
            </ul>

            {result.performance && (
                <p style={{ color: '#888', fontSize: 12 }}>⚡ {result.performance.execution_time_ms} ms</p>
            )}

            <details style={{ marginTop: 16 }}>
                <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>Raw JSON response</summary>
                <pre style={{ background: '#1e1e1e', color: '#d4d4d4', padding: 16, borderRadius: 6, overflow: 'auto', maxHeight: 480, fontSize: 12, marginTop: 8 }}>
                    {JSON.stringify(result, null, 2)}
                </pre>
            </details>
        </div>
    )
}

// ═══════════════════════════════════════════════════════════════════════════════
// ── App Root ──────────────────────────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════════════
function App() {
    const [tab, setTab] = useState('text')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    // Text mode — submit handler
    const handleAnalyze = async ({ text, inputType }) => {
        setLoading(true)
        setError(null)
        setResult(null)
        try {
            const data = await analyzeText(text, inputType, 0.72)
            setResult(data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    // Clear results when switching tabs
    const switchTab = (t) => { setTab(t); setResult(null); setError(null) }

    return (
        <div style={{ fontFamily: 'monospace', maxWidth: 940, margin: '40px auto', padding: '0 16px' }}>
            {/* ── Header ── */}
            <h1 style={{ marginBottom: 4 }}>DPIS — Deepfake Psychological Impact Shield</h1>
            <p style={{ color: '#555', marginTop: 0 }}>Multi-modal analysis pipeline · v2.0</p>

            <hr />

            {/* ── Tab nav ── */}
            <div style={{ display: 'flex', gap: 6, marginBottom: 20 }}>
                {TABS.map(t => (
                    <button
                        key={t.key}
                        onClick={() => switchTab(t.key)}
                        style={{
                            padding: '9px 18px',
                            fontSize: 14,
                            cursor: 'pointer',
                            borderRadius: 4,
                            border: tab === t.key ? '2px solid #333' : '1px solid #ccc',
                            background: tab === t.key ? '#1a1a2e' : '#f5f5f5',
                            color: tab === t.key ? '#fff' : '#333',
                            fontWeight: tab === t.key ? 'bold' : 'normal',
                        }}
                    >
                        {t.label}
                    </button>
                ))}
            </div>

            {/* ── Text Analysis tab ── */}
            {tab === 'text' && (
                <>
                    <UploadPanel onAnalyze={handleAnalyze} loading={loading} />
                    <hr style={{ marginTop: 24 }} />
                    {loading && <p>⏳ Analyzing…</p>}
                    {error && (
                        <div style={{ color: '#c00', background: '#fff0f0', border: '1px solid #f99', padding: '12px 16px', borderRadius: 4, marginTop: 16 }}>
                            <strong>Error:</strong> {error}
                        </div>
                    )}
                    <ResultDisplay result={result} />
                </>
            )}

            {/* ── Media Analysis tab ── */}
            {tab === 'media' && (
                <>
                    <p style={{ color: '#555', fontSize: 13, marginBottom: 16 }}>
                        Upload or record audio/video. Speech is transcribed in-browser via Web Speech API (Chrome required),
                        then sent to the DPIS analysis pipeline automatically.
                    </p>
                    <MediaAnalyzer />
                </>
            )}

            {/* ── Forensic Analysis tab ── */}
            {tab === 'forensic' && (
                <>
                    <FileForensicsPanel />
                </>
            )}
        </div>
    )
}

const TH = { border: '1px solid #ccc', padding: '8px 12px', textAlign: 'left' }
const TD = { border: '1px solid #ccc', padding: '8px 12px' }

export default App