"""
Tests for backend.file_utils: paths_from_upload and prepare_input_images.
"""
import os

import pytest

from backend.file_utils import paths_from_upload, prepare_input_images


class MockUploadedFile:
    """Streamlit-like upload: .name, .read() or .getvalue()."""

    def __init__(self, name: str, data: bytes, content_type: str = ""):
        self.name = name
        self._data = data
        self.type = content_type

    def read(self) -> bytes:
        return self._data

    def getvalue(self) -> bytes:
        return self._data


def test_paths_from_upload_single_image(tmp_path):
    """paths_from_upload with a single image returns one path; file type is preserved."""
    png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    upload = MockUploadedFile("notes.png", png_data, "image/png")
    paths = paths_from_upload(upload, str(tmp_path))
    assert isinstance(paths, list)
    assert len(paths) == 1
    assert paths[0].endswith(".png")
    assert os.path.isfile(paths[0])
    assert open(paths[0], "rb").read() == png_data


def test_paths_from_upload_pdf(tmp_path):
    """paths_from_upload with a PDF delegates to prepare_input_images; pdf_to_images is used."""
    # Minimal valid PDF bytes
    pdf_data = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n178\n%%EOF"
    upload = MockUploadedFile("doc.pdf", pdf_data, "application/pdf")
    paths = paths_from_upload(upload, str(tmp_path))
    assert isinstance(paths, list)
    # PDF is split into pages by pdf_to_images; one page => one PNG
    assert len(paths) >= 1
    for p in paths:
        assert p.endswith(".png")
        assert os.path.isfile(p)


def test_prepare_input_images_single_image(tmp_path):
    """prepare_input_images with one image returns one path with correct extension."""
    src = tmp_path / "input.jpg"
    src.write_bytes(b"fake jpeg content")
    out_dir = tmp_path / "out"
    paths = prepare_input_images(str(src), str(out_dir))
    assert paths == [str(out_dir / "page_001.jpg")]
    assert out_dir.joinpath("page_001.jpg").read_bytes() == b"fake jpeg content"


def test_prepare_input_images_unsupported_extension(tmp_path):
    """prepare_input_images raises ValueError for unsupported file type."""
    src = tmp_path / "file.xyz"
    src.write_bytes(b"x")
    with pytest.raises(ValueError, match="Unsupported file type"):
        prepare_input_images(str(src), str(tmp_path / "out"))


def test_paths_from_upload_creates_work_dir(tmp_path):
    """paths_from_upload creates work_dir if it does not exist."""
    work_dir = tmp_path / "sub" / "dir"
    assert not work_dir.exists()
    png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    upload = MockUploadedFile("x.png", png_data)
    paths = paths_from_upload(upload, str(work_dir))
    assert work_dir.exists()
    assert len(paths) == 1
    assert paths[0].startswith(str(work_dir))
