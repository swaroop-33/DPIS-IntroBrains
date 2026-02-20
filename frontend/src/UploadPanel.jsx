import { useState } from 'react'

/**
 * UploadPanel — Phase 1
 *
 * Props:
 *   onAnalyze({ text, inputType }) → called when user submits
 *   loading → boolean, disables button while fetch is in-flight
 *
 * Features:
 *   • Textarea for pasting text / transcript
 *   • Dropdown to select input_type (text | audio | video)
 *   • Submit button with basic validation (no empty text)
 */
function UploadPanel({ onAnalyze, loading }) {
    const [text, setText] = useState('')
    const [inputType, setInputType] = useState('text')

    const handleSubmit = (e) => {
        e.preventDefault()
        const trimmed = text.trim()
        if (!trimmed) {
            alert('Please enter some content to analyze.')
            return
        }
        onAnalyze({ text: trimmed, inputType })
    }

    return (
        <form onSubmit={handleSubmit}>
            <h2>Input</h2>

            {/* Input type selector */}
            <div style={{ marginBottom: 12 }}>
                <label htmlFor="input-type" style={{ marginRight: 8, fontWeight: 'bold' }}>
                    Input Type:
                </label>
                <select
                    id="input-type"
                    value={inputType}
                    onChange={(e) => setInputType(e.target.value)}
                    style={{ padding: '4px 8px', fontSize: 14 }}
                >
                    <option value="text">Text / Transcript</option>
                    <option value="audio">Audio (text proxy)</option>
                    <option value="video">Video (text proxy)</option>
                </select>
            </div>

            {/* Text / transcript input */}
            <div style={{ marginBottom: 12 }}>
                <label htmlFor="content-input" style={{ fontWeight: 'bold', display: 'block', marginBottom: 4 }}>
                    Content to Analyze:
                </label>
                <textarea
                    id="content-input"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    rows={8}
                    placeholder={
                        inputType === 'text'
                            ? 'Paste a social media post, news excerpt, or any text…'
                            : `Paste the ${inputType} transcript here…`
                    }
                    style={{
                        width: '100%',
                        padding: 10,
                        fontFamily: 'monospace',
                        fontSize: 13,
                        boxSizing: 'border-box',
                        resize: 'vertical',
                    }}
                />
            </div>

            {/* Demo note */}
            <p style={{ color: '#888', fontSize: 12, margin: '0 0 12px' }}>
                ℹ️ Demo mode: deepfake model confidence fixed at 0.72 (simulated).
            </p>

            {/* Submit */}
            <button
                type="submit"
                disabled={loading}
                style={{
                    padding: '10px 24px',
                    fontSize: 15,
                    cursor: loading ? 'not-allowed' : 'pointer',
                    background: loading ? '#aaa' : '#1a1a2e',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 4,
                }}
            >
                {loading ? '⏳ Analyzing…' : '🔍 Analyze'}
            </button>
        </form>
    )
}

export default UploadPanel
