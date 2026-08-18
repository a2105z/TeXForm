# Getting started with TeXForm

This guide walks you through setting up TeXForm, running the app, and producing your first LaTeX document from handwritten notes.

## 1. Clone the repository

```bash
git clone <your-repo-url>
cd TeXform
```

## 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

## 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, PyTorch/Transformers (TrOCR), Pillow, PyMuPDF, requests, PyYAML, pytest, and optionally Pix2Text for free math recognition.

## 4. Install frontend dependencies (for development)

```bash
cd frontend
npm install
cd ..
```

## 5. Optional: set MathPix (or use free math)

- **Paid path:** Set `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` environment variables, or add them to `config/secrets.yaml` (replace the placeholders).
- **Free path:** If you do not set MathPix, TeXForm uses [Pix2Text](https://github.com/breezedeus/Pix2Text) when installed (`pip install pix2text` is included in `requirements.txt`). No API keys needed. You can disable this with `math_recognition.use_free_backend: false` in `config/default.yaml`.

## 6. Run the app (development)

**Terminal 1 — Backend API (recommended):**
```bash
# From project root — sets TRANSFORMERS_NO_TF so OCR works without TensorFlow errors
python run.py
```
Or with uvicorn directly (set env first to avoid "handle" conversion errors):
```bash
# Windows PowerShell: $env:TRANSFORMERS_NO_TF = "1"; uvicorn api.main:app --reload --port 8000
# Linux/macOS: export TRANSFORMERS_NO_TF=1 && uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
# From project root
cd frontend
npm run dev
```

Open `http://localhost:5173` (Vite dev server). The frontend proxies `/api` requests to `http://localhost:8000`.

## 7. Upload a sample and download

1. On the TeXForm page (`http://localhost:5173`), drag-and-drop or click to choose a PDF or image (PNG, JPG, JPEG) of handwritten notes.
2. Click **"Convert to LaTeX"**.
3. Wait for processing (30–120 seconds for multi-page PDFs). The app converts pages to images, runs handwriting OCR, then math recognition (if configured).
4. Review the generated LaTeX in the preview area.
5. Use **"Download .tex"** to save the source file, and **"Download PDF"** to get a compiled PDF (requires a LaTeX distribution on the machine running the API).

If PDF download is not available (e.g. no LaTeX installed on the server), you still get the `.tex` file.

## Config file location and main options

- **Default config:** `config/default.yaml`  
  - `pdf_utils.dpi` — resolution for PDF → image (default `200`)
  - `ocr_engine.model_name`, `max_length`, `num_beams`, `device` — TrOCR settings
  - `math_recognition.use_free_backend` — use Pix2Text when MathPix is not set (default `true`)
  - `latex_generator.title`, `document_class`, `page_geometry`, etc. — LaTeX preamble and metadata

- **Secrets / API keys:** `config/secrets.yaml` (or environment variables)  
  - `mathpix.app_id`, `mathpix.app_key` — MathPix API credentials (optional)

Changes to config files take effect after restarting the API server.
