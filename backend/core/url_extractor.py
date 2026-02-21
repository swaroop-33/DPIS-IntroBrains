"""
DPIS — URL Media Extractor (v3.3)

Unified multi-platform media extraction. Platform detection is internal only —
never surfaced in API responses.

Supports:
  • Social video platforms  — via yt-dlp subprocess
  • Google Drive            — URL normalization + direct download
  • Direct CDN / any URL    — streaming download

Exposes:
  extract_media_from_url(url) -> (video_bytes, audio_bytes, image_bytes)
  infer_media_type(content_type) -> 'video' | 'audio' | 'image'

Security:
  • SSRF protection: all hostnames must resolve to public IPs
  • Size cap: MAX_REMOTE_MB (25 MB) per extraction
  • Timeout: 15s direct / 120s yt-dlp
  • No shell injection: yt-dlp invoked as argument list
  • Graceful 503 if yt-dlp missing
"""

from __future__ import annotations

import ipaddress
import logging
import os
import socket
import subprocess
import tempfile
from urllib.parse import parse_qs, urlparse
from typing import Optional

import requests
from fastapi import HTTPException

logger = logging.getLogger(__name__)

MAX_REMOTE_MB = 25
_MAX_BYTES    = MAX_REMOTE_MB * 1_048_576

# ── Internal platform routing table (not exposed externally) ──────────────────
_YTDLP_DOMAINS = frozenset({
    "youtube.com", "youtu.be",
    "twitter.com", "x.com",
    "instagram.com",
    "facebook.com", "fb.watch",
    "tiktok.com",
    "vimeo.com",
    "dailymotion.com",
    "twitch.tv",
    "rumble.com",
    "odysee.com",
    "bitchute.com",
    "reddit.com",
    "v.redd.it",
})

_DRIVE_DOMAINS = frozenset({"drive.google.com"})

# MIME → media slot mapping
_VIDEO_MIMES  = {"video/mp4", "video/webm", "video/x-matroska", "video/avi", "video/quicktime", "video/mpeg"}
_AUDIO_MIMES  = {"audio/mpeg", "audio/mp4", "audio/wav", "audio/ogg", "audio/webm", "audio/aac", "audio/flac"}
_IMAGE_MIMES  = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp", "image/tiff"}


# ─────────────────────────────────────────────────────────────────────────────
# SSRF Protection
# ─────────────────────────────────────────────────────────────────────────────

def _is_private_ip(ip: str) -> bool:
    try:
        obj = ipaddress.ip_address(ip)
        return (
            obj.is_private
            or obj.is_loopback
            or obj.is_reserved
            or obj.is_link_local
            or obj.is_multicast
        )
    except ValueError:
        return True


def _validate_host(host: str) -> None:
    if not host:
        raise HTTPException(status_code=400, detail="Missing hostname in URL")
    try:
        entries = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise HTTPException(status_code=400, detail=f"Cannot resolve host: {host}")

    for entry in entries:
        ip = entry[4][0]
        if _is_private_ip(ip):
            raise HTTPException(
                status_code=400,
                detail="URLs targeting private or internal network addresses are not permitted",
            )


# ─────────────────────────────────────────────────────────────────────────────
# URL helpers
# ─────────────────────────────────────────────────────────────────────────────

def _strip_www(hostname: str) -> str:
    return hostname.lstrip("www.") if hostname else ""


def _is_ytdlp_domain(hostname: str) -> bool:
    base = _strip_www(hostname.lower())
    return base in _YTDLP_DOMAINS or any(base.endswith("." + d) for d in _YTDLP_DOMAINS)


def _is_drive_domain(hostname: str) -> bool:
    base = _strip_www(hostname.lower())
    return base in _DRIVE_DOMAINS


def _normalize_drive_url(url: str) -> str:
    parsed = urlparse(url)
    if "/file/d/" in parsed.path:
        file_id = parsed.path.split("/file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    qs = parse_qs(parsed.query)
    if "id" in qs:
        return f"https://drive.google.com/uc?export=download&id={qs['id'][0]}"
    return url


# ─────────────────────────────────────────────────────────────────────────────
# MIME → media type
# ─────────────────────────────────────────────────────────────────────────────

def infer_media_type(content_type: str) -> str:
    """Map MIME type to 'video' | 'audio' | 'image'. Raises HTTPException if unrecognized."""
    base = content_type.split(";")[0].strip().lower()
    if base in _VIDEO_MIMES or base.startswith("video/"):
        return "video"
    if base in _AUDIO_MIMES or base.startswith("audio/"):
        return "audio"
    if base in _IMAGE_MIMES or base.startswith("image/"):
        return "image"
    raise HTTPException(
        status_code=400,
        detail=f"Unsupported or unrecognized media type: {content_type}",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Direct HTTP Download
# ─────────────────────────────────────────────────────────────────────────────

def _download_direct(url: str) -> tuple[bytes, str]:
    """
    Download a direct media URL with SSRF check and size cap.
    Returns (bytes, content_type_string).
    """
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are supported")

    _validate_host(parsed.hostname or "")

    if _is_drive_domain(parsed.hostname or ""):
        url = _normalize_drive_url(url)

    try:
        with requests.get(
            url,
            timeout=15,
            stream=True,
            allow_redirects=True,
            headers={"User-Agent": "DPIS-Forensic-Agent/3.3"},
        ) as resp:
            if not resp.ok:
                raise HTTPException(
                    status_code=400,
                    detail=f"Remote server returned {resp.status_code}",
                )

            content_type = resp.headers.get("content-type", "application/octet-stream").lower()
            total        = 0
            chunks: list[bytes] = []

            for chunk in resp.iter_content(chunk_size=65_536):
                if chunk:
                    total += len(chunk)
                    if total > _MAX_BYTES:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Remote file exceeds {MAX_REMOTE_MB} MB size limit",
                        )
                    chunks.append(chunk)

            return b"".join(chunks), content_type

    except HTTPException:
        raise
    except requests.Timeout:
        raise HTTPException(status_code=400, detail="Remote URL request timed out (>15s)")
    except Exception as exc:
        logger.exception("Direct download failed for URL: %s", url)
        raise HTTPException(status_code=400, detail=f"Failed to retrieve URL: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# yt-dlp Extraction
# ─────────────────────────────────────────────────────────────────────────────

def _extract_via_ytdlp(url: str) -> tuple[bytes, str]:
    """
    Extract and download a media stream via yt-dlp.
    Returns (bytes, mime_type).
    Raises HTTPException(503) if yt-dlp is not installed.
    """
    with tempfile.TemporaryDirectory() as tmp:
        output_tmpl = os.path.join(tmp, "media.%(ext)s")

        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--format",  "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "--max-filesize", f"{MAX_REMOTE_MB}M",
            "--output",  output_tmpl,
            "--no-warnings",
            "--quiet",
            url,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=120,
                text=True,
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail=(
                    "yt-dlp is not installed on the server. "
                    "Social media URL extraction is unavailable."
                ),
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=400,
                detail="Media extraction timed out (>120s)",
            )

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()[:400]
            raise HTTPException(
                status_code=400,
                detail=f"Media extraction failed: {stderr or 'unknown error'}",
            )

        downloaded = [f for f in os.listdir(tmp) if f.startswith("media.")]
        if not downloaded:
            raise HTTPException(
                status_code=400,
                detail="Extraction produced no output file",
            )

        filepath = os.path.join(tmp, downloaded[0])
        size     = os.path.getsize(filepath)
        if size > _MAX_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Extracted media exceeds {MAX_REMOTE_MB} MB size limit",
            )

        ext = downloaded[0].rsplit(".", 1)[-1].lower()
        mime = {
            "mp4":  "video/mp4",
            "webm": "video/webm",
            "mkv":  "video/x-matroska",
            "mp3":  "audio/mpeg",
            "m4a":  "audio/mp4",
            "wav":  "audio/wav",
            "ogg":  "audio/ogg",
        }.get(ext, "video/mp4")

        with open(filepath, "rb") as fh:
            return fh.read(), mime


# ─────────────────────────────────────────────────────────────────────────────
# Public Entry Points
# ─────────────────────────────────────────────────────────────────────────────

def extract_media_from_url(
    url: str,
) -> tuple[Optional[bytes], Optional[bytes], Optional[bytes]]:
    """
    Primary extraction function for unified media ingestion (v3.3).

    Returns (video_bytes, audio_bytes, image_bytes).
    Exactly one slot will be populated; the other two will be None.

    Platform routing is internal — not surfaced in return value or logs.
    Raises HTTPException on any failure.
    """
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="Empty URL provided")

    url    = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are supported")

    hostname = parsed.hostname or ""

    # Validate SSRF before any routing decision
    _validate_host(hostname)

    # Internal routing — not surfaced externally
    if _is_ytdlp_domain(hostname):
        content, mime = _extract_via_ytdlp(url)
    else:
        content, mime = _download_direct(url)

    media_type = infer_media_type(mime)

    if media_type == "video":
        return content, None, None
    if media_type == "audio":
        return None, content, None
    # image
    return None, None, content


# Legacy compatibility — used by older callers in main.py
def extract_url(url: str) -> tuple[bytes, str, str]:
    """
    Legacy interface. Returns (content_bytes, content_type, source_type).
    Prefer extract_media_from_url() for new code.
    """
    parsed   = urlparse(url.strip())
    hostname = parsed.hostname or ""
    _validate_host(hostname)

    if _is_ytdlp_domain(hostname):
        content, mime = _extract_via_ytdlp(url)
        return content, mime, "ytdlp"

    content, mime = _download_direct(url)
    return content, mime, "direct"
