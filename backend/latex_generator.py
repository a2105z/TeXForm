import logging
import os
import re
import shutil
import subprocess
import tempfile
from backend.config_loader import get


# ─── Helpers ──────────────────────────────────────────────────────────────────

def escape_text(paragraph: str) -> str:
    """
    Escape LaTeX special characters in a plaintext paragraph.
    """
    return (
        paragraph
        .replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("^", r"\^{}")
        .replace("~", r"\~{}")
    )

def is_display_math(p: str) -> bool:
    """
    Detect if a paragraph is already a LaTeX display‑math environment.
    """
    return (
        p.startswith("\\[") and p.endswith("\\]")
    ) or (
        p.startswith("\\begin{equation") and p.rstrip().endswith("\\end{equation}")
    )

def looks_like_math(p: str) -> bool:
    """
    Heuristic to catch math‑heavy paragraphs (contains =, ^, _, \\ etc).
    """
    return bool(re.search(r"[=\\\^_{}]", p))


# ─── Document Generation ────────────────────────────────────────────────────

def _build_preamble() -> str:
    """Build LaTeX preamble from config (or sensible defaults)."""
    doc_class = get("latex_generator.document_class", "article")
    font_size = get("latex_generator.font_size", "12pt")
    margin = "1in"
    geo = get("latex_generator.page_geometry") or {}
    if isinstance(geo, dict) and geo.get("margin"):
        margin = str(geo["margin"])
    title = get("latex_generator.title", "Converted Notes")
    author = get("latex_generator.author", "")
    date_val = get("latex_generator.date", r"\today")
    if date_val and not date_val.startswith("\\"):
        date_val = date_val.replace("\\", "\\\\")
    return (
        f"\\documentclass[{font_size}]{{{doc_class}}}\n"
        r"\usepackage[utf8]{inputenc}"
        "\n"
        r"\usepackage{amsmath, amssymb}"
        "\n"
        r"\usepackage{geometry}"
        "\n"
        f"\\geometry{{margin={margin}}}\n"
        r"\usepackage{graphicx}"
        "\n"
        f"\\title{{{title}}}\n"
        f"\\author{{{author}}}\n"
        f"\\date{{{date_val}}}\n"
        "\n"
        r"\begin{document}"
        "\n"
        r"\maketitle"
        "\n\n"
    )


def generate_full_document(content: str) -> str:
    """
    Wrap the provided text + LaTeX fragments into a full .tex document.
    """
    preamble = _build_preamble()
    body_parts = []
    # split on double‑newlines, filter out empty
    for p in filter(None, (p.strip() for p in content.split("\n\n"))):
        if is_display_math(p):
            # already a \[...\] or equation environment
            body_parts.append(p)
        elif p.startswith("$") and p.endswith("$"):
            # already inline‑math wrapped
            body_parts.append(p)
        elif looks_like_math(p):
            # wrap any stray math in display math
            math_code = p.strip("$")
            body_parts.append(f"\\[\n{math_code}\n\\]")
        else:
            # plain text → escape special chars
            body_parts.append(escape_text(p))

    closing = r"\end{document}"
    return preamble + "\n\n".join(body_parts) + "\n\n" + closing


# ─── PDF Compilation ────────────────────────────────────────────────────────

def compile_latex_to_pdf(latex_str: str) -> bytes:
    """
    Compile a LaTeX string to PDF, using latexmk if available,
    otherwise falling back to pdflatex.
    Returns raw PDF bytes.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "document.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_str)

        use_latexmk = get("latex_generator.use_latexmk", True)
        has_latexmk = use_latexmk and shutil.which("latexmk")
        compile_cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "document.tex"]
        fallback_cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "document.tex"]
        cmd = compile_cmd if has_latexmk else fallback_cmd

        # latexmk handles multiple passes internally; pdflatex needs two runs
        passes = 1 if has_latexmk else 2
        for _ in range(passes):
            proc = subprocess.run(
                cmd,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if proc.returncode != 0:
                log = (
                    proc.stdout.decode("utf-8", errors="replace")
                    + "\n"
                    + proc.stderr.decode("utf-8", errors="replace")
                )
                logging.error("LaTeX compile error:\n%s", log)
                raise RuntimeError(f"LaTeX compilation failed:\n{log}")

        pdf_path = os.path.join(tmpdir, "document.pdf")
        if not os.path.isfile(pdf_path):
            raise RuntimeError(
                "LaTeX compilation produced no PDF. "
                "Ensure pdflatex or latexmk is installed."
            )
        with open(pdf_path, "rb") as f:
            return f.read()