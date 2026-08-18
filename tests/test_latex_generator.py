import pytest
import os
import subprocess

from backend.latex_generator import generate_full_document, compile_latex_to_pdf


def test_generate_full_document_basic():
    content = (
        "Hello & world\n\n"
        "\\[E=mc^2\\]\n\n"
        "value = 42"
    )
    doc = generate_full_document(content)

    # Preamble and closing should be present
    assert doc.startswith(r"\documentclass")
    assert doc.strip().endswith(r"\end{document}")

    # Plain text should be escaped
    assert "Hello \\& world" in doc

    # Existing display math should remain intact
    assert r"\[E=mc^2\]" in doc

    # Math-like text should be wrapped in display math
    assert "\\[\nvalue = 42\n\\]" in doc


def test_compile_latex_to_pdf(monkeypatch):
    # Stub subprocess.run to simulate successful compilation
    def fake_run(cmd, cwd, stdout, stderr):
        # Create a dummy PDF file in the working dir
        pdf_path = os.path.join(cwd, "document.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")
        return subprocess.CompletedProcess(cmd, 0, stdout=b"", stderr=b"")

    monkeypatch.setattr("backend.latex_generator.subprocess.run", fake_run)

    minimal = r"\documentclass{article}\begin{document}Test\end{document}"
    pdf_data = compile_latex_to_pdf(minimal)

    # The returned bytes should start like a PDF file
    assert pdf_data.startswith(b"%PDF")
