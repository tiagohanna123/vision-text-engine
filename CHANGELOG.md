# Changelog

Todas as mudanças significativas neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-05-05

### Adicionado

- Version bump: v0.1.0 → v0.2.0 (consistente em todos os arquivos do projeto)

## [0.1.0] - 2026-05-05

### Adicionado

- Motor OCR principal `VisionEngine` com suporte a EasyOCR
- Pipeline de pré-processamento de imagem (contraste, denoise, sharpen, resize)
- Filtragem inteligente de texto com extração de @handles, hashtags, emails e URLs
- Funções de alto nível `extract_text()` e `extract_text_batch()`
- CLI via comando `vte` (extract, batch, info)
- Suporte a múltiplos idiomas (padrão: pt + en)
- Batch processing com barra de progresso
- Fallback automático entre backends
- Modelos de dados: `OCRResult`, `BatchResult`, `FilterRule`, `ImagePreprocessingConfig`
- Infraestrutura de projeto: pyproject.toml, Makefile, linting com Ruff, mypy
- Testes unitários: 204 testes, 99% de cobertura de código
- CI/CD via GitHub Actions (matrix 3.10/3.11/3.12/3.13)
- Build e wheel com Hatchling
- Documentação inicial (README, CHANGELOG, CONTRIBUTING, ROADMAP)
- SECURITY.md, CODE_OF_CONDUCT.md, .pre-commit-config.yaml
- Licença MIT

### Corrigido

- Import incorreto no pipeline.py (ajustado de `from .models` para `from ..core.models`)
- URL do repositório no CONTRIBUTING.md (nousresearch → tiagohanna123)
- 7 testes corrigidos após auditoria de documentação (remoção de `confidence_scores` obsoleto, alinhamento de exemplos CLI/API com a implementação real)

### Melhorado

- Cobertura de testes: de 79% para 99%
- Linting: Ruff 0 erros, mypy strict 0 erros
- Qualidade de código: todos os arquivos 100% tipados
