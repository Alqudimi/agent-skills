# PDFMathTranslate Core Translation Skill

## Overview
Expert-level skill for translating PDF documents from English to Arabic (or any language pair) using PDFMathTranslate (pdf2zh) with perfect formatting preservation.

## System Requirements
- Python 3.8+
- pip or Docker
- 2GB+ free disk space
- Internet connection (for cloud translation engines)

## Installation
```bash
# Method 1: pip
pip install pdf2zh

# Method 2: Docker
docker pull byaidu/pdf2zh

# Method 3: uv (fastest)
uv pip install pdf2zh
```

## Core Commands

### Basic Translation (English to Arabic)
```bash
pdf2zh input.pdf -li en -lo ar
```

### Bilingual Output (Original + Translation)
```bash
pdf2zh input.pdf -li en -lo ar --dual
```

### Monolingual Output (Translation Only)
```bash
pdf2zh input.pdf -li en -lo ar --mono
```

### Scanned/OCR Documents
```bash
pdf2zh scanned.pdf -li en -lo ar --ocr
```

## Translation Engines (Free Tier)
| Engine | Command | Limitations |
|--------|---------|-------------|
| Google Translate | `pdf2zh file.pdf` (default) | Rate limiting possible |
| Bing Translator | `pdf2zh file.pdf -s bing` | More stable than Google |
| LibreTranslate | `pdf2zh file.pdf -s libretranslate` | Requires local server |
| SiliconFlow | `pdf2zh file.pdf -s silicon` | Free tier available |

## Output Files
- `input-mono.pdf` - Translation only
- `input-dual.pdf` - Bilingual side-by-side
- `input-zh.pdf` - Legacy naming (mono)

## Best Practices
1. Always verify output file exists before proceeding
2. Check Arabic RTL rendering in the output
3. For large books (>500 pages), consider splitting
4. Use `--dual` for reference materials
5. Use `--mono` for final readable copies

## Common Issues
- **Rate limiting**: Switch to `-s bing` or wait 5 minutes
- **Missing fonts**: Install Arabic fonts on system
- **Large files**: Use `--pages` to process specific pages
- **OCR failures**: Ensure tesseract-ocr is installed
