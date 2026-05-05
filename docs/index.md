# Vision Text Engine

**Motor de extração inteligente de texto de imagens.**

Pipeline completo: **Pré-processamento → OCR → Filtragem Inteligente**.

## Recursos

- **OCR automático**: Detecta e extrai texto de imagens usando EasyOCR
- **Pré-processamento OpenCV**: Redimensionamento, correção de inclinação, realce de contraste
- **Filtragem inteligente**: Remove ruído, aplica regras (min_length, handles, regex)
- **Múltiplos backends**: EasyOCR (primário), Tesseract (fallback), API (fallback final)
- **CLI completa**: Comandos `extract`, `batch`, `info` com saída JSON
- **API Python**: `extract_text()` e `extract_text_batch()` para integração

## Links

- [Instalação](installation.md)
- [API Python](api.md)
- [CLI (Linha de Comando)](cli.md)
- [GitHub](https://github.com/tiagohanna123/vision-text-engine)
