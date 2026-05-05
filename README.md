<!-- markdownlint-disable MD033 MD041 -->

<div align="center">

# Vision Text Engine 🔍

**Motor de extração inteligente de texto de imagens**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
|[![Version](https://img.shields.io/badge/version-0.1.0-8A2BE2)](https://github.com/tiagohanna123/vision-text-engine)
|[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
|[![CI](https://github.com/tiagohanna123/vision-text-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/tiagohanna123/vision-text-engine/actions/workflows/ci.yml)
|[![Coverage](https://img.shields.io/badge/coverage-99%25-success)](https://github.com/tiagohanna123/vision-text-engine)
|[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
|[![Code style](https://img.shields.io/badge/code%20style-ruff-633f8b)](https://github.com/astral-sh/ruff)
|[![Hatchling](https://img.shields.io/badge/build-hatchling-9cf)](https://hatch.pypa.io/)
|[![Made by Tiago Hanna](https://img.shields.io/badge/made%20by-Tiago%20Hanna-8A2BE2)](https://tiagohanna.com)

</div>

> **Pipeline completo:** pré-processamento de imagem → OCR → filtragem inteligente.
> Múltiplos backends com fallback automático.

---

## ✨ Funcionalidades

- **Extraia texto de imagens** com EasyOCR (primário) e fallbacks automáticos
- **Pré-processamento inteligente** — contraste, denoise, sharpen, redimensionamento
- **Filtragem contextual** remove ruído de UI, datas, números irrelevantes
- **Extração específica** — @handles, hashtags, emails, URLs
- **Batch processing** com barra de progresso
- **CLI integrada** via comando `vte`
- **Suporte a múltiplos idiomas** (padrão: português + inglês)

## 🚀 Instalação

> ⚠️ **Ainda não publicado no PyPI.** Use o desenvolvimento local:

```bash
# Clone o repositório
git clone https://github.com/tiagohanna123/vision-text-engine.git
cd vision-text-engine

# Com uv (recomendado)
uv sync
uv run vte --help

# Ou com pip
python -m venv .venv
source .venv/bin/activate
make install-dev
```

## 📖 Uso

### Python API

```python
from vision_text_engine import extract_text, extract_text_batch, VisionEngine

# --- Funções de alto nível ---

# Extrair texto de uma imagem
result = extract_text("foto.jpg")
print(result.text)           # Texto filtrado
print(result.raw_text)       # Texto bruto
print(result.success)        # True/False

# Extrair de múltiplas imagens
batch = extract_text_batch(["img1.jpg", "img2.png"])
print(f"Processadas: {len(batch)} imagens")

# --- Classe VisionEngine (controle fino) ---

engine = VisionEngine(lang=["pt", "en"], gpu=False)
result = engine.extract("foto.jpg", detail=1)  # Com bounding boxes

# Usar filtros específicos
from vision_text_engine.filters import extract_handles
handles = extract_handles(result.raw_texts)
print(handles)  # ['@usuario1', '@usuario2']
```

### CLI

```bash
# Extrair texto de uma imagem
vte extract foto.jpg

# Extrair com bounding boxes em JSON
vte extract foto.jpg --json

# Extrair apenas @handles
vte extract foto.jpg --handles

# Processar diretório inteiro
vte batch ./imagens/ --recursive

# Informações do engine
vte info
```

### Python module

```bash
python -m vision_text_engine extract foto.jpg
python -m vision_text_engine batch ./imagens/
```

## 🧪 Exemplos

Veja o diretório [`examples/`](examples/) para exemplos completos:

| Exemplo | Descrição |
|---------|-----------|
| `basic_usage.py` | Extração básica com funções de alto nível |
| `batch_process.py` | Processamento em lote |
| `custom_filter.py` | Filtragem personalizada |
| `preprocessing_demo.py` | Demonstração do pipeline de pré-processamento |

## 🏗️ Arquitetura

```
src/vision_text_engine/
├── __init__.py          # Entry point, exports públicos
├── api.py               # Funções de alto nível (extract_text, extract_text_batch)
├── __main__.py          # Entry point para python -m
├── core/
│   ├── engine.py        # VisionEngine — motor OCR principal
│   └── models.py        # ExtractionResult, FilterRule, Config
├── preprocessing/
│   └── pipeline.py      # Pipeline de pré-processamento de imagem
├── filters/
│   └── smart_filter.py  # Filtragem inteligente (handles, hashtags, urls)
└── cli/
    ├── __init__.py      # Inicialização do pacote CLI
    └── main.py          # CLI com Click (vte extract, batch, info)
```

## 🔧 Stack

| Componente | Tecnologia |
|------------|------------|
| **OCR** | EasyOCR (primário) |
| **Processamento** | OpenCV + NumPy |
| **Pipeline** | Python 3.10+ |
| **Build** | Hatchling |
| **Linter** | Ruff |
| **Type Checker** | mypy |
| **CLI** | Click (opcional) |

## 🗺️ Roadmap

Consulte [ROADMAP.md](ROADMAP.md) para ver o planejamento de funcionalidades futuras.

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para guias e boas práticas.

## 📄 Licença

Este projeto é licenciado sob a [MIT License](LICENSE).
