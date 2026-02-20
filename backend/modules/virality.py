"""
DPIS — Virality Risk Estimation Module (Calibrated Stable)

Balanced nonlinear scaling.
No ceiling saturation.
Strong but controlled stacking.
"""

from typing import Dict, Any


def estimate_virality(
    emotional_amplification: float,    # 0–100
    manipulation_score: float,         # 0–100
    polarization_intensity: float,     # 0–1
    fear_score: float,                 # 0–1
    anger_score: float,                # 0–1
) -> Dict[str, Any]:

    ea = emotional_amplification / 100.0
    mp = manipulation_score / 100.0
    pi = polarization_intensity

    # Echo-chamber effect (softened)
    polarized = pi ** 1.2

    # Base weighted formula (rebalanced)
    base = (
        (0.50 * ea) +
        (0.28 * mp) +
        (0.32 * polarized)
    )

    # Prevent runaway base inflation
    base = min(base, 1.2)

    # Controlled nonlinear lift
    base = base ** 1.08

    # Stacking escalation (reduced)
    stacking_bonus = 0.0

    if ea > 0.6 and mp > 0.6:
        stacking_bonus += 0.06

    if mp > 0.6 and pi > 0.5:
        stacking_bonus += 0.06

    if ea > 0.6 and pi > 0.5:
        stacking_bonus += 0.05

    # High-arousal multiplier (reduced intensity)
    multiplier_applied = False
    multiplier_reason = None

    if fear_score > 0.65 and anger_score > 0.65:
        base *= 1.20
        multiplier_applied = True
        multiplier_reason = "Fear + Anger dual activation"

    elif fear_score > 0.65:
        base *= 1.15
        multiplier_applied = True
        multiplier_reason = "High fear activation"

    elif anger_score > 0.65:
        base *= 1.15
        multiplier_applied = True
        multiplier_reason = "High anger activation"

    # Final score
    vr_final = min(base + stacking_bonus, 1.0)
    vr_score = round(vr_final * 100, 2)

    if vr_score < 30:
        spread = "Low"
    elif vr_score < 65:
        spread = "Medium"
    else:
        spread = "High"

    return {
        "virality_score": vr_score,
        "multiplier_applied": multiplier_applied,
        "multiplier_reason": multiplier_reason,
        "spread_probability": spread,
        "component_breakdown": {
            "emotional_component": round(0.50 * ea * 100, 2),
            "manipulation_component": round(0.28 * mp * 100, 2),
            "polarization_component": round(0.32 * polarized * 100, 2),
            "echo_chamber_scaled": round(polarized, 3),
        },
    }