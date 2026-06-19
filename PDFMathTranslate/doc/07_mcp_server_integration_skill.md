# PDFMathTranslate MCP Server Skill

## Overview
Skill for integrating PDFMathTranslate with AI agents via Model Context Protocol (MCP) for structured tool calling and workflow automation.

## MCP Server Configuration

### Server Definition (mcp.json)
```json
{
    "mcpServers": {
        "pdf2zh": {
            "command": "python",
            "args": ["/path/to/pdf2zh_mcp_server.py"],
            "env": {
                "PDF2ZH_DEFAULT_LANG_IN": "en",
                "PDF2ZH_DEFAULT_LANG_OUT": "ar"
            }
        }
    }
}
```

### MCP Server Implementation
```python
#!/usr/bin/env python3
# MCP Server for PDFMathTranslate

import asyncio
import json
import subprocess
from pathlib import Path
from mcp.server import Server
from mcp.types import TextContent, Tool

app = Server("pdf2zh-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="translate_pdf",
            description="Translate a PDF file using pdf2zh",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to PDF file"},
                    "source_lang": {"type": "string", "default": "en"},
                    "target_lang": {"type": "string", "default": "ar"},
                    "engine": {"type": "string", "enum": ["google", "bing", "silicon"], "default": "google"},
                    "output_mode": {"type": "string", "enum": ["mono", "dual"], "default": "mono"},
                    "ocr": {"type": "boolean", "default": False},
                    "pages": {"type": "string", "description": "Page range (e.g., '1-50')"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="batch_translate",
            description="Translate multiple PDF files",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory containing PDFs"},
                    "source_lang": {"type": "string", "default": "en"},
                    "target_lang": {"type": "string", "default": "ar"},
                    "pattern": {"type": "string", "default": "*.pdf"}
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="check_system",
            description="Check if pdf2zh is properly installed",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "translate_pdf":
        return await translate_pdf_tool(arguments)
    elif name == "batch_translate":
        return await batch_translate_tool(arguments)
    elif name == "check_system":
        return await check_system_tool()
    else:
        raise ValueError(f"Unknown tool: {name}")

async def translate_pdf_tool(args: dict):
    cmd = ["pdf2zh", args["file_path"], "-li", args.get("source_lang", "en"), "-lo", args.get("target_lang", "ar")]
    
    if "engine" in args:
        cmd.extend(["-s", args["engine"]])
    if args.get("ocr"):
        cmd.append("--ocr")
    if "pages" in args:
        cmd.extend(["--pages", args["pages"]])
    if args.get("output_mode") == "dual":
        cmd.append("--dual")
    else:
        cmd.append("--mono")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    output_files = [str(p) for p in Path(".").glob("*-*.pdf")]
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_files": output_files
        }, indent=2)
    )]

async def batch_translate_tool(args: dict):
    directory = Path(args["directory"])
    pattern = args.get("pattern", "*.pdf")
    files = list(directory.glob(pattern))
    
    results = []
    for file in files:
        cmd = ["pdf2zh", str(file), "-li", args.get("source_lang", "en"), "-lo", args.get("target_lang", "ar"), "--mono"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        results.append({
            "file": str(file),
            "success": result.returncode == 0
        })
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "total": len(files),
            "successful": sum(1 for r in results if r["success"]),
            "results": results
        }, indent=2)
    )]

async def check_system_tool():
    result = subprocess.run(["pdf2zh", "--version"], capture_output=True, text=True)
    return [TextContent(
        type="text",
        text=json.dumps({
            "installed": result.returncode == 0,
            "version": result.stdout.strip() if result.returncode == 0 else None
        })
    )]

if __name__ == "__main__":
    asyncio.run(app.run())
```

## Claude Desktop Integration

### claude_desktop_config.json
```json
{
    "mcpServers": {
        "pdf2zh": {
            "command": "python3",
            "args": ["/Users/yourname/tools/pdf2zh_mcp_server.py"]
        }
    }
}
```

### Usage in Claude Desktop
```
User: Translate this PDF to Arabic: /path/to/book.pdf
Claude: I will translate that PDF for you using pdf2zh.
[Calls translate_pdf tool with file_path, source_lang="en", target_lang="ar"]
Claude: Translation complete! The file is saved as book-mono.pdf
```

## Cursor IDE Integration

### .cursorrules
```
When the user asks to translate a PDF:
1. Check if pdf2zh is installed using the check_system MCP tool
2. If not installed, provide installation instructions
3. Use the translate_pdf MCP tool with appropriate parameters
4. Report the output file path and any errors
5. Verify the output file exists
```

### Cursor MCP Config
```json
{
    "mcpServers": {
        "pdf2zh": {
            "type": "command",
            "command": "python3 /path/to/pdf2zh_mcp_server.py"
        }
    }
}
```

## Windsurf Integration

### windsurf_mcp_config.json
```json
{
    "mcpServers": [
        {
            "name": "pdf2zh",
            "command": "python3 /path/to/pdf2zh_mcp_server.py",
            "type": "stdio"
        }
    ]
}
```

## Skill Prompt for AI Agents
```
You are an expert PDF translator using PDFMathTranslate (pdf2zh). 

When asked to translate a PDF:
1. First check if the file exists and is a valid PDF
2. Determine the source and target languages (default: en -> ar)
3. Check if the PDF is scanned (needs OCR) or text-based
4. Choose the appropriate translation engine (bing for reliability, google for speed)
5. Execute the translation using the translate_pdf tool
6. Verify the output file was created successfully
7. Report the output file path and any issues encountered

For batch translations:
1. List all PDF files in the specified directory
2. Process them sequentially or in parallel based on system resources
3. Report progress and any failures
4. Provide a summary of all translated files

Always handle errors gracefully and provide actionable solutions.
```
