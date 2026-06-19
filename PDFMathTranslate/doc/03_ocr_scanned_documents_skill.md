# PDFMathTranslate OCR & Scanned Documents Skill

## Overview
Specialized skill for handling scanned PDFs, image-based documents, and OCR-enabled translation workflows.

## OCR Prerequisites

### Tesseract OCR Installation
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

### Verify OCR Installation
```bash
tesseract --version
```

## OCR Translation Commands

### Basic OCR Translation
```bash
pdf2zh scanned_book.pdf -li en -lo ar --ocr
```

### OCR with Specific Page Range
```bash
pdf2zh scanned.pdf -li en -lo ar --ocr --pages 1-100
```

### OCR with Bilingual Output
```bash
pdf2zh scanned.pdf -li en -lo ar --ocr --dual
```

## OCR Language Support
Tesseract supports 100+ languages. For Arabic OCR:
```bash
# Install Arabic language pack
sudo apt-get install tesseract-ocr-ara

# For mixed English-Arabic documents
# Tesseract handles mixed content automatically with --ocr flag
```

## Advanced OCR Options

### Custom OCR Configuration
```bash
# High quality OCR (slower but more accurate)
pdf2zh document.pdf -li en -lo ar --ocr --thread 4

# Fast OCR (lower quality)
pdf2zh document.pdf -li en -lo ar --ocr --thread 8
```

### OCR Preprocessing Tips
1. Ensure scanned images are 300 DPI minimum
2. Grayscale images process faster than color
3. Deskew (straighten) pages before OCR if possible
4. Remove watermarks and stamps for better accuracy

## Troubleshooting OCR Issues

### Problem: OCR not working
```bash
# Check if tesseract is in PATH
which tesseract

# Verify Arabic language data exists
ls /usr/share/tesseract-ocr/4.00/tessdata/ara.traineddata
```

### Problem: Poor OCR accuracy
- Increase scan resolution to 300+ DPI
- Clean up noise in scanned images
- Use `--thread 2` for more careful processing
- Consider preprocessing with image enhancement tools

### Problem: Mixed language documents
```bash
# For documents with both English and Arabic text
pdf2zh mixed.pdf -li en -lo ar --ocr
# pdf2zh handles mixed content automatically
```

## OCR + Translation Pipeline
```bash
#!/bin/bash
# Complete pipeline for scanned books

INPUT="scanned_book.pdf"
OUTPUT_DIR="./translated"
mkdir -p "$OUTPUT_DIR"

echo "Step 1: OCR and Translation"
pdf2zh "$INPUT" -li en -lo ar --ocr --mono

echo "Step 2: Verify output"
if [ -f "${INPUT%.pdf}-mono.pdf" ]; then
    mv "${INPUT%.pdf}-mono.pdf" "$OUTPUT_DIR/"
    echo "Success: Translation complete"
else
    echo "Error: Translation failed"
    exit 1
fi
```
