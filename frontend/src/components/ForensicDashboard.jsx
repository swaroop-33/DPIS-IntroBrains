import { useState } from 'react'

/* ─────────────────────────────────────────────────────────────
   Utility Functions
───────────────────────────────────────────────────────────── */

function scoreColor(val) {
    if (val >= 75) return '#ef4444'
    if (val >= 50) return '#f97316'
    if (val >= 25) return '#eab308'
    return '#22c55e'
}

function threatBadgeStyle(pps) {
    if (pps >= 75) return { bg: '#3b0000', border: '#ef4444', text: '#fca5a5' }
    if (pps >= 50) return { bg: '#2d1500', border: '#f97316', text: '#fdba74' }
    if (pps >= 25) return { bg: '#2d2500', border: '#eab308', text: '#fde047' }
    return { bg: '#00200a', border: '#22c55e', text: '#86efac' }
}

/* ─────────────────────────────────────────────────────────────
   Gauge
───────────────────────────────────────────────────────────── */

function Gauge({ label, value }) {
    const pct = Math.min(Math.max(value, 0), 100)
    const color = scoreColor(pct)

    return (
        <div style={{
            flex: 1,
            minWidth: 160,
            background: '#0e0e1a',
            border: `1px solid ${color}44`,
            borderRadius: 10,
            padding: 18,
            textAlign: 'center'
        }}>
            <div style={{ fontSize: 28, fontWeight: 'bold', color }}>
                {pct.toFixed(1)}
            </div>
            <div style={{ fontSize: 12, color: '#888' }}>{label}</div>
        </div>
    )
}

/* ─────────────────────────────────────────────────────────────
   Bar
───────────────────────────────────────────────────────────── */

function Bar({ label, value }) {
    const pct = Math.min(Math.max(value, 0), 100)
    const color = scoreColor(pct)

    return (
        <div style={{ marginBottom: 16 }}>
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: 13,
                marginBottom: 6,
                color: '#ccc'
            }}>
                <span>{label}</span>
                <span style={{ color, fontWeight: 'bold' }}>{pct.toFixed(1)}</span>
            </div>

            <div style={{
                height: 22,
                borderRadius: 999,
                background: '#1e1e2e',
                overflow: 'hidden'
            }}>
                <div style={{
                    width: `${pct}%`,
                    height: '100%',
                    background: color,
                    transition: 'width .6s ease'
                }} />
            </div>
        </div>
    )
}

/* ─────────────────────────────────────────────────────────────
   Signal List
───────────────────────────────────────────────────────────── */

function SignalList({ title, signals }) {
    const [open, setOpen] = useState(false)

    if (!signals || signals.length === 0) return null

    return (
        <div style={{ marginBottom: 12 }}>
            <button
                onClick={() => setOpen(o => !o)}
                style={{
                    width: '100%',
                    padding: '8px 12px',
                    textAlign: 'left',
                    background: '#0e0e1a',
                    border: '1px solid #2a2a3a',
                    borderRadius: 6,
                    color: '#ccc',
                    fontSize: 13,
                    cursor: 'pointer'
                }}
            >
                {title} ({signals.length})
            </button>

            {open && (
                <div style={{
                    padding: 12,
                    background: '#090914',
                    border: '1px solid #1e1e2e',
                    borderTop: 'none',
                    fontSize: 12,
                    color: '#aaa'
                }}>
                    {signals.map((s, i) => (
                        <div key={i} style={{ marginBottom: 6 }}>
                            • {s}
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

/* ─────────────────────────────────────────────────────────────
   MAIN COMPONENT
───────────────────────────────────────────────────────────── */

export default function ForensicDashboard({ result }) {
    if (!result) return null

    const {
        deepfake_score = 0,
        audio_spoof_score = 0,
        image_ai_score = 0,
        emotional_score = 0,
        manipulation_score = 0,
        virality_score = 0,
        pps = 0,
        blended_deepfake_score = 0,
        forensic_signals = {},
        performance = {}
    } = result

    const threatStyle = threatBadgeStyle(pps)

    const riskLabel =
        pps < 20
            ? "LOW PSYCHOLOGICAL RISK"
            : pps < 50
                ? "MODERATE DISRUPTION RISK"
                : "HIGH SOCIETAL THREAT"

    const riskColor =
        pps < 20
            ? "#22c55e"
            : pps < 50
                ? "#eab308"
                : "#ef4444"

    return (
        <div style={{
            marginTop: 20,
            background: '#07070f',
            border: '1px solid #1e1e2e',
            borderRadius: 12,
            padding: 24,
            color: '#e2e8f0'
        }}>

            {/* PRIMARY RISK BANNER */}
            <div style={{
                padding: 16,
                marginBottom: 20,
                borderRadius: 10,
                background: riskColor + "22",
                border: `2px solid ${riskColor}`,
                color: riskColor,
                fontWeight: 'bold',
                textAlign: 'center',
                fontSize: 18
            }}>
                🚨 {riskLabel}
            </div>

            {/* PPS HEADER */}
            <div style={{
                background: threatStyle.bg,
                border: `1px solid ${threatStyle.border}`,
                borderRadius: 10,
                padding: 16,
                marginBottom: 20
            }}>
                <div style={{ fontSize: 12, color: '#888' }}>
                    Psychological Persuasion Score
                </div>
                <div style={{
                    fontSize: 40,
                    fontWeight: 'bold',
                    color: threatStyle.text
                }}>
                    {pps.toFixed(1)} / 100
                </div>
                <div style={{ fontSize: 11, color: '#555' }}>
                    Execution time: {performance.execution_time_ms ?? '—'} ms
                </div>
            </div>

            {/* MEDIA SCORES */}
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
                <Gauge label="Video Deepfake" value={deepfake_score} />
                <Gauge label="Audio Spoof" value={audio_spoof_score} />
                <Gauge label="Image AI" value={image_ai_score} />
                <Gauge label="Blended Deepfake" value={blended_deepfake_score} />
            </div>

            {/* TEXT SCORES */}
            <div style={{
                background: '#0e0e1a',
                border: '1px solid #1e1e2e',
                borderRadius: 10,
                padding: 16,
                marginBottom: 24
            }}>
                <Bar label="Emotional Amplification" value={emotional_score} />
                <Bar label="Manipulation Score" value={manipulation_score} />
                <Bar label="Virality Score" value={virality_score} />
            </div>

            {/* SIGNALS */}
            <SignalList title="Video Analysis" signals={forensic_signals.video} />
            <SignalList title="Audio Analysis" signals={forensic_signals.audio} />
            <SignalList title="Image Analysis" signals={forensic_signals.image} />

        </div>
    )
}