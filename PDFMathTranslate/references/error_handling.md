# Error Handling & Troubleshooting

## Common Errors and Solutions

### 1. Rate Limiting (HTTP 429)
**Symptom**: `HTTP Error 429: Too Many Requests`
**Solutions**:
- Switch to Bing: `pdf2zh book.pdf -li en -lo ar -s bing`
- Reduce threads: `--thread 1`
- Add delay between requests: `sleep 60 && pdf2zh ...`
- For batch scripts, add `time.sleep(5)` between files

### 2. Missing Dependencies
**Symptom**: `No module named 'pdf2zh'`
**Solutions**:
```bash
pip install --force-reinstall pdf2zh
# OR use Docker:
docker pull byaidu/pdf2zh
```

### 3. Tesseract Not Found (OCR)
**Symptom**: `tesseract is not installed or not in PATH`
**Solutions**:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```
Verify: `tesseract --version`

### 4. PDF is Encrypted
**Symptom**: `File has not been decrypted`
**Solutions**:
```bash
# Decrypt with qpdf
qpdf --decrypt encrypted.pdf decrypted.pdf

# Or with pdftk
pdftk encrypted.pdf input_pw ownerpw output decrypted.pdf

# Then translate
pdf2zh decrypted.pdf -li en -lo ar
```

### 5. Corrupted PDF
**Symptom**: `PDF is corrupted or cannot be read`
**Solutions**:
```bash
# Repair with Ghostscript
gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=fixed.pdf corrupted.pdf

# Or with qpdf
qpdf --repair corrupted.pdf fixed.pdf
```

### 6. Arabic Text Not Displaying
**Symptom**: Arabic text appears as boxes or gibberish
**Solutions**:
```bash
# Install Arabic fonts
sudo apt-get install fonts-hosny-amiri fonts-noto-core

# On macOS: install Arabic fonts via Font Book
# On Windows: install Arabic language pack
```

### 7. Large File Memory Error
**Symptom**: Process killed or out of memory
**Solutions**:
- Reduce threads: `--thread 1`
- Split PDF first: `python scripts/split_large_pdf.py split big.pdf --pages 50`
- Translate chunks individually, then merge

### 8. Timeout / Stuck Translation
**Symptom**: Translation hangs indefinitely
**Solutions**:
- Set timeout: `pdf2zh book.pdf -li en -lo ar --timeout 300`
- Process specific pages: `--pages 1-50`
- Check internet connection
- Switch engine: `-s bing`

## Diagnostic Script
```bash
#!/bin/bash
# pdf2zh_system_check.sh

echo "=== PDF2ZH System Diagnostic ==="
echo "Python version:"
python --version

echo -e "
PDF2ZH version:"
pdf2zh --version 2>/dev/null || echo "pdf2zh not found"

echo -e "
Tesseract OCR:"
which tesseract 2>/dev/null || echo "tesseract not installed"

echo -e "
Arabic fonts:"
fc-list :lang=ar 2>/dev/null | head -5 || echo "fontconfig not available"

echo -e "
Disk space:"
df -h .

echo -e "
Network:"
ping -c 1 google.com 2>/dev/null || echo "No internet"
```

## Recovery Strategies

### Partial Translation
If translation stopped at page X:
```bash
pdf2zh book.pdf -li en -lo ar --pages X-END
```

### Fallback Engine
```bash
#!/bin/bash
for engine in google bing silicon; do
    echo "Trying $engine..."
    pdf2zh book.pdf -li en -lo ar -s "$engine" && break
done
```

### Merge Partial Results
```bash
pdftk part1.pdf part2.pdf cat output complete.pdf
# OR
qpdf --empty --pages part1.pdf part2.pdf -- complete.pdf
```
