# Contribuindo para Vision Text Engine

Obrigado por considerar contribuir! 🎉

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Git
- Pip

## 🛠️ Setup de desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/nousresearch/vision-text-engine.git
cd vision-text-engine

# Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instale dependências de desenvolvimento
make install-all
```

## ✅ Padrões de código

Usamos [Ruff](https://github.com/astral-sh/ruff) para linting e formatação:

```bash
# Verificar linting
make lint

# Auto-corrigir problemas de linting
make lint-fix

# Verificar tipos
make typecheck
```

Requisitos:
- Código em **Python 3.10+**
- **Docstrings** em módulos públicos, classes e métodos
- **Type hints** em todas as funções públicas
- **Cobertura de testes** para novas funcionalidades
- Seguir [PEP 8](https://peps.python.org/pep-0008/) (verificado pelo Ruff)

## 🧪 Testes

```bash
# Rodar todos os testes
make test

# Testes com cobertura
make test-cov

# Testes rápidos (para debug)
make test-fast
```

## 🔄 Fluxo de contribuição

1. **Crie uma issue** descrevendo a mudança proposta
2. **Faça um fork** do repositório
3. **Crie um branch**: `git checkout -b feature/nome-da-feature`
4. **Faça suas alterações** com commits claros e descritivos
5. **Rode os testes**: `make test`
6. **Verifique linting**: `make lint && make typecheck`
7. **Envie um Pull Request** para o branch `main`

## 📝 Convenções de commit

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — nova funcionalidade
- `fix:` — correção de bug
- `docs:` — documentação
- `refactor:` — refatoração sem mudança funcional
- `test:` — adição/correção de testes
- `chore:` — tarefas de manutenção

## 📁 Estrutura do projeto

```
src/vision_text_engine/
├── __init__.py          # Entry point
├── api.py               # API de alto nível
├── __main__.py          # Execução como módulo
├── core/
│   ├── engine.py        # Motor OCR
│   └── models.py        # Modelos de dados
├── preprocessing/
│   └── pipeline.py      # Pipeline de imagem
├── filters/
│   └── smart_filter.py  # Filtros inteligentes
└── cli/
    └── main.py          # CLI
```

Dúvidas? Abra uma [issue](https://github.com/nousresearch/vision-text-engine/issues).
