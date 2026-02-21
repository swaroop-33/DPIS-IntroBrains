"""
DPIS — FastAPI Backend (v3.3)

Run from project ROOT:
    python -m uvicorn api.index:app --reload

Routes (mounted under /api by api/index.py):
    GET  /           -> service info
    GET  /health     -> health check
    POST /analyze         -> text / transcript analysis
    POST /analyze/media   -> multi-modal file upload + remote URL (unified ingestion)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import Optional
import traceback
import time

from .models import AnalyzeRequest
from .pipeline import run_pipeline

app = FastAPI(
    title="DPIS — Deepfake Psychological Impact Shield",
    version="3.3.0",
    description=(
        "Multi-modal forensic + adversarial psychological intelligence engine. "
        "Supports text, image, audio, video, and remote URL ingestion."
    ),
)

# Per-type upload size caps (MB)
MAX_FILE_MB = {"video": 50, "audio": 20, "image": 10}


# ─────────────────────────────────────────────────────────────────────────────
# Root + Health
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "DPIS — Deepfake Psychological Impact Shield",
        "version": "3.3.0",
        "status":  "running",
        "endpoints": {
            "text_analysis":  "POST /analyze",
            "media_analysis": "POST /analyze/media",
            "docs":           "/docs",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "3.3.0"}


# ─────────────────────────────────────────────────────────────────────────────
# Text Analysis
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if not req.text or len(req.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Text must be at least 5 characters")

    try:
        return run_pipeline(
            text=req.text.strip(),
            input_type=req.input_type,
            simulated_deepfake_score=req.simulated_deepfake_score,
            media_url=None,
            has_media=False,
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal processing error")


# ─────────────────────────────────────────────────────────────────────────────
# Unified Multi-Modal Media Analysis
# ─────────────────────────────────────────────────────────────────────────────

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
    from .core.url_extractor import extract_media_from_url, infer_media_type

    start = time.time()

    video_bytes: Optional[bytes] = None
    audio_bytes: Optional[bytes] = None
    image_bytes: Optional[bytes] = None

    def _mb(b: bytes) -> float:
        return len(b) / 1_048_576

    def _check_size(b: bytes, slot: str) -> None:
        cap = MAX_FILE_MB.get(slot, 25)
        if _mb(b) > cap:
            raise HTTPException(
                status_code=400,
                detail=f"{slot.capitalize()} file exceeds {cap} MB size limit",
            )

    # ── 1. Read uploaded files ────────────────────────────────────────────────
    if video and video.filename:
        video_bytes = await video.read()
        _check_size(video_bytes, "video")

    if audio and audio.filename:
        audio_bytes = await audio.read()
        _check_size(audio_bytes, "audio")

    if image and image.filename:
        image_bytes = await image.read()
        _check_size(image_bytes, "image")

    # ── 2. URL extraction (delegates entirely to url_extractor) ───────────────
    # Platform detection is internal to url_extractor — not exposed here.
    if media_url and media_url.strip() and not any([video_bytes, audio_bytes, image_bytes]):
        try:
            v_bytes, a_bytes, i_bytes = extract_media_from_url(media_url.strip())
            video_bytes = video_bytes or v_bytes
            audio_bytes = audio_bytes or a_bytes
            image_bytes = image_bytes or i_bytes
        except HTTPException:
            raise
        except Exception as exc:
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"URL extraction failed: {exc}")

    # ── Guard: at least one media slot must be populated ─────────────────────
    if not any([video_bytes, audio_bytes, image_bytes]):
        raise HTTPException(
            status_code=400,
            detail="No media provided. Supply a file upload or a public media URL.",
        )

    # ── 3. Forensic analysis per slot ─────────────────────────────────────────
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

    # ── 4. Intelligence pipeline ──────────────────────────────────────────────
    caption      = (text or "").strip() or "neutral media content"
    _img_ai_prob = round(image_result.get("ai_image_probability", 0.0) * 100, 2)

    pipeline_result = run_pipeline(
        text=caption,
        input_type="media",
        simulated_deepfake_score=None,
        media_url=media_url,
        has_media=True,
        image_ai_probability=_img_ai_prob,
    )

    elapsed_ms = round((time.time() - start) * 1000, 2)

    # ── 5. Override stub forensic layer with real analysis data ───────────────
    pipeline_result["forensic"] = {
        "video_deepfake_probability": round(
            video_result.get("deepfake_probability", 0.0) * 100, 2
        ),
        "audio_spoof_probability": round(
            audio_result.get("spoof_probability", 0.0) * 100, 2
        ),
        "image_ai_probability": _img_ai_prob,
        "authenticity_degradation_index": pipeline_result["forensic"].get(
            "authenticity_degradation_index", 0.0
        ),
        "degradation_trajectory": pipeline_result["forensic"].get(
            "degradation_trajectory", []
        ),
        "signals": {
            "video": video_result.get("signals", []),
            "audio": audio_result.get("signals", []),
            "image": image_result.get("signals", []),
        },
    }

    # Update performance metadata with real elapsed time
    pipeline_result["performance"]["execution_time_ms"] = elapsed_ms

    return pipeline_result
