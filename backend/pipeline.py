"""
DPIS — Pipeline Orchestrator (v3.0)

Upgrades:
• Psychological Density Index (PDI)
• Cross-module stacking awareness
• Cleaner signal passing
• Hackathon-optimized output clarity
"""

from typing import Optional
import time

from modules.deepfake import analyze_deepfake
from modules.emotion import analyze_emotion
from modules.propaganda import analyze_propaganda
from modules.virality import estimate_virality
from modules.pps import compute_pps, compute_sdi
from modules.explainability import build_explanation


def _compute_pdi(text: str, manipulation_score: float, emotion_score: float) -> float:
    """
    Psychological Density Index
    Measures manipulation intensity per 100 tokens.
    """
    tokens = max(len(text.split()), 1)

    density_factor = min((manipulation_score + emotion_score) / 200, 1.0)

    length_modifier = 100 / tokens if tokens < 100 else 1.0

    pdi = min(density_factor * length_modifier * 100, 100)
    return round(pdi, 2)


def run_pipeline(
    text: str,
    input_type: str = "text",
    simulated_deepfake_score: Optional[float] = None,
) -> dict:

    start_time = time.time()

    # ── 1. Deepfake Detection ──────────────────────────────────────────────
    deepfake = analyze_deepfake(
        text=text,
        input_type=input_type,
        simulated_deepfake_score=simulated_deepfake_score,
    )

    # ── 2. Emotional Amplification ─────────────────────────────────────────
    emotion = analyze_emotion(text)

    # ── 3. Propaganda Detection ────────────────────────────────────────────
    propaganda = analyze_propaganda(text)
    polarization_intensity = propaganda.pop("_polarization_intensity", 0.0)

    # ── 4. Virality Estimation ─────────────────────────────────────────────
    virality = estimate_virality(
        emotional_amplification=emotion["amplification_score"],
        manipulation_score=propaganda["manipulation_score"],
        polarization_intensity=polarization_intensity,
        fear_score=emotion["density_scores"].get("fear", 0.0),
        anger_score=emotion["density_scores"].get("anger", 0.0),
    )

    # ── 5. PPS Aggregation ─────────────────────────────────────────────────
    pps = compute_pps(
        deepfake_score=deepfake["final_deepfake_score"],
        emotion_score=emotion["amplification_score"],
        manipulation_score=propaganda["manipulation_score"],
        virality_score=virality["virality_score"],
    )

    # ── 6. Societal Disruption Index ───────────────────────────────────────
    sdi = compute_sdi(
        pps_score=pps["score"],
        virality_score=virality["virality_score"],
    )

    # ── 7. Psychological Density Index ─────────────────────────────────────
    pdi = _compute_pdi(
        text=text,
        manipulation_score=propaganda["manipulation_score"],
        emotion_score=emotion["amplification_score"],
    )

    # ── 8. Explainability ───────────────────────────────────────────────────
    explanation = build_explanation(
        deepfake_result=deepfake,
        emotion_result=emotion,
        propaganda_result=propaganda,
        virality_result=virality,
        pps_result=pps,
    )

    total_time_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "input_type": input_type,
        "deepfake": deepfake,
        "emotion": emotion,
        "propaganda": propaganda,
        "virality": virality,
        "pps": pps,
        "sdi": sdi,
        "pdi": {
            "psychological_density_index": pdi
        },
        "explanation": explanation,
        "performance": {
            "execution_time_ms": total_time_ms
        }
    }