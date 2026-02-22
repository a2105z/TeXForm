import os
from typing import List, Optional

import numpy as np
import torch
from PIL import Image

from backend.config_loader import get

_processor = None
_model = None
_device = None


def _ensure_model_loaded():
    """Lazy-load the TrOCR model and processor once."""
    global _processor, _model, _device

    if _processor is not None and _model is not None:
        return

    os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    except ImportError as e:
        raise RuntimeError(
            f"Failed to import transformers: {e}. "
            "Please install: pip install transformers"
        ) from e

    model_name = get("ocr_engine.model_name", "microsoft/trocr-base-handwritten")
    _processor = TrOCRProcessor.from_pretrained(model_name)
    _model = VisionEncoderDecoderModel.from_pretrained(model_name)

    device_str = (get("ocr_engine.device") or "").strip().lower()
    if device_str == "cpu":
        _device = torch.device("cpu")
    elif device_str == "cuda" and torch.cuda.is_available():
        _device = torch.device("cuda")
    else:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _model.to(_device)


# ---------------------------------------------------------------------------
# Line segmentation — split a page image into individual text-line crops
# Uses horizontal projection profile (no extra ML dependency needed).
# ---------------------------------------------------------------------------

def _segment_lines(image: Image.Image, min_line_height: int = 15) -> List[Image.Image]:
    """
    Split a page image into horizontal line crops using projection profile.

    1. Convert to grayscale, binarise (Otsu-style threshold).
    2. Compute row-wise ink density (horizontal projection).
    3. Find contiguous runs of rows with ink → each run is a text line.
    4. Crop each line with a small vertical padding.

    Returns a list of PIL images, one per detected line (top→bottom).
    Falls back to returning the whole image if no lines are detected.
    """
    gray = np.array(image.convert("L"), dtype=np.float32)
    threshold = gray.mean() - 30  # simple adaptive threshold
    ink = (gray < max(threshold, 80)).astype(np.uint8)

    row_ink = ink.sum(axis=1)
    # A row counts as "has text" if > 1% of its width has ink
    width = ink.shape[1]
    text_rows = row_ink > (width * 0.01)

    lines: List[Image.Image] = []
    in_line = False
    start = 0
    h = image.height
    pad = 4

    for y in range(len(text_rows)):
        if text_rows[y] and not in_line:
            in_line = True
            start = y
        elif not text_rows[y] and in_line:
            in_line = False
            if y - start >= min_line_height:
                top = max(0, start - pad)
                bottom = min(h, y + pad)
                lines.append(image.crop((0, top, image.width, bottom)))
            start = y

    # handle line that extends to the bottom of the page
    if in_line and h - start >= min_line_height:
        top = max(0, start - pad)
        lines.append(image.crop((0, top, image.width, h)))

    if not lines:
        return [image]

    return lines


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ocr_text_from_page(
    image_path: str,
    max_length: Optional[int] = None,
    num_beams: Optional[int] = None,
) -> str:
    """
    Perform OCR on a full page image using TrOCR.

    The page is first segmented into individual text lines (via horizontal
    projection), then each line is fed to TrOCR independently.  The per-line
    results are joined with newlines and returned.
    """
    _ensure_model_loaded()

    if max_length is None:
        max_length = get("ocr_engine.max_length", 512)
    if num_beams is None:
        num_beams = get("ocr_engine.num_beams", 4)
    max_length = max(1, min(int(max_length), 1024))
    num_beams = max(1, min(int(num_beams), 16))

    page_image = Image.open(image_path).convert("RGB")
    line_images = _segment_lines(page_image)

    texts: List[str] = []
    for line_img in line_images:
        pixel_values = _processor(images=line_img, return_tensors="pt").pixel_values.to(_device)
        generated_ids = _model.generate(
            pixel_values,
            max_length=max_length,
            num_beams=num_beams,
            early_stopping=True,
        )
        decoded = _processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        line_text = decoded.strip()
        if line_text:
            texts.append(line_text)

    return "\n".join(texts)
