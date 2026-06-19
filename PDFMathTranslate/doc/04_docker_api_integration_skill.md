# PDFMathTranslate Docker & API Integration Skill

## Overview
Skill for containerized deployment, API integration, and programmatic access to PDFMathTranslate.

## Docker Deployment

### Basic Docker Usage
```bash
# Pull image
docker pull byaidu/pdf2zh

# Single file translation
docker run -v $(pwd):/app byaidu/pdf2zh     pdf2zh /app/book.pdf -li en -lo ar

# With output directory
docker run -v $(pwd)/input:/input -v $(pwd)/output:/output     byaidu/pdf2zh pdf2zh /input/book.pdf -li en -lo ar
```

### Docker Compose Setup
```yaml
version: '3.8'
services:
  pdf2zh:
    image: byaidu/pdf2zh
    volumes:
      - ./input:/input
      - ./output:/output
    command: pdf2zh /input/book.pdf -li en -lo ar --mono
```

### Running Docker Container as Server
```bash
# Start container with shell access
docker run -it -v $(pwd):/app --name pdf2zh-server byaidu/pdf2zh /bin/sh

# Then inside container:
pdf2zh /app/*.pdf -li en -lo ar
```

## GUI Mode via Docker
```bash
# Run web GUI on port 7860
docker run -d -p 7860:7860 -v $(pwd):/app byaidu/pdf2zh     pdf2zh -i --host 0.0.0.0

# Access at http://localhost:7860
```

## Python API Integration

### Direct Python Usage
```python
from pdf2zh import translate

# Basic translation
translate(
    files=["book.pdf"],
    lang_in="en",
    lang_out="ar",
    service="google",
    output="./output"
)

# Advanced options
translate(
    files=["book.pdf"],
    lang_in="en",
    lang_out="ar",
    service="bing",
    output="./output",
    pages=[1, 2, 3, 10-50],  # Specific pages
    thread=4,  # Parallel processing
    ocr=True,  # Enable OCR
    dual=True  # Bilingual output
)
```

### Flask API Wrapper
```python
from flask import Flask, request, send_file
from pdf2zh import translate
import os
import tempfile

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate_pdf():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400
    
    file = request.files['file']
    lang_in = request.form.get('lang_in', 'en')
    lang_out = request.form.get('lang_out', 'ar')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, file.filename)
        file.save(input_path)
        
        translate(
            files=[input_path],
            lang_in=lang_in,
            lang_out=lang_out,
            output=tmpdir
        )
        
        output_file = os.path.join(tmpdir, f"{os.path.splitext(file.filename)[0]}-mono.pdf")
        return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### FastAPI Integration
```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pdf2zh import translate
import tempfile
import os

app = FastAPI()

@app.post("/translate/")
async def translate_endpoint(
    file: UploadFile = File(...),
    source_lang: str = "en",
    target_lang: str = "ar"
):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, file.filename)
        with open(input_path, "wb") as f:
            f.write(await file.read())
        
        translate(
            files=[input_path],
            lang_in=source_lang,
            lang_out=target_lang,
            output=tmpdir
        )
        
        output_path = os.path.join(tmpdir, f"{os.path.splitext(file.filename)[0]}-mono.pdf")
        return FileResponse(output_path, filename=f"translated_{file.filename}")
```

## CLI Wrapper for AI Agents
```python
#!/usr/bin/env python3
# AI Agent wrapper for pdf2zh with structured output

import subprocess
import json
import sys
from pathlib import Path

def translate_with_metadata(input_file: str, **kwargs):
    cmd = ["pdf2zh", input_file]
    
    for key, value in kwargs.items():
        if key == "lang_in":
            cmd.extend(["-li", value])
        elif key == "lang_out":
            cmd.extend(["-lo", value])
        elif key == "service":
            cmd.extend(["-s", value])
        elif key == "pages":
            cmd.extend(["--pages", value])
        elif key == "ocr":
            if value:
                cmd.append("--ocr")
        elif key == "dual":
            if value:
                cmd.append("--dual")
        elif key == "mono":
            if value:
                cmd.append("--mono")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": [str(p) for p in Path(".").glob("*-*.pdf")]
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input PDF file")
    parser.add_argument("--lang-in", default="en")
    parser.add_argument("--lang-out", default="ar")
    parser.add_argument("--service", default="google")
    args = parser.parse_args()
    
    result = translate_with_metadata(
        args.file,
        lang_in=args.lang_in,
        lang_out=args.lang_out,
        service=args.service
    )
    
    print(json.dumps(result, indent=2))
```
