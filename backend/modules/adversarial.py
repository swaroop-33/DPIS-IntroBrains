"""
DPIS — Adversarial Evasion Detection Module (v3.3)

Detects attempts to bypass keyword-based filters through:
  • Unicode homoglyph substitution  (e.g. "fеar" using Cyrillic е)
  • Zero-width space / invisible character injection
  • Leetspeak / alphanumeric substitution (f3ar, s4fe, d1srupt)
  • Deliberate misspelling with recognizable stems (k1ll, suiciide)
  • Strategic word fragmentation ("act n o w")
  • All-caps evasion signals
  • Repetition-based salience inflation

Returns:
  evasion_detected: bool
  evasion_score: float (0–100)
  evasion_signals: list[str]
  normalized_text: str  (de-obfuscated, used by propaganda module)
"""

import re
import unicodedata
from typing import Dict, Any

# Explicit homoglyph substitution map (Cyrillic/Latin confusables + invisible chars)
_HOMOGLYPH_MAP = {
    'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'х': 'x',
    'у': 'y', 'і': 'i', 'ї': 'i', 'ℯ': 'e', 'ℨ': 'z', 'ℬ': 'b',
    '\u200b': '', '\u200c': '', '\u200d': '',   # zero-width chars
    '\u00ad': '',  # soft hyphen
    '\ufeff': '',  # BOM
}

# Leet → standard
_LEET_MAP = str.maketrans("013456789@$", "oieashbgas ")

# ──────────────────────────────────────────────────────────────────────────────
# High-risk keyword stems (post-normalization match)
# ──────────────────────────────────────────────────────────────────────────────
_RISK_STEMS = [
    r"k[i1]ll", r"b[o0]mb", r"d[i1]e", r"suic[i1]d",
    r"h[a4]te", r"v[i1]rus", r"d[e3]str[o0]y",
    r"w[a4]r", r"r[e3]v[o0]lt", r"exp[l1][o0]d",
    r"bl[o0][o0]d", r"sl[a4]ught[e3]r",
]
_RISK_STEM_RE = re.compile("|".join(_RISK_STEMS), re.IGNORECASE)

# Zero-width and invisible char detection
_ZW_RE = re.compile(r"[\u200b\u200c\u200d\ufeff\u00ad]")

# Fragmented word: "a c t   n o w"
_FRAG_RE = re.compile(r"(?:\b\w\s){3,}")

# All-caps ratio pattern
def _allcaps_ratio(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    caps = sum(1 for w in words if len(w) >= 3 and w.isupper())
    return caps / len(words)


def _normalize(text: str) -> str:
    """Return de-obfuscated version of text for downstream analysis."""
    # 1. Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)

    # 2. Homoglyph substitution
    out = []
    for ch in text:
        out.append(_HOMOGLYPH_MAP.get(ch, ch))
    text = "".join(out)

    # 3. Leet decode
    text = text.translate(_LEET_MAP)

    # 4. Strip zero-width chars (already handled above via map)
    text = _ZW_RE.sub("", text)

    return text


def detect_evasion(text: str) -> Dict[str, Any]:
    signals = []
    score   = 0.0

    # ── 1. Zero-width / invisible character injection ─────────────────────────
    zw_count = len(_ZW_RE.findall(text))
    if zw_count > 0:
        signals.append(
            f"Invisible character injection detected ({zw_count} zero-width/soft-hyphen characters)"
        )
        score += min(zw_count * 8.0, 30.0)

    # ── 2. Homoglyph substitution ─────────────────────────────────────────────
    normalized = _normalize(text)
    homoglyph_diffs = sum(
        1 for a, b in zip(text, normalized) if a != b and _HOMOGLYPH_MAP.get(a) is not None
    )
    if homoglyph_diffs > 0:
        signals.append(
            f"Homoglyph/Unicode substitution detected ({homoglyph_diffs} character(s) normalized)"
        )
        score += min(homoglyph_diffs * 5.0, 25.0)

    # ── 3. Leet substitution on risk stems ───────────────────────────────────
    leet_hits = _RISK_STEM_RE.findall(normalized)
    if leet_hits:
        signals.append(
            f"Leet-encoded high-risk term(s) detected post-normalization: {leet_hits[:4]}"
        )
        score += min(len(leet_hits) * 10.0, 30.0)

    # ── 4. Fragmented word spacing ────────────────────────────────────────────
    if _FRAG_RE.search(text):
        signals.append("Deliberate word fragmentation via spacing detected (filter bypass pattern)")
        score += 15.0

    # ── 5. All-caps inflation ─────────────────────────────────────────────────
    caps_ratio = _allcaps_ratio(text)
    if caps_ratio > 0.50:
        signals.append(
            f"All-caps salience inflation: {caps_ratio:.0%} of substantive words uppercase"
        )
        score += min(caps_ratio * 20.0, 15.0)

    # ── 6. Repetition inflation ───────────────────────────────────────────────
    words = text.lower().split()
    if words:
        from collections import Counter
        counts = Counter(words)
        most_common_word, freq = counts.most_common(1)[0]
        rep_ratio = freq / len(words)
        if rep_ratio > 0.12 and freq > 3:
            signals.append(
                f"Repetition-based salience inflation: '{most_common_word}' appears "
                f"{freq}× ({rep_ratio:.0%} of tokens)"
            )
            score += min(rep_ratio * 30.0, 15.0)

    score = round(min(score, 100.0), 2)

    return {
        "evasion_detected":  score > 10.0,
        "evasion_score":     score,
        "evasion_signals":   signals,
        "normalized_text":   normalized,
    }
