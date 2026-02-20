"""
DPIS — Virality Risk Estimation Module (v3.2)

Additions:
• target_vulnerability_group — demographic / behavioral segment most at risk
• Controlled nonlinear scaling, no ceiling saturation
"""

from typing import Dict, Any, Optional


_VULNERABILITY_MAP = [
    # (ea_threshold, mp_threshold, pi_threshold, group_label)
    (0.70, 0.70, 0.60, "Highly-polarized partisan communities with pre-existing confirmation bias"),
    (0.65, 0.50, 0.70, "Ideologically homogeneous echo chambers with low cross-exposure media diets"),
    (0.70, 0.40, 0.40, "Emotionally primed audiences during high-salience news cycles"),
    (0.50, 0.70, 0.40, "Low media-literacy demographics susceptible to authority-exploitation framing"),
    (0.50, 0.50, 0.50, "General social media users with moderate emotional reactivity"),
]


def _infer_vulnerability_group(ea: float, mp: float, pi: float) -> str:
    for ea_t, mp_t, pi_t, label in _VULNERABILITY_MAP:
        if ea >= ea_t and mp >= mp_t and pi >= pi_t:
            return label
    return "Broad general audience — no specific high-risk demographic cluster identified"


def estimate_virality(
    emotional_amplification: float,   # 0–100
    manipulation_score: float,        # 0–100
    polarization_intensity: float,    # 0–1
    fear_score: float,                # 0–1
    anger_score: float,               # 0–1
) -> Dict[str, Any]:

    ea = emotional_amplification / 100.0
    mp = manipulation_score / 100.0
    pi = polarization_intensity

    # Echo-chamber effect
    polarized = pi ** 1.2

    # Base weighted formula
    base = (
        (0.50 * ea) +
        (0.28 * mp) +
        (0.32 * polarized)
    )
    base = min(base, 1.2)
    base = base ** 1.08

    # Stacking escalation
    stacking_bonus = 0.0
    if ea > 0.6 and mp > 0.6:
        stacking_bonus += 0.06
    if mp > 0.6 and pi > 0.5:
        stacking_bonus += 0.06
    if ea > 0.6 and pi > 0.5:
        stacking_bonus += 0.05

    # High-arousal multiplier
    multiplier_applied = False
    multiplier_reason: Optional[str] = None

    if fear_score > 0.65 and anger_score > 0.65:
        base *= 1.20
        multiplier_applied = True
        multiplier_reason = "Fear + Anger dual-activation — maximum arousal propagation pathway"
    elif fear_score > 0.65:
        base *= 1.15
        multiplier_applied = True
        multiplier_reason = "High fear activation — threat-salience increases share impulse"
    elif anger_score > 0.65:
        base *= 1.15
        multiplier_applied = True
        multiplier_reason = "High anger activation — moral outrage drives amplification behavior"

    vr_final = min(base + stacking_bonus, 1.0)
    vr_score = round(vr_final * 100, 2)

    if vr_score < 21:
        spread = "LOW"
    elif vr_score < 41:
        spread = "ELEVATED"
    elif vr_score < 61:
        spread = "MODERATE"
    elif vr_score < 81:
        spread = "HIGH"
    else:
        spread = "CRITICAL"

    target_group = _infer_vulnerability_group(ea, mp, pi)

    return {
        "virality_score":           vr_score,
        "spread_probability":       spread,
        "target_vulnerability_group": target_group,
        "multiplier_applied":       multiplier_applied,
        "multiplier_reason":        multiplier_reason,
        "component_breakdown": {
            "emotional_component":     round(0.50 * ea * 100, 2),
            "manipulation_component":  round(0.28 * mp * 100, 2),
            "polarization_component":  round(0.32 * polarized * 100, 2),
        },
    }