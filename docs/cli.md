# CLI — Linha de Comando

A CLI `vte` (Vision Text Engine) oferece comandos para extração de texto de imagens.

## Uso Básico

```bash
vte --help
vte info
vte extract imagem.jpg
vte batch "images/*.png"
```

## Comando `extract`

Extrai texto de uma única imagem.

```bash
vte extract [opções] CAMINHO
```

### Opções

| Opção           | Descrição                               |
|-----------------|-----------------------------------------|
| `--json`        | Saída em formato JSON                   |
| `--raw`         | Exibir texto bruto (sem filtragem)      |
| `--handles`     | Extrair apenas handles (@user)          |
| `--lang`        | Idiomas para OCR (ex: `--lang pt,en`)   |

### Exemplos

```bash
# Extração básica
vte extract documento.jpg

# Saída JSON
vte extract --json foto.png

# Extrair apenas handles do Twitter/Instagram
vte extract --handles screenshot.jpg

# Especificar idiomas
vte extract --lang pt,en,es imagem.jpg
```

## Comando `batch`

Processa múltiplas imagens de uma vez.

```bash
vte batch [opções] CAMINHO
```

O `CAMINHO` pode ser um glob (`*.png`), um padrão (`images/*.jpg`) ou um diretório.

### Opções

| Opção           | Descrição                               |
|-----------------|-----------------------------------------|
| `--json`        | Saída em formato JSON                   |
| `--lang`        | Idiomas para OCR                        |

### Exemplos

```bash
# Processar todos PNGs do diretório
vte batch "downloads/*.png"

# Processar diretório inteiro
vte batch images/

# Saída JSON
vte batch --json "fotos/*.jpg"
```

## Comando `info`

Exibe informações sobre o Vision Text Engine, backends disponíveis e configuração.

```bash
vte info [opções]
```

### Opções

| Opção              | Descrição                               |
|--------------------|-----------------------------------------|
| `--lang`           | Idiomas para verificar disponibilidade  |
| `--gpu`            | Verificar disponibilidade de GPU        |
| `--no-preprocess`  | Desabilitar pré-processamento           |

### Exemplo

```bash
vte info --lang pt,en --gpu
```

Saída típica:

```
╭──────────────────────────────────────╮
│        Vision Text Engine           │
│          v0.1.0 — Alpha            │
├──────────────────────────────────────┤
│ Python:   3.11.5                     │
│ GPU:      ✅ CUDA disponível         │
│ Idiomas:  pt, en                     │
│ Backends: ✅ easyocr ❌ opencv       │
│ Pré-processamento: ✅ ativo          │
╰──────────────────────────────────────╯
```

## Opções Globais

As seguintes opções podem ser usadas com qualquer comando:

| Opção              | Descrição                               |
|--------------------|-----------------------------------------|
| `--lang`           | Idiomas para OCR (lista separada por vírgula) |
| `--gpu`            | Habilitar GPU                           |
| `--no-preprocess`  | Desabilitar pré-processamento           |
