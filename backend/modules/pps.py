"""
DPIS — PPS Aggregator + Societal Disruption Index (Calibrated Stable)

Controlled nonlinear amplification.
No automatic 100 saturation.
Strong stacking but realistic ceiling.
"""

from typing import Dict, Any


def _threat_level(score: float) -> str:
    if score <= 30:
        return "Low Psychological Threat"
    elif score <= 60:
        return "Moderate Manipulation Risk"
    elif score <= 80:
        return "High Persuasion Threat"
    else:
        return "Severe Societal Disruption Potential"


def _disruption_level(sdi: float) -> str:
    if sdi <= 25:
        return "Low"
    elif sdi <= 55:
        return "Moderate"
    else:
        return "Severe"


def compute_pps(
    deepfake_score: float,
    emotion_score: float,
    manipulation_score: float,
    virality_score: float,
) -> Dict[str, Any]:

    # Base weighted score
    df_contrib = 0.30 * deepfake_score
    ea_contrib = 0.30 * emotion_score
    mp_contrib = 0.25 * manipulation_score
    vr_contrib = 0.15 * virality_score

    base_score = df_contrib + ea_contrib + mp_contrib + vr_contrib

    # Controlled arousal amplification
    arousal_factor = (emotion_score / 100) * (virality_score / 100)
    if arousal_factor > 0.30:
        base_score *= 1 + (arousal_factor * 0.25)

    # Controlled multi-signal escalation
    high_dims = sum(
        score > 65
        for score in [
            deepfake_score,
            emotion_score,
            manipulation_score,
            virality_score,
        ]
    )

    if high_dims >= 2:
        base_score *= 1 + (0.05 * high_dims)

    # Softer nonlinear scaling
    normalized = min(base_score / 100, 1.2)
    escalated = normalized ** 1.08

    pps_score = round(min(escalated * 100, 100), 2)

    return {
        "score": pps_score,
        "threat_level": _threat_level(pps_score),
        "breakdown": {
            "deepfake_contribution": round(df_contrib, 2),
            "emotion_contribution": round(ea_contrib, 2),
            "manipulation_contribution": round(mp_contrib, 2),
            "virality_contribution": round(vr_contrib, 2),
        },
        "interaction_effects": {
            "arousal_multiplier_applied": arousal_factor > 0.30,
            "high_dimension_count": high_dims,
        },
        "score_rationale": {
            "deepfake": "Authenticity breach risk — erodes trust in digital reality",
            "emotion": "Psychological leverage — high-arousal emotion drives compliance",
            "manipulation": "Intent-based framing tactics that bypass rational scrutiny",
            "virality": "Amplification potential — determines societal spread",
            "interaction": "Stacked high-risk signals amplify psychological impact nonlinearly",
        },
    }


def compute_sdi(pps_score: float, virality_score: float) -> Dict[str, Any]:

    sdi_score = round(pps_score * (virality_score / 100.0), 2)
    sdi_score = min(max(sdi_score, 0.0), 100.0)

    return {
        "sdi_score": sdi_score,
        "disruption_level": _disruption_level(sdi_score),
    }