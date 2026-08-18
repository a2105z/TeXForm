import pytest
from PIL import Image, ImageDraw
import torch
import os

import backend.ocr_engine as ocr_engine


def test_ocr_text_from_page(monkeypatch, tmp_path):
    """OCR returns joined lines for a page with visible text lines."""
    # Create an image with two dark horizontal bands (simulating text lines)
    img = Image.new("RGB", (200, 100), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 190, 30], fill=(0, 0, 0))
    draw.rectangle([10, 50, 190, 70], fill=(0, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(str(img_path))

    dummy_tensor = torch.zeros((1, 3, 10, 10), dtype=torch.float)

    class DummyProcessor:
        def __call__(self, images, return_tensors):
            return type("obj", (), {"pixel_values": dummy_tensor})

        def batch_decode(self, generated_ids, skip_special_tokens):
            return ["decoded text"]

    class DummyModel:
        def generate(self, pixel_values, max_length, num_beams, early_stopping):
            return [[1, 2, 3]]

    monkeypatch.setattr(ocr_engine, "_processor", DummyProcessor())
    monkeypatch.setattr(ocr_engine, "_model", DummyModel())
    monkeypatch.setattr(ocr_engine, "_device", torch.device("cpu"))

    result = ocr_engine.ocr_text_from_page(str(img_path))

    # Two lines detected → two "decoded text" joined by newline
    assert result == "decoded text\ndecoded text"


def test_ocr_blank_page(monkeypatch, tmp_path):
    """OCR on a blank white page returns the whole-image fallback result."""
    img_path = tmp_path / "blank.png"
    Image.new("RGB", (100, 100), (255, 255, 255)).save(str(img_path))

    dummy_tensor = torch.zeros((1, 3, 10, 10), dtype=torch.float)

    class DummyProcessor:
        def __call__(self, images, return_tensors):
            return type("obj", (), {"pixel_values": dummy_tensor})

        def batch_decode(self, generated_ids, skip_special_tokens):
            return [""]

    class DummyModel:
        def generate(self, pixel_values, max_length, num_beams, early_stopping):
            return [[1]]

    monkeypatch.setattr(ocr_engine, "_processor", DummyProcessor())
    monkeypatch.setattr(ocr_engine, "_model", DummyModel())
    monkeypatch.setattr(ocr_engine, "_device", torch.device("cpu"))

    result = ocr_engine.ocr_text_from_page(str(img_path))
    assert result == ""
