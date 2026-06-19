# PDFMathTranslate Quality Assurance & Validation Skill

## Overview
Skill for ensuring translation quality, validating output files, and verifying Arabic text rendering in translated PDFs.

## Output Validation Checklist

### File Integrity Checks
```bash
#!/bin/bash
# validate_translation.sh

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: validate_translation.sh <translated.pdf>"
    exit 1
fi

echo "=== Validation Report for $FILE ==="

# Check file exists and is not empty
if [ ! -f "$FILE" ]; then
    echo "FAIL: File does not exist"
    exit 1
fi

SIZE=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE" 2>/dev/null)
if [ "$SIZE" -lt 1024 ]; then
    echo "FAIL: File is too small ($SIZE bytes)"
    exit 1
fi
echo "PASS: File exists and has content ($SIZE bytes)"

# Check PDF validity
if command -v pdfinfo &> /dev/null; then
    PAGES=$(pdfinfo "$FILE" 2>/dev/null | grep Pages | awk '{print $2}')
    if [ -n "$PAGES" ] && [ "$PAGES" -gt 0 ]; then
        echo "PASS: Valid PDF with $PAGES pages"
    else
        echo "FAIL: Invalid PDF or no pages"
    fi
else
    echo "WARN: pdfinfo not available, skipping page check"
fi

# Check for Arabic text
if command -v pdftotext &> /dev/null; then
    ARABIC_CHARS=$(pdftotext "$FILE" - 2>/dev/null | grep -o '[\u0600-\u06FF]' | wc -l)
    if [ "$ARABIC_CHARS" -gt 10 ]; then
        echo "PASS: Arabic text detected ($ARABIC_CHARS characters)"
    else
        echo "WARN: Very few Arabic characters found ($ARABIC_CHARS)"
    fi
else
    echo "WARN: pdftotext not available, skipping text check"
fi

# Check for embedded fonts
if command -v pdffonts &> /dev/null; then
    FONTS=$(pdffonts "$FILE" 2>/dev/null | wc -l)
    if [ "$FONTS" -gt 2 ]; then
        echo "PASS: Fonts embedded ($FONTS font entries)"
    else
        echo "WARN: No fonts detected"
    fi
else
    echo "WARN: pdffonts not available, skipping font check"
fi

echo "=== Validation Complete ==="
```

## Arabic Text Quality Checks

### RTL Verification
```bash
# Extract text and check RTL markers
pdftotext translated.pdf - | head -100 | cat -v

# Look for RTL markers (U+202E, U+202F, U+061C)
# Proper Arabic text should show these or render correctly
```

### Font Rendering Test
```bash
# Generate a test PDF with Arabic text
cat > arabic_test.txt << 'EOF'
مرحبا بك في اختبار الترجمة العربية
هذا نص تجريبي للتحقق من جودة الخطوط
EOF

# Convert to PDF (requires appropriate tools)
# Then compare rendering with translated output
```

## Visual Comparison

### Side-by-side Comparison
```bash
# Convert both PDFs to images
# Requires: pdftoppm, ImageMagick

pdftoppm -png original.pdf original_page
pdftoppm -png translated.pdf translated_page

# Compare page count
ORIG_PAGES=$(ls original_page*.png | wc -l)
TRANS_PAGES=$(ls translated_page*.png | wc -l)

echo "Original pages: $ORIG_PAGES"
echo "Translated pages: $TRANS_PAGES"

if [ "$ORIG_PAGES" -eq "$TRANS_PAGES" ]; then
    echo "PASS: Page counts match"
else
    echo "WARN: Page count mismatch"
fi
```

## Translation Accuracy Sampling

### Random Page Verification
```bash
#!/bin/bash
# Sample random pages for manual verification

PDF="translated.pdf"
TOTAL_PAGES=$(pdfinfo "$PDF" | grep Pages | awk '{print $2}')
SAMPLE_SIZE=5

echo "Sampling $SAMPLE_SIZE random pages from $TOTAL_PAGES total pages:"

for i in $(seq 1 $SAMPLE_SIZE); do
    PAGE=$(( (RANDOM % TOTAL_PAGES) + 1 ))
    echo "Page $PAGE:"
    pdftotext -f $PAGE -l $PAGE "$PDF" -
    echo "---"
done
```

## Automated Quality Metrics

### Text Extraction Comparison
```python
#!/usr/bin/env python3
# Compare text density between original and translated PDF

import subprocess
import sys

def extract_text(pdf_path):
    result = subprocess.run(
        ["pdftotext", pdf_path, "-"],
        capture_output=True, text=True
    )
    return result.stdout

def compare_text_density(original, translated):
    orig_text = extract_text(original)
    trans_text = extract_text(translated)
    
    orig_words = len(orig_text.split())
    trans_words = len(trans_text.split())
    
    ratio = trans_words / orig_words if orig_words > 0 else 0
    
    print(f"Original words: {orig_words}")
    print(f"Translated words: {trans_words}")
    print(f"Ratio: {ratio:.2f}")
    
    # Arabic text is typically 0.8-1.2x the length of English
    if 0.7 <= ratio <= 1.3:
        print("PASS: Text density within expected range")
    else:
        print("WARN: Text density outside expected range")
    
    return ratio

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: compare_density.py original.pdf translated.pdf")
        sys.exit(1)
    
    compare_text_density(sys.argv[1], sys.argv[2])
```

## Report Generation

### Translation Report Template
```bash
#!/bin/bash
# generate_report.sh

INPUT="$1"
OUTPUT="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: generate_report.sh input.pdf output.pdf"
    exit 1
fi

cat > translation_report.md << EOF
# Translation Report

## Source Information
- Original File: $INPUT
- Translated File: $OUTPUT
- Date: $(date)
- Tool: PDFMathTranslate (pdf2zh)

## File Statistics
EOF

if command -v pdfinfo &> /dev/null; then
    echo "### Original" >> translation_report.md
    pdfinfo "$INPUT" >> translation_report.md 2>/dev/null
    echo "" >> translation_report.md
    echo "### Translated" >> translation_report.md
    pdfinfo "$OUTPUT" >> translation_report.md 2>/dev/null
fi

echo "" >> translation_report.md
echo "## Validation Results" >> translation_report.md
if [ -f "$OUTPUT" ]; then
    echo "- Output file: EXISTS" >> translation_report.md
    SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)
    echo "- File size: $SIZE bytes" >> translation_report.md
else
    echo "- Output file: MISSING" >> translation_report.md
fi

echo "" >> translation_report.md
echo "## Notes" >> translation_report.md
echo "- Verify Arabic text rendering manually" >> translation_report.md
echo "- Check mathematical formulas preserved" >> translation_report.md
echo "- Confirm tables and images intact" >> translation_report.md

echo "Report generated: translation_report.md"
```
