"""
DPIS — FastAPI Backend (v3.2)

Run from project ROOT:
    python -m uvicorn api.index:app --reload

Routes (mounted under /api by api/index.py):
    GET  /          → service info
    GET  /health    → health check
    POST /analyze         → text / transcript analysis
    POST /analyze/media   → multi-modal file upload + remote URL
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import Optional
import traceback
import time

from .models import AnalyzeRequest
from .pipeline import run_pipeline

app = FastAPI(
    title="DPIS — Deepfake Psychological Impact Shield",
    version="3.2.0",
    description="Multi-modal AI forensic analysis: deepfake, emotion, propaganda, virality, PPS.",
)

MAX_FILE_MB = {"video": 50, "audio": 20, "image": 10}


# ─────────────────────────────────────────────
# Root + Health
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service": "DPIS — Deepfake Psychological Impact Shield",
        "version": "3.2.0",
        "status": "running",
        "endpoints": {
            "text_analysis": "POST /analyze",
            "media_analysis": "POST /analyze/media",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "3.2.0"}


# ─────────────────────────────────────────────
# Text Analysis
# ─────────────────────────────────────────────
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if not req.text or len(req.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Text must be at least 5 characters")

    try:
        return run_pipeline(
            text=req.text.strip(),
            input_type=req.input_type,
            simulated_deepfake_score=req.simulated_deepfake_score,
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal processing error")


# ─────────────────────────────────────────────
# Multi-Modal Media Analysis
# ─────────────────────────────────────────────
@app.post("/analyze/media")
async def analyze_media(
    video:     Optional[UploadFile] = File(default=None),
    audio:     Optional[UploadFile] = File(default=None),
    image:     Optional[UploadFile] = File(default=None),
    media_url: Optional[str]        = Form(default=None),
    text:      Optional[str]        = Form(default=""),
):
    from .core.media_forensics import (
        analyze_video_frames,
        analyze_audio_waveform,
        analyze_image_artifacts,
    )
    from .core.url_extractor import extract_url, infer_media_type

    start = time.time()

    video_bytes: Optional[bytes] = None
    audio_bytes: Optional[bytes] = None
    image_bytes: Optional[bytes] = None
    url_source: Optional[str]   = None

    # ── 1. Read uploaded files ──────────────────────────────────────────────
    def _mb(b: bytes) -> float:
        return len(b) / 1_048_576

    try:
        if video:
            data = await video.read()
            if _mb(data) > MAX_FILE_MB["video"]:
                raise HTTPException(status_code=400, detail=f"Video exceeds {MAX_FILE_MB['video']} MB limit")
            video_bytes = data

        if audio:
            data = await audio.read()
            if _mb(data) > MAX_FILE_MB["audio"]:
                raise HTTPException(status_code=400, detail=f"Audio exceeds {MAX_FILE_MB['audio']} MB limit")
            audio_bytes = data

        if image:
            data = await image.read()
            if _mb(data) > MAX_FILE_MB["image"]:
                raise HTTPException(status_code=400, detail=f"Image exceeds {MAX_FILE_MB['image']} MB limit")
            image_bytes = data

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read uploaded files")

    # ── 2. URL ingestion (YouTube, Drive, CDN, …) ────────────────────────────
    if media_url and media_url.strip():
        try:
            content, content_type, src_type = extract_url(media_url.strip())
            media_type = infer_media_type(content_type)
            url_source = f"{src_type}:{media_type}"

            if media_type == "video" and not video_bytes:
                video_bytes = content
            elif media_type == "audio" and not audio_bytes:
                audio_bytes = content
            elif media_type == "image" and not image_bytes:
                image_bytes = content

        except HTTPException:
            raise
        except Exception:
            traceback.print_exc()
            raise HTTPException(status_code=400, detail="URL extraction failed")

    if not any([video_bytes, audio_bytes, image_bytes]):
        raise HTTPException(
            status_code=400,
            detail="No media provided. Upload a file or supply a public media URL.",
        )

    # ── 3. Forensic analysis ─────────────────────────────────────────────────
    try:
        video_result = (
            analyze_video_frames(video_bytes)
            if video_bytes
            else {"deepfake_probability": 0.0, "signals": ["No video provided"]}
        )

        audio_result = (
            analyze_audio_waveform(audio_bytes)
            if audio_bytes
            else {"spoof_probability": 0.0, "signals": ["No audio provided"]}
        )

        image_result = (
            analyze_image_artifacts(image_bytes)
            if image_bytes
            else {"ai_image_probability": 0.0, "signals": ["No image provided"]}
        )

        caption = text.strip() if text and text.strip() else "neutral media content"

        pipeline_result = run_pipeline(
            text=caption,
            input_type="media",
            simulated_deepfake_score=None,
        )

        elapsed_ms = round((time.time() - start) * 1000, 2)

        return {
            **pipeline_result,
            "forensic": {
                "video_deepfake_probability": round(
                    video_result.get("deepfake_probability", 0.0) * 100, 2
                ),
                "audio_spoof_probability": round(
                    audio_result.get("spoof_probability", 0.0) * 100, 2
                ),
                "image_ai_probability": round(
                    image_result.get("ai_image_probability", 0.0) * 100, 2
                ),
                "signals": {
                    "video": video_result.get("signals", []),
                    "audio": audio_result.get("signals", []),
                    "image": image_result.get("signals", []),
                },
                "media_stats": {
                    "video": video_result.get("frame_stats"),
                    "audio": audio_result.get("audio_stats"),
                    "image": image_result.get("image_stats"),
                },
                "url_source": url_source,
            },
            "performance": {"execution_time_ms": elapsed_ms},
        }

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal media processing error")