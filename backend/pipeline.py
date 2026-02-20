"""
DPIS — Pipeline Orchestrator (v3.2)

Produces the 8-layer intelligence-grade output schema:
  1. pps          — Psychological Persuasion Score
  2. sdi          — Social Disruption Index
  3. forensic     — (injected by main.py for media input; stub for text)
  4. emotion      — Emotional Amplification Engine
  5. propaganda   — Manipulation & Propaganda Layer
  6. virality     — Virality Engine
  7. counterfactual — Counterfactual Stability Analysis
  8. performance  — Execution Metadata
"""

from typing import Optional
import time

from .modules.deepfake      import analyze_deepfake
from .modules.emotion       import analyze_emotion
from .modules.propaganda    import analyze_propaganda
from .modules.virality      import estimate_virality
from .modules.pps           import compute_pps, compute_sdi
from .modules.explainability import build_explanation


def _safe(d: dict, key: str, default=0.0):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


def _compute_pdi(text: str, manipulation_score: float, emotion_score: float) -> float:
    tokens = max(len(text.split()), 1)
    density_factor = min((manipulation_score + emotion_score) / 200, 1.0)
    length_modifier = 100 / tokens if tokens < 100 else 1.0
    return round(min(density_factor * length_modifier * 100, 100), 2)


def run_pipeline(
    text: str,
    input_type: str = "text",
    simulated_deepfake_score: Optional[float] = None,
    platform_multiplier: float = 1.0,
) -> dict:

    start = time.time()

    # ── 1. Deepfake Detection ─────────────────────────────────────────────────
    deepfake = analyze_deepfake(
        text=text,
        input_type=input_type,
        simulated_deepfake_score=simulated_deepfake_score,
    ) or {}
    deepfake_score = _safe(deepfake, "final_deepfake_score", 0.0)

    # ── 2. Emotion Analysis ───────────────────────────────────────────────────
    emotion = analyze_emotion(text) or {}
    amplification_score = _safe(emotion, "amplification_score", 0.0)
    density_scores      = emotion.get("density_scores", {}) if isinstance(emotion, dict) else {}
    fear_score          = density_scores.get("fear",  0.0)
    anger_score         = density_scores.get("anger", 0.0)

    # ── 3. Propaganda Detection ───────────────────────────────────────────────
    propaganda = analyze_propaganda(text) or {}
    manipulation_score     = _safe(propaganda, "manipulation_score", 0.0)
    polarization_intensity = propaganda.get("polarization_intensity", 0.0)

    # ── 4. Virality Estimation ────────────────────────────────────────────────
    virality = estimate_virality(
        emotional_amplification=amplification_score,
        manipulation_score=manipulation_score,
        polarization_intensity=polarization_intensity,
        fear_score=fear_score,
        anger_score=anger_score,
    ) or {}
    virality_score = _safe(virality, "virality_score", 0.0)

    # ── 5. PPS Aggregation ────────────────────────────────────────────────────
    pps = compute_pps(
        deepfake_score=deepfake_score,
        emotion_score=amplification_score,
        manipulation_score=manipulation_score,
        virality_score=virality_score,
        platform_multiplier=platform_multiplier,
    ) or {}
    pps_score = _safe(pps, "score", 0.0)

    # ── 6. Societal Disruption Index ──────────────────────────────────────────
    sdi = compute_sdi(pps_score=pps_score, virality_score=virality_score) or {}

    # ── 7. Psychological Density Index (internal) ──────────────────────────────
    pdi = _compute_pdi(
        text=text,
        manipulation_score=manipulation_score,
        emotion_score=amplification_score,
    )

    # ── 8. Explainability + Counterfactual ────────────────────────────────────
    explanation = build_explanation(
        deepfake_result=deepfake,
        emotion_result=emotion,
        propaganda_result=propaganda,
        virality_result=virality,
        pps_result=pps,
    ) or {}

    elapsed_ms = round((time.time() - start) * 1000, 2)

    # ── Structured Output — 8-layer schema ────────────────────────────────────
    return {
        # Layer 1
        "pps": {
            "score":         pps_score,
            "threat_level":  pps.get("threat_level", "UNKNOWN"),
            "interpretation": pps.get("interpretation", ""),
            "breakdown":     pps.get("breakdown", {}),
            "interaction_effects": pps.get("interaction_effects", {}),
        },

        # Layer 2
        "sdi": {
            "sdi_score":             sdi.get("sdi_score", 0.0),
            "disruption_level":      sdi.get("disruption_level", "UNKNOWN"),
            "spread_risk_assessment": sdi.get("spread_risk_assessment", ""),
        },

        # Layer 3 — injected by main.py for media inputs; text stub shown here
        "forensic": {
            "video_deepfake_probability": round(deepfake_score, 2),
            "audio_spoof_probability":    0.0,
            "image_ai_probability":       0.0,
            "signals": {
                "video": deepfake.get("signals", []),
                "audio": ["No audio input"],
                "image": ["No image input"],
            },
        },

        # Layer 4
        "emotion": {
            "dominant_emotion":    emotion.get("dominant_emotion", "neutral"),
            "amplification_score": amplification_score,
            "density_scores": {
                "fear":    density_scores.get("fear",    0.0),
                "anger":   density_scores.get("anger",   0.0),
                "outrage": density_scores.get("outrage", density_scores.get("disgust", 0.0)),
                "sadness": density_scores.get("sadness", 0.0),
                "joy":     density_scores.get("joy",     0.0),
            },
            "stacking_bonus_applied": emotion.get("stacking_bonus_applied", 0.0),
        },

        # Layer 5
        "propaganda": {
            "manipulation_score":             manipulation_score,
            "trigger_phrases_detected":       propaganda.get("trigger_phrases_detected", []),
            "persuasion_techniques_detected": propaganda.get("persuasion_techniques_detected", []),
            "polarization_intensity":         polarization_intensity,
            "pattern_breakdown":              propaganda.get("pattern_breakdown", {}),
        },

        # Layer 6
        "virality": {
            "virality_score":             virality_score,
            "spread_probability":         virality.get("spread_probability", "UNKNOWN"),
            "target_vulnerability_group": virality.get("target_vulnerability_group", ""),
            "multiplier_applied":         virality.get("multiplier_applied", False),
            "multiplier_reason":          virality.get("multiplier_reason", None),
            "component_breakdown":        virality.get("component_breakdown", {}),
        },

        # Layer 7
        "counterfactual": explanation.get("counterfactual_analysis", {}),

        # Explainability (supplemental, not in schema but useful for UI)
        "explanation": {
            "summary":     explanation.get("summary", ""),
            "top_signals": explanation.get("top_signals", []),
        },

        # Internal indices
        "indices": {
            "psychological_density_index": pdi,
        },

        # Layer 8
        "performance": {
            "execution_time_ms": elapsed_ms,
            "input_type":        input_type,
        },
    }