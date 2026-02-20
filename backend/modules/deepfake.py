"""
DPIS — Deepfake Detection Module (v3.0)

Upgrades:
• Density-aware lexical anomaly
• Stronger repetition detection
• Escalation for stacked synthetic markers
• Nonlinear top-heavy scaling
• Still heuristic-only, instant execution
"""

from typing import Dict, Any, Optional


ANOMALY_SIGNALS_WEIGHTS = {
    "face_embedding_variance": 0.35,
    "lip_sync_mismatch":       0.35,
    "metadata_inconsistency":  0.15,
    "synthetic_pattern_stack": 0.15,
}


def _compute_anomaly_heuristic(text: str, input_type: str) -> tuple[float, list[str]]:

    signals = []
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)

    if word_count == 0:
        return 0.0, []

    # ── 1️⃣ Lexical Diversity (Density-aware) ───────────────────────
    unique_ratio = len(set(words)) / word_count
    repetition_score = max(0.0, 1.0 - unique_ratio)

    if repetition_score > 0.35:
        signals.append(
            f"Low lexical diversity (unique ratio {unique_ratio:.2f}) — repetition anomaly"
        )

    # ── 2️⃣ Emotional Spike Density ─────────────────────────────────
    spike_markers = [
        "!!!", "??", "urgent", "alert", "breaking",
        "warning", "now", "immediately", "shocking"
    ]

    spike_hits = sum(text_lower.count(marker) for marker in spike_markers)
    spike_density = min((spike_hits / max(word_count, 20)) * 50, 1.0)

    if spike_density > 0.4:
        signals.append(
            f"High emotional spike density ({spike_hits} markers)"
        )

    # ── 3️⃣ Synthetic Phrase Repetition ─────────────────────────────
    synthetic_phrases = [
        "act now",
        "share immediately",
        "100% proven",
        "they don't want you",
        "wake up"
    ]

    synthetic_hits = sum(text_lower.count(p) for p in synthetic_phrases)
    synthetic_stack_score = min(synthetic_hits / 4.0, 1.0)

    if synthetic_hits >= 2:
        signals.append(
            f"Stacked synthetic persuasion phrases ({synthetic_hits})"
        )

    # ── 4️⃣ Metadata Proxy (for media inputs) ───────────────────────
    meta_score = 0.0
    if input_type in ("video", "audio"):
        meta_score = 0.6
        signals.append(
            f"Claimed {input_type} input — authenticity unverifiable in text mode"
        )

    # ── Hybrid anomaly score ────────────────────────────────────────
    anomaly_score = (
        ANOMALY_SIGNALS_WEIGHTS["face_embedding_variance"] * repetition_score +
        ANOMALY_SIGNALS_WEIGHTS["lip_sync_mismatch"]       * spike_density +
        ANOMALY_SIGNALS_WEIGHTS["metadata_inconsistency"]  * meta_score +
        ANOMALY_SIGNALS_WEIGHTS["synthetic_pattern_stack"] * synthetic_stack_score
    )

    # Nonlinear escalation for stronger anomalies
    anomaly_score = anomaly_score ** 1.15

    return min(anomaly_score, 1.0), signals


def analyze_deepfake(
    text: str,
    input_type: str = "text",
    simulated_deepfake_score: Optional[float] = None
) -> Dict[str, Any]:

    # ── Model Confidence ───────────────────────────────────────────
    if simulated_deepfake_score is not None:
        model_confidence = float(simulated_deepfake_score)
        model_label = "[SIMULATED] Pretrained API not available — demo confidence"
    else:
        model_confidence = 0.30
        model_label = "[HEURISTIC] No deepfake API configured — elevated baseline"

    # ── Anomaly Heuristic ───────────────────────────────────────────
    anomaly_raw, anomaly_signals = _compute_anomaly_heuristic(text, input_type)

    # ── Hybrid Combination ──────────────────────────────────────────
    df_normalized = (0.55 * model_confidence) + (0.45 * anomaly_raw)

    # Top-heavy scaling
    df_normalized = df_normalized ** 1.10

    df_score = round(min(df_normalized, 1.0) * 100, 2)

    model_confidence_pct = round(model_confidence * 100, 2)
    anomaly_pct = round(anomaly_raw * 100, 2)

    all_signals = [model_label] + anomaly_signals

    if df_score > 70:
        all_signals.append("Hybrid authenticity risk exceeds high threshold")

    return {
        "method": "Hybrid Authenticity Risk Estimation",
        "model_confidence": model_confidence_pct,
        "anomaly_score": anomaly_pct,
        "final_deepfake_score": df_score,
        "signals": all_signals,
        "label": f"[HYBRID] Authenticity Risk — {df_score:.1f}/100",
    }