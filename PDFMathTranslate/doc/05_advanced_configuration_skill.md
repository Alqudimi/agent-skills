# PDFMathTranslate Advanced Configuration Skill

## Overview
Expert skill for configuring PDFMathTranslate with custom settings, translation engines, and advanced options.

## Configuration File Format

### config.json Structure
```json
{
    "translate": {
        "lang_in": "en",
        "lang_out": "ar",
        "service": "bing",
        "thread": 4,
        "pages": null,
        "ocr": false,
        "dual": false,
        "mono": true,
        "debug": false,
        "interactive": false
    },
    "output": {
        "dir": "./translated",
        "naming": "{filename}_AR"
    },
    "engines": {
        "google": {
            "enabled": true,
            "rate_limit": 100
        },
        "bing": {
            "enabled": true,
            "rate_limit": 200
        },
        "libretranslate": {
            "enabled": false,
            "url": "http://localhost:5000/translate"
        }
    }
}
```

## Translation Engine Configuration

### Google Translate (Default)
```bash
# Default - no extra config needed
pdf2zh book.pdf -li en -lo ar

# With rate limiting awareness
pdf2zh book.pdf -li en -lo ar --thread 2
```

### Bing Translator (More Stable)
```bash
pdf2zh book.pdf -li en -lo ar -s bing
```

### LibreTranslate (Self-Hosted)
```bash
# Start LibreTranslate server
docker run -d -p 5000:5000 libretranslate/libretranslate

# Use with pdf2zh
pdf2zh book.pdf -li en -lo ar -s libretranslate

# With custom URL
pdf2zh book.pdf -li en -lo ar -s libretranslate --libre-url http://localhost:5000
```

### SiliconFlow (Free AI Translation)
```bash
# Requires API key
export SILICON_API_KEY="your-api-key"
pdf2zh book.pdf -li en -lo ar -s silicon
```

## Advanced CLI Options

### Thread Control
```bash
# Single thread (slower, more reliable)
pdf2zh book.pdf -li en -lo ar --thread 1

# Multi-thread (faster, higher resource usage)
pdf2zh book.pdf -li en -lo ar --thread 8

# Auto-detect optimal threads
pdf2zh book.pdf -li en -lo ar --thread 0
```

### Page Selection
```bash
# Single page
pdf2zh book.pdf -li en -lo ar --pages 5

# Page range
pdf2zh book.pdf -li en -lo ar --pages 1-50

# Multiple ranges
pdf2zh book.pdf -li en -lo ar --pages 1-10,20-30,50-100

# Specific pages
pdf2zh book.pdf -li en -lo ar --pages 1,3,5,7,9
```

### Output Control
```bash
# Specify output directory
pdf2zh book.pdf -li en -lo ar -o ./output/

# Custom output filename
pdf2zh book.pdf -li en -lo ar --output translated_book.pdf
```

## Environment Variables
```bash
# Default language settings
export PDF2ZH_LANG_IN=en
export PDF2ZH_LANG_OUT=ar

# Default translation engine
export PDF2ZH_SERVICE=bing

# Default thread count
export PDF2ZH_THREAD=4

# API keys for premium services
export SILICON_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
```

## Custom Post-Processing
```bash
#!/bin/bash
# Post-processing pipeline

INPUT="book.pdf"
OUTPUT_DIR="./final"
mkdir -p "$OUTPUT_DIR"

# Step 1: Translate
pdf2zh "$INPUT" -li en -lo ar --mono

# Step 2: Optimize file size
if command -v ps2pdf &> /dev/null; then
    ps2pdf "${INPUT%.pdf}-mono.pdf" "$OUTPUT_DIR/optimized.pdf"
else
    mv "${INPUT%.pdf}-mono.pdf" "$OUTPUT_DIR/"
fi

# Step 3: Generate metadata
cat > "$OUTPUT_DIR/info.json" << EOF
{
    "source": "$INPUT",
    "source_language": "en",
    "target_language": "ar",
    "translation_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tool": "pdf2zh",
    "pages": "$(pdfinfo "$OUTPUT_DIR/optimized.pdf" 2>/dev/null | grep Pages | awk '{print $2}')"
}
EOF

echo "Translation pipeline complete"
```

## Language Code Reference
```
Arabic: ar
English: en
French: fr
German: de
Spanish: es
Chinese (Simplified): zh
Chinese (Traditional): zh-TW
Japanese: ja
Korean: ko
Russian: ru
Portuguese: pt
Italian: it
Turkish: tr
Hindi: hi
```
