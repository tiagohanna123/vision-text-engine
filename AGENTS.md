# Vision Text Engine — Contexto para Agentes de IA

## Descrição do Projeto

Motor de extração inteligente de texto de imagens com pipeline completo:

```
Imagem → Pré-processamento → OCR (EasyOCR) → Filtragem Inteligente → Texto Extraído
```

- **Backend principal**: EasyOCR (com fallback Tesseract e API)
- **Pré-processamento**: OpenCV (redimensionamento, correção de inclinação, realce)
- **Filtragem**: Regras configuráveis (min_length, handles, regex, noise)
- **CLI**: Click com comandos `extract`, `batch`, `info`
- **API pública**: `extract_text()`, `extract_text_batch()`
- **Versão**: 0.1.0 (Alpha)
- **Testes**: 204 testes unitários, 99% de cobertura de código
- **Linting**: Ruff 0 erros, mypy strict 0 erros

## Estrutura de Diretórios

```
vision-text-engine/
├── src/
│   └── vision_text_engine/
│       ├── __init__.py          # Módulo principal com lazy imports
│       ├── __main__.py          # Entry point python -m
│       ├── api.py               # API pública (extract_text, extract_text_batch)
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py          # CLI Click (vte)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── engine.py        # VisionEngine — orquestrador
│       │   └── models.py        # Modelos de dados (ExtractionResult, FilterRule, etc.)
│       ├── filters/
│       │   ├── __init__.py
│       │   └── smart_filter.py  # Filtragem inteligente pós-OCR
│       └── preprocessing/
│           ├── __init__.py
│           └── pipeline.py      # Pipeline de pré-processamento OpenCV
├── tests/
│   ├── test_api.py
│   ├── test_cli.py
│   ├── test_cli_integration.py
│   ├── test_engine.py
│   ├── test_integration.py
│   ├── test_main_module.py
│   ├── test_models.py
│   ├── test_package_init.py
│   ├── test_preprocessing.py
│   └── test_smart_filter.py
├── docs/
│   ├── index.md
│   ├── api.md
│   ├── cli.md
│   └── installation.md
├── .github/workflows/
│   ├── ci.yml                   # CI matrix (3.10–3.13)
│   └── release.yml              # Release automatizada
├── pyproject.toml
├── .pre-commit-config.yaml
└── AGENTS.md
```

## Comandos Úteis

```bash
# Gerenciamento
uv sync                     # Sincronizar dependências
uv add <pkg>                # Adicionar dependência
uv pip install -e ".[dev]"  # Instalar em modo editable com dev

# Lint e tipo
uv run ruff check src/ tests/         # Verificar lint
uv run ruff check --fix src/ tests/   # Corrigir lint automaticamente
uv run ruff format src/ tests/        # Formatar código
uv run mypy src/                      # Verificar tipos (strict)
uv run pre-commit run --all-files     # Rodar pre-commit manualmente

# Testes
uv run pytest tests/ -v                        # Rodar testes
uv run pytest tests/ -v --cov=vision_text_engine  # Com cobertura
uv run pytest tests/test_cli_integration.py -v # Apenas CLI

# CLI
uv run vte --help                 # Ajuda
uv run vte info                   # Info do engine
uv run vte extract imagem.jpg     # Extrair texto
uv run vte extract --json img.jpg # JSON output
uv run vte batch "images/*.png"   # Batch processing
uv run python -m vision_text_engine  # Via módulo

# CI local
act                                    # Rodar GitHub Actions localmente
act -j test                            # Apenas job test
```

## Convenções

- **Python**: >=3.10, tipagem estrita (mypy strict)
- **Estilo**: Ruff (pycodestyle E/W, pyflakes F, isort I, pep8-naming N, pydocstyle D, pyupgrade UP, bugbear B, simplify SIM)
- **Formatação**: Aspas duplas, line-length 100, indentação espaços
- **Testes**: pytest com fixtures, CliRunner para CLI, mocks para EasyOCR (evitar dependência pesada)
- **Imports**: Lazy imports para dependências pesadas (easyocr, cv2, torch)
- **Documentação**: Docstrings em português (projeto brasileiro)
- **Commits**: pre-commit roda ruff check --fix, mypy, trailing-whitespace, end-of-file-fixer
- **CI**: Testa python 3.10, 3.11, 3.12, 3.13 com ruff + mypy + pytest-cov
- **PEP 639**: Licença declarada via `license = { text = "MIT" }`, não via classifier
- **Versão**: Sempre em `__version__` no `__init__.py` e no `pyproject.toml`

## CLI — Comandos Disponíveis

| Comando     | Descrição                           | Opções                                     |
|-------------|-------------------------------------|--------------------------------------------|
| `extract`   | Extrair texto de uma imagem         | `--json`, `--raw`, `--handles`, `--lang`   |
| `batch`     | Extrair texto de múltiplas imagens  | `--json`, `--glob`, `--dir`, `--lang`      |
| `info`      | Mostrar informações do engine       | `--lang`, `--gpu`, `--no-preprocess`       |

## Modelo de Dados Principal

```python
@dataclass
class ExtractionResult:
    file_path: str
    success: bool
    text: str
    raw_text: str
    raw_texts: list[str]
    filtered_texts: list[str]
    error: Optional[str]
    ocr_time: float
    total_time: float
```
