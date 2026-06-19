# Supported Language Codes

PDFMathTranslate supports 100+ languages via Google Translate, Bing, and other engines.

## Common Language Codes

| Language | Code | Notes |
|----------|------|-------|
| Arabic | ar | RTL direction supported |
| English | en | Default source |
| French | fr | |
| German | de | |
| Spanish | es | |
| Chinese (Simplified) | zh | |
| Chinese (Traditional) | zh-TW | |
| Japanese | ja | |
| Korean | ko | |
| Russian | ru | |
| Portuguese | pt | |
| Italian | it | |
| Turkish | tr | |
| Hindi | hi | |
| Dutch | nl | |
| Polish | pl | |
| Ukrainian | uk | |
| Vietnamese | vi | |
| Indonesian | id | |
| Thai | th | |
| Persian (Farsi) | fa | RTL |
| Hebrew | he | RTL |
| Urdu | ur | RTL |

## Usage in CLI
```bash
pdf2zh book.pdf -li en -lo ar
pdf2zh book.pdf -li fr -lo ar
pdf2zh book.pdf -li en -lo zh
```

## Arabic-Specific Notes
- Arabic is RTL (Right-to-Left). pdf2zh preserves layout but verify output rendering.
- Ensure Arabic fonts are installed on the system:
  - Ubuntu: `sudo apt-get install fonts-hosny-amiri fonts-noto-core`
  - macOS: Install Arabic fonts via Font Book
  - Windows: Install Arabic language pack

## Full List
For the complete list of supported codes, see:
- Google Translate: https://cloud.google.com/translate/docs/languages
- Bing Translator: https://docs.microsoft.com/azure/cognitive-services/translator/language-support
