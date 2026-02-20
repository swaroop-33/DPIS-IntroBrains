"""
DPIS — Propaganda & Manipulation Pattern Engine (Final Calibrated)

Stable.
No saturation.
Stack-sensitive.
Predictable.
"""

import re
from typing import Dict, Any, List


PATTERNS: List[Dict] = [
    # URGENCY
    {"regex": r"\bact now\b", "category": "urgency", "weight": 3.0},
    {"regex": r"before it'?s? deleted", "category": "urgency", "weight": 3.5},
    {"regex": r"\bshare (?:this |now|immediately)\b", "category": "urgency", "weight": 3.0},
    {"regex": r"\bbreaking[\s:]", "category": "urgency", "weight": 2.5},
    {"regex": r"\burgent[\s!:]", "category": "urgency", "weight": 2.5},
    {"regex": r"before it'?s? too late", "category": "urgency", "weight": 3.0},

    # AUTHORITY
    {"regex": r"\bofficial (?:report|statement|data|source)\b", "category": "authority", "weight": 2.5},
    {"regex": r"\b(government|ministry|health department|cdc|who|fda|authorities)\b", "category": "authority", "weight": 2.0},
    {"regex": r"\baccording to (?:experts?|scientists?|insiders?)\b", "category": "authority", "weight": 2.0},
    {"regex": r"\bclassified|confidential|leaked document\b", "category": "authority", "weight": 3.0},

    # POLARIZATION
    {"regex": r"\bthey (?:don'?t want you|are hiding|are suppressing)\b", "category": "polarization", "weight": 3.5},
    {"regex": r"\bmainstream media\b", "category": "polarization", "weight": 3.0},
    {"regex": r"\bwake up\b", "category": "polarization", "weight": 3.0},
    {"regex": r"\bus vs\.? them\b", "category": "polarization", "weight": 3.5},
    {"regex": r"\bdeep state|elites?|globalists?\b", "category": "polarization", "weight": 3.0},

    # ABSOLUTIST
    {"regex": r"\beveryone knows\b", "category": "absolutist", "weight": 1.8},
    {"regex": r"\bno one will tell\b", "category": "absolutist", "weight": 2.0},
    {"regex": r"\balways|never\b", "category": "absolutist", "weight": 2.0},
    {"regex": r"\b100% proven\b", "category": "absolutist", "weight": 2.5},
]


def analyze_propaganda(text: str) -> Dict[str, Any]:

    text_lower = text.lower()

    total_weight = 0.0
    category_hits = {"urgency": 0, "authority": 0, "polarization": 0, "absolutist": 0}
    trigger_phrases = []

    for pat in PATTERNS:
        matches = re.findall(pat["regex"], text_lower)

        if matches:
            repeat_factor = min(len(matches), 3)
            weight_applied = pat["weight"] * repeat_factor

            total_weight += weight_applied
            category_hits[pat["category"]] += repeat_factor

            for m in matches:
                clean = m.strip()
                if clean and clean not in trigger_phrases:
                    trigger_phrases.append(clean)

    # Calibrated base divisor
    base_score = total_weight / 80.0

    # Pre-cap before stacking
    base_score = min(base_score, 0.85)

    # Mild nonlinear lift
    scaled = base_score ** 1.08

    # Controlled stacking
    active_categories = sum(1 for v in category_hits.values() if v > 0)
    if active_categories >= 2:
        scaled *= 1 + (0.06 * active_categories)

    # Controlled polarization boost
    polarization_intensity = min(category_hits["polarization"] / 6.0, 1.0)
    if polarization_intensity > 0.3:
        scaled *= 1 + (polarization_intensity * 0.20)

    manipulation_score = round(min(scaled, 1.0) * 100, 2)

    return {
        "manipulation_score": manipulation_score,
        "trigger_phrases": trigger_phrases,
        "pattern_breakdown": category_hits,
        "_polarization_intensity": round(polarization_intensity, 3),
    }