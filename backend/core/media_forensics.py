"""
DPIS — Advanced Multi-Modal Media Forensics Engine (v3.4)

• Stronger separation curves
• Nonlinear anomaly escalation
• Cross-signal amplification
"""

from __future__ import annotations

import io
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Optional Dependencies (Graceful Fallback)
# ─────────────────────────────────────────────

try:
    import cv2
    _CV2_OK = True
except ImportError:
    _CV2_OK = False

try:
    import librosa
    import soundfile as sf  # noqa
    _LIBROSA_OK = True
except ImportError:
    _LIBROSA_OK = False

try:
    from PIL import Image
    _PIL_OK = True
except ImportError:
    _PIL_OK = False


# ─────────────────────────────────────────────
# VIDEO FORENSICS
# ─────────────────────────────────────────────

def analyze_video_frames(file_bytes: bytes) -> Dict[str, Any]:

    if not _CV2_OK or np is None:
        return {
            "deepfake_probability": 0.0,
            "signals": ["OpenCV not installed"],
        }

    try:
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        cap = cv2.VideoCapture(tmp_path)
        os.unlink(tmp_path)

        if not cap.isOpened():
            return {
                "deepfake_probability": 0.0,
                "signals": ["Cannot open video"],
            }

        lap_vars = []
        temporal_diff = []
        prev_gray = None
        frame_count = 0

        while frame_count < 80:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            lap_vars.append(cv2.Laplacian(gray, cv2.CV_64F).var())

            if prev_gray is not None:
                diff = np.mean(np.abs(gray - prev_gray))
                temporal_diff.append(diff)

            prev_gray = gray
            frame_count += 1

        cap.release()

        if not lap_vars:
            return {
                "deepfake_probability": 0.0,
                "signals": ["No frames sampled"],
            }

        sharpness_instability = float(np.std(lap_vars))
        motion_instability = float(np.std(temporal_diff)) if temporal_diff else 0.0

        combined = (sharpness_instability / 500.0) + (motion_instability / 50.0)
        score = min(combined ** 0.75, 1.0)

        return {
            "deepfake_probability": round(score, 4),
            "signals": [
                f"Sharpness instability: {sharpness_instability:.2f}",
                f"Temporal instability: {motion_instability:.2f}",
            ],
            "frame_stats": {"frames_sampled": frame_count},
        }

    except Exception as e:
        logger.exception("Video processing failed")
        return {
            "deepfake_probability": 0.0,
            "signals": [str(e)],
        }


# ─────────────────────────────────────────────
# AUDIO FORENSICS
# ─────────────────────────────────────────────

def analyze_audio_waveform(file_bytes: bytes) -> Dict[str, Any]:

    if not _LIBROSA_OK or np is None:
        return {
            "spoof_probability": 0.0,
            "signals": ["librosa not installed"],
        }

    try:
        buf = io.BytesIO(file_bytes)
        y, sr = librosa.load(buf, sr=None, mono=True)

        flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
        rms = float(np.mean(librosa.feature.rms(y=y)))

        anomaly = (flatness * 6.0) + (zcr * 2.0) + (abs(rms - 0.1) * 3.0)
        score = min(anomaly ** 0.8, 1.0)

        return {
            "spoof_probability": round(score, 4),
            "signals": [
                f"Spectral flatness: {flatness:.5f}",
                f"Zero-cross rate: {zcr:.5f}",
                f"RMS deviation: {rms:.5f}",
            ],
            "audio_stats": {"sample_rate": sr},
        }

    except Exception as e:
        logger.exception("Audio processing failed")
        return {
            "spoof_probability": 0.0,
            "signals": [str(e)],
        }


# ─────────────────────────────────────────────
# IMAGE FORENSICS
# ─────────────────────────────────────────────

def analyze_image_artifacts(file_bytes: bytes) -> Dict[str, Any]:

    if not _PIL_OK or np is None:
        return {
            "ai_image_probability": 0.0,
            "signals": ["Pillow not installed"],
        }

    try:
        img = Image.open(io.BytesIO(file_bytes))
        gray = np.array(img.convert("L"))

        variance = float(np.var(gray))

        hist = np.histogram(gray, bins=256)[0]
        hist = hist / np.sum(hist)
        entropy = float(-np.sum(hist * np.log2(hist + 1e-7)))

        anomaly = (variance / 3000.0) + (entropy / 8.0)
        score = min(anomaly ** 0.8, 1.0)

        return {
            "ai_image_probability": round(score, 4),
            "signals": [
                f"Pixel variance: {variance:.2f}",
                f"Entropy: {entropy:.2f}",
            ],
            "image_stats": {"dimensions": f"{img.width}x{img.height}"},
        }

    except Exception as e:
        logger.exception("Image processing failed")
        return {
            "ai_image_probability": 0.0,
            "signals": [str(e)],
        }