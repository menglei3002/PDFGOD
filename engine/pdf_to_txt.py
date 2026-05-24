"""PDF to TXT conversion using PyMuPDF (primary) and pdfplumber (fallback)."""

import os


def convert(input_path: str, output_path: str, report_fn) -> str:
    report_fn(10, "Extracting text with PyMuPDF...")

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(input_path)
        total = len(doc)
        lines = []

        for i in range(total):
            page = doc[i]
            text = page.get_text("text")
            lines.append(text)
            if total > 1:
                lines.append(f"\n--- Page {i+1} ---\n")
            pct = 10 + int(80 * (i + 1) / total)
            report_fn(pct, f"Extracting page {i+1}/{total}...")

        doc.close()
        full_text = "\n".join(lines)

    except ImportError:
        report_fn(10, "PyMuPDF not available, using pdfplumber...")
        import pdfplumber
        with pdfplumber.open(input_path) as pdf:
            total = len(pdf.pages)
            lines = []
            for i in range(total):
                page = pdf.pages[i]
                text = page.extract_text()
                if text:
                    lines.append(text)
                if total > 1:
                    lines.append(f"\n--- Page {i+1} ---\n")
                pct = 10 + int(80 * (i + 1) / total)
                report_fn(pct, f"Extracting page {i+1}/{total}...")

        full_text = "\n".join(lines)

    report_fn(90, "Writing text file...")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    if os.path.exists(output_path):
        return os.path.abspath(output_path)
    raise RuntimeError("TXT conversion failed: output file not created")
