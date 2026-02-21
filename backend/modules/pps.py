"""
DPIS — PPS Aggregator + Societal Disruption Index (v3.3)

Req #8: Nonlinear interaction escalation — exponential convergence.
  When multiple dimensions simultaneously exceed thresholds, the combined
  risk is modeled as an exponential function of convergence depth, not
  linear stacking.

  Mathematical model:
    convergence_score = Σ (dim_i / 100) for high-risk dims
    escalation_factor = e^(α × convergence_score) — true exponential

  where α is calibrated to ensure realistic ceiling behavior.

Threat bands: 0-20 LOW | 21-40 ELEVATED | 41-60 MODERATE | 61-80 HIGH | 81-100 CRITICAL
"""

import math
from typing import Dict, Any


# ── Threat classification ──────────────────────────────────────────────────────

def _classify_pps(score: float) -> tuple[str, str]:
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


# ── Exponential convergence escalation ────────────────────────────────────────

_CONVERGENCE_THRESHOLD = 62.0   # score above which a dimension is "high risk"
_CONVERGENCE_ALPHA     = 0.38   # tuning constant for e^(α × score)

def _exponential_convergence_factor(
    deepfake: float, emotion: float, manipulation: float, virality: float
) -> tuple[float, int, float]:
    """
    Computes exponential escalation factor from convergent high-risk dimensions.

    Returns (factor, high_dim_count, convergence_score).
    factor > 1.0 → PPS is amplified exponentially.
    """
    dims = [deepfake, emotion, manipulation, virality]
    high_dims     = [d for d in dims if d > _CONVERGENCE_THRESHOLD]
    high_dim_count = len(high_dims)

    if high_dim_count < 2:
        return 1.0, high_dim_count, 0.0

    # Convergence score: normalized sum of excess above threshold
    excess_sum = sum((d - _CONVERGENCE_THRESHOLD) / (100.0 - _CONVERGENCE_THRESHOLD)
                     for d in high_dims)

    # True exponential: e^(α × excess_sum)
    # α = 0.38 → at 2 fully-maxed dims, factor ≈ 1.46; at 4 dims ≈ 2.13 (capped)
    raw_factor = math.exp(_CONVERGENCE_ALPHA * excess_sum)

    # Soft cap at 2.2× to prevent unrealistic saturation (scores still reach 100)
    factor = min(raw_factor, 2.20)

    return factor, high_dim_count, round(excess_sum, 3)


# ── PPS computation ────────────────────────────────────────────────────────────

def compute_pps(
    deepfake_score:    float,
    emotion_score:     float,
    manipulation_score: float,
    virality_score:    float,
    platform_multiplier: float = 1.0,
) -> Dict[str, Any]:
    """
    Multi-signal PPS with true exponential convergence escalation (req #8).
    platform_multiplier: from platform_amp module (1.00–1.22).
    """

    # Base weighted contributions
    df_contrib = 0.28 * deepfake_score
    ea_contrib = 0.30 * emotion_score
    mp_contrib = 0.27 * manipulation_score
    vr_contrib = 0.15 * virality_score
    base_score = df_contrib + ea_contrib + mp_contrib + vr_contrib

    # Arousal × virality synergy (high-arousal + high-spread = max propagation multiplier)
    arousal_factor = (emotion_score / 100.0) * (virality_score / 100.0)
    if arousal_factor > 0.30:
        base_score *= 1.0 + (arousal_factor * 0.22)

    # Exponential convergence escalation (req #8)
    conv_factor, high_dim_count, convergence_score = _exponential_convergence_factor(
        deepfake_score, emotion_score, manipulation_score, virality_score
    )
    base_score *= conv_factor

    # Platform amplification
    base_score *= platform_multiplier

    # Nonlinear normalization
    normalized = min(base_score / 100.0, 1.25)
    escalated  = normalized ** 1.06     # mild final lift, doesn't reset exponential gains
    pps_score  = round(min(escalated * 100.0, 100.0), 2)

    threat_level, interpretation = _classify_pps(pps_score)

    return {
        "score":         pps_score,
        "threat_level":  threat_level,
        "interpretation": interpretation,
        "breakdown": {
            "deepfake_contribution":     round(df_contrib, 2),
            "emotion_contribution":      round(ea_contrib, 2),
            "manipulation_contribution": round(mp_contrib, 2),
            "virality_contribution":     round(vr_contrib, 2),
        },
        "interaction_effects": {
            "arousal_virality_synergy":  round(arousal_factor, 3),
            "arousal_multiplier_applied": arousal_factor > 0.30,
            "convergence_factor":        round(conv_factor, 3),
            "convergence_score":         convergence_score,
            "high_dimension_count":      high_dim_count,
            "platform_multiplier":       round(platform_multiplier, 3),
        },
    }


# ── SDI computation ────────────────────────────────────────────────────────────

def compute_sdi(pps_score: float, virality_score: float) -> Dict[str, Any]:
    sdi_score = round(pps_score * (virality_score / 100.0), 2)
    sdi_score = min(max(sdi_score, 0.0), 100.0)

    disruption_level, spread_risk_assessment = _classify_sdi(sdi_score)

    return {
        "sdi_score":              sdi_score,
        "disruption_level":       disruption_level,
        "spread_risk_assessment": spread_risk_assessment,
    }