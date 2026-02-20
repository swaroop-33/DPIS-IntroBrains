"""
DPIS — PPS Aggregator + Societal Disruption Index (v3.2)

Threat bands (0–20 LOW, 21–40 ELEVATED, 41–60 MODERATE, 61–80 HIGH, 81–100 CRITICAL)
SDI includes spread_risk_assessment for downstream reporting.
PPS includes interpretation for dashboard display.
"""

from typing import Dict, Any


# ──────────────────────────────────────────────────────────────────────────────
# Threat classification
# ──────────────────────────────────────────────────────────────────────────────

def _classify_pps(score: float) -> tuple[str, str]:
    """Returns (threat_level, interpretation)."""
    if score <= 20:
        return (
            "LOW",
            "Content presents negligible psychological manipulation risk. "
            "No significant disinformation indicators detected.",
        )
    elif score <= 40:
        return (
            "ELEVATED",
            "Content exhibits limited but detectable persuasion signals. "
            "Monitoring is advised; no immediate intervention required.",
        )
    elif score <= 60:
        return (
            "MODERATE",
            "Content demonstrates measurable emotional and rhetorical manipulation. "
            "Fact-verification and source authentication are recommended.",
        )
    elif score <= 80:
        return (
            "HIGH",
            "Content carries substantial disinformation and psychological manipulation potential. "
            "Counter-narrative deployment and platform flagging are warranted.",
        )
    else:
        return (
            "CRITICAL",
            "Content exhibits maximum-risk multi-layered psychological warfare characteristics. "
            "Immediate escalation, platform-level suppression, and stakeholder alert are required.",
        )


def _classify_sdi(sdi: float) -> tuple[str, str]:
    """Returns (disruption_level, spread_risk_assessment)."""
    if sdi <= 20:
        return (
            "NEGLIGIBLE",
            "Societal impact probability is negligible. Content is unlikely to propagate beyond origin network.",
        )
    elif sdi <= 40:
        return (
            "LOW",
            "Content may achieve limited organic reach. Social disruption potential is below threshold for active response.",
        )
    elif sdi <= 60:
        return (
            "MODERATE",
            "Content carries moderate cross-platform spread risk. Polarization and echo-chamber seeding are possible.",
        )
    elif sdi <= 80:
        return (
            "HIGH",
            "Content exhibits high societal disruption potential. Viral amplification via high-arousal networks is probable.",
        )
    else:
        return (
            "SEVERE",
            "Content poses severe societal destabilization risk. Multi-platform cascade propagation is highly likely if unrestricted.",
        )


# ──────────────────────────────────────────────────────────────────────────────
# PPS Computation
# ──────────────────────────────────────────────────────────────────────────────

def compute_pps(
    deepfake_score: float,
    emotion_score: float,
    manipulation_score: float,
    virality_score: float,
    platform_multiplier: float = 1.0,
) -> Dict[str, Any]:
    """
    Weighted multi-signal PPS aggregation with controlled nonlinear escalation.
    platform_multiplier: minor boost for public social platform URLs (e.g. 1.05).
    """

    # Base weighted contributions
    df_contrib = 0.28 * deepfake_score
    ea_contrib = 0.30 * emotion_score
    mp_contrib = 0.27 * manipulation_score
    vr_contrib = 0.15 * virality_score

    base_score = df_contrib + ea_contrib + mp_contrib + vr_contrib

    # High-arousal nonlinear amplification
    arousal_factor = (emotion_score / 100.0) * (virality_score / 100.0)
    if arousal_factor > 0.30:
        base_score *= 1 + (arousal_factor * 0.22)

    # Multi-signal stacking escalation
    high_dims = sum(
        s > 65
        for s in [deepfake_score, emotion_score, manipulation_score, virality_score]
    )
    if high_dims >= 2:
        base_score *= 1 + (0.045 * high_dims)

    # Platform origin risk adjustment
    base_score *= platform_multiplier

    # Nonlinear normalization — soft ceiling prevents trivial saturation
    normalized = min(base_score / 100.0, 1.2)
    escalated  = normalized ** 1.08
    pps_score  = round(min(escalated * 100.0, 100.0), 2)

    threat_level, interpretation = _classify_pps(pps_score)

    return {
        "score": pps_score,
        "threat_level": threat_level,
        "interpretation": interpretation,
        "breakdown": {
            "deepfake_contribution":     round(df_contrib, 2),
            "emotion_contribution":      round(ea_contrib, 2),
            "manipulation_contribution": round(mp_contrib, 2),
            "virality_contribution":     round(vr_contrib, 2),
        },
        "interaction_effects": {
            "arousal_multiplier_applied": arousal_factor > 0.30,
            "high_dimension_count":       high_dims,
            "platform_multiplier":        round(platform_multiplier, 3),
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# SDI Computation
# ──────────────────────────────────────────────────────────────────────────────

def compute_sdi(pps_score: float, virality_score: float) -> Dict[str, Any]:
    sdi_score = round(pps_score * (virality_score / 100.0), 2)
    sdi_score = min(max(sdi_score, 0.0), 100.0)

    disruption_level, spread_risk_assessment = _classify_sdi(sdi_score)

    return {
        "sdi_score": sdi_score,
        "disruption_level": disruption_level,
        "spread_risk_assessment": spread_risk_assessment,
    }