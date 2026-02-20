import { useState } from 'react'

/** Score → color class */
function scoreClass(score) {
    if (score == null) return { text: 'score-low', fill: 'fill-low' }
    if (score <= 20) return { text: 'score-low', fill: 'fill-low' }
    if (score <= 40) return { text: 'score-low', fill: 'fill-low' }
    if (score <= 60) return { text: 'score-med', fill: 'fill-med' }
    if (score <= 80) return { text: 'score-high', fill: 'fill-high' }
    return { text: 'score-high', fill: 'fill-high' }
}

function threatClass(level) {
    if (!level) return 'threat-low'
    const l = level.toLowerCase()
    if (l === 'critical') return 'threat-critical'
    if (l === 'high') return 'threat-high'
    if (l === 'moderate') return 'threat-moderate'
    if (l === 'elevated') return 'threat-moderate'
    return 'threat-low'
}

function ScoreCard({ label, score, detail }) {
    const s = Number(score ?? 0)
    const cls = scoreClass(s)
    return (
        <div className="score-card">
            <div className="score-card-label">{label}</div>
            <div className={`score-card-value ${cls.text}`}>{s.toFixed(1)}</div>
            {detail && <div className="score-card-detail">{detail}</div>}
            <div className="score-bar-track">
                <div className={`score-bar-fill ${cls.fill}`} style={{ width: `${Math.min(s, 100)}%` }} />
            </div>
        </div>
    )
}

function SectionCard({ title, children }) {
    return (
        <div className="card" style={{ marginBottom: 16 }}>
            <p className="section-label">{title}</p>
            {children}
        </div>
    )
}

function ResultDisplay({ result, showForensic = false }) {
    const [showRaw, setShowRaw] = useState(false)
    if (!result) return null

    const pps = result.pps ?? {}
    const sdi = result.sdi ?? {}
    const emo = result.emotion ?? {}
    const prop = result.propaganda ?? {}
    const vir = result.virality ?? {}
    const cf = result.counterfactual ?? result.explanation?.counterfactual_analysis ?? {}
    const expl = result.explanation ?? {}
    const foren = result.forensic ?? {}
    const perf = result.performance ?? {}
    // v3.3
    const adv = result.adversarial ?? {}
    const plat = result.platform ?? {}
    const cred = result.credibility_erosion ?? {}
    const calib = result.calibration ?? {}

    const ppsScore = Number(pps.score ?? 0)
    const ppsC = scoreClass(ppsScore)

    const density = emo.density_scores ?? {}
    const triggers = prop.trigger_phrases_detected ?? prop.trigger_phrases ?? []
    const techniques = prop.persuasion_techniques_detected ?? []

    return (
        <div style={{ marginTop: 24, animation: 'fadeIn 0.4s ease' }}>

            {/* ── PPS Hero ── */}
            <div className="pps-hero">
                <div>
                    <div className="pps-label">Psychological Persuasion Score</div>
                    <div className={`pps-score-num ${ppsC.text}`}>{ppsScore.toFixed(1)}</div>
                    <span className={`pps-threat ${threatClass(pps.threat_level)}`}>
                        {pps.threat_level ?? 'UNKNOWN'}
                    </span>
                    {pps.interpretation && (
                        <p style={{ margin: '0.6rem 0 0', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: 420 }}>
                            {pps.interpretation}
                        </p>
                    )}
                </div>
                <div style={{ textAlign: 'right', color: 'var(--text-muted)', fontSize: 13, display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <div>SDI&nbsp;<span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{Number(sdi.sdi_score ?? 0).toFixed(1)}</span></div>
                    <div style={{ fontSize: '0.75rem' }}>{sdi.disruption_level ?? '—'}</div>
                    {perf.execution_time_ms && (
                        <div className="perf-badge" style={{ justifyContent: 'flex-end', marginTop: 4 }}>
                            ⚡ {perf.execution_time_ms} ms
                        </div>
                    )}
                </div>
            </div>

            {/* ── SDI Spread Risk ── */}
            {sdi.spread_risk_assessment && (
                <SectionCard title="SOCIAL DISRUPTION INDEX — Spread Risk Assessment">
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                        {sdi.spread_risk_assessment}
                    </p>
                </SectionCard>
            )}

            {/* ── Score Grid ── */}
            <div className="score-grid">
                <ScoreCard
                    label="Deepfake (DF)"
                    score={result.deepfake?.final_deepfake_score}
                    detail={result.deepfake?.method ?? 'Hybrid heuristic'}
                />
                <ScoreCard
                    label="Emotional Amplification"
                    score={emo.amplification_score}
                    detail={`Dominant: ${emo.dominant_emotion ?? '—'}`}
                />
                <ScoreCard
                    label="Manipulation (MP)"
                    score={prop.manipulation_score}
                    detail={`${techniques.length} technique(s) active`}
                />
                <ScoreCard
                    label="Virality Risk"
                    score={vir.virality_score}
                    detail={`Spread: ${vir.spread_probability ?? '—'}`}
                />
            </div>

            {/* ── Emotion Density ── */}
            {Object.keys(density).length > 0 && (
                <SectionCard title="EMOTIONAL AMPLIFICATION — Density Scores">
                    <div className="score-grid" style={{ marginBottom: 0 }}>
                        {Object.entries(density).map(([emotion, val]) => (
                            <ScoreCard
                                key={emotion}
                                label={emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                                score={Number(val) * 100}
                            />
                        ))}
                    </div>
                </SectionCard>
            )}

            {/* ── Persuasion Techniques ── */}
            {techniques.length > 0 && (
                <SectionCard title="MANIPULATION — Active Persuasion Techniques">
                    <ul className="signals-list">
                        {techniques.map((t, i) => (
                            <li key={i} className="signal-item">
                                <span className="signal-dot" />
                                <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{t}</span>
                            </li>
                        ))}
                    </ul>
                </SectionCard>
            )}

            {/* ── Trigger Phrases ── */}
            {triggers.length > 0 && (
                <SectionCard title="DETECTED TRIGGER PHRASES">
                    <div className="trigger-wrap">
                        {triggers.map((p, i) => (
                            <span key={i} className="trigger-pill">{p}</span>
                        ))}
                    </div>
                </SectionCard>
            )}

            {/* ── Virality — Target Vulnerability Group ── */}
            {vir.target_vulnerability_group && (
                <SectionCard title="VIRALITY ENGINE — Target Vulnerability Group">
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                        {vir.target_vulnerability_group}
                    </p>
                    {vir.multiplier_applied && vir.multiplier_reason && (
                        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 8, fontStyle: 'italic' }}>
                            High-arousal multiplier active — {vir.multiplier_reason}
                        </p>
                    )}
                </SectionCard>
            )}

            {/* ── Explanation ── */}
            {expl.summary && (
                <SectionCard title="ANALYSIS SUMMARY">
                    <p style={{ fontSize: '0.82rem', lineHeight: 1.7, color: 'var(--text-secondary)', margin: 0 }}>
                        {expl.summary}
                    </p>
                    {expl.top_signals?.length > 0 && (
                        <>
                            <div className="divider" />
                            <p className="section-label">Top Signals</p>
                            <ul className="signals-list">
                                {expl.top_signals.map((s, i) => (
                                    <li key={i} className="signal-item">
                                        <span className="signal-dot" />
                                        <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s}</span>
                                    </li>
                                ))}
                            </ul>
                        </>
                    )}
                </SectionCard>
            )}

            {/* ── Counterfactual Stability Analysis ── */}
            {cf.impact_statement && (
                <SectionCard title="COUNTERFACTUAL STABILITY ANALYSIS">
                    {cf.stability_score != null && (
                        <div style={{ marginBottom: 12 }}>
                            <ScoreCard label="Stability Score" score={cf.stability_score} detail="Higher = PPS resists signal removal" />
                        </div>
                    )}
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: '0 0 12px' }}>
                        {cf.impact_statement}
                    </p>
                    <div className="score-grid" style={{ marginBottom: 0 }}>
                        {[
                            { label: 'Original PPS', val: ppsScore },
                            { label: 'Without urgency', val: cf.pps_without_urgency },
                            { label: 'With fear halved', val: cf.pps_without_fear },
                        ].map((row, i) => (
                            <ScoreCard key={i} label={row.label} score={Number(row.val ?? 0)} />
                        ))}
                    </div>
                    {cf.recommended_intervention && (
                        <>
                            <div className="divider" />
                            <p className="section-label">Recommended Intervention</p>
                            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                                {cf.recommended_intervention}
                            </p>
                        </>
                    )}
                </SectionCard>
            )}

            {/* ── Forensic Scores (media tab only) ── */}
            {showForensic && Object.keys(foren).length > 0 && (
                <SectionCard title="FORENSIC DETECTION — Media Analysis">
                    <div className="score-grid" style={{ marginBottom: 12 }}>
                        <ScoreCard label="Video Deepfake" score={foren.video_deepfake_probability} detail="Frame-level analysis" />
                        <ScoreCard label="Audio Spoof" score={foren.audio_spoof_probability} detail="Spectral + GAN detection" />
                        <ScoreCard label="Image (AI-Gen)" score={foren.image_ai_probability} detail="Artifact pattern analysis" />
                    </div>
                    {foren.signals && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {Object.entries(foren.signals).map(([slot, sigs]) =>
                                sigs?.length > 0 ? (
                                    <div key={slot}>
                                        <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 4 }}>
                                            {slot} forensic signals
                                        </div>
                                        <ul className="signals-list">
                                            {sigs.map((s, i) => (
                                                <li key={i} className="signal-item">
                                                    <span className="signal-dot" />
                                                    <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                ) : null
                            )}
                        </div>
                    )}
                    {foren.url_source && (
                        <p style={{ marginTop: 10, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            Source type: <code style={{ fontSize: '0.75rem' }}>{foren.url_source}</code>
                        </p>
                    )}
                </SectionCard>
            )}

            {/* ── v3.3: Platform Amplification ── */}
            {plat.platform && (
                <SectionCard title="PLATFORM AMPLIFICATION — Propagation Coefficient">
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12 }}>
                        <div className="score-card" style={{ flex: '0 0 auto', minWidth: 100 }}>
                            <div className="score-card-label">Coefficient</div>
                            <div className="score-card-value score-cyan">
                                {Number(plat.amplification_coefficient ?? 1).toFixed(2)}×
                            </div>
                            <div className="score-card-detail">{plat.platform}</div>
                        </div>
                        <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                            {plat.propagation_risk_note}
                        </p>
                    </div>
                </SectionCard>
            )}

            {/* ── v3.3: Adversarial Evasion Detection ── */}
            {(adv.evasion_detected || adv.evasion_score > 0) && (
                <SectionCard title="ADVERSARIAL EVASION DETECTION">
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: adv.evasion_signals?.length ? 12 : 0 }}>
                        <ScoreCard label="Evasion Score" score={adv.evasion_score} detail={adv.evasion_detected ? 'OBFUSCATION ACTIVE' : 'None detected'} />
                    </div>
                    {adv.evasion_signals?.length > 0 && (
                        <ul className="signals-list">
                            {adv.evasion_signals.map((s, i) => (
                                <li key={i} className="signal-item">
                                    <span className="signal-dot" />
                                    <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s}</span>
                                </li>
                            ))}
                        </ul>
                    )}
                </SectionCard>
            )}

            {/* ── v3.3: Credibility Erosion Index ── */}
            {cred.credibility_erosion_index != null && (
                <SectionCard title="CREDIBILITY EROSION INDEX">
                    <div style={{ marginBottom: 12 }}>
                        <ScoreCard
                            label="Credibility Erosion Index"
                            score={cred.credibility_erosion_index}
                            detail={cred.erosion_level ?? ''}
                        />
                    </div>
                    {cred.erosion_drivers?.length > 0 && (
                        <ul className="signals-list">
                            {cred.erosion_drivers.map((d, i) => (
                                <li key={i} className="signal-item">
                                    <span className="signal-dot" />
                                    <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{d}</span>
                                </li>
                            ))}
                        </ul>
                    )}
                </SectionCard>
            )}

            {/* ── v3.3: Calibration & Confidence ── */}
            {calib.confidence_band && (
                <SectionCard title="CALIBRATION — Confidence Assessment">
                    <div className="score-grid" style={{ marginBottom: 12 }}>
                        <ScoreCard label="Data Quality" score={calib.data_quality_score} detail={calib.confidence_band} />
                        <div className="score-card">
                            <div className="score-card-label">PPS Confidence Interval</div>
                            <div className="score-card-value score-cyan">
                                [{Number(calib.confidence_interval?.lower ?? 0).toFixed(1)},&nbsp;
                                {Number(calib.confidence_interval?.upper ?? 0).toFixed(1)}]
                            </div>
                            <div className="score-card-detail">at {calib.confidence_band} confidence</div>
                        </div>
                    </div>
                    {calib.calibration_notes?.length > 0 && (
                        <ul className="signals-list">
                            {calib.calibration_notes.map((n, i) => (
                                <li key={i} className="signal-item">
                                    <span className="signal-dot" />
                                    <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{n}</span>
                                </li>
                            ))}
                        </ul>
                    )}
                </SectionCard>
            )}

            {/* ── PPS Breakdown ── */}
            {pps.breakdown && (
                <SectionCard title="PPS — Contribution Breakdown">
                    <div className="score-grid" style={{ marginBottom: 0 }}>
                        {Object.entries(pps.breakdown).map(([key, val]) => (
                            <div key={key} className="score-card">
                                <div className="score-card-label">{key.replace(/_/g, ' ')}</div>
                                <div className="score-card-value score-cyan">{Number(val).toFixed(1)}</div>
                                <div className="score-bar-track">
                                    <div className="score-bar-fill fill-cyan" style={{ width: `${Math.min(Number(val) * 4, 100)}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </SectionCard>
            )}

            {/* ── Raw JSON ── */}
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
