"""
Deepfake / AI-generated image detector.

Model: dima806/deepfake_vs_real_image_detection (EfficientNet-B4, HuggingFace)
Labels emitted by the model: "Fake" | "Real"

Verdict thresholds (applied to the Fake score):
  > 0.75  →  AI_GENERATED
  < 0.35  →  REAL
  else    →  UNCERTAIN
"""

from __future__ import annotations

import os
import sys
import traceback

# LOCAL DEV ONLY: bypass LibreSSL / OpenSSL incompatibility on macOS
# (urllib3 v2 cannot verify certs against LibreSSL 2.8.3 that ships with macOS).
# Remove these two lines before deploying to any non-local environment.
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

from PIL import Image
from transformers import pipeline

MODEL_ID = "dima806/deepfake_vs_real_image_detection"

AI_GENERATED_THRESHOLD = 0.75
REAL_THRESHOLD = 0.35

# Eager load at startup so failures surface immediately rather than on the
# first request, and so Flask's health endpoint always responds.
print(f"[detector] Loading model '{MODEL_ID}' …", flush=True)
_pipe = None
try:
    _pipe = pipeline("image-classification", model=MODEL_ID)
    print("[detector] Model loaded successfully.", flush=True)
except Exception:
    print("[detector] ERROR: model failed to load — /analyze will return 503.", file=sys.stderr, flush=True)
    traceback.print_exc()


def detect(image: Image.Image) -> dict:
    """
    Analyse a PIL image and return a classification result.

    Args:
        image: RGB PIL image.

    Returns:
        {
            "verdict":    "REAL" | "AI_GENERATED" | "UNCERTAIN",
            "confidence": float (0–1, probability of AI generation),
            "reason":     str (plain-English explanation),
        }

    Raises:
        RuntimeError: if the model failed to load at startup.
    """
    if _pipe is None:
        raise RuntimeError("Model is unavailable — check startup logs for the load error.")

    results = _pipe(image)

    # Build a label → score lookup (case-insensitive).
    scores: dict[str, float] = {r["label"].lower(): r["score"] for r in results}

    # "fake" score = probability the image is AI-generated.
    fake_score: float = scores.get("fake", 0.5)

    if fake_score > AI_GENERATED_THRESHOLD:
        verdict = "AI_GENERATED"
        reason = (
            f"Strong indicators of AI generation were detected "
            f"(model confidence {fake_score:.0%})."
        )
    elif fake_score < REAL_THRESHOLD:
        verdict = "REAL"
        real_score = 1.0 - fake_score
        reason = (
            f"No significant signs of AI generation were found "
            f"(authenticity confidence {real_score:.0%})."
        )
    else:
        verdict = "UNCERTAIN"
        reason = (
            f"The model could not confidently determine whether this image "
            f"is real or AI-generated (AI score {fake_score:.0%})."
        )

    return {
        "verdict": verdict,
        "confidence": round(fake_score, 4),
        "reason": reason,
    }
