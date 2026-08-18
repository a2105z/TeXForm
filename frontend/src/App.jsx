import { useState, useCallback, useEffect } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || '/api'
const ALLOWED_TYPES = ['.pdf', '.png', '.jpg', '.jpeg']
const MAX_SIZE_MB = 50
const REQUEST_TIMEOUT_MS = 300_000 // 5 min for large multi-page PDFs

export default function App() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState('')
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [backendOk, setBackendOk] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(8000) })
      .then((r) => r.ok && setBackendOk(true))
      .catch(() => setBackendOk(false))
  }, [])

  const reset = useCallback(() => {
    setFile(null)
    setPreview(null)
    setError(null)
    setResult(null)
    setProgress('')
  }, [])

  const handleFile = useCallback((f) => {
    if (!f) return
    const ext = '.' + (f.name.split('.').pop() || '').toLowerCase()
    if (!ALLOWED_TYPES.includes(ext)) {
      setError(`Unsupported type. Allowed: ${ALLOWED_TYPES.join(', ')}`)
      return
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File too large. Maximum: ${MAX_SIZE_MB} MB`)
      return
    }
    setError(null)
    setResult(null)
    setFile(f)

    if (f.type.startsWith('image/')) {
      const url = URL.createObjectURL(f)
      setPreview(url)
    } else {
      setPreview(null)
    }
  }, [])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer?.files?.[0])
  }, [handleFile])

  const onDragOver = useCallback((e) => { e.preventDefault(); setDragOver(true) }, [])
  const onDragLeave = useCallback((e) => { e.preventDefault(); setDragOver(false) }, [])
  const onInputChange = useCallback((e) => { handleFile(e.target?.files?.[0]) }, [handleFile])

  const process = useCallback(async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    setProgress('Uploading file...')

    const formData = new FormData()
    formData.append('file', file)
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

    const progressSteps = [
      { ms: 3000, msg: 'Converting pages to images...' },
      { ms: 8000, msg: 'Running handwriting OCR (TrOCR)...' },
      { ms: 25000, msg: 'Detecting math and formulas...' },
      { ms: 60000, msg: 'Assembling LaTeX document...' },
      { ms: 120000, msg: 'Still working — large files take longer...' },
    ]
    const timers = progressSteps.map(({ ms, msg }) =>
      setTimeout(() => setProgress(msg), ms)
    )

    try {
      const res = await fetch(`${API_BASE}/process`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      })
      clearTimeout(timeoutId)
      timers.forEach(clearTimeout)
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(data.detail || res.statusText || 'Processing failed')
        return
      }
      setResult({ latex: data.latex || '', pdfBase64: data.pdf_base64 ?? null })
      setProgress('')
    } catch (err) {
      clearTimeout(timeoutId)
      timers.forEach(clearTimeout)
      if (err.name === 'AbortError') {
        setError('Request timed out. Try a smaller file or fewer pages.')
      } else {
        setError(err.message || 'Network or server error')
      }
    } finally {
      setLoading(false)
      setProgress('')
    }
  }, [file])

  const downloadTex = useCallback(() => {
    if (!result?.latex) return
    const blob = new Blob([result.latex], { type: 'text/x-tex' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'texform_notes.tex'
    a.click()
    URL.revokeObjectURL(url)
  }, [result])

  const downloadPdf = useCallback(() => {
    if (!result?.pdfBase64) return
    const bin = atob(result.pdfBase64)
    const arr = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i)
    const blob = new Blob([arr], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'texform_notes.pdf'
    a.click()
    URL.revokeObjectURL(url)
  }, [result])

  const copyLatex = useCallback(() => {
    if (!result?.latex) return
    navigator.clipboard.writeText(result.latex).catch(() => {})
  }, [result])

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-icon">T<sub>E</sub>X</span>
          <h1>TeXForm</h1>
        </div>
        <p className="tagline">Handwritten notes &rarr; LaTeX, instantly</p>
        {backendOk === false && (
          <div className="message warning" role="status">
            Backend is not reachable. The server may be starting up — please wait a moment and refresh.
          </div>
        )}
      </header>

      <main className="main">
        {!result ? (
          <>
            <section className="intro">
              <div className="steps">
                <div className="step">
                  <span className="step-num">1</span>
                  <span>Upload a <strong>PDF</strong> or <strong>image</strong> of handwritten notes</span>
                </div>
                <div className="step">
                  <span className="step-num">2</span>
                  <span>TeXForm runs <strong>handwriting OCR</strong> and <strong>math detection</strong></span>
                </div>
                <div className="step">
                  <span className="step-num">3</span>
                  <span>Download your <strong>LaTeX document</strong> or <strong>compiled PDF</strong></span>
                </div>
              </div>
            </section>

            <div
              className={`upload-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
            >
              <input
                type="file"
                id="file-input"
                accept={ALLOWED_TYPES.join(',')}
                onChange={onInputChange}
                className="file-input"
              />
              <label htmlFor="file-input" className="upload-label">
                {file ? (
                  <div className="file-selected">
                    {preview && (
                      <img src={preview} alt="preview" className="file-preview" />
                    )}
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">({(file.size / 1024).toFixed(0)} KB)</span>
                  </div>
                ) : (
                  <>
                    <span className="upload-icon">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                      </svg>
                    </span>
                    <span className="upload-text">Drop a file here or click to choose</span>
                    <span className="upload-hint">PDF, PNG, JPG — up to 50 MB</span>
                  </>
                )}
              </label>
            </div>

            {error && (
              <div className="message error" role="alert">{error}</div>
            )}

            <div className="actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={process}
                disabled={!file || loading}
              >
                {loading ? 'Processing...' : 'Convert to LaTeX'}
              </button>
              {file && !loading && (
                <button type="button" className="btn btn-secondary" onClick={reset}>
                  Clear
                </button>
              )}
            </div>

            {loading && (
              <div className="loading-section">
                <div className="spinner" />
                <p className="loading-note">{progress}</p>
              </div>
            )}
          </>
        ) : (
          <section className="result">
            <div className="result-header">
              <h2>Generated LaTeX</h2>
              <button type="button" className="btn btn-small btn-ghost" onClick={copyLatex} title="Copy to clipboard">
                Copy
              </button>
            </div>
            <div className="latex-preview">
              <pre><code>{result.latex}</code></pre>
            </div>
            <div className="downloads">
              <button type="button" className="btn btn-primary" onClick={downloadTex}>
                Download .tex
              </button>
              {result.pdfBase64 ? (
                <button type="button" className="btn btn-primary" onClick={downloadPdf}>
                  Download PDF
                </button>
              ) : (
                <span className="no-pdf">PDF not available (LaTeX not installed on server)</span>
              )}
              <button type="button" className="btn btn-secondary" onClick={reset}>
                Convert another
              </button>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>
          TeXForm &mdash; Handwriting OCR (TrOCR) + math recognition (MathPix / Pix2Text)
        </p>
      </footer>
    </div>
  )
}
