"""
DPIS — Pipeline Orchestrator (v3.3)

Full 8-layer intelligence schema + v3.3 extensions:
  • Adversarial Evasion Detection
  • Calibration & Confidence Intervals
  • Credibility Erosion Index
  • Platform Amplification Coefficient
"""

from typing import Optional
import time

from .modules.deepfake      import analyze_deepfake
from .modules.emotion       import analyze_emotion
from .modules.propaganda    import analyze_propaganda
from .modules.virality      import estimate_virality
from .modules.pps           import compute_pps, compute_sdi
from .modules.explainability import build_explanation
from .modules.adversarial   import detect_evasion
from .modules.calibration   import compute_calibration
from .modules.credibility   import compute_credibility_erosion
from .modules.platform_amp  import get_platform_profile


def _safe(d, key, default=0.0):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


def _pdi(text: str, manipulation_score: float, emotion_score: float) -> float:
    tokens = max(len(text.split()), 1)
    density_factor = min((manipulation_score + emotion_score) / 200.0, 1.0)
    length_modifier = 100.0 / tokens if tokens < 100 else 1.0
    return round(min(density_factor * length_modifier * 100.0, 100.0), 2)


def run_pipeline(
    text: str,
    input_type: str = "text",
    simulated_deepfake_score: Optional[float] = None,
    platform_multiplier: float = 1.0,
    media_url: Optional[str] = None,
    has_media: bool = False,
    image_ai_probability: float = 0.0,
) -> dict:

    start = time.time()

    # ── 0. Adversarial Evasion Detection ──────────────────────────────────────
    evasion = detect_evasion(text)
    normalized_text = evasion.get("normalized_text", text)
    evasion_score   = evasion.get("evasion_score", 0.0)

    # Boost multiplier if evasion detected (attacker expecting moderation bypass)
    if evasion.get("evasion_detected"):
        platform_multiplier = max(platform_multiplier, 1.0) * 1.05

    # ── 0b. Platform Profile ───────────────────────────────────────────────────
    platform_profile = get_platform_profile(media_url)
    # Override multiplier with platform coefficient if platform is known
    platform_coeff = platform_profile.get("amplification_coefficient", 1.0)
    effective_multiplier = max(platform_multiplier, platform_coeff)

    # ── 1. Deepfake Detection ─────────────────────────────────────────────────
    deepfake = analyze_deepfake(
        text=normalized_text,
        input_type=input_type,
        simulated_deepfake_score=simulated_deepfake_score,
    ) or {}
    deepfake_score = _safe(deepfake, "final_deepfake_score", 0.0)

    # ── 2. Emotion Analysis ───────────────────────────────────────────────────
    emotion = analyze_emotion(normalized_text) or {}
    amplification_score = _safe(emotion, "amplification_score", 0.0)
    density_scores      = emotion.get("density_scores", {}) if isinstance(emotion, dict) else {}
    fear_score          = density_scores.get("fear",  0.0)
    anger_score         = density_scores.get("anger", 0.0)

    # ── 3. Propaganda Detection ───────────────────────────────────────────────
    propaganda = analyze_propaganda(normalized_text) or {}
    manipulation_score      = _safe(propaganda, "manipulation_score", 0.0)
    polarization_intensity  = propaganda.get("polarization_intensity", 0.0)
    pattern_breakdown       = propaganda.get("pattern_breakdown", {})

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
        platform_multiplier=effective_multiplier,
    ) or {}
    pps_score = _safe(pps, "score", 0.0)

    # ── 6. Societal Disruption Index ──────────────────────────────────────────
    sdi = compute_sdi(pps_score=pps_score, virality_score=virality_score) or {}

    # ── 7. Credibility Erosion Index ──────────────────────────────────────────
    credibility = compute_credibility_erosion(
        deepfake_score=deepfake_score,
        image_ai_probability=image_ai_probability,
        manipulation_score=manipulation_score,
        authority_hits=pattern_breakdown.get("authority_exploitation", 0),
        absolutist_hits=pattern_breakdown.get("absolutist_framing", 0),
        has_source_attribution=False,  # conservative default
    )

    # ── 8. Explainability + Counterfactual ────────────────────────────────────
    explanation = build_explanation(
        deepfake_result=deepfake,
        emotion_result=emotion,
        propaganda_result=propaganda,
        virality_result=virality,
        pps_result=pps,
    ) or {}

    # ── 9. Calibration ────────────────────────────────────────────────────────
    calibration = compute_calibration(
        text=text,
        pps_score=pps_score,
        has_media=has_media,
        evasion_score=evasion_score,
        input_type=input_type,
    )

    # ── 10. PDI (internal index) ──────────────────────────────────────────────
    pdi = _pdi(text=text, manipulation_score=manipulation_score, emotion_score=amplification_score)

    elapsed_ms = round((time.time() - start) * 1000, 2)

    # ── Structured Output — v3.3 Schema ───────────────────────────────────────
    return {

        # Layer 1 — PPS
        "pps": {
            "score":              pps_score,
            "threat_level":       pps.get("threat_level", "UNKNOWN"),
            "interpretation":     pps.get("interpretation", ""),
            "breakdown":          pps.get("breakdown", {}),
            "interaction_effects": pps.get("interaction_effects", {}),
        },

        # Layer 2 — SDI
        "sdi": {
            "sdi_score":              sdi.get("sdi_score", 0.0),
            "disruption_level":       sdi.get("disruption_level", "UNKNOWN"),
            "spread_risk_assessment": sdi.get("spread_risk_assessment", ""),
        },

        # Layer 3 — Forensic (stub for text; overridden by main.py for media)
        "forensic": {
            "video_deepfake_probability": round(deepfake_score, 2),
            "audio_spoof_probability":    0.0,
            "image_ai_probability":       round(image_ai_probability, 2),
            "signals": {
                "video": deepfake.get("signals", []),
                "audio": ["No audio input"],
                "image": ["No image input"],
            },
        },

        # Layer 4 — Emotional Amplification
        "emotion": {
            "dominant_emotion":       emotion.get("dominant_emotion", "neutral"),
            "amplification_score":    amplification_score,
            "density_scores": {
                "fear":    density_scores.get("fear",    0.0),
                "anger":   density_scores.get("anger",   0.0),
                "outrage": density_scores.get("outrage", density_scores.get("disgust", 0.0)),
                "sadness": density_scores.get("sadness", 0.0),
                "joy":     density_scores.get("joy",     0.0),
            },
            "stacking_bonus_applied": emotion.get("stacking_bonus_applied", 0.0),
        },

        # Layer 5 — Manipulation & Propaganda
        "propaganda": {
            "manipulation_score":             manipulation_score,
            "trigger_phrases_detected":       propaganda.get("trigger_phrases_detected", []),
            "persuasion_techniques_detected": propaganda.get("persuasion_techniques_detected", []),
            "polarization_intensity":         polarization_intensity,
            "pattern_breakdown":              pattern_breakdown,
        },

        # Layer 6 — Virality Engine
        "virality": {
            "virality_score":             virality_score,
            "spread_probability":         virality.get("spread_probability", "UNKNOWN"),
            "target_vulnerability_group": virality.get("target_vulnerability_group", ""),
            "multiplier_applied":         virality.get("multiplier_applied", False),
            "multiplier_reason":          virality.get("multiplier_reason", None),
            "component_breakdown":        virality.get("component_breakdown", {}),
        },

        # Layer 7 — Counterfactual Stability
        "counterfactual": explanation.get("counterfactual_analysis", {}),

        # ──── v3.3 Extension Layers ────────────────────────────────────────────

        # v3.3 — Adversarial Evasion Detection
        "adversarial": {
            "evasion_detected": evasion.get("evasion_detected", False),
            "evasion_score":    evasion_score,
            "evasion_signals":  evasion.get("evasion_signals", []),
        },

        # v3.3 — Platform Amplification
        "platform": platform_profile,

        # v3.3 — Credibility Erosion Index
        "credibility_erosion": credibility,

        # v3.3 — Calibration & Confidence
        "calibration": calibration,

        # Supplemental explainability (for UI)
        "explanation": {
            "summary":     explanation.get("summary", ""),
            "top_signals": explanation.get("top_signals", []),
        },

        # Internal indices
        "indices": {
            "psychological_density_index": pdi,
            "effective_platform_multiplier": round(effective_multiplier, 3),
        },

        # Layer 8 — Performance
        "performance": {
            "execution_time_ms": elapsed_ms,
            "input_type":        input_type,
            "dpis_version":      "3.3",
        },
    }