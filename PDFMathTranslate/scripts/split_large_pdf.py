#!/usr/bin/env python3
"""
Split large PDFs into chunks for safer translation with pdf2zh.
Also supports merging translated chunks back together.
"""

import subprocess
import sys
import os
from pathlib import Path
from math import ceil


def split_pdf(input_path: str, output_dir: str, pages_per_chunk: int = 100):
    """
    Split a PDF into chunks of N pages each using pdftk or pypdf.

    Args:
        input_path: Path to large PDF.
        output_dir: Directory to save chunks.
        pages_per_chunk: Number of pages per chunk (default 100).
    """
    inp = Path(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Get total pages
    stdout, stderr, rc = subprocess.run(
        ["pdfinfo", str(inp)], capture_output=True, text=True
    ).__reduce__()
    # Re-run properly
    result = subprocess.run(["pdfinfo", str(inp)], capture_output=True, text=True)
    total_pages = None
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            total_pages = int(line.split()[1])
            break

    if not total_pages:
        print("Error: Could not determine page count. Is pdfinfo installed?")
        sys.exit(1)

    chunks = ceil(total_pages / pages_per_chunk)
    print(f"Splitting {inp.name} ({total_pages} pages) into {chunks} chunks of ~{pages_per_chunk} pages...")

    for i in range(chunks):
        start = i * pages_per_chunk + 1
        end = min((i + 1) * pages_per_chunk, total_pages)
        chunk_name = out / f"{inp.stem}_chunk_{i+1:03d}_p{start}-{end}.pdf"

        # Try pdftk first, then qpdf, then pypdf CLI
        cmds = [
            ["pdftk", str(inp), "cat", f"{start}-{end}", "output", str(chunk_name)],
            ["qpdf", str(inp), "--pages", ".", f"{start}-{end}", "--", str(chunk_name)],
        ]
        success = False
        for cmd in cmds:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and Path(chunk_name).exists():
                success = True
                break

        if not success:
            # Fallback: Python pypdf
            try:
                from pypdf import PdfReader, PdfWriter
                reader = PdfReader(str(inp))
                writer = PdfWriter()
                for p in range(start - 1, end):
                    writer.add_page(reader.pages[p])
                with open(chunk_name, "wb") as f:
                    writer.write(f)
                success = True
            except ImportError:
                print("Install pypdf: pip install pypdf")
                sys.exit(1)

        if success:
            print(f"  Created: {chunk_name.name}")
        else:
            print(f"  FAILED: {chunk_name.name}")

    print(f"Done. Chunks saved to: {out}")


def merge_pdfs(input_dir: str, output_path: str):
    """
    Merge translated PDF chunks back into a single file.
    Sorts files alphabetically (chunk_001, chunk_002, etc.).
    """
    inp = Path(input_dir)
    out = Path(output_path)
    files = sorted(inp.glob("*.pdf"))
    if not files:
        print(f"No PDF files found in {input_dir}")
        sys.exit(1)

    print(f"Merging {len(files)} files into {out.name}...")

    # Try pdftk
    cmd = ["pdftk"] + [str(f) for f in files] + ["cat", "output", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        print(f"Success: {out}")
        return

    # Try qpdf
    cmd = ["qpdf", "--empty", "--pages"] + [str(f) for f in files] + ["--", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        print(f"Success: {out}")
        return

    # Fallback: pypdf
    try:
        from pypdf import PdfMerger
        merger = PdfMerger()
        for f in files:
            merger.append(str(f))
        merger.write(str(out))
        merger.close()
        print(f"Success (pypdf): {out}")
    except ImportError:
        print("Merge failed. Install pdftk, qpdf, or pypdf.")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Split or merge PDFs for translation")
    sub = parser.add_subparsers(dest="command", required=True)

    split_p = sub.add_parser("split", help="Split a large PDF into chunks")
    split_p.add_argument("input", help="Input PDF path")
    split_p.add_argument("--output-dir", default="./chunks", help="Output directory")
    split_p.add_argument("--pages", type=int, default=100, help="Pages per chunk")

    merge_p = sub.add_parser("merge", help="Merge translated chunks")
    merge_p.add_argument("input_dir", help="Directory with PDF chunks")
    merge_p.add_argument("output", help="Output merged PDF path")

    args = parser.parse_args()

    if args.command == "split":
        split_pdf(args.input, args.output_dir, args.pages)
    elif args.command == "merge":
        merge_pdfs(args.input_dir, args.output)
