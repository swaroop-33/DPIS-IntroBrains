"""
DPIS — Emotional Amplification Module (v3.0)

Upgrades:
• Repetition-aware detection
• Emotional density scaling
• High-arousal stacking amplification
• Short-text boost
• Nonlinear top-heavy escalation
• Fully heuristic, instant execution
"""

import re
from typing import Dict, Any

# ─── Keyword mappings ────────────────────────────────────────────────
FEAR_KEYWORDS = [
    "danger", "threat", "risk", "warning", "scared",
    "terrified", "panic", "afraid", "deadly", "crisis"
]

ANGER_KEYWORDS = [
    "outrage", "furious", "disgusted", "unacceptable",
    "corrupt", "lies", "betrayal", "angry", "rage"
]

URGENCY_KEYWORDS = [
    "now", "immediately", "urgent", "hurry",
    "before it's too late", "act fast", "share now",
    "breaking", "critical", "alert"
]

SHOCK_KEYWORDS = [
    "unbelievable", "shocking", "exposed", "secret",
    "hidden", "cover-up", "scandal", "bombshell", "leaked"
]


# ─────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────
def _count_occurrences(text: str, keywords: list) -> int:
    count = 0
    for kw in keywords:
        count += len(re.findall(r"\b" + re.escape(kw) + r"\b", text))
    return count


def analyze_emotion(text: str) -> Dict[str, Any]:

    text_lower = text.lower()
    tokens = len(text_lower.split())
    tokens = max(tokens, 1)

    # ─────────────────────────────────────────
    # 1️⃣ Repetition-aware counts
    # ─────────────────────────────────────────
    fear_count = _count_occurrences(text_lower, FEAR_KEYWORDS)
    anger_count = _count_occurrences(text_lower, ANGER_KEYWORDS)
    urgency_count = _count_occurrences(text_lower, URGENCY_KEYWORDS)
    shock_count = _count_occurrences(text_lower, SHOCK_KEYWORDS)

    # ─────────────────────────────────────────
    # 2️⃣ Emotional density (per 100 tokens)
    # ─────────────────────────────────────────
    fear_density = min((fear_count / tokens) * 100, 1.0)
    anger_density = min((anger_count / tokens) * 100, 1.0)
    urgency_density = min((urgency_count / tokens) * 100, 1.0)
    shock_density = min((shock_count / tokens) * 100, 1.0)

    # ─────────────────────────────────────────
    # 3️⃣ Base weighted emotional intensity
    # ─────────────────────────────────────────
    ea_raw = (
        (0.35 * fear_density) +
        (0.30 * anger_density) +
        (0.20 * urgency_density) +
        (0.15 * shock_density)
    )

    # ─────────────────────────────────────────
    # 4️⃣ High-arousal stacking boost
    # If fear + anger both present, escalate
    # ─────────────────────────────────────────
    high_arousal_stack = 0
    if fear_count > 0 and anger_count > 0:
        high_arousal_stack += 0.15

    if urgency_count > 0 and fear_count > 0:
        high_arousal_stack += 0.10

    if shock_count > 0 and urgency_count > 0:
        high_arousal_stack += 0.08

    ea_raw *= (1 + high_arousal_stack)

    # ─────────────────────────────────────────
    # 5️⃣ Short-text amplification
    # Social media messages are more volatile
    # ─────────────────────────────────────────
    if tokens < 80:
        ea_raw *= 1.10

    # ─────────────────────────────────────────
    # 6️⃣ Nonlinear escalation
    # ─────────────────────────────────────────
    ea_normalized = min(ea_raw, 1.0)
    ea_score = (ea_normalized ** 1.2) * 100
    ea_score = round(min(ea_score, 100), 2)

    # ─────────────────────────────────────────
    # Determine dominant emotion
    # ─────────────────────────────────────────
    emotion_map = {
        "fear": fear_density,
        "anger": anger_density,
        "urgency": urgency_density,
        "shock": shock_density,
    }

    dominant = max(emotion_map, key=emotion_map.get)

    return {
        "dominant_emotion": dominant,
        "raw_counts": {
            "fear": fear_count,
            "anger": anger_count,
            "urgency": urgency_count,
            "shock": shock_count,
        },
        "density_scores": {
            "fear": round(fear_density, 3),
            "anger": round(anger_density, 3),
            "urgency": round(urgency_density, 3),
            "shock": round(shock_density, 3),
        },
        "stacking_bonus_applied": round(high_arousal_stack, 3),
        "amplification_score": ea_score,
    }