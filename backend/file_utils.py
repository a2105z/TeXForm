import os
import shutil
import tempfile
from typing import Any, List

from backend.pdf_utils import pdf_to_images


def _saved_upload_path(uploaded_file: Any, work_dir: str) -> str:
    """
    Save an uploaded file (e.g. Streamlit UploadedFile) into work_dir
    and return the path. Infers extension from filename or content type if needed.
    """
    raw_name = getattr(uploaded_file, "name", "") or "upload"
    ext = os.path.splitext(raw_name)[1].lower()

    if not ext and hasattr(uploaded_file, "type") and uploaded_file.type:
        mime = (uploaded_file.type or "").lower()
        if "pdf" in mime:
            ext = ".pdf"
        elif "png" in mime:
            ext = ".png"
        elif "jpeg" in mime or "jpg" in mime:
            ext = ".jpg"
        elif "tiff" in mime:
            ext = ".tiff"
        elif "bmp" in mime:
            ext = ".bmp"
        else:
            ext = ".bin"

    if not ext:
        ext = ".bin"

    base = os.path.basename(raw_name) if raw_name else "upload"
    if not os.path.splitext(base)[1]:
        base = (base or "upload") + ext
    out_path = os.path.join(work_dir, base)

    data = uploaded_file.read() if callable(getattr(uploaded_file, "read", None)) else uploaded_file.getvalue()
    with open(out_path, "wb") as f:
        f.write(data)
    return out_path


def paths_from_upload(uploaded_file: Any, work_dir: str) -> List[str]:
    """
    Turn a Streamlit-style upload (object with .name and .read() or .getvalue())
    into a list of image file paths for downstream processing.

    The file is written into work_dir (caller must create and own work_dir so
    that paths remain valid for the duration of use). PDFs become one path per
    page; a single image becomes one path.
    """
    os.makedirs(work_dir, exist_ok=True)
    saved_path = _saved_upload_path(uploaded_file, work_dir)
    return prepare_input_images(saved_path, work_dir)


def prepare_input_images(upload_path: str, output_folder: str) -> List[str]:
    """
    Given a path to an uploaded file (PDF or image), convert it
    into one-or-more image file paths for downstream processing.

    - PDFs → get split into pages via pdf_to_images()
    - Single images → copied into our working folder

    Returns a sorted list of image file paths.
    """
    os.makedirs(output_folder, exist_ok=True)
    ext = os.path.splitext(upload_path)[1].lower()

    if ext == ".pdf":

        # split PDF into page images
        return pdf_to_images(upload_path, output_folder)

    elif ext in {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}:

        # just copy the single image
        dst = os.path.join(output_folder, f"page_001{ext}")
        shutil.copy(upload_path, dst)
        return [dst]

    else:
        raise ValueError(f"Unsupported file type '{ext}'. Upload PDF or image.")
