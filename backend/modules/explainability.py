"""
DPIS — Explainability Engine (v3.0)

Upgrades:
• Supports density-based emotion output
• Includes PDI-aware messaging
• Reflects interaction effects from PPS
• Stronger counterfactual modeling
• Safe against missing keys
"""

from typing import Dict, Any, List


def build_explanation(
    deepfake_result: Dict[str, Any],
    emotion_result: Dict[str, Any],
    propaganda_result: Dict[str, Any],
    virality_result: Dict[str, Any],
    pps_result: Dict[str, Any],
) -> Dict[str, Any]:

    top_signals: List[str] = []

    # ── Deepfake ─────────────────────────────────────────
    df_score = deepfake_result.get("final_deepfake_score", 0.0)
    model_conf = deepfake_result.get("model_confidence", 0.0)
    anomaly = deepfake_result.get("anomaly_score", 0.0)

    top_signals.append(
        f"Deepfake score {df_score:.1f}/100 "
        f"(model_confidence={model_conf:.1f}, anomaly={anomaly:.1f})"
    )

    for sig in deepfake_result.get("signals", [])[:2]:
        top_signals.append(f"  ↳ {sig}")

    # ── Emotion ─────────────────────────────────────────
    dominant = emotion_result.get("dominant_emotion", "neutral")
    density_scores = emotion_result.get("density_scores", {})
    dom_score = density_scores.get(dominant, 0.0)

    top_signals.append(
        f"Dominant emotion: {dominant.upper()} "
        f"(density={dom_score:.2f}) — EA score "
        f"{emotion_result.get('amplification_score', 0.0):.1f}/100"
    )

    if emotion_result.get("stacking_bonus_applied", 0) > 0:
        top_signals.append(
            f"  ↳ Emotional stacking boost applied "
            f"(+{emotion_result.get('stacking_bonus_applied'):.2f})"
        )

    # ── Propaganda ──────────────────────────────────────
    mp_score = propaganda_result.get("manipulation_score", 0.0)
    triggers = propaganda_result.get("trigger_phrases", [])
    category_breakdown = propaganda_result.get("pattern_breakdown", {})

    active_categories = sum(1 for v in category_breakdown.values() if v > 0)

    top_signals.append(
        f"Propaganda score {mp_score:.1f}/100 — "
        f"{len(triggers)} trigger phrase(s), "
        f"{active_categories} active manipulation categories"
    )

    for tp in triggers[:4]:
        top_signals.append(f"  ↳ Trigger: '{tp}'")

    # ── Virality ────────────────────────────────────────
    vr_score = virality_result.get("virality_score", 0.0)
    spread = virality_result.get("spread_probability", "Unknown")

    top_signals.append(
        f"Virality risk {vr_score:.1f}/100 — spread probability: {spread}"
    )

    if virality_result.get("multiplier_applied"):
        top_signals.append(
            f"  ↳ High-arousal multiplier: "
            f"{virality_result.get('multiplier_reason')}"
        )

    # ── PPS Interaction Effects ─────────────────────────
    interaction_effects = pps_result.get("interaction_effects", {})
    high_dims = interaction_effects.get("high_dimension_count", 0)

    if high_dims >= 2:
        top_signals.append(
            f"  ↳ Cross-signal escalation: {high_dims} high-risk dimensions stacked"
        )

    # ── Summary ─────────────────────────────────────────
    pps = pps_result.get("score", 0.0)
    threat = pps_result.get("threat_level", "Unknown")

    summary = (
        f"This content scores {pps:.1f}/100 ({threat}). "
        f"Primary drivers: {dominant} activation, "
        f"{active_categories} manipulation categories, "
        f"and {spread.lower()} virality amplification."
    )

    # ── Counterfactual Analysis ─────────────────────────
    # Remove urgency effect
    urgency_density = density_scores.get("urgency", 0.0)
    pps_no_urgency = round(pps * (1 - (urgency_density * 0.15)), 2)

    # Reduce fear by 50%
    fear_density = density_scores.get("fear", 0.0)
    pps_no_fear = round(pps * (1 - (fear_density * 0.10)), 2)

    impact_statement = (
        f"Reducing urgency intensity lowers PPS to {pps_no_urgency:.1f}. "
        f"Reducing fear activation lowers PPS to {pps_no_fear:.1f}."
    )

    return {
        "summary": summary,
        "top_signals": top_signals,
        "counterfactual_analysis": {
            "pps_without_urgency": pps_no_urgency,
            "pps_without_fear": pps_no_fear,
            "impact_statement": impact_statement,
        },
    }