"""PDF to Word conversion using pdf2docx."""

import os


def convert(input_path: str, output_path: str, report_fn) -> str:
    from pdf2docx import Converter

    report_fn(10, "Loading PDF document...")

    cv = Converter(input_path)
    total = len(cv.pages) if hasattr(cv, 'pages') else 1

    def progress_callback(current, total_pages):
        pct = 10 + int(80 * current / total_pages)
        report_fn(pct, f"Converting page {current}/{total_pages}...")

    # pdf2docx supports a callback-like approach via convert with start/end
    cv.convert(output_path, start=0, end=None)
    cv.close()

    report_fn(95, "Finalizing Word document...")

    if os.path.exists(output_path):
        return os.path.abspath(output_path)
    raise RuntimeError("Word conversion failed: output file not created")
