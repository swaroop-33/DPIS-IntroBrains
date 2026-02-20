import { useState } from 'react'

const INPUT_TYPES = [
    { value: 'text', label: 'Text / Post' },
    { value: 'audio', label: 'Audio Transcript' },
    { value: 'video', label: 'Video Transcript' },
]

const EXAMPLES = [
    { label: 'Neutral', text: 'Scientists discovered a new species of deep-sea fish in the Pacific Ocean this week.' },
    { label: 'Moderate', text: 'BREAKING: You need to see this before it gets deleted. Share before they silence the truth!' },
    { label: 'High Risk', text: 'URGENT ACT NOW!! They dont want you to know the TRUTH. The mainstream media is LYING. Wake up people! Share this immediately. 100% proven. Fear is everywhere. The elites are suppressing this. Undeniable proof!' },
]

function UploadPanel({ onAnalyze, loading }) {
    const [text, setText] = useState('')
    const [inputType, setInputType] = useState('text')
    const [charCount, setCharCount] = useState(0)

    const handleText = (val) => { setText(val); setCharCount(val.length) }

    const handleSubmit = (e) => {
        e.preventDefault()
        const trimmed = text.trim()
        if (!trimmed || trimmed.length < 5) return
        onAnalyze({ text: trimmed, inputType })
    }

    const loadExample = (t) => { handleText(t) }

    return (
        <form onSubmit={handleSubmit}>
            <div className="card">
                <p className="section-label">Input Type</p>
                <div className="pill-group" style={{ marginBottom: 20 }}>
                    {INPUT_TYPES.map(o => (
                        <button
                            key={o.value}
                            type="button"
                            className={`pill-option${inputType === o.value ? ' selected' : ''}`}
                            onClick={() => setInputType(o.value)}
                        >
                            {o.label}
                        </button>
                    ))}
                </div>

                <p className="section-label">Content</p>
                <div className="input-group">
                    <textarea
                        id="content-input"
                        className="dpis-textarea"
                        value={text}
                        onChange={e => handleText(e.target.value)}
                        rows={7}
                        placeholder={
                            inputType === 'text'
                                ? 'Paste a social media post, news excerpt, or any text…'
                                : `Paste the ${inputType} transcript here…`
                        }
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 11, color: 'var(--t3)' }}>{charCount} characters</span>
                        <span style={{ fontSize: 11, color: 'var(--t3)' }}>ℹ️ Deepfake score simulated at 0.72</span>
                    </div>
                </div>

                {/* Example loader */}
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 20 }}>
                    <span style={{ fontSize: 11, color: 'var(--t3)', whiteSpace: 'nowrap' }}>Try example:</span>
                    {EXAMPLES.map(ex => (
                        <button
                            key={ex.label}
                            type="button"
                            onClick={() => loadExample(ex.text)}
                            style={{
                                fontSize: 11, padding: '4px 10px', cursor: 'pointer',
                                background: 'var(--surface)', border: '1px solid var(--border)',
                                borderRadius: 6, color: 'var(--t2)', fontFamily: 'var(--font)',
                            }}
                        >
                            {ex.label}
                        </button>
                    ))}
                </div>

                <button
                    type="submit"
                    disabled={loading || text.trim().length < 5}
                    className="btn-primary"
                >
                    {loading ? <><span className="loading-spinner" /> Analyzing…</> : '🔍 Run Analysis'}
                </button>
            </div>
        </form>
    )
}

export default UploadPanel
