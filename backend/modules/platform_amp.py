"""
DPIS — Platform Amplification Coefficient Engine (v3.3)

Computes per-platform risk multipliers and propagation profiles.

Platform categories:
  • short_video_social   (TikTok, YouTube Shorts, Instagram Reels)
  • long_video           (YouTube, Facebook Video)
  • micro_social         (Twitter/X, Mastodon)
  • image_social         (Instagram, Facebook)
  • messaging            (WhatsApp, Telegram — estimated)
  • cdn_direct           (Raw CDN, Google Drive links)
  • text_only            (No URL / plain text)

Multiplier range: 1.00 – 1.25
Higher multiplier → platform architecture favors emotional virality spread.
"""

from typing import Dict, Any, Optional
from urllib.parse import urlparse

# Platform signature → (category, multiplier, platform_label, risk_note)
_PLATFORM_PROFILES = [
    # Social video — highest multiplier (algorithmic recommendation + autoplay)
    (["tiktok.com", "vm.tiktok.com"],
     "short_video_social", 1.22,
     "TikTok",
     "Recommendation algorithm optimizes for high-arousal, short-form content. "
     "Autoplay and full-screen immersion amplify emotional response before cognitive appraisal."),

    (["instagram.com", "www.instagram.com"],
     "image_social", 1.18,
     "Instagram",
     "Reels and Story autoplay increase passive exposure. "
     "Visual-first format elevates image AI probability impact."),

    (["youtube.com", "www.youtube.com", "youtu.be"],
     "long_video", 1.15,
     "YouTube",
     "Recommendation engine amplifies high-engagement (fear/anger) content. "
     "Long-form format enables sustained emotional conditioning."),

    (["twitter.com", "www.twitter.com", "x.com", "www.x.com"],
     "micro_social", 1.20,
     "Twitter/X",
     "Quote-tweet and retweet mechanics enable rapid cross-network propagation. "
     "Character limits incentivize decontextualized framing."),

    (["facebook.com", "www.facebook.com", "fb.watch"],
     "image_social", 1.16,
     "Facebook",
     "Emotionally reactive sharing behavior documented extensively in behavioral studies. "
     "Group mechanics enable closed echo-chamber seeding."),

    (["t.me", "telegram.org", "telegram.me"],
     "messaging", 1.10,
     "Telegram",
     "End-to-end encrypted group channels limit moderation intervention. "
     "Forwarding mechanics bypass source tracing."),

    (["drive.google.com"],
     "cdn_direct", 1.03,
     "Google Drive",
     "Public share links enable bypass of platform moderation. "
     "Perceived institutional legitimacy inflates credibility."),
]

_CDN_INDICATORS = [".mp4", ".webm", ".mkv", ".mp3", ".wav", ".jpg", ".png", ".gif"]


def get_platform_profile(url: Optional[str]) -> Dict[str, Any]:
    """
    Returns platform amplification coefficient and metadata for a given URL.
    If no URL provided or unrecognized, returns text-only baseline.
    """
    if not url or not url.strip():
        return {
            "platform":             "TEXT_INPUT",
            "platform_category":    "text_only",
            "amplification_coefficient": 1.00,
            "propagation_risk_note": (
                "Text-only submission — no platform amplification factor applied. "
                "Propagation risk is determined entirely by content characteristics."
            ),
        }

    url = url.strip()
    try:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        hostname = (parsed.hostname or "").lower().lstrip("www.")
    except Exception:
        hostname = ""

    for domains, category, multiplier, label, note in _PLATFORM_PROFILES:
        if any(hostname == d or hostname.endswith("." + d) for d in domains):
            return {
                "platform":             label,
                "platform_category":    category,
                "amplification_coefficient": multiplier,
                "propagation_risk_note": note,
            }

    # CDN / direct file link
    if any(url.lower().endswith(ext) for ext in _CDN_INDICATORS):
        return {
            "platform":             "CDN_DIRECT",
            "platform_category":    "cdn_direct",
            "amplification_coefficient": 1.05,
            "propagation_risk_note": (
                "Direct media file link — bypasses platform moderation pipeline. "
                "Distribution velocity depends on hosting infrastructure accessibility."
            ),
        }

    # Unknown URL — apply minimal lift
    return {
        "platform":             "UNKNOWN_URL",
        "platform_category":    "unknown",
        "amplification_coefficient": 1.04,
        "propagation_risk_note": (
            "Unrecognized platform — minimal amplification coefficient applied. "
            "Manual source verification recommended."
        ),
    }
