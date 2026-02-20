"""
DPIS — Credibility Erosion Index (v3.3)

Computes a composite index (0–100) measuring how much a piece of content
destabilizes the audience's epistemic trust baseline.

Drivers:
  • Deepfake probability     (direct authenticity breach)
  • Image AI probability     (visual fabrication reduces source credibility)
  • Authority exploitation   (misappropriated credibility markers)
  • Absolutist framing       (epistemic closure)
  • Source opacity           (no attributable source markers)

Output:
  credibility_erosion_index:  float 0–100
  erosion_level:              MINIMAL | MODERATE | SIGNIFICANT | SEVERE
  erosion_drivers:            list[str]
"""

from typing import Dict, Any, List


def _erosion_level(score: float) -> str:
    if score <= 20:  return "MINIMAL"
    if score <= 45:  return "MODERATE"
    if score <= 70:  return "SIGNIFICANT"
    return "SEVERE"


def compute_credibility_erosion(
    deepfake_score: float,            # 0–100
    image_ai_probability: float,      # 0–100 (from forensic layer)
    manipulation_score: float,        # 0–100 (from propaganda)
    authority_hits: int,              # pattern_breakdown["authority_exploitation"]
    absolutist_hits: int,             # pattern_breakdown["absolutist_framing"]
    has_source_attribution: bool = False,
) -> Dict[str, Any]:

    drivers: List[str] = []
    score = 0.0

    # ── Deepfake contribution (30%) ───────────────────────────────────────────
    df_contrib = deepfake_score * 0.30
    if deepfake_score > 50:
        drivers.append(
            f"Deepfake probability {deepfake_score:.1f}% introduces authentic-media impersonation risk — "
            "credibility of purported source undermined."
        )

    # ── Image AI contribution (20%) ───────────────────────────────────────────
    img_contrib = image_ai_probability * 0.20
    if image_ai_probability > 40:
        drivers.append(
            f"Image AI-generation probability {image_ai_probability:.1f}% — "
            "fabricated visuals inflate perceived evidentiary weight."
        )

    # ── Authority exploitation (25%) ──────────────────────────────────────────
    auth_contrib = min(authority_hits * 8.0, 25.0)
    if authority_hits > 0:
        drivers.append(
            f"Authority exploitation detected ({authority_hits} marker(s)) — "
            "false or unverifiable credibility markers inflate perceived legitimacy."
        )

    # ── Absolutist framing (15%) ──────────────────────────────────────────────
    abs_contrib = min(absolutist_hits * 5.0, 15.0)
    if absolutist_hits > 0:
        drivers.append(
            f"Absolutist framing ({absolutist_hits} instance(s)) — "
            "binary certainty language eliminates epistemic nuance."
        )

    # ── Source opacity (10% penalty) ──────────────────────────────────────────
    if not has_source_attribution:
        score += 10.0
        drivers.append(
            "No verifiable source attribution detected — anonymous or opaque origin "
            "increases susceptibility to fabrication acceptance."
        )

    score += df_contrib + img_contrib + auth_contrib + abs_contrib
    score = round(min(score, 100.0), 2)

    return {
        "credibility_erosion_index": score,
        "erosion_level":            _erosion_level(score),
        "erosion_drivers":          drivers,
    }
