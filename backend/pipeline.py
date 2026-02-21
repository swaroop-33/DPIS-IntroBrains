"""
DPIS — Pipeline Orchestrator (v3.4)

Full 8-layer intelligence schema + v3.3/v3.4 extensions:
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

    if evasion.get("evasion_detected"):
        platform_multiplier = max(platform_multiplier, 1.0) * 1.05

    # ── 0b. Platform Profile (FIXED LOGIC) ───────────────────────────────────
    if has_media and not media_url:
        # Direct file upload (not URL-based)
        platform_profile = {
            "platform": "DIRECT_MEDIA_UPLOAD",
            "platform_category": "media_only",
            "amplification_coefficient": 1.1,
            "propagation_risk_note":
                "Direct uploaded media — amplification potential depends on downstream distribution platform."
        }
    else:
        platform_profile = get_platform_profile(media_url)

    platform_coeff = platform_profile.get("amplification_coefficient", 1.0)
    effective_multiplier = max(platform_multiplier, platform_coeff)

    # ── 1. Deepfake Detection ────────────────────────────────────────────────
    deepfake = analyze_deepfake(
        text=normalized_text,
        input_type=input_type,
        simulated_deepfake_score=simulated_deepfake_score,
    ) or {}
    deepfake_score = _safe(deepfake, "final_deepfake_score", 0.0)

    # ── 2. Emotion Analysis ───────────────────────────────────────────────────
    emotion = analyze_emotion(normalized_text) or {}
    amplification_score = _safe(emotion, "amplification_score", 0.0)
    density_scores = emotion.get("density_scores", {}) if isinstance(emotion, dict) else {}
    fear_score = density_scores.get("fear", 0.0)
    anger_score = density_scores.get("anger", 0.0)

    # ── 3. Propaganda Detection ───────────────────────────────────────────────
    propaganda = analyze_propaganda(normalized_text) or {}
    manipulation_score = _safe(propaganda, "manipulation_score", 0.0)
    polarization_intensity = propaganda.get("polarization_intensity", 0.0)
    pattern_breakdown = propaganda.get("pattern_breakdown", {})

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
    blended_authenticity = max(deepfake_score, image_ai_probability)

    pps = compute_pps(
        deepfake_score=deepfake_score,
        emotion_score=amplification_score,
        manipulation_score=manipulation_score,
        virality_score=virality_score,
        platform_multiplier=effective_multiplier,
        blended_authenticity=blended_authenticity,
        evasion_score=evasion_score,
    ) or {}
    pps_score = _safe(pps, "score", 0.0)

    # ── 6. SDI ────────────────────────────────────────────────────────────────
    sdi = compute_sdi(pps_score=pps_score, virality_score=virality_score) or {}

    # ── 7. Credibility Erosion Index ─────────────────────────────────────────
    credibility = compute_credibility_erosion(
        deepfake_score=deepfake_score,
        image_ai_probability=image_ai_probability,
        manipulation_score=manipulation_score,
        authority_hits=pattern_breakdown.get("authority_exploitation", 0),
        absolutist_hits=pattern_breakdown.get("absolutist_framing", 0),
        has_source_attribution=False,
    )

    # ── 8. Explainability ─────────────────────────────────────────────────────
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

    # ── 10. PDI ───────────────────────────────────────────────────────────────
    pdi = _pdi(text=text, manipulation_score=manipulation_score, emotion_score=amplification_score)

    elapsed_ms = round((time.time() - start) * 1000, 2)

    return {
        "pps": pps,
        "sdi": sdi,
        "forensic": {
            "video_deepfake_probability": round(deepfake_score, 2),
            "audio_spoof_probability": 0.0,
            "image_ai_probability": round(image_ai_probability, 2),
            "authenticity_degradation_index": deepfake.get("authenticity_degradation_index", 0.0),
            "degradation_trajectory": deepfake.get("degradation_trajectory", []),
            "signals": {
                "video": deepfake.get("signals", []),
                "audio": ["No audio input"],
                "image": ["No image input"],
            },
        },
        "emotion": emotion,
        "propaganda": propaganda,
        "virality": virality,
        "counterfactual": explanation.get("counterfactual_analysis", {}),
        "adversarial": evasion,
        "platform": platform_profile,
        "credibility_erosion": credibility,
        "calibration": calibration,
        "explanation": explanation,
        "indices": {
            "psychological_density_index": pdi,
            "effective_platform_multiplier": round(effective_multiplier, 3),
        },
        "performance": {
            "execution_time_ms": elapsed_ms,
            "input_type": input_type,
            "dpis_version": "3.4.0",
        },
    }