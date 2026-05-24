#!/usr/bin/env python3
"""PDFGOD Conversion Engine - CLI Entry Point"""

import argparse
import json
import os
import sys
import time
from pathlib import Path


def report(progress, message, output=None, error=None):
    """Send JSON progress report to stdout for Tauri to read."""
    data = {"type": "progress", "percent": progress, "message": message}
    if output:
        data["type"] = "done"
        data["output"] = output
    if error:
        data["type"] = "error"
        data["error"] = error
    print(json.dumps(data, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description="PDFGOD Conversion Engine")
    parser.add_argument("--input", required=True, help="Input PDF file path")
    parser.add_argument("--format", required=True,
                        choices=["word", "excel", "ppt", "txt", "image", "ocr"],
                        help="Output format")
    parser.add_argument("--output", help="Output file path (auto-generated if omitted)")
    parser.add_argument("--pages", help="Page range, e.g. 1-5 or 1,3,5")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for image output (default: 200)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        report(0, "", error=f"File not found: {args.input}")
        sys.exit(1)

    if not args.output:
        suffix_map = {"word": ".docx", "excel": ".xlsx", "ppt": ".pptx",
                      "txt": ".txt", "image": "", "ocr": ".docx"}
        stem = input_path.stem
        out_dir = input_path.parent
        if args.format == "image":
            args.output = str(out_dir / f"{stem}_images")
        else:
            args.output = str(out_dir / f"{stem}_converted{suffix_map[args.format]}")

    report(0, f"Starting {args.format} conversion...")

    try:
        if args.format == "word":
            from pdf_to_word import convert
            result = convert(str(input_path), args.output, report)
        elif args.format == "excel":
            from pdf_to_excel import convert
            result = convert(str(input_path), args.output, report)
        elif args.format == "ppt":
            from pdf_to_ppt import convert
            result = convert(str(input_path), args.output, report)
        elif args.format == "txt":
            from pdf_to_txt import convert
            result = convert(str(input_path), args.output, report)
        elif args.format == "image":
            from pdf_to_image import convert
            result = convert(str(input_path), args.output, args.dpi, report)
        elif args.format == "ocr":
            from pdf_ocr import convert
            result = convert(str(input_path), args.output, report)
        else:
            report(0, "", error=f"Unknown format: {args.format}")
            sys.exit(1)

        report(100, "Conversion complete", output=result)

    except Exception as e:
        report(0, "", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
