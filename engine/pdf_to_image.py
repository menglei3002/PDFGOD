"""PDF to Image conversion using PyMuPDF (fitz)."""

import os
from pathlib import Path


def convert(input_path: str, output_dir: str, dpi: int, report_fn) -> str:
    import fitz  # PyMuPDF

    doc = fitz.open(input_path)
    total = len(doc)

    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    for i in range(total):
        page = doc[i]
        # Render page to image
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        out_file = os.path.join(output_dir, f"page_{i+1:03d}.png")
        pix.save(out_file)
        saved_files.append(out_file)

        pct = 10 + int(80 * (i + 1) / total)
        report_fn(pct, f"Rendering page {i+1}/{total} at {dpi} DPI...")

    doc.close()

    report_fn(95, f"Saved {len(saved_files)} images to {output_dir}")

    if saved_files:
        return os.path.abspath(output_dir)
    raise RuntimeError("Image conversion failed: no images created")
