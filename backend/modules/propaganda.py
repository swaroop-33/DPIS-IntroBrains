"""
DPIS — Propaganda & Manipulation Pattern Engine (v3.2)

Additions:
• polarization_intensity exported in main dict (no longer private key)
• persuasion_techniques_detected — named list of active technique categories
• trigger_phrases_detected (renamed alias) for consistency with output schema
"""

import re
from typing import Dict, Any, List


PATTERNS: List[Dict] = [
    # URGENCY
    {"regex": r"\bact now\b",                      "category": "urgency",      "weight": 3.0},
    {"regex": r"before it'?s? deleted",            "category": "urgency",      "weight": 3.5},
    {"regex": r"\bshare (?:this |now|immediately)\b", "category": "urgency",   "weight": 3.0},
    {"regex": r"\bbreaking[\s:]",                  "category": "urgency",      "weight": 2.5},
    {"regex": r"\burgent[\s!:]",                   "category": "urgency",      "weight": 2.5},
    {"regex": r"before it'?s? too late",           "category": "urgency",      "weight": 3.0},
    {"regex": r"\blast chance\b",                  "category": "urgency",      "weight": 2.8},

    # AUTHORITY EXPLOITATION
    {"regex": r"\bofficial (?:report|statement|data|source)\b", "category": "authority_exploitation", "weight": 2.5},
    {"regex": r"\b(government|ministry|health department|cdc|who|fda|authorities)\b", "category": "authority_exploitation", "weight": 2.0},
    {"regex": r"\baccording to (?:experts?|scientists?|insiders?)\b", "category": "authority_exploitation", "weight": 2.0},
    {"regex": r"\bclassified|confidential|leaked document\b",  "category": "authority_exploitation", "weight": 3.0},
    {"regex": r"\bwhistleblower\b",                "category": "authority_exploitation", "weight": 2.5},

    # POLARIZATION
    {"regex": r"\bthey (?:don'?t want you|are hiding|are suppressing)\b", "category": "polarization", "weight": 3.5},
    {"regex": r"\bmainstream media\b",             "category": "polarization", "weight": 3.0},
    {"regex": r"\bwake up\b",                      "category": "polarization", "weight": 3.0},
    {"regex": r"\bus vs\.? them\b",                "category": "polarization", "weight": 3.5},
    {"regex": r"\bdeep state|elites?|globalists?\b", "category": "polarization", "weight": 3.0},
    {"regex": r"\bpuppets?\b",                     "category": "polarization", "weight": 2.5},

    # ABSOLUTIST FRAMING
    {"regex": r"\beveryone knows\b",               "category": "absolutist_framing", "weight": 1.8},
    {"regex": r"\bno one will tell\b",             "category": "absolutist_framing", "weight": 2.0},
    {"regex": r"\balways|never\b",                 "category": "absolutist_framing", "weight": 2.0},
    {"regex": r"\b100% proven\b",                  "category": "absolutist_framing", "weight": 2.5},
    {"regex": r"\bindisputable\b",                 "category": "absolutist_framing", "weight": 1.8},

    # FEAR INDUCTION
    {"regex": r"\byou will (?:die|lose|be arrested|be tracked)\b", "category": "fear_induction", "weight": 3.5},
    {"regex": r"\bdanger(?:ous)? for you\b",       "category": "fear_induction", "weight": 3.0},
    {"regex": r"\byour (?:life|family|future) (?:at risk|in danger)\b", "category": "fear_induction", "weight": 3.5},
    {"regex": r"\bdo not ignore\b",                "category": "fear_induction", "weight": 2.5},
    {"regex": r"\bsilent killer\b",                "category": "fear_induction", "weight": 3.0},
]

# Human-readable technique descriptions
_TECHNIQUE_LABELS = {
    "urgency":               "Urgency Exploitation — time-pressure triggers that suppress deliberative reasoning",
    "authority_exploitation": "Authority Exploitation — false or misappropriated credibility markers",
    "polarization":          "Social Polarization — in-group/out-group identity framing to deepen tribal divisions",
    "absolutist_framing":    "Absolutist Framing — binary certainty language that eliminates nuance",
    "fear_induction":        "Fear Induction — direct threat narratives targeting personal safety or in-group identity",
}


def analyze_propaganda(text: str) -> Dict[str, Any]:

    text_lower = text.lower()

    total_weight = 0.0
    category_hits: Dict[str, int] = {k: 0 for k in _TECHNIQUE_LABELS}
    trigger_phrases: List[str] = []

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

    # Calibrated scoring
    base_score = min(total_weight / 80.0, 0.85)
    scaled = base_score ** 1.08

    active_categories = sum(1 for v in category_hits.values() if v > 0)
    if active_categories >= 2:
        scaled *= 1 + (0.06 * active_categories)

    polarization_raw = category_hits.get("polarization", 0)
    polarization_intensity = round(min(polarization_raw / 6.0, 1.0), 3)
    if polarization_intensity > 0.3:
        scaled *= 1 + (polarization_intensity * 0.20)

    manipulation_score = round(min(scaled, 1.0) * 100, 2)

    # Build human-readable technique list
    persuasion_techniques_detected = [
        _TECHNIQUE_LABELS[cat]
        for cat, hits in category_hits.items()
        if hits > 0
    ]

    return {
        "manipulation_score":           manipulation_score,
        "trigger_phrases_detected":     trigger_phrases,
        "persuasion_techniques_detected": persuasion_techniques_detected,
        "polarization_intensity":       polarization_intensity,
        "pattern_breakdown":            category_hits,
        # Legacy alias for backward compatibility
        "trigger_phrases":              trigger_phrases,
    }