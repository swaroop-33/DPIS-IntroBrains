from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import Optional
import traceback

from models import AnalyzeRequest
from pipeline import run_pipeline

app = FastAPI(
    title="DPIS — Deepfake Psychological Impact Shield",
    version="3.0.0",
)

# ─────────────────────────────────────────────
# Root
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service": "DPIS — Deepfake Psychological Impact Shield",
        "version": "3.0.0",
        "status": "running",
        "docs": "/docs",
    }

# ─────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}

# ─────────────────────────────────────────────
# Text Analysis (Existing)
# ─────────────────────────────────────────────
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if not req.text or len(req.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Text too short")

    try:
        return run_pipeline(
            text=req.text,
            input_type=req.input_type,
            simulated_deepfake_score=req.simulated_deepfake_score,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────
# Media Analysis (Fixed)
# ─────────────────────────────────────────────
@app.post("/analyze/media")
async def analyze_media(
    video: Optional[UploadFile] = File(default=None),
    audio: Optional[UploadFile] = File(default=None),
    image: Optional[UploadFile] = File(default=None),
    text: Optional[str] = Form(default=""),
):
    from core.media_forensics import (
        analyze_video_frames,
        analyze_audio_waveform,
        analyze_image_artifacts,
        compute_forensic_pps,
    )
    from modules.emotion import analyze_emotion
    from modules.propaganda import analyze_propaganda
    from modules.virality import estimate_virality
    import time

    start = time.time()

    video_bytes = await video.read() if video else None
    audio_bytes = await audio.read() if audio else None
    image_bytes = await image.read() if image else None

    # Size protection
    def size_mb(data): return len(data) / (1024 * 1024)

    if video_bytes and size_mb(video_bytes) > 20:
        raise HTTPException(status_code=400, detail="Video too large (max 20MB)")
    if audio_bytes and size_mb(audio_bytes) > 10:
        raise HTTPException(status_code=400, detail="Audio too large (max 10MB)")
    if image_bytes and size_mb(image_bytes) > 5:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")

    video_result = analyze_video_frames(video_bytes) if video_bytes else {
        "deepfake_probability": 0.0,
        "signals": ["No video file provided"],
    }

    audio_result = analyze_audio_waveform(audio_bytes) if audio_bytes else {
        "spoof_probability": 0.0,
        "signals": ["No audio file provided"],
    }

    image_result = analyze_image_artifacts(image_bytes) if image_bytes else {
        "ai_image_probability": 0.0,
        "signals": ["No image file provided"],
    }

    fallback_text = text.strip() if text.strip() else "neutral content"
    emotion = analyze_emotion(fallback_text)
    propaganda = analyze_propaganda(fallback_text)
    polarization_intensity = propaganda.pop("_polarization_intensity", 0.0)

    virality = estimate_virality(
        emotional_amplification=emotion["amplification_score"],
        manipulation_score=propaganda["manipulation_score"],
        polarization_intensity=polarization_intensity,
        fear_score=emotion["density_scores"].get("fear", 0.0),
        anger_score=emotion["density_scores"].get("anger", 0.0),
    )

    mp_score = propaganda["manipulation_score"]

    severity_level = (
        "Low" if mp_score < 30 else
        "Moderate" if mp_score < 60 else
        "High"
    )

    base_text_risk = min(
        (emotion["amplification_score"] * 0.3) +
        (mp_score * 0.2),
        40
    )

    forensic_pps = compute_forensic_pps(
        deepfake_score=base_text_risk,
        video_deepfake_prob=video_result.get("deepfake_probability", 0.0),
        audio_spoof_prob=audio_result.get("spoof_probability", 0.0),
        image_ai_prob=image_result.get("ai_image_probability", 0.0),
        emotion_score=emotion["amplification_score"],
        manipulation_score=mp_score,
        virality_score=virality["virality_score"],
    )

    elapsed_ms = round((time.time() - start) * 1000, 2)

    return {
        "deepfake_score": round(video_result.get("deepfake_probability", 0.0) * 100, 2),
        "audio_spoof_score": round(audio_result.get("spoof_probability", 0.0) * 100, 2),
        "image_ai_score": round(image_result.get("ai_image_probability", 0.0) * 100, 2),
        "emotional_score": round(emotion["amplification_score"], 2),
        "manipulation_score": round(mp_score, 2),
        "manipulation_severity": severity_level,
        "virality_score": round(virality["virality_score"], 2),
        "pps": forensic_pps["pps"],
        "virality_risk": forensic_pps["virality_risk"],
        "blended_deepfake_score": forensic_pps["blended_deepfake_score"],
        "contribution_breakdown": forensic_pps["contribution_breakdown"],
        "forensic_signals": {
            "video": video_result.get("signals", []),
            "audio": audio_result.get("signals", []),
            "image": image_result.get("signals", []),
        },
        "media_stats": {
            "video": video_result.get("frame_stats"),
            "audio": audio_result.get("audio_stats"),
            "image": image_result.get("image_stats"),
        },
        "performance": {"execution_time_ms": elapsed_ms},
    }