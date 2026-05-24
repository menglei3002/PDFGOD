"""OCR for scanned PDFs. Uses PaddleOCR (best for Chinese) with Tesseract fallback."""

import os


def convert(input_path: str, output_path: str, report_fn) -> str:
    report_fn(5, "Rendering PDF to images for OCR...")

    import fitz
    doc = fitz.open(input_path)
    total = len(doc)

    ocr_texts = []
    ocr_engine = None

    # Try PaddleOCR first (best for Chinese)
    try:
        from paddleocr import PaddleOCR
        ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
        report_fn(10, "Using PaddleOCR (Chinese-optimized)...")
    except ImportError:
        report_fn(10, "PaddleOCR not available, trying Tesseract...")
        try:
            import pytesseract
            from PIL import Image
            ocr_engine = "tesseract"
        except ImportError:
            raise RuntimeError(
                "No OCR engine available. Install paddleocr or pytesseract."
            )

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(total):
            page = doc[i]
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_path = os.path.join(tmpdir, f"ocr_page_{i:03d}.png")
            pix.save(img_path)

            if ocr_engine == "tesseract":
                import pytesseract
                from PIL import Image
                img = Image.open(img_path)
                text = pytesseract.image_to_string(img, lang="chi_sim+eng")
            else:
                result = ocr_engine.ocr(img_path, cls=True)
                lines = []
                if result and result[0]:
                    for line_info in result[0]:
                        if line_info and len(line_info) > 1:
                            text_part = line_info[1][0] if line_info[1] else ""
                            lines.append(text_part)
                text = "\n".join(lines)

            ocr_texts.append(text)
            if total > 1:
                ocr_texts.append(f"\n--- Page {i+1} ---\n")

            pct = 10 + int(80 * (i + 1) / total)
            report_fn(pct, f"OCR processing page {i+1}/{total}...")

    doc.close()

    # Save as docx
    report_fn(90, "Saving OCR result as Word document...")
    from docx import Document
    word_doc = Document()
    for text in ocr_texts:
        for paragraph in text.split("\n"):
            if paragraph.strip():
                word_doc.add_paragraph(paragraph.strip())
    word_doc.save(output_path)

    if os.path.exists(output_path):
        return os.path.abspath(output_path)
    raise RuntimeError("OCR conversion failed")
