"""
DPIS — Calibration & Confidence Engine (v3.3)

Computes:
  • data_quality_score — based on input length, richness, media presence
  • confidence_band — LOW / MODERATE / HIGH
  • confidence_interval — [lower, upper] around PPS
  • calibration_notes — list of factors affecting confidence
"""

from typing import Dict, Any, List


def compute_calibration(
    text: str,
    pps_score: float,
    has_media: bool = False,
    evasion_score: float = 0.0,
    input_type: str = "text",
) -> Dict[str, Any]:

    notes: List[str] = []
    quality = 100.0

    # ── Text length ───────────────────────────────────────────────────────────
    word_count = len(text.split())
    if word_count < 10:
        quality -= 30.0
        notes.append(
            f"Short input ({word_count} tokens) — limited signal extraction; "
            "confidence band widened."
        )
    elif word_count < 30:
        quality -= 15.0
        notes.append(f"Moderate input length ({word_count} tokens) — acceptable signal density.")
    else:
        notes.append(f"Sufficient input length ({word_count} tokens) — high lexical signal coverage.")

    # ── Media presence ────────────────────────────────────────────────────────
    if has_media:
        quality = min(quality + 8.0, 100.0)
        notes.append("Multi-modal media input detected — forensic signals augment confidence.")
    else:
        quality -= 5.0
        notes.append("Text-only input — forensic layer operates on lexical heuristics only.")

    # ── Evasion penalty ───────────────────────────────────────────────────────
    if evasion_score > 30.0:
        quality -= 20.0
        notes.append(
            f"Adversarial obfuscation detected (evasion_score={evasion_score:.1f}) — "
            "PPS may underestimate true manipulation intent. Confidence band widened."
        )
    elif evasion_score > 10.0:
        quality -= 8.0
        notes.append(
            f"Minor obfuscation signals present (evasion_score={evasion_score:.1f})."
        )

    quality = round(max(0.0, min(quality, 100.0)), 2)

    # ── Confidence band ───────────────────────────────────────────────────────
    if quality >= 75:
        band = "HIGH"
        half_width = 5.0
    elif quality >= 50:
        band = "MODERATE"
        half_width = 10.0
    else:
        band = "LOW"
        half_width = 18.0

    lower = round(max(pps_score - half_width, 0.0), 2)
    upper = round(min(pps_score + half_width, 100.0), 2)

    return {
        "data_quality_score": quality,
        "confidence_band":    band,
        "confidence_interval": {"lower": lower, "upper": upper},
        "calibration_notes":  notes,
    }
