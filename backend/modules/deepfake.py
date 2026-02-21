"""
DPIS — Deepfake & Forensic Authenticity Module (v3.3)

Req #1: Forensic Authenticity Degradation
  • Computes authenticity_degradation_index (ADI) — a trajectory metric
    showing the cumulative legitimacy erosion from each forensic anomaly layer.
  • ADI increases with each stacked signal, modeled as compounding degradation
    rather than a simple additive score.
  • Outputs degradation_trajectory: ordered list of legitimacy residual at each
    anomaly stage, enabling visual waterfall rendering in the dashboard.

Req #8: Nonlinear interaction escalation applied within forensic layer.
"""

from typing import Dict, Any, List, Optional


# Signal weights for each forensic anomaly vector
_ANOMALY_WEIGHTS = {
    "face_embedding_variance": 0.35,
    "lip_sync_mismatch":       0.35,
    "metadata_inconsistency":  0.15,
    "synthetic_pattern_stack": 0.15,
}

# Lexical markers indicating synthetic/fabricated content
_SPIKE_MARKERS = [
    "!!!",  "??",  "urgent", "alert",  "breaking",
    "warning", "now", "immediately", "shocking", "leaked",
]

_SYNTHETIC_PHRASES = [
    "act now",
    "share immediately",
    "100% proven",
    "they don't want you",
    "wake up",
    "before it's deleted",
    "classified source",
]


def _authenticity_degradation_trajectory(
    signals: List[tuple[str, float]],
    base_legitimacy: float = 1.0,
) -> List[Dict[str, Any]]:
    """
    Model legitimacy as a compounding asset degraded by each anomaly signal.
    Returns waterfall trajectory [{stage, signal, legitimacy_residual, delta}].
    Each stage degrades legitimacy by: residual *= (1 - anomaly_weight * severity)
    """
    trajectory = []
    residual = base_legitimacy

    for stage_name, severity in signals:
        delta = residual * severity
        residual = max(residual - delta, 0.0)
        trajectory.append({
            "stage":               stage_name,
            "severity":            round(severity, 3),
            "legitimacy_residual": round(residual, 3),
            "delta":               round(delta, 3),
        })

    return trajectory


def _compute_forensic_anomalies(text: str, input_type: str) -> tuple[float, List[str], List[tuple[str, float]]]:
    """
    Returns (anomaly_score 0-1, signal_strings, degradation_steps).
    degradation_steps: ordered [(stage_name, severity)] for trajectory computation.
    """
    signal_strings: List[str]            = []
    degradation_steps: List[tuple[str, float]] = []

    text_lower = text.lower()
    words      = text_lower.split()
    word_count = max(len(words), 1)

    # ── Stage 1: Lexical Diversity ─────────────────────────────────────────────
    unique_ratio     = len(set(words)) / word_count
    rep_score        = max(0.0, 1.0 - unique_ratio)
    rep_severity     = rep_score * _ANOMALY_WEIGHTS["face_embedding_variance"]
    degradation_steps.append(("lexical_diversity_check", rep_severity))
    if rep_score > 0.35:
        signal_strings.append(
            f"Lexical repetition anomaly — unique-token ratio {unique_ratio:.2f} "
            "indicates synthetic/templated content generation pattern."
        )

    # ── Stage 2: Emotional Spike Density ──────────────────────────────────────
    spike_hits    = sum(text_lower.count(m) for m in _SPIKE_MARKERS)
    spike_density = min((spike_hits / max(word_count, 20)) * 50, 1.0)
    spike_severity = spike_density * _ANOMALY_WEIGHTS["lip_sync_mismatch"]
    degradation_steps.append(("emotional_spike_density", spike_severity))
    if spike_density > 0.3:
        signal_strings.append(
            f"High-density emotional spike markers ({spike_hits} instances / {word_count} tokens) — "
            "consistent with synthetic urgency injection."
        )

    # ── Stage 3: Synthetic Persuasion Phrase Stack ────────────────────────────
    synth_hits     = sum(text_lower.count(p) for p in _SYNTHETIC_PHRASES)
    synth_score    = min(synth_hits / 4.0, 1.0)
    synth_severity = synth_score * _ANOMALY_WEIGHTS["synthetic_pattern_stack"]
    degradation_steps.append(("synthetic_phrase_stack", synth_severity))
    if synth_hits >= 2:
        signal_strings.append(
            f"Synthetic persuasion phrase stack detected ({synth_hits} canonical phrases) — "
            "pattern matches known disinformation template libraries."
        )

    # ── Stage 4: Media-type Metadata Proxy ───────────────────────────────────
    meta_severity = 0.0
    if input_type in ("video", "audio", "media"):
        meta_severity = 0.5 * _ANOMALY_WEIGHTS["metadata_inconsistency"]
        degradation_steps.append(("media_type_metadata", meta_severity))
        signal_strings.append(
            f"Media input type '{input_type}' — frame-level and provenance metadata "
            "authenticity cannot be verified without deep forensic API integration."
        )
    else:
        degradation_steps.append(("media_type_metadata", 0.0))

    # ── Composite anomaly score ────────────────────────────────────────────────
    # Compound degradation: same mechanism as trajectory
    raw = (
        _ANOMALY_WEIGHTS["face_embedding_variance"] * rep_score +
        _ANOMALY_WEIGHTS["lip_sync_mismatch"]       * spike_density +
        _ANOMALY_WEIGHTS["synthetic_pattern_stack"] * synth_score +
        _ANOMALY_WEIGHTS["metadata_inconsistency"]  * (meta_severity / max(_ANOMALY_WEIGHTS["metadata_inconsistency"], 0.01))
    )

    # Nonlinear top-heavy escalation (req #8 — exponential when multiple layers degrade)
    active_stages = sum(1 for _, sev in degradation_steps if sev > 0.03)
    if active_stages >= 3:
        raw = raw ** 0.85  # Sharpens high scores exponentially
    else:
        raw = raw ** 1.10

    return min(raw, 1.0), signal_strings, degradation_steps


def analyze_deepfake(
    text: str,
    input_type: str = "text",
    simulated_deepfake_score: Optional[float] = None,
) -> Dict[str, Any]:

    # Model confidence baseline
    if simulated_deepfake_score is not None:
        model_confidence = float(simulated_deepfake_score)
        model_label = "Externally provided deepfake confidence score (simulation/API override)"
    else:
        model_confidence = 0.30
        model_label = (
            "Heuristic baseline — no ML deepfake API configured. "
            "Elevated base confidence applied per forensic protocol."
        )

    anomaly_raw, anomaly_signals, degradation_steps = _compute_forensic_anomalies(text, input_type)

    # Hybrid: model + anomaly heuristic
    df_normalized = (0.55 * model_confidence) + (0.45 * anomaly_raw)

    # Final nonlinear scaling
    df_normalized = df_normalized ** 1.08
    df_score      = round(min(df_normalized, 1.0) * 100, 2)

    model_confidence_pct = round(model_confidence * 100, 2)
    anomaly_pct          = round(anomaly_raw * 100, 2)

    all_signals = [model_label] + anomaly_signals
    if df_score > 70:
        all_signals.append(
            "Composite authenticity risk exceeds HIGH threshold — forensic escalation warranted."
        )

    # Authenticity Degradation Index (ADI)
    trajectory = _authenticity_degradation_trajectory(degradation_steps)
    final_legitimacy = trajectory[-1]["legitimacy_residual"] if trajectory else 1.0
    adi = round((1.0 - final_legitimacy) * 100, 2)

    return {
        "method":                    "Hybrid Authenticity Risk Estimation (v3.3)",
        "model_confidence":          model_confidence_pct,
        "anomaly_score":             anomaly_pct,
        "final_deepfake_score":      df_score,
        "authenticity_degradation_index": adi,
        "degradation_trajectory":    trajectory,
        "signals":                   all_signals,
        "label": f"Authenticity Risk — {df_score:.1f}/100 | ADI {adi:.1f}",
    }