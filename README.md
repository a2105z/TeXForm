---
title: TeXForm
emoji: "📝"
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
suggested_hardware: cpu-basic
---

# TeXForm

**Handwritten notes → LaTeX.**

Upload a PDF or image. TeXForm segments lines, runs handwriting OCR (TrOCR), recognizes math, and assembles a downloadable `.tex` or compiled PDF.

**[Live demo on Hugging Face Spaces →](https://huggingface.co/spaces/amittal417/texform)**

## Pipeline

```
PDF / image → line segmentation → TrOCR (handwriting) → math recognition → LaTeX document
```

| Piece | Choice |
| --- | --- |
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python 3.11) |
| OCR | `microsoft/trocr-base-handwritten` |
| Math | Pix2Text (free) or MathPix (optional) |
| Deploy | Docker (Hugging Face Spaces / Render) |

## Features

- Upload PDF or images (PNG, JPG, JPEG)
- Line segmentation for more accurate OCR
- Math / formula recognition alongside prose
- Download as `.tex` or PDF
- One-command Docker deploy

## Quick start (local)

```bash
docker build -t texform .
docker run -p 7860:7860 texform
# open http://localhost:7860
```

Or without Docker: run the FastAPI backend and Vite frontend from their respective folders (see repo layout).

## Hosting notes

The public Space runs on free CPU (expect ~30–90s/page). It may sleep after inactivity — the first request after sleep can be slow while the container wakes.

[Deploy to Render](https://render.com/deploy?repo=https://github.com/a2105z/TeXForm) is also supported via the included render config.
