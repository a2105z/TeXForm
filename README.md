# TeXForm: Handwritten Notes → LaTeX

TeXForm turns handwritten notes (PDF or images) into LaTeX documents. You upload a PDF or image; the app converts pages to images, runs handwriting OCR (TrOCR), detects and converts math (via MathPix or free Pix2Text), then assembles a LaTeX document you can download as `.tex` or compile to PDF.

## Features

- **Upload** PDF or images (PNG, JPG, JPEG)
- **Handwriting OCR** via TrOCR (Microsoft)
- **Math / formula recognition** via MathPix (optional, paid) or Pix2Text (optional, free)
- **Single LaTeX document** with download as `.tex` or PDF
- **Modern React frontend** + FastAPI backend

## Prerequisites

- **Python** 3.10+ (for backend API)
- **Node.js** 18+ (for frontend development; not needed for Docker)
- **LaTeX** (e.g. TeX Live, MiKTeX) if you want PDF downloads from the API
- **MathPix** (optional): Set `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` env vars for paid math recognition

## Install

```bash
git clone <your-repo-url>
cd TeXform

# Backend
pip install -r requirements.txt

# Frontend (for development)
cd frontend
npm install
```

See [docs/getting_started.md](docs/getting_started.md) for a step-by-step guide.

## How to run

### Run locally (development)

**Terminal 1 — Backend API (recommended):**
```bash
# From project root — sets TRANSFORMERS_NO_TF=1 so OCR works without TensorFlow/ml_dtypes errors
python run.py
```
Or with uvicorn directly (set env first to avoid "handle" conversion errors):
```bash
# Windows PowerShell
$env:TRANSFORMERS_NO_TF = "1"; uvicorn api.main:app --reload --port 8000
# Linux/macOS
export TRANSFORMERS_NO_TF=1 && uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
# From project root
cd frontend
npm run dev
```

Open `http://localhost:5173` (Vite dev server). The frontend proxies `/api` requests to `http://localhost:8000`.

### Run with Docker (production)

Build and run the app in a container (includes React build + FastAPI + LaTeX):

```bash
docker build -t texform .
docker run -p 8000:8000 texform
```

Then open `http://localhost:8000`. The API serves the React app at `/` and exposes endpoints at `/api/*`.

### Run with docker-compose

```bash
docker-compose up --build
```

The app is exposed on port 8000. Set `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` in `.env` or pass them to docker-compose.

## Configuration and environment

| What | Where |
|------|--------|
| App defaults (DPI, OCR model, LaTeX preamble, etc.) | `config/default.yaml` |
| MathPix / secrets | `config/secrets.yaml` or env: `MATHPIX_APP_ID`, `MATHPIX_APP_KEY` |
| Free math (Pix2Text) | `math_recognition.use_free_backend` in `config/default.yaml` (default: `true`) |

MathPix is optional: you can use the free Pix2Text path when MathPix is not set, or skip math recognition and still get OCR + LaTeX. See the [Free vs paid math recognition](#free-vs-paid-math-recognition) section below.

## Free vs paid math recognition

| Option | Cost | How it works |
|--------|------|----------------|
| **Free (Pix2Text)** | No API cost | When MathPix is not configured, TeXForm uses [Pix2Text](https://github.com/breezedeus/Pix2Text) if installed. Runs offline; output is text + formulas in Markdown/LaTeX. |
| **Paid (MathPix)** | API subscription | Set `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` environment variables. TeXForm sends page images to the MathPix API for math recognition. |

With neither MathPix nor Pix2Text, you still get handwriting OCR and the assembled LaTeX; only the extra math-from-image step is skipped.

## API

- `POST /api/process` — Upload a file (multipart/form-data), get back `{ "latex": "...", "pdf_base64": "..." | null }`
- `GET /api/health` — Health check

See [docs/api_reference.md](docs/api_reference.md) for details.

## Documentation

- [Getting started](docs/getting_started.md) — Clone, venv, install, run, upload a sample, download .tex/PDF; config file location and main options
- [API reference](docs/api_reference.md) — Backend function signatures

## Contributing

Contributions are welcome. Open an issue or pull request on the repository.

## License

See [LICENSE](LICENSE).
