import pytest
from PIL import Image
import os

import backend.math_recognition as mr
from backend.math_recognition import recognize_math_in_text


def test_recognize_math_without_image():
    text = "No image provided"
    result = recognize_math_in_text(text)
    assert result == text  # unchanged when no image_path


def test_recognize_math_with_image(monkeypatch, tmp_path):
    # Create a small dummy image
    img_path = tmp_path / "math.png"
    Image.new("RGB", (5, 5), (0, 0, 0)).save(str(img_path))

    # Ensure credentials are set (even though _call_mathpix will be stubbed)
    monkeypatch.setenv("MATHPIX_APP_ID", "test_id")
    monkeypatch.setenv("MATHPIX_APP_KEY", "test_key")

    # Stub out the API call to return a known LaTeX snippet
    monkeypatch.setattr(mr, "_call_mathpix", lambda img_b64: "E=mc^2")

    raw = "Here is some text"
    enriched = recognize_math_in_text(raw, str(img_path))

    # Should contain the original text
    assert raw in enriched
    # Should append a display-math block
    assert "\\[" in enriched and "E=mc^2" in enriched and enriched.rstrip().endswith("\\]")
