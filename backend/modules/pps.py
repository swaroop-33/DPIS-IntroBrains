"""
DPIS — PPS Aggregator + Societal Disruption Index (v3.4)

MODE B: Nonlinear exponential convergence (req #8).
  escalation_factor = e^(α × convergence_score), α ∈ [0.32–0.40]

MODE C: Competitive differentiation fields — no artificial inflation.
  - dynamic_forensic_weight   : 0.28 → 0.45–0.55 when media authenticity is high
  - delta_pps                 : % PPS uplift attributable to convergence factor
  - escalation_driver         : dominant threat dimension label
  - severity_badge            : 5-tier color-coded label (same bands as threat_level)

Threat bands: 0-20 LOW | 21-40 ELEVATED | 41-60 MODERATE | 61-80 HIGH | 81-100 CRITICAL
"""

import math
from typing import Dict, Any, Optional


# ── Threat / Severity classification ──────────────────────────────────────────

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


# Severity badge: identical bands, adds color tier for frontend rendering
_SEVERITY_COLORS = {
    "LOW":      "#22c55e",   # green
    "ELEVATED": "#eab308",   # amber
    "MODERATE": "#f97316",   # orange
    "HIGH":     "#ef4444",   # red
    "CRITICAL": "#7c3aed",   # violet
}


def _severity_badge(pps_score: float) -> Dict[str, str]:
    level, _ = _classify_pps(pps_score)
    return {
        "label": level,
        "color": _SEVERITY_COLORS[level],
    }


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
_CONVERGENCE_ALPHA     = 0.38   # tuning constant: e^(α × score)

def _exponential_convergence_factor(
    deepfake: float, emotion: float, manipulation: float, virality: float
) -> tuple[float, int, float]:
    """
    Computes exponential escalation factor from convergent high-risk dimensions.

    Returns (factor, high_dim_count, convergence_score).
    factor > 1.0 → PPS is amplified exponentially above baseline.

    At 2 fully-maxed dims: factor ≈ 1.46
    At 4 fully-maxed dims: factor ≈ 2.13 (hard-capped at 2.20)
    """
    dims = [deepfake, emotion, manipulation, virality]
    high_dims      = [d for d in dims if d > _CONVERGENCE_THRESHOLD]
    high_dim_count = len(high_dims)

    if high_dim_count < 2:
        return 1.0, high_dim_count, 0.0

    excess_sum = sum(
        (d - _CONVERGENCE_THRESHOLD) / (100.0 - _CONVERGENCE_THRESHOLD)
        for d in high_dims
    )

    raw_factor = math.exp(_CONVERGENCE_ALPHA * excess_sum)
    factor     = min(raw_factor, 2.20)     # hard cap per spec

    return factor, high_dim_count, round(excess_sum, 3)


# ── Dynamic forensic weight (Mode C) ─────────────────────────────────────────

_DF_WEIGHT_BASE  = 0.28   # baseline forensic weight
_DF_WEIGHT_MAX   = 0.50   # ceiling when blended_authenticity = 100%
_DF_THRESHOLD    = 50.0   # authenticity score above which dynamic upweight begins


def _dynamic_forensic_weight(blended_authenticity: float) -> float:
    """
    Mode C — Req 1: Increase forensic contribution weight when media
    authenticity evidence is strong (blended_authenticity > 50%).

    Returns forensic weight in [0.28, 0.50].
    Linearly interpolated from base to max as authenticity goes 50→100%.
    Scientifically defensible: high forensic confidence justifies higher weight.
    """
    if blended_authenticity <= _DF_THRESHOLD:
        return _DF_WEIGHT_BASE
    frac = min((blended_authenticity - _DF_THRESHOLD) / (100.0 - _DF_THRESHOLD), 1.0)
    return round(_DF_WEIGHT_BASE + frac * (_DF_WEIGHT_MAX - _DF_WEIGHT_BASE), 4)


# ── Escalation driver (Mode C) ────────────────────────────────────────────────

def _identify_escalation_driver(
    deepfake_score: float,
    emotion_score: float,
    manipulation_score: float,
    virality_score: float,
    evasion_score: float,
    platform_multiplier: float,
) -> str:
    """
    Identifies the dominant driver of PPS elevation.
    Uses a composite signal: raw score + presence-of-threshold bonus.
    """
    candidates = {
        "Media Authenticity":     deepfake_score * 1.1 if deepfake_score > _CONVERGENCE_THRESHOLD else deepfake_score,
        "Emotional Convergence":  emotion_score  * 1.1 if emotion_score  > _CONVERGENCE_THRESHOLD else emotion_score,
        "Manipulation Stack":     manipulation_score,
        "Platform Amplification": (platform_multiplier - 1.0) * 200.0,  # normalise to 0-50 range
        "Adversarial Evasion":    evasion_score,
    }
    return max(candidates, key=candidates.__getitem__)


# ── PPS computation ────────────────────────────────────────────────────────────

def compute_pps(
    deepfake_score:        float,
    emotion_score:         float,
    manipulation_score:    float,
    virality_score:        float,
    platform_multiplier:   float = 1.0,
    blended_authenticity:  float = 0.0,   # MODE C: drives dynamic forensic weight
    evasion_score:         float = 0.0,   # MODE C: escalation_driver input
) -> Dict[str, Any]:
    """
    Multi-signal PPS with:
    - True exponential convergence escalation (Mode B, req #8)
    - Dynamic forensic weight based on media evidence strength (Mode C, req 1)
    - ΔPPS indicator showing convergence uplift % (Mode C, req 5)
    - Escalation driver field (Mode C, req 4)
    - Severity badge (Mode C, req 3)
    """

    # ── Dynamic forensic weight ────────────────────────────────────────────────
    df_weight = _dynamic_forensic_weight(blended_authenticity)
    # Redistribute remaining weight pro-rata to other dims
    remaining = 1.0 - df_weight
    ea_weight = round(0.30 * remaining / 0.72, 4)   # original share = 30/72
    mp_weight = round(0.27 * remaining / 0.72, 4)
    vr_weight = round(1.0 - df_weight - ea_weight - mp_weight, 4)

    df_contrib = df_weight * deepfake_score
    ea_contrib = ea_weight * emotion_score
    mp_contrib = mp_weight * manipulation_score
    vr_contrib = vr_weight * virality_score
    base_score = df_contrib + ea_contrib + mp_contrib + vr_contrib

    # Arousal × virality synergy (high-arousal + high-spread = max propagation)
    arousal_factor = (emotion_score / 100.0) * (virality_score / 100.0)
    if arousal_factor > 0.30:
        base_score *= 1.0 + (arousal_factor * 0.22)

    # ── Baseline (pre-convergence) PPS for ΔPPS ───────────────────────────────
    pre_convergence_score = min(base_score * platform_multiplier / 100.0, 1.25) ** 1.06 * 100.0
    pre_convergence_score = round(min(pre_convergence_score, 100.0), 2)

    # ── Exponential convergence escalation (Mode B, req #8) ───────────────────
    conv_factor, high_dim_count, convergence_score = _exponential_convergence_factor(
        deepfake_score, emotion_score, manipulation_score, virality_score
    )
    base_score *= conv_factor

    # Platform amplification
    base_score *= platform_multiplier

    # Nonlinear normalization
    normalized = min(base_score / 100.0, 1.25)
    escalated  = normalized ** 1.06
    pps_score  = round(min(escalated * 100.0, 100.0), 2)

    # ── ΔPPS — convergence uplift (Mode C, req 5) ─────────────────────────────
    if pre_convergence_score > 0:
        delta_pps_pct = round(((pps_score - pre_convergence_score) / pre_convergence_score) * 100.0, 1)
    else:
        delta_pps_pct = 0.0

    threat_level, interpretation = _classify_pps(pps_score)

    # ── Escalation driver (Mode C, req 4) ─────────────────────────────────────
    escalation_driver = _identify_escalation_driver(
        deepfake_score, emotion_score, manipulation_score,
        virality_score, evasion_score, platform_multiplier,
    )

    return {
        "score":         pps_score,
        "threat_level":  threat_level,
        "interpretation": interpretation,

        # Mode C — severity badge
        "severity_badge": _severity_badge(pps_score),

        "breakdown": {
            "deepfake_contribution":     round(df_contrib, 2),
            "emotion_contribution":      round(ea_contrib, 2),
            "manipulation_contribution": round(mp_contrib, 2),
            "virality_contribution":     round(vr_contrib, 2),
            "forensic_weight_applied":   round(df_weight, 4),
        },
        "interaction_effects": {
            "arousal_virality_synergy":   round(arousal_factor, 3),
            "arousal_multiplier_applied": arousal_factor > 0.30,
            "convergence_factor":         round(conv_factor, 3),
            "convergence_score":          convergence_score,
            "high_dimension_count":       high_dim_count,
            "platform_multiplier":        round(platform_multiplier, 3),

            # Mode C fields
            "delta_pps_pct":              delta_pps_pct,
            "escalation_driver":          escalation_driver,
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