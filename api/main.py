"""
TeXForm API: upload a PDF or image, get back LaTeX and optional PDF.
"""
import os
import sys

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TORCH", "1")

# Block TensorFlow from being imported by transformers.
# Even with TRANSFORMERS_NO_TF=1, some versions of transformers unconditionally
# import TF in image_transforms.py, hitting the ml_dtypes "handle" crash.
# The stub needs __spec__ so torch._dynamo.trace_rules doesn't crash on find_spec().
if "tensorflow" not in sys.modules:
    _fake_tf = type(sys)("tensorflow")
    _fake_tf.__version__ = "0.0.0"
    _fake_tf.__spec__ = None  # torch.dynamo may inspect this; None is fine in newer PyTorch
    import importlib
    _fake_tf.__spec__ = importlib.machinery.ModuleSpec("tensorflow", None)
    sys.modules["tensorflow"] = _fake_tf

import base64
import logging
import re
import sys
import tempfile
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config_loader import get
from backend.file_utils import prepare_input_images
from backend.latex_generator import compile_latex_to_pdf, generate_full_document
from backend.math_recognition import recognize_math_in_text
from backend.ocr_engine import ocr_text_from_page

# Configure logging
log_level = get("logging.level", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Limits
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
FILENAME_SAFE = re.compile(r"^[a-zA-Z0-9_.-]+$")

app = FastAPI(
    title="TeXForm API",
    description="Handwritten notes → LaTeX: upload PDF or image, get LaTeX and optional PDF.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _safe_filename(filename: str) -> str:
    """Return a safe basename; no path traversal."""
    base = os.path.basename(filename).strip()
    if not base:
        return "upload"
    if not FILENAME_SAFE.match(base):
        base = "upload"
    return base[:200]


def _get_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return ext if ext in ALLOWED_EXTENSIONS else ""


@app.get("/api/health")
def health():
    """Health check for load balancers and scripts."""
    return {"status": "ok"}


@app.post("/api/process")
async def process_upload(file: UploadFile = File(...)):
    """
    Upload a PDF or image (PNG, JPG, JPEG). Returns LaTeX source and optional PDF (base64).
    Processing can take 30–120 seconds for multi-page PDFs.
    """
    ext = _get_extension(file.filename or "")
    if not ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_BYTES // (1024*1024)} MB",
        )

    safe_name = _safe_filename(file.filename or "upload")
    if not safe_name.lower().endswith(ext):
        safe_name = (safe_name or "upload") + ext

    with tempfile.TemporaryDirectory() as work_dir:
        upload_path = os.path.join(work_dir, safe_name)
        with open(upload_path, "wb") as f:
            f.write(content)

        try:
            page_image_paths = prepare_input_images(upload_path, work_dir)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not page_image_paths:
            raise HTTPException(status_code=400, detail="No pages or images produced from upload.")

        all_pages_text = []
        for img_path in page_image_paths:
            try:
                raw_text = ocr_text_from_page(img_path)
                enriched = recognize_math_in_text(raw_text, img_path)
                all_pages_text.append(enriched)
            except Exception as e:
                logger.exception("OCR or math recognition failed for %s", img_path)
                raise HTTPException(status_code=500, detail=f"Processing failed: {e}") from e

        combined = "\n\n".join(all_pages_text)
        try:
            latex_doc = generate_full_document(combined)
        except Exception as e:
            logger.exception("LaTeX generation failed")
            raise HTTPException(status_code=500, detail=f"LaTeX generation failed: {e}") from e

        pdf_base64: Optional[str] = None
        try:
            pdf_bytes = compile_latex_to_pdf(latex_doc)
            pdf_base64 = base64.b64encode(pdf_bytes).decode("ascii")
        except Exception as e:
            logger.warning("PDF compilation failed (user can still download .tex): %s", e)

    return {"latex": latex_doc, "pdf_base64": pdf_base64}


# Serve React static files in production (when built) - mount AFTER routes
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
