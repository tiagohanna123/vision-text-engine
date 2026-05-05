# Instalação

## Pré-requisitos

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (recomendado) ou pip

## Instalação via pip

```bash
# Instalação básica
pip install vision-text-engine

# Com suporte a CLI
pip install "vision-text-engine[cli]"

# Completa (CLI + dev)
pip install "vision-text-engine[all]"
```

## Instalação via uv (recomendado)

```bash
# Instalação básica
uv pip install vision-text-engine

# Com CLI
uv pip install "vision-text-engine[cli]"

# Completa
uv pip install "vision-text-engine[all]"
```

## Instalação para Desenvolvimento

```bash
# Clonar o repositório
git clone https://github.com/tiagohanna123/vision-text-engine.git
cd vision-text-engine

# Criar ambiente virtual e instalar
uv sync
uv pip install -e ".[dev]"

# Verificar instalação
uv run vte --help
uv run vte info
```

## Dependências de Sistema

No Linux, algumas bibliotecas do OpenCV podem ser necessárias:

```bash
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 tesseract-ocr
```

## Verificação

Após instalar, execute:

```bash
vte info
```

Se tudo estiver correto, você verá as informações do engine, backends disponíveis e configuração.

## Docker

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN pip install vision-text-engine[cli]

ENTRYPOINT ["vte"]
```
