import { useState } from 'react'

/** Returns CSS class and fill class based on score 0–100 */
function scoreClass(score) {
    if (score == null) return { text: 'score-low', fill: 'fill-low' }
    if (score < 30) return { text: 'score-low', fill: 'fill-low' }
    if (score < 60) return { text: 'score-med', fill: 'fill-med' }
    return { text: 'score-high', fill: 'fill-high' }
}

function threatClass(level) {
    if (!level) return 'threat-low'
    const l = level.toLowerCase()
    if (l.includes('critical')) return 'threat-critical'
    if (l.includes('high')) return 'threat-high'
    if (l.includes('moderate')) return 'threat-moderate'
    return 'threat-low'
}

function ScoreCard({ label, score, detail, variant }) {
    const s = Number(score ?? 0)
    const cls = variant ? { text: `score-${variant}`, fill: `fill-${variant}` } : scoreClass(s)
    return (
        <div className="score-card">
            <div className="score-card-label">{label}</div>
            <div className={`score-card-value ${cls.text}`}>{s.toFixed(1)}</div>
            <div className="score-card-detail">{detail || '—'}</div>
            <div className="score-bar-track">
                <div className={`score-bar-fill ${cls.fill}`} style={{ width: `${Math.min(s, 100)}%` }} />
            </div>
        </div>
    )
}

function ResultDisplay({ result }) {
    const [showRaw, setShowRaw] = useState(false)
    if (!result) return null

    const pps = result.pps?.score ?? 0
    const ppsC = scoreClass(pps)

    return (
        <div style={{ marginTop: 24, animation: 'fadeIn 0.4s ease' }}>

            {/* ── PPS Hero ── */}
            <div className="pps-hero">
                <div>
                    <div className="pps-label">Psychological Persuasion Score</div>
                    <div className={`pps-score-num ${ppsC.text}`}>{pps.toFixed(1)}</div>
                    <span className={`pps-threat ${threatClass(result.pps?.threat_level)}`}>
                        {result.pps?.threat_level ?? 'Unknown'}
                    </span>
                </div>
                <div style={{ textAlign: 'right', color: 'var(--t3)', fontSize: 13 }}>
                    <div style={{ marginBottom: 6 }}>SDI&nbsp;
                        <span style={{ color: 'var(--t1)', fontWeight: 600 }}>
                            {(result.sdi?.sdi_score ?? 0).toFixed(1)}
                        </span>
                    </div>
                    <div>Disruption: {result.sdi?.disruption_level}</div>
                    {result.performance && (
                        <div className="perf-badge" style={{ justifyContent: 'flex-end' }}>
                            ⚡ {result.performance.execution_time_ms} ms
                        </div>
                    )}
                </div>
            </div>

            {/* ── Score Grid ── */}
            <div className="score-grid">
                <ScoreCard
                    label="🎭 Deepfake (DF)"
                    score={result.deepfake?.final_deepfake_score}
                    detail={result.deepfake?.method ?? 'Hybrid'}
                />
                <ScoreCard
                    label="😡 Emotion (EA)"
                    score={result.emotion?.amplification_score}
                    detail={`Dominant: ${result.emotion?.dominant_emotion ?? '—'}`}
                />
                <ScoreCard
                    label="📢 Propaganda (MP)"
                    score={result.propaganda?.manipulation_score}
                    detail={`${result.propaganda?.trigger_phrases?.length ?? 0} trigger(s)`}
                />
                <ScoreCard
                    label="📈 Virality (VR)"
                    score={result.virality?.virality_score}
                    detail={`Spread: ${result.virality?.spread_probability ?? '—'}`}
                    variant="cyan"
                />
            </div>

            {/* ── Trigger Phrases ── */}
            {result.propaganda?.trigger_phrases?.length > 0 && (
                <div className="card" style={{ marginBottom: 16 }}>
                    <p className="section-label">🚨 Detected Trigger Phrases</p>
                    <div className="trigger-wrap">
                        {result.propaganda.trigger_phrases.map((p, i) => (
                            <span key={i} className="trigger-pill">{p}</span>
                        ))}
                    </div>
                </div>
            )}

            {/* ── Explanation ── */}
            {result.explanation?.summary && (
                <div className="card" style={{ marginBottom: 16 }}>
                    <p className="section-label">📋 Analysis Summary</p>
                    <p style={{ fontSize: 14, lineHeight: 1.7, color: 'var(--t2)' }}>
                        {result.explanation.summary}
                    </p>

                    {result.explanation?.top_signals?.length > 0 && (
                        <>
                            <div className="divider" />
                            <p className="section-label">🔍 Top Signals</p>
                            <ul className="signals-list">
                                {result.explanation.top_signals.map((s, i) => (
                                    <li key={i} className="signal-item">
                                        <span className="signal-dot" />
                                        <span style={{ fontSize: 13, color: 'var(--t2)' }}>{s}</span>
                                    </li>
                                ))}
                            </ul>
                        </>
                    )}
                </div>
            )}

            {/* ── Counterfactual ── */}
            {result.explanation?.counterfactual_analysis && (
                <div className="card" style={{ marginBottom: 16 }}>
                    <p className="section-label">🔀 Counterfactual — What If?</p>
                    <p style={{ fontSize: 13, color: 'var(--t2)', marginBottom: 14 }}>
                        {result.explanation.counterfactual_analysis.impact_statement}
                    </p>
                    <div className="score-grid" style={{ marginBottom: 0 }}>
                        {[
                            { label: 'Original PPS', val: result.pps?.score },
                            { label: 'Without urgency', val: result.explanation.counterfactual_analysis.pps_without_urgency },
                            { label: 'With fear halved', val: result.explanation.counterfactual_analysis.pps_without_fear },
                        ].map((row, i) => (
                            <div key={i} className="score-card">
                                <div className="score-card-label">{row.label}</div>
                                <div className={`score-card-value ${scoreClass(row.val).text}`}>
                                    {row.val != null ? Number(row.val).toFixed(1) : '—'}
                                </div>
                                <div className="score-bar-track">
                                    <div className={`score-bar-fill ${scoreClass(row.val).fill}`} style={{ width: `${Math.min(row.val ?? 0, 100)}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ── PPS Breakdown ── */}
            {result.pps?.breakdown && (
                <div className="card" style={{ marginBottom: 16 }}>
                    <p className="section-label">🧠 PPS Contribution Breakdown</p>
                    <div className="score-grid" style={{ marginBottom: 0 }}>
                        {Object.entries(result.pps.breakdown).map(([key, val]) => (
                            <div key={key} className="score-card">
                                <div className="score-card-label">{key.replace(/_/g, ' ')}</div>
                                <div className="score-card-value score-cyan">{Number(val).toFixed(1)}</div>
                                <div className="score-bar-track">
                                    <div className="score-bar-fill fill-cyan" style={{ width: `${Math.min(val * 4, 100)}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ── Raw JSON toggle ── */}
            <button className="raw-json-toggle" onClick={() => setShowRaw(v => !v)}>
                {showRaw ? '▲' : '▼'} {showRaw ? 'Hide' : 'Show'} raw JSON
            </button>
            {showRaw && (
                <div className="raw-json">
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    )
}

export default ResultDisplay
