"""
DPIS — Explainability Engine (v3.2)

Additions:
• Counterfactual Stability Analysis: stability_score + recommended_intervention
• Professional intelligence-tier language throughout
• No emojis, no casual tone
"""

from typing import Dict, Any, List


def _stability_score(pps: float, urgency_density: float, fear_density: float) -> float:
    """
    Counterfactual Stability Score (0–100).
    High score = content PPS is ROBUST to single-signal removal (harder to counter).
    Low score  = content PPS collapses if key emotional driver is neutralized.
    Derived from the gap between original PPS and counterfactual PPS values.
    """
    pps_no_urgency = pps * (1 - (urgency_density * 0.15))
    pps_no_fear    = pps * (1 - (fear_density * 0.10))

    max_reduction = max(pps - pps_no_urgency, pps - pps_no_fear)

    if pps == 0:
        return 0.0

    # Stability inversely proportional to how much PPS drops when one signal removed
    fragility = max_reduction / max(pps, 1.0)
    stability = round((1 - fragility) * 100, 2)
    return max(0.0, min(stability, 100.0))


def _recommended_intervention(pps: float, spread: str, dominant_emotion: str) -> str:
    """Generate intervention recommendation based on threat profile."""
    spread_upper = spread.upper()
    base = ""

    if pps >= 81:
        base = (
            "Immediate escalation to platform trust-and-safety and relevant authorities. "
            "Apply content suppression or demotion. Deploy targeted counter-narrative to primary "
            "distribution nodes within 2 hours."
        )
    elif pps >= 61:
        base = (
            "Initiate platform-level flagging and independent fact-check referral. "
            "Monitor cross-platform propagation vectors. Prepare counter-narrative assets."
        )
    elif pps >= 41:
        base = (
            "Apply context labels and source attribution review. "
            "Strengthen algorithmic demotion in recommendation systems. Monitor virality trend."
        )
    elif pps >= 21:
        base = (
            "Log for trend analysis. No immediate intervention required. "
            "Review if cross-posted to high-risk communities."
        )
    else:
        base = "No intervention required. Standard content moderation workflow applies."

    emotion_note = ""
    if dominant_emotion in ("fear", "anger", "outrage"):
        emotion_note = (
            f" Priority target: neutralize {dominant_emotion.upper()} activation vector "
            "through prebunking or inoculation messaging."
        )

    return base + emotion_note


def build_explanation(
    deepfake_result:   Dict[str, Any],
    emotion_result:    Dict[str, Any],
    propaganda_result: Dict[str, Any],
    virality_result:   Dict[str, Any],
    pps_result:        Dict[str, Any],
) -> Dict[str, Any]:

    top_signals: List[str] = []

    # ── Deepfake ──────────────────────────────────────────────────────────────
    df_score   = deepfake_result.get("final_deepfake_score", 0.0)
    model_conf = deepfake_result.get("model_confidence", 0.0)
    anomaly    = deepfake_result.get("anomaly_score", 0.0)

    top_signals.append(
        f"Deepfake probability {df_score:.1f}/100 "
        f"(model_confidence={model_conf:.1f}, anomaly_score={anomaly:.1f})"
    )
    for sig in deepfake_result.get("signals", [])[:2]:
        top_signals.append(f"  → {sig}")

    # ── Emotion ────────────────────────────────────────────────────────────────
    dominant      = emotion_result.get("dominant_emotion", "neutral")
    density_scores = emotion_result.get("density_scores", {})
    dom_score     = density_scores.get(dominant, 0.0)

    top_signals.append(
        f"Dominant affect: {dominant.upper()} "
        f"(density={dom_score:.2f}) — "
        f"amplification score {emotion_result.get('amplification_score', 0.0):.1f}/100"
    )
    if emotion_result.get("stacking_bonus_applied", 0) > 0:
        top_signals.append(
            f"  → Multi-affect stacking bonus applied "
            f"(+{emotion_result.get('stacking_bonus_applied'):.2f})"
        )

    # ── Propaganda ────────────────────────────────────────────────────────────
    mp_score = propaganda_result.get("manipulation_score", 0.0)
    triggers = propaganda_result.get("trigger_phrases_detected", propaganda_result.get("trigger_phrases", []))
    techniques = propaganda_result.get("persuasion_techniques_detected", [])

    top_signals.append(
        f"Manipulation score {mp_score:.1f}/100 — "
        f"{len(triggers)} trigger phrase(s) across "
        f"{len(techniques)} active persuasion technique category/categories"
    )
    for tp in triggers[:4]:
        top_signals.append(f"  → Trigger phrase: '{tp}'")

    # ── Virality ──────────────────────────────────────────────────────────────
    vr_score = virality_result.get("virality_score", 0.0)
    spread   = virality_result.get("spread_probability", "UNKNOWN")

    top_signals.append(
        f"Virality index {vr_score:.1f}/100 — spread classification: {spread}"
    )
    if virality_result.get("multiplier_applied"):
        top_signals.append(
            f"  → High-arousal multiplier active: "
            f"{virality_result.get('multiplier_reason', '')}"
        )

    # ── Cross-signal interaction ───────────────────────────────────────────────
    interaction_effects = pps_result.get("interaction_effects", {})
    high_dims = interaction_effects.get("high_dimension_count", 0)
    if high_dims >= 2:
        top_signals.append(
            f"  → Cross-signal escalation: {high_dims} dimensions above risk threshold — "
            f"nonlinear PPS amplification applied"
        )

    # ── Summary ───────────────────────────────────────────────────────────────
    pps     = pps_result.get("score", 0.0)
    threat  = pps_result.get("threat_level", "UNKNOWN")
    active_cats = len(techniques)

    summary = (
        f"Threat classification: {threat} (PPS {pps:.1f}/100). "
        f"Primary manipulation vectors: {dominant.lower()} affect activation, "
        f"{active_cats} propaganda technique(s), "
        f"and {spread.lower()} virality amplification potential."
    )

    # ── Counterfactual Stability Analysis ──────────────────────────────────────
    urgency_density = density_scores.get("urgency", 0.0)
    fear_density    = density_scores.get("fear", 0.0)

    pps_no_urgency = round(pps * (1 - (urgency_density * 0.15)), 2)
    pps_no_fear    = round(pps * (1 - (fear_density * 0.10)), 2)

    stability = _stability_score(pps, urgency_density, fear_density)
    intervention = _recommended_intervention(pps, spread, dominant)

    impact_statement = (
        f"Removing urgency signals reduces PPS to {pps_no_urgency:.1f} "
        f"(delta: {pps - pps_no_urgency:.1f} points). "
        f"Neutralizing fear activation reduces PPS to {pps_no_fear:.1f} "
        f"(delta: {pps - pps_no_fear:.1f} points)."
    )

    return {
        "summary": summary,
        "top_signals": top_signals,
        "counterfactual_analysis": {
            "stability_score":         stability,
            "pps_without_urgency":     pps_no_urgency,
            "pps_without_fear":        pps_no_fear,
            "impact_statement":        impact_statement,
            "recommended_intervention": intervention,
        },
    }