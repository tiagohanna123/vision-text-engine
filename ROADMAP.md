# Roadmap

## v0.1.0 — Alpha ✅

- [x] Motor OCR com EasyOCR
- [x] Pipeline de pré-processamento (OpenCV + CLAHE + denoise + sharpen)
- [x] Filtragem inteligente (handles, hashtags, emails, URLs)
- [x] API de alto nível (extract_text, extract_text_batch)
- [x] CLI integrada (extract, batch, info)
- [x] Infraestrutura de projeto (pyproject, Makefile, CI/CD)
- [x] Testes unitários completos (204 testes, 99% cobertura)
- [x] Linting (Ruff) e type checking (mypy strict)
- [x] Build e wheel publicáveis
- [x] Cobertura de código >95%
- [x] SECURITY.md, CODE_OF_CONDUCT.md, .pre-commit-config.yaml
- [x] Documentação bilingue (README, CONTRIBUTING, CHANGELOG)

## v0.2.0 — Estabilização

- [ ] Suporte a Tesseract como backend fallback
- [ ] Modo servidor HTTP (`vte serve`)
- [ ] Documentação em inglês e português no readthedocs
- [ ] Exemplos completos em `examples/`
- [ ] CLI com rich (saída colorida, tabelas, progresso)

## v0.3.0 — Funcionalidades avançadas

- [ ] Cache de OCR para imagens recorrentes
- [ ] Detecção de idioma automática
- [ ] Processamento paralelo em batch (multiprocessing)
- [ ] Pós-processamento com LLM para correção de OCR
- [ ] Suporte a PDF (extração de imagens + OCR)
- [ ] Plugin system para filtros customizados
- [ ] Modo watchdog (monitorar diretório)

## v0.4.0 — Performance & escala

- [ ] Suporte a GPU otimizado
- [ ] Quantização de modelo para inferência mais rápida
- [ ] Benchmark suite

## v1.0.0 — Produção

- [ ] API estável
- [ ] Documentação completa em readthedocs
- [ ] Pacote publicado no PyPI
- [ ] Imagem Docker
- [ ] Integração com ferramentas de terceiros

## Ideias futuras

- [ ] Detecção de tabelas em imagens
- [ ] Extração de texto de vídeos (frames)
- [ ] Reconhecimento de handwriting
- [ ] Suporte a formatos de documento (DOCX, XLSX)
- [ ] UI web com Streamlit/Gradio
- [ ] API REST com FastAPI
