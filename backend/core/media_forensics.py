"""
DPIS — Lightweight Multi-Modal Media Forensics Engine
backend/core/media_forensics.py
"""

from __future__ import annotations
import io
import logging
from typing import Dict, Any, Optional
import numpy as np
logger = logging.getLogger(__name__)

# Optional dependencies (graceful fallback)

try:
    import cv2
    import numpy as np
    _CV2_OK = True
except ImportError:
    _CV2_OK = False

try:
    import librosa
    import soundfile as sf
    import numpy as np  # noqa
    _LIBROSA_OK = True
except ImportError:
    _LIBROSA_OK = False

try:
    from PIL import Image
    import numpy as np  # noqa
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

try:
    import numpy as np
except ImportError:
    np = None


# ─────────────────────────────────────────────
# VIDEO FORENSICS (Improved Sensitivity)
# ─────────────────────────────────────────────

def analyze_video_frames(file_bytes: bytes) -> Dict[str, Any]:
    if not _CV2_OK or np is None:
        return {
            "deepfake_probability": 0.0,
            "signals": ["[VIDEO FORENSICS UNAVAILABLE] OpenCV not installed"],
        }

    try:
        import tempfile, os

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        cap = cv2.VideoCapture(tmp_path)
        os.unlink(tmp_path)

        if not cap.isOpened():
            return {
                "deepfake_probability": 0.0,
                "signals": ["Could not open video file"],
            }

        frame_count = 0
        lap_vars = []

        while frame_count < 40:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            lap_vars.append(cv2.Laplacian(gray, cv2.CV_64F).var())
            frame_count += 1

        cap.release()

        if not lap_vars:
            return {
                "deepfake_probability": 0.0,
                "signals": ["No frames sampled"],
            }

        variance = float(np.std(lap_vars))

        # Stronger nonlinear scaling
        score = min((variance / 600.0) ** 0.7, 1.0)

        return {
            "deepfake_probability": round(score, 4),
            "signals": [f"Frame sharpness instability: {variance:.2f}"],
            "frame_stats": {"frames_sampled": frame_count},
        }

    except Exception as e:
        logger.exception("Video processing failed")
        return {
            "deepfake_probability": 0.0,
            "signals": [f"Processing error: {str(e)}"],
        }


# ─────────────────────────────────────────────
# AUDIO FORENSICS (Improved Sensitivity)
# ─────────────────────────────────────────────

def analyze_audio_waveform(file_bytes: bytes) -> Dict[str, Any]:
    if not _LIBROSA_OK or np is None:
        return {
            "spoof_probability": 0.0,
            "signals": ["[AUDIO FORENSICS UNAVAILABLE] librosa not installed"],
        }

    try:
        buf = io.BytesIO(file_bytes)
        y, sr = librosa.load(buf, sr=None, mono=True)

        flatness = librosa.feature.spectral_flatness(y=y)
        mean_flat = float(np.mean(flatness))

        # Better scaling curve
        score = min((mean_flat * 8) ** 0.8, 1.0)

        return {
            "spoof_probability": round(score, 4),
            "signals": [f"Spectral flatness anomaly: {mean_flat:.5f}"],
            "audio_stats": {"sample_rate": sr},
        }

    except Exception as e:
        logger.exception("Audio processing failed")
        return {
            "spoof_probability": 0.0,
            "signals": [f"Processing error: {str(e)}"],
        }


# ─────────────────────────────────────────────
# IMAGE FORENSICS (Improved Sensitivity)
# ─────────────────────────────────────────────

def analyze_image_artifacts(file_bytes: bytes) -> Dict[str, Any]:
    if not _PIL_OK or np is None:
        return {
            "ai_image_probability": 0.0,
            "signals": ["[IMAGE FORENSICS UNAVAILABLE] Pillow not installed"],
        }

    try:
        img = Image.open(io.BytesIO(file_bytes))
        gray = np.array(img.convert("L"))

        variance = float(np.var(gray))

        # Nonlinear scaling makes AI textures trigger higher
        score = min((variance / 3500.0) ** 0.75, 1.0)

        return {
            "ai_image_probability": round(score, 4),
            "signals": [f"Pixel variance anomaly: {variance:.2f}"],
            "image_stats": {
                "dimensions": f"{img.width}x{img.height}"
            },
        }

    except Exception as e:
        logger.exception("Image processing failed")
        return {
            "ai_image_probability": 0.0,
            "signals": [f"Processing error: {str(e)}"],
        }


# ─────────────────────────────────────────────
# PPS CALCULATION (Stronger Model)
# ─────────────────────────────────────────────

def compute_forensic_pps(
    deepfake_score: float,
    video_deepfake_prob: float,
    audio_spoof_prob: float,
    image_ai_prob: float,
    emotion_score: float,
    manipulation_score: float,
    virality_score: float,
) -> Dict[str, Any]:

    # Stronger media emphasis
    media_score = max(
        deepfake_score,
        video_deepfake_prob * 100,
        image_ai_prob * 100,
    )

    blended = 0.80 * media_score + 0.20 * (audio_spoof_prob * 100)

    # Adjusted weights (more emotion impact)
    df = 0.35 * blended
    em = 0.35 * emotion_score
    mp = 0.20 * manipulation_score
    vr = 0.10 * virality_score

    pps = min(df + em + mp + vr, 100.0)

    virality_risk = min(
        (emotion_score / 100)
        * (virality_score / 100)
        * (blended / 100),
        1.0,
    )

    return {
        "pps": round(pps, 2),
        "blended_deepfake_score": round(blended, 2),
        "virality_risk": round(virality_risk, 4),
        "contribution_breakdown": {
            "deepfake_component": round(df, 2),
            "emotional_component": round(em, 2),
            "manipulation_component": round(mp, 2),
            "virality_component": round(vr, 2),
        },
    }