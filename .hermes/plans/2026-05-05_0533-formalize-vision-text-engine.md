# Plano: Formalização do Vision Text Engine como Projeto

## Goal

Transformar Vision Text Engine v0.1.0 de motor funcional em projeto formal — com todas as engrenagens de qualidade, CI/CD, documentação, e preparação para PyPI.

## O que já existe (não mexer)

- Motor OCR, CLI, API, filtros, preprocessing — funcionando
- 165 testes, 79% coverage
- CI (ci.yml + release.yml), .gitignore, .editorconfig
- CHANGELOG, CONTRIBUTING, ROADMAP, README, LICENSE
- pyproject.toml (hatchling), Makefile
- GitHub repo: tiagohanna123/vision-text-engine

## O que falta fazer

### 1. Qualidade — coverage >95%
- Identificar gaps de cobertura nos módulos
- Adicionar testes para branches não cobertos
- Alvo: >95% coverage total

### 2. PEP 639 — remover License classifier duplicado
- classifiers tem `License :: OSI Approved :: MIT License` E license={text="MIT"}
- PEP 639 diz: quando license field é usado, remover classifier correspondente

### 3. Pre-commit hooks
- `.pre-commit-config.yaml` com ruff, mypy, trailing-whitespace, end-of-file-fixer

### 4. AGENTS.md
- AI agent context file — instruções para LLMs que navegarem o repo

### 5. Docs estruturais
- docs/index.md como entrypoint de documentação
- docs/api.md, docs/cli.md, docs/installation.md

### 6. CI — adicionar Python 3.13
- Matrix CI: 3.10, 3.11, 3.12, 3.13

### 7. Lint fixes
- 2 warnings no ruff (test_cli_integration.py): unused import + nested with

### 8. PyPI readiness
- Verificar se build funciona (`python -m build`)
- Verificar se twine check passa

## Execução

Cascata em 3 tracks paralelas:
- **Track A**: Coverage >95% (subagente especialista em testes)
- **Track B**: Infraestrutura do projeto (pre-commit, AGENTS.md, PEP 639, docs, CI, lint)
- **Track C**: PyPI readiness (build, twine check, publish workflow)

## Validação

- `pytest --cov=src/vision_text_engine --cov-fail-under=95`
- `ruff check src/ tests/` — 0 warnings
- `mypy src/ --strict --ignore-missing-imports` — 0 issues
- `python -m build && twine check dist/*` — passa
- `pre-commit run --all-files` — passa
