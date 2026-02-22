# API reference

Short reference for the main functions used by TeXForm. Private helpers are not listed unless useful for integration.

---

## File and upload handling

### `paths_from_upload(uploaded_file, work_dir) -> List[str]`

**Module:** `backend.file_utils`

Turns an upload-like object (with `.name` and `.read()` or `.getvalue()`) into a list of image file paths. Writes the upload into `work_dir`, then delegates to `prepare_input_images`. PDFs yield one path per page; a single image yields one path. The caller must create and own `work_dir` so paths stay valid.

- **uploaded_file:** Object with `.name` (or `.filename`) and `.read()` or `.getvalue()`.
- **work_dir:** Directory path (created if missing). All returned paths lie under it.
- **Returns:** List of image file paths (e.g. PNGs).

---

### `prepare_input_images(upload_path, output_folder) -> List[str]`

**Module:** `backend.file_utils`

Converts a single file path (PDF or image) into one or more image paths under `output_folder`. PDFs are split into pages via `pdf_to_images`; a single image is copied as `page_001.<ext>`.

- **upload_path:** Path to a PDF or image (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`).
- **output_folder:** Directory for output images (created if missing).
- **Returns:** Sorted list of image file paths.
- **Raises:** `ValueError` for unsupported file types.

---

## PDF and images

### `pdf_to_images(pdf_path, output_folder, dpi=None) -> list`

**Module:** `backend.pdf_utils`

Renders each page of a PDF as a PNG in `output_folder`. DPI comes from config `pdf_utils.dpi` (default 200) when `dpi` is not provided; it is clamped to a valid range.

- **pdf_path:** Path to the PDF file.
- **output_folder:** Directory for output PNGs (created if missing).
- **dpi:** Optional. If `None`, uses `config.pdf_utils.dpi`.
- **Returns:** List of PNG file paths.

---

## OCR and math recognition

### `ocr_text_from_page(image_path, max_length=None, num_beams=None) -> str`

**Module:** `backend.ocr_engine`

Runs TrOCR (handwritten) on a single page image and returns the recognized text. Parameters default from config (`ocr_engine.max_length`, `ocr_engine.num_beams`) and are clamped.

- **image_path:** Path to a page image (e.g. PNG).
- **max_length:** Optional; max generated tokens.
- **num_beams:** Optional; beam search width.
- **Returns:** Recognized text string.

---

### `recognize_math_in_text(raw_text, image_path=None) -> str`

**Module:** `backend.math_recognition`

Takes raw OCR text and, if `image_path` is given, enriches it with math from the image. Uses MathPix when credentials are set; otherwise uses Pix2Text when `math_recognition.use_free_backend` is true. Math is appended as LaTeX (e.g. display-math blocks).

- **raw_text:** String from OCR.
- **image_path:** Optional path to the page image for math extraction.
- **Returns:** Combined string (OCR text + any math LaTeX).

---

## LaTeX document and PDF

### `generate_full_document(content) -> str`

**Module:** `backend.latex_generator`

Builds a full `.tex` document from mixed text and LaTeX fragments. Preamble (document class, geometry, title, etc.) comes from config. Paragraphs are classified as plain text (escaped), display math, or inline math and formatted accordingly.

- **content:** String with paragraphs separated by `\n\n`; may contain `\[...\]`, `$...$`, or plain text.
- **Returns:** Full LaTeX source as a single string.

---

### `compile_latex_to_pdf(latex_str) -> bytes`

**Module:** `backend.latex_generator`

Compiles a LaTeX string to PDF using `latexmk` if available, otherwise `pdflatex`. Runs in a temporary directory; runs the compiler twice to resolve references.

- **latex_str:** Full LaTeX document source.
- **Returns:** Raw PDF bytes.
- **Raises:** `RuntimeError` if compilation fails.

---

## HTTP API (FastAPI)

### `POST /api/process`

**Endpoint:** `/api/process`

Upload a PDF or image (PNG, JPG, JPEG) and get back LaTeX source and optional PDF (base64-encoded).

- **Request:** `multipart/form-data` with field `file` (PDF or image file)
- **Response:** JSON `{ "latex": "<full .tex string>", "pdf_base64": "<base64 string>" | null }`
- **Status codes:**
  - `200` — Success
  - `400` — Unsupported file type, file too large (>50MB), or no pages produced
  - `500` — Processing error (OCR, math recognition, or LaTeX generation failed)
- **Processing time:** 30–120 seconds for multi-page PDFs (synchronous request)

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/process \
  -F "file=@notes.pdf" \
  -o result.json
```

---

### `GET /api/health`

**Endpoint:** `/api/health`

Health check endpoint for load balancers and monitoring.

- **Response:** JSON `{ "status": "ok" }`
- **Status code:** `200`
