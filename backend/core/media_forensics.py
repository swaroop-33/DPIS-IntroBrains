def build_explanation(
    deepfake_result:    Dict[str, Any],
    emotion_result:     Dict[str, Any],
    propaganda_result:  Dict[str, Any],
    virality_result:    Dict[str, Any],
    pps_result:         Dict[str, Any],
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
    raw_scores = emotion_result.get("raw_scores", {})
    dom_score = raw_scores.get(dominant, 0.0)

    top_signals.append(
        f"Dominant emotion: {dominant.upper()} ({dom_score:.2f}) "
        f"— EA score {emotion_result.get('amplification_score', 0.0):.1f}/100"
    )

    # ── Propaganda ──────────────────────────────────────
    mp_score = propaganda_result.get("manipulation_score", 0.0)
    triggers = propaganda_result.get("trigger_phrases", [])
    pattern_breakdown = propaganda_result.get("pattern_breakdown", {})

    top_signals.append(
        f"Propaganda score {mp_score:.1f}/100 — {len(triggers)} trigger phrase(s)"
    )

    for tp in triggers[:4]:
        top_signals.append(f"  ↳ Trigger: '{tp}'")

    # ── Virality ────────────────────────────────────────
    vr_score = virality_result.get("virality_score", 0.0)
    spread = virality_result.get("spread_probability", "Unknown")

    top_signals.append(
        f"Virality risk {vr_score:.1f}/100 — spread: {spread}"
    )

    if virality_result.get("multiplier_applied"):
        top_signals.append(
            f"  ↳ Multiplier applied: {virality_result.get('multiplier_reason')}"
        )

    # ── Summary ─────────────────────────────────────────
    pps = pps_result.get("score", 0.0)
    threat = pps_result.get("threat_level", "Unknown")

    summary = (
        f"This content scores {pps:.1f}/100 ({threat}). "
        f"Primary drivers: {dominant} amplification, "
        f"{len(triggers)} propaganda triggers, and "
        f"{spread.lower()} virality risk."
    )

    # ── Counterfactual (safe) ───────────────────────────
    df = df_score
    ea = emotion_result.get("amplification_score", 0.0)
    mp = mp_score
    vr = vr_score

    pps_no_urgency = round(pps * 0.85, 2)
    pps_no_fear = round(pps * 0.95, 2)

    impact_statement = (
        f"Removing urgency language would reduce PPS to {pps_no_urgency:.1f}. "
        f"Reducing fear intensity would reduce PPS to {pps_no_fear:.1f}."
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