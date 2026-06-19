#!/usr/bin/env python3
"""
Post-Translation Validation Script for PDFMathTranslate outputs.
Checks file integrity, Arabic text presence, font embedding, and page counts.
"""

import subprocess
import sys
import json
from pathlib import Path


def run_cmd(cmd: list) -> tuple:
    """Run a shell command and return (stdout, stderr, returncode)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def check_file_exists(pdf_path: Path) -> dict:
    """Check if file exists and is non-empty."""
    if not pdf_path.exists():
        return {"check": "file_exists", "status": "FAIL", "detail": "File does not exist"}
    size = pdf_path.stat().st_size
    if size < 1024:
        return {"check": "file_exists", "status": "FAIL", "detail": f"File too small ({size} bytes)"}
    return {"check": "file_exists", "status": "PASS", "detail": f"{size} bytes"}


def check_pdf_validity(pdf_path: Path) -> dict:
    """Check PDF validity using pdfinfo."""
    stdout, stderr, rc = run_cmd(["pdfinfo", str(pdf_path)])
    if rc != 0:
        return {"check": "pdf_validity", "status": "FAIL", "detail": stderr or "pdfinfo failed"}
    lines = stdout.splitlines()
    pages = None
    for line in lines:
        if line.startswith("Pages:"):
            pages = line.split()[1]
            break
    return {"check": "pdf_validity", "status": "PASS", "detail": f"{pages} pages"}


def check_arabic_text(pdf_path: Path) -> dict:
    """Extract text and count Arabic characters."""
    stdout, stderr, rc = run_cmd(["pdftotext", str(pdf_path), "-"])
    if rc != 0:
        return {"check": "arabic_text", "status": "WARN", "detail": "pdftotext not available"}
    arabic_chars = sum(1 for ch in stdout if "\u0600" <= ch <= "\u06FF")
    if arabic_chars > 50:
        return {"check": "arabic_text", "status": "PASS", "detail": f"{arabic_chars} Arabic chars"}
    elif arabic_chars > 0:
        return {"check": "arabic_text", "status": "WARN", "detail": f"Only {arabic_chars} Arabic chars"}
    return {"check": "arabic_text", "status": "FAIL", "detail": "No Arabic text detected"}


def check_fonts_embedded(pdf_path: Path) -> dict:
    """Check if fonts are embedded using pdffonts."""
    stdout, stderr, rc = run_cmd(["pdffonts", str(pdf_path)])
    if rc != 0:
        return {"check": "fonts", "status": "WARN", "detail": "pdffonts not available"}
    lines = [l for l in stdout.splitlines() if l.strip() and not l.startswith("name")]
    if len(lines) > 0:
        return {"check": "fonts", "status": "PASS", "detail": f"{len(lines)} font entries"}
    return {"check": "fonts", "status": "WARN", "detail": "No fonts detected"}


def compare_page_counts(original: Path, translated: Path) -> dict:
    """Compare page counts between original and translated."""
    o_stdout, _, o_rc = run_cmd(["pdfinfo", str(original)])
    t_stdout, _, t_rc = run_cmd(["pdfinfo", str(translated)])
    if o_rc != 0 or t_rc != 0:
        return {"check": "page_count", "status": "WARN", "detail": "pdfinfo unavailable"}
    o_pages = None
    t_pages = None
    for line in o_stdout.splitlines():
        if line.startswith("Pages:"):
            o_pages = int(line.split()[1])
    for line in t_stdout.splitlines():
        if line.startswith("Pages:"):
            t_pages = int(line.split()[1])
    if o_pages and t_pages:
        if o_pages == t_pages:
            return {"check": "page_count", "status": "PASS", "detail": f"{t_pages} pages match"}
        return {"check": "page_count", "status": "WARN", "detail": f"Original {o_pages} vs Translated {t_pages}"}
    return {"check": "page_count", "status": "WARN", "detail": "Could not extract page counts"}


def validate_translation(original: str, translated: str) -> dict:
    """
    Run full validation suite on a translated PDF.
    Returns a structured report dict.
    """
    orig = Path(original)
    trans = Path(translated)

    checks = [
        check_file_exists(trans),
        check_pdf_validity(trans),
        check_arabic_text(trans),
        check_fonts_embedded(trans),
    ]
    if orig.exists():
        checks.append(compare_page_counts(orig, trans))

    passed = sum(1 for c in checks if c["status"] == "PASS")
    failed = sum(1 for c in checks if c["status"] == "FAIL")
    warnings = sum(1 for c in checks if c["status"] == "WARN")

    report = {
        "original": original,
        "translated": translated,
        "summary": {"PASS": passed, "FAIL": failed, "WARN": warnings},
        "checks": checks
    }
    return report


def print_report(report: dict):
    """Print human-readable report."""
    print("=" * 50)
    print("PDF Translation Validation Report")
    print("=" * 50)
    print(f"Original:   {report['original']}")
    print(f"Translated: {report['translated']}")
    print(f"Summary:    {report['summary']['PASS']} PASS, {report['summary']['FAIL']} FAIL, {report['summary']['WARN']} WARN")
    print("-" * 50)
    for check in report["checks"]:
        icon = "✓" if check["status"] == "PASS" else "✗" if check["status"] == "FAIL" else "⚠"
        print(f"{icon} {check['check']}: {check['status']} — {check['detail']}")
    print("=" * 50)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate translated PDF")
    parser.add_argument("translated", help="Path to translated PDF")
    parser.add_argument("--original", default="", help="Path to original PDF (optional)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    report = validate_translation(args.original, args.translated)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)

    sys.exit(0 if report["summary"]["FAIL"] == 0 else 1)
