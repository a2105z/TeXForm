import base64
import logging
import os
from typing import Optional

import requests

from backend.config_loader import get

# Placeholder values in config that mean "not set"
_CRED_PLACEHOLDERS = {"<YOUR_MATHPIX_APP_ID>", "<YOUR_MATHPIX_APP_KEY>", ""}

# Optional free math backend (Pix2Text); used when MathPix is not configured
_PIX2TEXT_AVAILABLE: Optional[bool] = None


def _pix2text_available() -> bool:
    global _PIX2TEXT_AVAILABLE
    if _PIX2TEXT_AVAILABLE is not None:
        return _PIX2TEXT_AVAILABLE
    try:
        from pix2text import Pix2Text  # noqa: F401
        _PIX2TEXT_AVAILABLE = True
    except ImportError:
        _PIX2TEXT_AVAILABLE = False
    return _PIX2TEXT_AVAILABLE


def _call_pix2text(image_path: str) -> Optional[str]:
    """
    Use Pix2Text (free, offline) to extract text and formulas from the image.
    Returns a string (e.g. Markdown with LaTeX) or None on failure or if not installed.
    """
    if not _pix2text_available():
        return None
    try:
        from pix2text import Pix2Text
        p2t = Pix2Text.from_config()
        # Prefer recognize() (1.x); fallback to recognize_text_formula()
        if hasattr(p2t, "recognize"):
            out = p2t.recognize(image_path)
        elif hasattr(p2t, "recognize_text_formula"):
            out = p2t.recognize_text_formula(image_path, return_text=True)
        else:
            return None
        if out is None:
            return None
        if isinstance(out, str):
            return out.strip() or None
        if isinstance(out, list):
            parts = []
            for item in out:
                if hasattr(item, "get"):
                    text = item.get("text") or item.get("latex") or item.get("content")
                    if text:
                        parts.append(text)
                elif isinstance(item, str):
                    parts.append(item)
            return "\n\n".join(parts).strip() or None
        return str(out).strip() or None
    except Exception as e:
        logging.warning("Pix2Text fallback failed for %s: %s", image_path, e)
        return None


def _mathpix_credentials() -> tuple[Optional[str], Optional[str]]:
    """Return (app_id, app_key) from env first, then config, ignoring placeholders."""
    app_id = os.getenv("MATHPIX_APP_ID") or get("mathpix.app_id")
    app_key = os.getenv("MATHPIX_APP_KEY") or get("mathpix.app_key")
    if not app_id or str(app_id).strip() in _CRED_PLACEHOLDERS:
        app_id = None
    if not app_key or str(app_key).strip() in _CRED_PLACEHOLDERS:
        app_key = None
    return (app_id, app_key)


def _call_mathpix(image_b64: str) -> Optional[str]:
    """
    Send a base64‑encoded PNG to MathPix and return the 'latex_normal' result.
    Returns None on error or if credentials are missing.
    """
    app_id, app_key = _mathpix_credentials()
    if not app_id or not app_key:
        logging.warning("MathPix credentials not set; skipping math recognition.")
        return None

    api_url = get("math_recognition.api_url", "https://api.mathpix.com/v3/latex")
    timeout = get("math_recognition.timeout", 30)
    timeout = max(5, min(int(timeout) if isinstance(timeout, (int, float)) else 30, 120))

    include_mathml = get("math_recognition.include_mathml", False)
    headers = {
        "app_id": app_id,
        "app_key": app_key,
        "Content-Type": "application/json",
    }
    payload = {
        "src": f"data:image/png;base64,{image_b64}",
        "formats": ["latex_normal"],
        "data_options": {
            "include_latex": get("math_recognition.include_latex", True),
            "include_mathml": include_mathml,
        },
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("latex_normal")
    except Exception as e:
        logging.error("MathPix API error: %s", e)
        return None


def recognize_math_in_text(raw_text: str, image_path: Optional[str] = None) -> str:
    """
    Take raw OCR text and (optionally) an image; detect math via MathPix (if configured)
    or Pix2Text (free, offline fallback), and return a combined string.
    """
    enriched = raw_text.strip()

    if not image_path:
        return enriched

    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
    except Exception as e:
        logging.error("Error reading image for math recognition %s: %s", image_path, e)
        return enriched

    # Prefer MathPix when credentials are set
    latex_math = _call_mathpix(img_b64)
    if latex_math:
        enriched += "\n\n" + "\\[\n" + latex_math.strip() + "\n\\]"
        return enriched

    # Free path: Pix2Text when MathPix is not configured (or failed)
    use_free = get("math_recognition.use_free_backend", True)
    if use_free:
        p2t_result = _call_pix2text(image_path)
        if p2t_result:
            enriched += "\n\n" + p2t_result
    return enriched
