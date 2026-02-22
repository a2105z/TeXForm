# TeXForm: Handwritten Notes → LaTeX

TeXForm turns handwritten notes (PDF or images) into LaTeX documents. Upload a PDF or image — the app segments text lines, runs handwriting OCR (TrOCR), detects math (MathPix or Pix2Text), and assembles a LaTeX document you can download as `.tex` or compiled PDF.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/a2105z/TeXForm)

## Features

- **Upload** PDF or images (PNG, JPG, JPEG)
- **Line segmentation** — splits full pages into individual text lines for accurate OCR
- **Handwriting OCR** via TrOCR (Microsoft)
- **Math / formula recognition** via MathPix (optional, paid) or Pix2Text (optional, free)
- **Single LaTeX document** with download as `.tex` or PDF
- **Modern React frontend** + FastAPI backend
- **Docker ready** — one-command deployment

## Quick deploy

### One-click deploy to Render

Click the button above, or go to:

```
https://render.com/deploy?repo=https://github.com/a2105z/TeXForm
```

### Deploy to Hugging Face Spaces

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space) — select **Docker** as the SDK
2. Clone this repo and push to the Space:
   ```bash
   git clone https://github.com/a2105z/TeXForm.git
   cd TeXForm
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/texform
   git push hf main
   ```

## Prerequisites (local development)

- **Python** 3.10+
- **Node.js** 18+ (for frontend dev; not needed for Docker)
- **LaTeX** (e.g. TeX Live, MiKTeX) — optional, for PDF compilation
- **MathPix** (optional): Set `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` env vars

## Install

```bash
git clone https://github.com/a2105z/TeXForm.git
cd TeXForm

# Backend
pip install -r requirements.txt

# Frontend (for development)
cd frontend
npm install
```

See [docs/getting_started.md](docs/getting_started.md) for a step-by-step guide.

## How to run

### Run locally (development)

**Terminal 1 — Backend API:**
```bash
python run.py
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`. The frontend proxies `/api` to `http://localhost:8000`.

### Run with Docker

```bash
docker build -t texform .
docker run -p 8000:8000 -e PORT=8000 texform
```

Open `http://localhost:8000`.

### Run with docker-compose

```bash
docker-compose up --build
```

## Configuration

| What | Where |
|------|--------|
| App defaults (DPI, OCR model, LaTeX preamble, etc.) | `config/default.yaml` |
| MathPix / secrets | `config/secrets.yaml` or env: `MATHPIX_APP_ID`, `MATHPIX_APP_KEY` |
| Free math (Pix2Text) | `math_recognition.use_free_backend` in `config/default.yaml` (default: `true`) |

## Math recognition options

| Option | Cost | How it works |
|--------|------|----------------|
| **Free (Pix2Text)** | None | Uses [Pix2Text](https://github.com/breezedeus/Pix2Text) if installed. Runs offline. |
| **Paid (MathPix)** | API subscription | Set `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` environment variables. |

With neither configured, you still get handwriting OCR and LaTeX output — only the math detection step is skipped.

## API

- `POST /api/process` — Upload a file (multipart/form-data), returns `{ "latex": "...", "pdf_base64": "..." | null }`
- `GET /api/health` — Health check

See [docs/api_reference.md](docs/api_reference.md) for details.

## Documentation

- [Getting started](docs/getting_started.md)
- [API reference](docs/api_reference.md)

## Contributing

Contributions welcome. Open an issue or pull request.

## License

See [LICENSE](LICENSE).
