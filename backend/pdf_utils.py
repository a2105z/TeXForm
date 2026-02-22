import os
from typing import Optional

import fitz  # PyMuPDF

from backend.config_loader import get


def pdf_to_images(
    pdf_path: str,
    output_folder: str,
    dpi: Optional[int] = None,
) -> list:
    """Convert each page of a PDF into a PNG image."""
    if dpi is None:
        dpi = get("pdf_utils.dpi", 200)
    if not isinstance(dpi, int) or dpi < 72 or dpi > 600:
        dpi = 200

    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(dpi=dpi)

        # Construct output file path
        filename = f"page_{page_index + 1:03d}.png"
        img_path = os.path.join(output_folder, filename)
        
        # Save the image
        pix.save(img_path)
        image_paths.append(img_path)

    # Close the document
    doc.close()

    # Return the list of image paths
    return image_paths