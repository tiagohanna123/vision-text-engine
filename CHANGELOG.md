# Changelog

Todas as mudanças significativas neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Infraestrutura de projeto: pyproject.toml, Makefile, linting com Ruff
- Documentação inicial (README, CHANGELOG, CONTRIBUTING, ROADMAP)
- Licença MIT
