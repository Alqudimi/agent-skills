# PDFMathTranslate Error Handling & Troubleshooting Skill

## Overview
Comprehensive skill for diagnosing, resolving, and preventing issues during PDF translation with PDFMathTranslate.

## Common Error Codes & Solutions

### Error: Connection Timeout / Rate Limiting
```
Error: HTTP Error 429: Too Many Requests
```
**Solution:**
```bash
# Switch to Bing (more generous limits)
pdf2zh book.pdf -li en -lo ar -s bing

# Add delay between requests
pdf2zh book.pdf -li en -lo ar --thread 1

# Wait and retry
sleep 60 && pdf2zh book.pdf -li en -lo ar
```

### Error: Missing Dependencies
```
Error: No module named 'pdf2zh'
```
**Solution:**
```bash
# Reinstall with dependencies
pip install --force-reinstall pdf2zh

# Or use Docker
docker pull byaidu/pdf2zh
```

### Error: Tesseract Not Found (OCR)
```
Error: tesseract is not installed or not in PATH
```
**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Verify
which tesseract
tesseract --version
```

### Error: PDF is Encrypted
```
Error: File has not been decrypted
```
**Solution:**
```bash
# Decrypt using qpdf
qpdf --decrypt encrypted.pdf decrypted.pdf

# Or using pdftk
pdftk encrypted.pdf input_pw ownerpw output decrypted.pdf

# Then translate
pdf2zh decrypted.pdf -li en -lo ar
```

### Error: Corrupted PDF
```
Error: PDF is corrupted or cannot be read
```
**Solution:**
```bash
# Repair with Ghostscript
gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=fixed.pdf corrupted.pdf

# Or using qpdf
qpdf --repair corrupted.pdf fixed.pdf

# Then translate
pdf2zh fixed.pdf -li en -lo ar
```

### Error: Arabic Text Not Displaying
```
Problem: Arabic text appears as boxes or gibberish
```
**Solution:**
```bash
# Install Arabic fonts
sudo apt-get install fonts-hosny-amiri fonts-noto-core

# On macOS, install Arabic fonts via Font Book
# On Windows, install Arabic language pack

# Verify font embedding in output
pdfinfo output.pdf | grep "PDF version"
```

## Diagnostic Commands

### System Check Script
```bash
#!/bin/bash
# pdf2zh_system_check.sh

echo "=== PDF2ZH System Diagnostic ==="

# Check Python
echo "Python version:"
python --version

# Check pip
echo -e "\nPip packages:"
pip list | grep -E "pdf2zh|pymupdf|requests"

# Check pdf2zh
echo -e "\nPDF2ZH version:"
pdf2zh --version 2>/dev/null || echo "pdf2zh not found in PATH"

# Check tesseract
echo -e "\nTesseract OCR:"
which tesseract 2>/dev/null || echo "tesseract not installed"
tesseract --version 2>/dev/null | head -1

# Check Arabic fonts
echo -e "\nArabic fonts:"
fc-list :lang=ar 2>/dev/null | head -5 || echo "fontconfig not available"

# Check disk space
echo -e "\nDisk space:"
df -h .

# Check network
echo -e "\nNetwork connectivity:"
ping -c 1 google.com 2>/dev/null || echo "No internet connection"

echo -e "\n=== Diagnostic Complete ==="
```

### Translation Test Script
```bash
#!/bin/bash
# Quick test with a sample PDF

cat > test_content.txt << 'EOF'
This is a test document for PDF translation.
It contains simple English text.
EOF

# Convert to PDF (requires enscript and ps2pdf)
enscript -p - test_content.txt | ps2pdf - test.pdf

# Translate
pdf2zh test.pdf -li en -lo ar --mono

# Check result
if [ -f "test-mono.pdf" ]; then
    echo "SUCCESS: Translation works"
    ls -lh test-mono.pdf
else
    echo "FAILED: Translation did not produce output"
fi

# Cleanup
rm -f test.pdf test_content.txt test-mono.pdf
```

## Logging & Debugging

### Enable Debug Mode
```bash
# Verbose output
pdf2zh book.pdf -li en -lo ar --debug

# Log to file
pdf2zh book.pdf -li en -lo ar 2>&1 | tee translation.log

# Debug with specific page
pdf2zh book.pdf -li en -lo ar --pages 1 --debug
```

### Monitor Progress
```bash
# Real-time progress (if supported)
pdf2zh book.pdf -li en -lo ar -v

# Watch output directory
watch -n 1 ls -lh *.pdf
```

## Recovery Strategies

### Partial Translation Recovery
```bash
# If translation stopped at page X, resume from there
pdf2zh book.pdf -li en -lo ar --pages X-END

# Merge partial translations later
# (use pdftk or pypdf)
```

### Fallback Engine Strategy
```bash
#!/bin/bash
# Try multiple engines in order

FILE="book.pdf"
ENGINES="google bing silicon"

for engine in $ENGINES; do
    echo "Trying engine: $engine"
    pdf2zh "$FILE" -li en -lo ar -s "$engine" && break
    echo "Engine $engine failed, trying next..."
done
```

## Performance Optimization

### For Large Files (>100MB)
```bash
# Split into chunks
pdftk large.pdf burst output page_%04d.pdf

# Translate chunks in parallel
ls page_*.pdf | xargs -P 4 -I {} pdf2zh {} -li en -lo ar

# Merge results
pdftk *_translated.pdf cat output final.pdf
```

### Memory Issues
```bash
# Reduce thread count
pdf2zh book.pdf -li en -lo ar --thread 1

# Process page by page
for i in $(seq 1 $TOTAL_PAGES); do
    pdf2zh book.pdf -li en -lo ar --pages $i
    sleep 2
done
```
