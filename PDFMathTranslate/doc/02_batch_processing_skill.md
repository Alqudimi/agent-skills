# PDFMathTranslate Batch Processing Skill

## Overview
Advanced skill for processing multiple PDF files, directories, and automated translation workflows using PDFMathTranslate.

## Batch Translation Patterns

### 1. Directory Processing
```bash
# Translate all PDFs in current directory
pdf2zh *.pdf -li en -lo ar

# Translate all PDFs in specific directory
pdf2zh /path/to/books/*.pdf -li en -lo ar

# Recursive directory processing (with find)
find /path/to/library -name "*.pdf" -exec pdf2zh {} -li en -lo ar \;
```

### 2. Sequential Processing Script
```bash
#!/bin/bash
# batch_translate.sh
SOURCE_DIR="./english_books"
OUTPUT_DIR="./arabic_books"
mkdir -p "$OUTPUT_DIR"

for file in "$SOURCE_DIR"/*.pdf; do
    filename=$(basename "$file")
    echo "Translating: $filename"
    pdf2zh "$file" -li en -lo ar --mono
    mv "${file%.pdf}-mono.pdf" "$OUTPUT_DIR/${filename%.pdf}_AR.pdf"
done
```

### 3. Python Automation Wrapper
```python
import subprocess
import os
from pathlib import Path

def batch_translate_pdf(
    source_dir: str,
    target_dir: str,
    source_lang: str = "en",
    target_lang: str = "ar",
    engine: str = "bing",  # More stable for batch
    output_mode: str = "mono"
):
    source = Path(source_dir)
    target = Path(target_dir)
    target.mkdir(exist_ok=True)
    
    pdf_files = list(source.glob("*.pdf"))
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        cmd = [
            "pdf2zh",
            str(pdf_file),
            "-li", source_lang,
            "-lo", target_lang,
            "-s", engine,
            f"--{output_mode}"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                output_name = f"{pdf_file.stem}_AR.pdf"
                # Move output to target directory
                for output in source.glob(f"{pdf_file.stem}*-*.pdf"):
                    output.rename(target / output_name)
                print(f"  Success: {output_name}")
            else:
                print(f"  Error: {result.stderr}")
        except Exception as e:
            print(f"  Failed: {str(e)}")

# Usage
batch_translate_pdf("./books", "./translated")
```

### 4. Page Range Processing
```bash
# Translate only specific pages
pdf2zh book.pdf -li en -lo ar --pages 1-50
pdf2zh book.pdf -li en -lo ar --pages 100-200
pdf2zh book.pdf -li en -lo ar --pages 1,5,10-20
```

## Docker Batch Processing
```bash
# Batch via Docker with volume mount
docker run -v $(pwd):/app byaidu/pdf2zh     sh -c "cd /app && pdf2zh *.pdf -li en -lo ar"

# Docker with specific output directory
docker run -v $(pwd)/input:/input -v $(pwd)/output:/output     byaidu/pdf2zh sh -c "pdf2zh /input/*.pdf -li en -lo ar && mv /input/*-*.pdf /output/"
```

## Progress Tracking & Logging
```bash
# Log all operations
pdf2zh book.pdf -li en -lo ar 2>&1 | tee translation.log

# Batch with error logging
for f in *.pdf; do
    pdf2zh "$f" -li en -lo ar 2>>errors.log || echo "FAILED: $f" >>errors.log
done
```

## Rate Limiting Protection
```bash
# Add delay between requests to avoid rate limits
for f in *.pdf; do
    pdf2zh "$f" -li en -lo ar -s bing
    sleep 10  # 10 second delay
done
```
