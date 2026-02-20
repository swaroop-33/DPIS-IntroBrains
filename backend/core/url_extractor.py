"""
DPIS — URL Media Extractor (v3.2)

Handles:
  • YouTube, Twitter/X, Instagram, Facebook — via yt-dlp subprocess
  • Google Drive public share links — URL normalization + direct download
  • Direct CDN/.media file URLs — requests streaming download

Security:
  • SSRF protection: validates all hostnames resolve to public IPs only
  • Size cap: MAX_REMOTE_MB per download
  • Timeout: 15s per request, 60s for yt-dlp
  • No subprocess shell injection — yt-dlp called as argument list

Usage:
  from .core.url_extractor import extract_url
  content_bytes, content_type, source_type = extract_url(url)
"""

from __future__ import annotations

import ipaddress
import logging
import os
import socket
import subprocess
import tempfile
from urllib.parse import parse_qs, urlparse

import requests
from fastapi import HTTPException

logger = logging.getLogger(__name__)

MAX_REMOTE_MB = 25
_MAX_BYTES = MAX_REMOTE_MB * 1024 * 1024

# Domains handled by yt-dlp
_YTDLP_DOMAINS = {
    "youtube.com", "www.youtube.com", "youtu.be",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "instagram.com", "www.instagram.com",
    "facebook.com", "www.facebook.com", "fb.watch",
    "tiktok.com", "www.tiktok.com",
    "vimeo.com", "www.vimeo.com",
    "dailymotion.com", "www.dailymotion.com",
}

_DRIVE_DOMAINS = {"drive.google.com"}


# ──────────────────────────────────────────────────────────────────────────────
# SSRF Protection
# ──────────────────────────────────────────────────────────────────────────────

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
                detail="URLs pointing to private/internal networks are not allowed",
            )


# ──────────────────────────────────────────────────────────────────────────────
# Google Drive URL Normalizer
# ──────────────────────────────────────────────────────────────────────────────

def _normalize_drive_url(url: str) -> str:
    parsed = urlparse(url)

    # /file/d/<id>/view
    if "/file/d/" in parsed.path:
        file_id = parsed.path.split("/file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    # open?id=<id>
    qs = parse_qs(parsed.query)
    if "id" in qs:
        file_id = qs["id"][0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    return url


# ──────────────────────────────────────────────────────────────────────────────
# Direct HTTP Download
# ──────────────────────────────────────────────────────────────────────────────

def _download_direct(url: str) -> tuple[bytes, str]:
    """Download a direct file URL with SSRF check and size cap.
    Returns (content_bytes, content_type).
    """
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed")

    _validate_host(parsed.hostname)

    # Google Drive normalization
    if parsed.hostname in _DRIVE_DOMAINS:
        url = _normalize_drive_url(url)

    try:
        with requests.get(
            url,
            timeout=15,
            stream=True,
            allow_redirects=True,
            headers={"User-Agent": "DPIS-Forensic-Agent/3.2"},
        ) as resp:
            if not resp.ok:
                raise HTTPException(
                    status_code=400,
                    detail=f"Remote server returned {resp.status_code}",
                )

            content_type = resp.headers.get("content-type", "application/octet-stream").lower()
            total = 0
            chunks: list[bytes] = []

            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    total += len(chunk)
                    if total > _MAX_BYTES:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Remote file exceeds {MAX_REMOTE_MB} MB limit",
                        )
                    chunks.append(chunk)

            return b"".join(chunks), content_type

    except HTTPException:
        raise
    except requests.Timeout:
        raise HTTPException(status_code=400, detail="Remote URL timed out (>15s)")
    except Exception as exc:
        logger.exception("Direct download failed")
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {exc}")


# ──────────────────────────────────────────────────────────────────────────────
# yt-dlp Extractor (YouTube, Twitter, Instagram, Facebook, TikTok, …)
# ──────────────────────────────────────────────────────────────────────────────

def _extract_via_ytdlp(url: str) -> tuple[bytes, str]:
    """Use yt-dlp to extract and download a stream from a social platform.
    Returns (content_bytes, 'video/mp4').
    """
    with tempfile.TemporaryDirectory() as tmp:
        output_path = os.path.join(tmp, "media.%(ext)s")

        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "--max-filesize", f"{MAX_REMOTE_MB}M",
            "--output", output_path,
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
                detail="yt-dlp not installed — required for social media URL extraction",
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=400,
                detail="yt-dlp extraction timed out (>120s)",
            )

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()[:400]
            raise HTTPException(
                status_code=400,
                detail=f"yt-dlp failed: {stderr or 'unknown error'}",
            )

        # Find downloaded file
        downloaded = [f for f in os.listdir(tmp) if f.startswith("media.")]
        if not downloaded:
            raise HTTPException(
                status_code=400,
                detail="yt-dlp ran but produced no output file",
            )

        filepath = os.path.join(tmp, downloaded[0])
        size = os.path.getsize(filepath)
        if size > _MAX_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Extracted media exceeds {MAX_REMOTE_MB} MB limit",
            )

        ext = downloaded[0].rsplit(".", 1)[-1].lower()
        mime = {
            "mp4": "video/mp4",
            "webm": "video/webm",
            "mkv": "video/x-matroska",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4",
            "wav": "audio/wav",
        }.get(ext, "video/mp4")

        with open(filepath, "rb") as f:
            return f.read(), mime


# ──────────────────────────────────────────────────────────────────────────────
# Public Entry Point
# ──────────────────────────────────────────────────────────────────────────────

def extract_url(url: str) -> tuple[bytes, str, str]:
    """
    Primary URL extraction function.

    Args:
        url: Any public media URL (YouTube, Drive, CDN, social media)

    Returns:
        (content_bytes, content_type_string, source_type)
        where source_type is "ytdlp" | "direct"

    Raises:
        HTTPException on any failure
    """
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="Empty URL provided")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are supported")

    hostname = (parsed.hostname or "").lower().lstrip("www.")

    # Route to yt-dlp for social platforms
    if any(hostname == d or hostname.endswith("." + d) for d in _YTDLP_DOMAINS):
        logger.info("Routing to yt-dlp: %s", url)
        content, content_type = _extract_via_ytdlp(url)
        return content, content_type, "ytdlp"

    # Everything else: direct download
    logger.info("Routing to direct download: %s", url)
    content, content_type = _download_direct(url)
    return content, content_type, "direct"


def infer_media_type(content_type: str) -> str:
    """Map MIME type to 'video' | 'audio' | 'image'."""
    ct = content_type.lower()
    if "video" in ct:
        return "video"
    if "audio" in ct:
        return "audio"
    if "image" in ct:
        return "image"
    raise HTTPException(
        status_code=400,
        detail=f"Unsupported media type: {content_type}",
    )
