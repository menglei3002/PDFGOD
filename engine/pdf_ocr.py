"""OCR for scanned PDFs. Uses PaddleOCR (best for Chinese) with Tesseract fallback."""

import os


def convert(input_path: str, output_path: str, report_fn) -> str:
    report_fn(5, "Rendering PDF to images for OCR...")

    import fitz
    doc = fitz.open(input_path)
    total = len(doc)
    total_pages = total

    ocr_engine = None

    # Try PaddleOCR first (best for Chinese)
    try:
        from paddleocr import PaddleOCR

        # Store models on D drive, not C drive
        model_dir = os.path.join(os.path.dirname(__file__), "..", "PaddleOCR", "models")
        model_dir = os.path.abspath(model_dir)
        os.environ.setdefault("PADDLE_PDX_CACHE_HOME", model_dir)

        # PaddleOCR 3.5 — use mobile models for speed (3-5x faster than server)
        # Disable unnecessary preprocessors: PDF pages don't need orientation fix or unwarping
        # Disable MKLDNN to avoid oneDNN attribute conversion bug on some CPUs
        ocr_engine = PaddleOCR(
            lang="ch",
            enable_mkldnn=False,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="PP-OCRv5_mobile_rec",
        )
        report_fn(10, "Using PaddleOCR (Chinese-optimized)...")
    except ImportError:
        report_fn(10, "PaddleOCR not available, trying Tesseract...")
        try:
            ocr_engine = "tesseract"
        except ImportError:
            raise RuntimeError(
                "No OCR engine available. Install paddleocr or pytesseract."
            )

    import tempfile

    all_page_texts = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(total):
            page = doc[i]
            # 1.5x zoom balances OCR accuracy and speed
            mat = fitz.Matrix(1.5, 1.5)
            pix = page.get_pixmap(matrix=mat)
            img_path = os.path.join(tmpdir, f"ocr_page_{i:03d}.png")
            pix.save(img_path)

            if ocr_engine == "tesseract":
                import pytesseract
                from PIL import Image

                img = Image.open(img_path)
                text = pytesseract.image_to_string(img, lang="chi_sim+eng")
                all_page_texts.append(text)
            else:
                result = ocr_engine.ocr(img_path)
                # PaddleOCR v3 returns list of OCRResult objects (one per image)
                page_texts = []
                for ocr_result in result:
                    texts = ocr_result.get("rec_texts", [])
                    page_texts.extend(texts)
                all_page_texts.append("\n".join(page_texts))

            if total > 1:
                all_page_texts.append(f"\n--- Page {i + 1} ---\n")

            pct = 10 + int(80 * (i + 1) / total)
            report_fn(pct, f"OCR processing page {i + 1}/{total_pages}...")

    doc.close()

    # Save as docx
    report_fn(90, "Saving OCR result as Word document...")
    from docx import Document

    word_doc = Document()
    full_text = "\n".join(all_page_texts)
    for paragraph in full_text.split("\n"):
        stripped = paragraph.strip()
        if stripped:
            word_doc.add_paragraph(stripped)
    word_doc.save(output_path)

    if os.path.exists(output_path):
        return os.path.abspath(output_path)
    raise RuntimeError("OCR conversion failed")
