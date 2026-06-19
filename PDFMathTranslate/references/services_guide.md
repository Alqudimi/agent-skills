# Translation Services Guide

PDFMathTranslate supports multiple translation engines. This guide helps you choose and configure the right one.

## 1. Google Translate (Default)
- **CLI flag**: (none, default)
- **Cost**: Free (unofficial, may rate-limit)
- **Speed**: Fast
- **Reliability**: Medium — occasional 429 errors
- **Best for**: Quick tests, small files
- **Rate limit workaround**: `--thread 1` or add delays

```bash
pdf2zh book.pdf -li en -lo ar
```

## 2. Bing Translator (Microsoft)
- **CLI flag**: `-s bing`
- **Cost**: Free
- **Speed**: Fast
- **Reliability**: High — more stable than Google
- **Best for**: Batch processing, large books

```bash
pdf2zh book.pdf -li en -lo ar -s bing
```

## 3. LibreTranslate (Self-Hosted)
- **CLI flag**: `-s libretranslate`
- **Cost**: Free (self-hosted)
- **Speed**: Depends on your hardware
- **Reliability**: High (local)
- **Best for**: Privacy, offline use, no rate limits

### Setup
```bash
# Start LibreTranslate server
docker run -d -p 5000:5000 libretranslate/libretranslate

# Use with pdf2zh
pdf2zh book.pdf -li en -lo ar -s libretranslate
```

### Custom URL
```bash
pdf2zh book.pdf -li en -lo ar -s libretranslate --libre-url http://localhost:5000
```

## 4. SiliconFlow (Free AI Tier)
- **CLI flag**: `-s silicon`
- **Cost**: Free tier available
- **Speed**: Medium (AI-based)
- **Reliability**: High
- **Best for**: High-quality AI translation

### Setup
```bash
export SILICON_API_KEY="your-api-key"
pdf2zh book.pdf -li en -lo ar -s silicon
```

## 5. OpenAI / Gemini / DeepL (Premium)
- **CLI flags**: `-s openai`, `-s gemini`, `-s deepl`
- **Cost**: Paid API required
- **Speed**: Medium
- **Reliability**: High
- **Best for**: Professional quality, when free engines fail

### Setup
```bash
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
export DEEPL_API_KEY="..."
pdf2zh book.pdf -li en -lo ar -s openai
```

## Engine Selection Strategy
| Scenario | Recommended Engine | Reason |
|----------|-------------------|--------|
| Single small file | Google | Fast, no setup |
| Batch / large book | Bing | Stable, no rate limits |
| Privacy sensitive | LibreTranslate | Local, no data leaves network |
| Best quality | SiliconFlow / OpenAI | AI-powered context awareness |
| Offline / air-gapped | LibreTranslate | Fully self-hosted |

## Environment Variables
```bash
export PDF2ZH_SERVICE=bing          # Default engine
export PDF2ZH_LANG_IN=en            # Default source
export PDF2ZH_LANG_OUT=ar           # Default target
export SILICON_API_KEY="..."
export OPENAI_API_KEY="..."
export GEMINI_API_KEY="..."
export DEEPL_API_KEY="..."
```
