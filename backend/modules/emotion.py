"""
DPIS — Emotional Arousal Density & Amplification Module (v3.3)

Req #2: Quantify emotional arousal density and amplification.

Computes:
  • Per-affect density scores (fear, anger, urgency, shock, sadness, outrage)
  • Arousal density index (ADenI) — normalized composite arousal level
  • High-arousal stacking amplification with nonlinear escalation
  • Cross-affect interference model (fear × anger = maximum propagation pathway)
"""

import re
from typing import Dict, Any

# ── Affect keyword banks ───────────────────────────────────────────────────────

FEAR_KEYWORDS = [
    "danger", "threat", "risk", "warning", "scared",
    "terrified", "panic", "afraid", "deadly", "crisis",
    "lethal", "catastrophic", "survive", "imminent",
]

ANGER_KEYWORDS = [
    "outrage", "furious", "disgusted", "unacceptable",
    "corrupt", "lies", "betrayal", "angry", "rage",
    "injustice", "criminals", "evil", "traitors",
]

URGENCY_KEYWORDS = [
    "now", "immediately", "urgent", "hurry",
    "before it's too late", "act fast", "share now",
    "breaking", "critical", "alert", "last chance",
]

SHOCK_KEYWORDS = [
    "unbelievable", "shocking", "exposed", "secret",
    "hidden", "cover-up", "scandal", "bombshell", "leaked",
    "classified", "what they don't want", "suppressed",
]

SADNESS_KEYWORDS = [
    "tragedy", "devastating", "heartbreaking", "suffering",
    "victims", "loss", "mourn", "grief", "desperate", "hopeless",
]

OUTRAGE_KEYWORDS = [
    "censored", "banned", "silenced", "erased", "suppressed",
    "they are hiding", "wake up", "resist", "fight back", "stand up",
]


def _count_occurrences(text: str, keywords: list) -> int:
    count = 0
    for kw in keywords:
        count += len(re.findall(r"\b" + re.escape(kw) + r"\b", text))
    return count


def analyze_emotion(text: str) -> Dict[str, Any]:

    text_lower = text.lower()
    tokens     = max(len(text_lower.split()), 1)

    # ── Per-affect raw counts ─────────────────────────────────────────────────
    fear_count    = _count_occurrences(text_lower, FEAR_KEYWORDS)
    anger_count   = _count_occurrences(text_lower, ANGER_KEYWORDS)
    urgency_count = _count_occurrences(text_lower, URGENCY_KEYWORDS)
    shock_count   = _count_occurrences(text_lower, SHOCK_KEYWORDS)
    sadness_count = _count_occurrences(text_lower, SADNESS_KEYWORDS)
    outrage_count = _count_occurrences(text_lower, OUTRAGE_KEYWORDS)

    # ── Emotional arousal density (per 100 tokens) ────────────────────────────
    def _density(count: int) -> float:
        return min((count / tokens) * 100, 1.0)

    fear_d    = _density(fear_count)
    anger_d   = _density(anger_count)
    urgency_d = _density(urgency_count)
    shock_d   = _density(shock_count)
    sadness_d = _density(sadness_count)
    outrage_d = _density(outrage_count)

    # ── Base weighted arousal ─────────────────────────────────────────────────
    ea_raw = (
        (0.30 * fear_d) +
        (0.25 * anger_d) +
        (0.18 * urgency_d) +
        (0.12 * shock_d) +
        (0.08 * sadness_d) +
        (0.07 * outrage_d)
    )

    # ── High-arousal stacking amplification (req #8: nonlinear convergence) ───
    # Each co-active pair adds a multiplicative boost
    # Fear × Anger: maximum propagation pathway (documented in behavioral research)
    stacking_bonus = 0.0

    if fear_count > 0 and anger_count > 0:
        # Nonlinear cross-amplification — synergistic arousal pathway
        synergy = (fear_d * anger_d) ** 0.5   # geometric mean of two affect densities
        stacking_bonus += 0.15 + (synergy * 0.20)

    if urgency_count > 0 and fear_count > 0:
        stacking_bonus += 0.10

    if shock_count > 0 and urgency_count > 0:
        stacking_bonus += 0.08

    if outrage_count > 0 and anger_count > 0:
        stacking_bonus += 0.07

    # Triple-affect convergence: fear + anger + urgency = exponential escalation
    if fear_count > 0 and anger_count > 0 and urgency_count > 0:
        stacking_bonus += 0.15  # additional jump for 3-affect convergence

    ea_raw = ea_raw * (1.0 + stacking_bonus)

    # ── Short-text volatility boost (social media density inflation) ──────────
    if tokens < 80:
        ea_raw *= 1.12

    # ── Nonlinear escalation — top-heavy (req #8) ─────────────────────────────
    ea_normalized = min(ea_raw, 1.0)
    ea_score      = round((ea_normalized ** 1.18) * 100, 2)
    ea_score      = min(ea_score, 100.0)

    # ── Dominant affect ───────────────────────────────────────────────────────
    emotion_map = {
        "fear":    fear_d,
        "anger":   anger_d,
        "urgency": urgency_d,
        "shock":   shock_d,
        "sadness": sadness_d,
        "outrage": outrage_d,
    }
    dominant = max(emotion_map, key=emotion_map.get)

    # ── Arousal Density Index (ADenI) ─────────────────────────────────────────
    # Normalizes total arousal signal weight independent of scaling
    arousal_density_index = round(
        (fear_d + anger_d + urgency_d + shock_d + sadness_d + outrage_d) / 6.0, 3
    )

    return {
        "dominant_emotion":     dominant,
        "amplification_score":  ea_score,
        "arousal_density_index": arousal_density_index,
        "density_scores": {
            "fear":    round(fear_d, 3),
            "anger":   round(anger_d, 3),
            "urgency": round(urgency_d, 3),
            "shock":   round(shock_d, 3),
            "sadness": round(sadness_d, 3),
            "outrage": round(outrage_d, 3),
        },
        "raw_counts": {
            "fear":    fear_count,
            "anger":   anger_count,
            "urgency": urgency_count,
            "shock":   shock_count,
            "sadness": sadness_count,
            "outrage": outrage_count,
        },
        "stacking_bonus_applied": round(stacking_bonus, 3),
    }