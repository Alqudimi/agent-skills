#!/usr/bin/env python3
"""
Batch PDF Translation Script using PDFMathTranslate (pdf2zh)
Translates all PDFs in a source directory to a target directory.
"""

import subprocess
import os
import time
import json
from pathlib import Path
from datetime import datetime


def batch_translate(
    source_dir: str,
    target_dir: str,
    source_lang: str = "en",
    target_lang: str = "ar",
    engine: str = "bing",
    output_mode: str = "mono",
    ocr: bool = False,
    delay_seconds: int = 5,
    timeout: int = 600
):
    """
    Batch translate all PDF files in source_dir to target_dir.

    Args:
        source_dir: Directory containing source PDFs.
        target_dir: Directory to save translated PDFs.
        source_lang: Source language code (default: en).
        target_lang: Target language code (default: ar).
        engine: Translation engine — google, bing, silicon, libretranslate.
        output_mode: "mono" or "dual".
        ocr: Enable OCR for scanned documents.
        delay_seconds: Delay between files to avoid rate limits.
        timeout: Max seconds per file.
    """
    source = Path(source_dir)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(source.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {source_dir}")
        return

    results = []
    total = len(pdf_files)

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{total}] Translating: {pdf_file.name}")

        cmd = [
            "pdf2zh",
            str(pdf_file),
            "-li", source_lang,
            "-lo", target_lang,
            "-s", engine,
            f"--{output_mode}"
        ]
        if ocr:
            cmd.append("--ocr")

        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed = time.time() - start

            # Find generated output file(s)
            output_files = list(source.glob(f"{pdf_file.stem}*-*.pdf"))
            output_path = None
            if output_files:
                # Move to target directory with clean name
                suffix = "_AR" if output_mode == "mono" else "_AR_dual"
                output_path = target / f"{pdf_file.stem}{suffix}.pdf"
                output_files[0].rename(output_path)

            success = result.returncode == 0 and output_path and output_path.exists()
            results.append({
                "file": str(pdf_file),
                "success": success,
                "output": str(output_path) if output_path else None,
                "elapsed_sec": round(elapsed, 2),
                "stderr": result.stderr if not success else None
            })
            status = "OK" if success else "FAIL"
            print(f"  [{status}] {elapsed:.1f}s -> {output_path.name if output_path else 'N/A'}")

        except subprocess.TimeoutExpired:
            print(f"  [FAIL] Timeout after {timeout}s")
            results.append({
                "file": str(pdf_file),
                "success": False,
                "output": None,
                "elapsed_sec": timeout,
                "stderr": "Timeout"
            })
        except Exception as e:
            print(f"  [FAIL] {e}")
            results.append({
                "file": str(pdf_file),
                "success": False,
                "output": None,
                "elapsed_sec": 0,
                "stderr": str(e)
            })

        if i < total and delay_seconds > 0:
            time.sleep(delay_seconds)

    # Save report
    report_path = target / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "source_dir": source_dir,
            "target_dir": target_dir,
            "engine": engine,
            "total": total,
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\nBatch complete. Report saved: {report_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch translate PDFs with pdf2zh")
    parser.add_argument("source", help="Source directory containing PDFs")
    parser.add_argument("target", help="Target directory for translated PDFs")
    parser.add_argument("--li", default="en", help="Source language")
    parser.add_argument("--lo", default="ar", help="Target language")
    parser.add_argument("--engine", default="bing", choices=["google", "bing", "silicon", "libretranslate"])
    parser.add_argument("--mode", default="mono", choices=["mono", "dual"])
    parser.add_argument("--ocr", action="store_true", help="Enable OCR")
    parser.add_argument("--delay", type=int, default=5, help="Seconds between files")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per file (seconds)")
    args = parser.parse_args()

    batch_translate(
        source_dir=args.source,
        target_dir=args.target,
        source_lang=args.li,
        target_lang=args.lo,
        engine=args.engine,
        output_mode=args.mode,
        ocr=args.ocr,
        delay_seconds=args.delay,
        timeout=args.timeout
    )
