import { useState } from "react";
import UploadPanel from "./UploadPanel.jsx";
import MediaAnalyzer from "./components/MediaAnalyzer.jsx";
import ResultDisplay from "./components/ResultDisplay.jsx";
import { analyzeText } from "./services/api.js";

const TABS = [
    {
        key: "text",
        label: "📝 Text Analysis",
        desc: "Paste any text, transcript, or social media post",
    },
    {
        key: "media",
        label: "🎬 Media Analysis",
        desc: "Upload image or capture from camera for analysis",
    },
];

function App() {
    const [tab, setTab] = useState("text");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalyze = async ({ text, inputType }) => {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const data = await analyzeText(text, inputType, 0.72);
            setResult(data);
        } catch (err) {
            setError(err.message || "Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    const switchTab = (t) => {
        setTab(t);
        setResult(null);
        setError(null);
    };

    const activeTab = TABS.find((t) => t.key === tab);

    return (
        <div className="app-shell">
            {/* Header */}
            <header className="app-header">
                <div className="header-brand">
                    <div className="header-logo">🛡️</div>
                    <div>
                        <div className="header-title">DPIS</div>
                        <div className="header-subtitle">
                            Deepfake Psychological Impact Shield · v3.0
                        </div>
                    </div>
                </div>
                <div className="header-badge">DEMO</div>
            </header>

            {/* Tabs */}
            <nav className="tab-nav" role="tablist">
                {TABS.map((t) => (
                    <button
                        key={t.key}
                        role="tab"
                        aria-selected={tab === t.key}
                        className={`tab-btn${tab === t.key ? " active" : ""}`}
                        onClick={() => switchTab(t.key)}
                    >
                        {t.label}
                    </button>
                ))}
            </nav>

            {/* Description */}
            <p className="tab-description">{activeTab?.desc}</p>

            {/* Text Analysis */}
            {tab === "text" && (
                <>
                    <UploadPanel onAnalyze={handleAnalyze} loading={loading} />

                    {loading && <div className="loading-bar" style={{ margin: "16px 0" }} />}

                    {error && (
                        <div className="alert alert-error">
                            <span className="alert-icon">⚠️</span>
                            <span>
                                <strong>Error:</strong> {error}
                            </span>
                        </div>
                    )}

                    {result && <ResultDisplay result={result} />}
                </>
            )}

            {/* Media Analysis */}
            {tab === "media" && <MediaAnalyzer />}
        </div>
    );
}

export default App;