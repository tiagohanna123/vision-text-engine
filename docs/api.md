# API Python

A API pública do Vision Text Engine expõe funções de alto nível para extração de texto.

## `extract_text()`

```python
from vision_text_engine import extract_text

result = extract_text("caminho/para/imagem.jpg", lang=["pt", "en"])
print(result.text)
```

### Parâmetros

| Parâmetro    | Tipo           | Padrão          | Descrição                              |
|-------------|----------------|-----------------|----------------------------------------|
| `image_path` | `str`          | —               | Caminho para a imagem                  |
| `lang`       | `list[str]`    | `["pt", "en"]`  | Idiomas para OCR                       |
| `gpu`        | `bool`         | `False`         | Usar GPU (CUDA)                        |
| `preprocess` | `bool`         | `True`          | Aplicar pré-processamento OpenCV       |

### Retorno

Retorna um `ExtractionResult` com os campos:

| Campo            | Tipo     | Descrição                          |
|------------------|----------|------------------------------------|
| `file_path`      | `str`    | Caminho do arquivo processado      |
| `success`        | `bool`   | True se a extração foi bem-sucedida |
| `text`           | `str`    | Texto filtrado final               |
| `raw_text`       | `str`    | Texto bruto do OCR                 |
| `raw_texts`      | `list`   | Lista de textos detectados         |
| `filtered_texts` | `list`   | Lista de textos após filtragem     |
| `error`          | `str\|None` | Mensagem de erro, se houver      |
| `ocr_time`       | `float`  | Tempo do OCR em segundos           |
| `total_time`     | `float`  | Tempo total em segundos            |

## `extract_text_batch()`

```python
from vision_text_engine import extract_text_batch

result = extract_text_batch(
    ["img1.jpg", "img2.png"],
    lang=["pt", "en"]
)
print(f"Processadas: {result.successful}/{result.total_images}")
```

### Parâmetros

| Parâmetro     | Tipo           | Padrão          | Descrição                             |
|--------------|----------------|-----------------|---------------------------------------|
| `image_paths` | `list[str]`    | —               | Lista de caminhos de imagens          |
| `lang`        | `list[str]`    | `["pt", "en"]`  | Idiomas para OCR                      |
| `gpu`         | `bool`         | `False`         | Usar GPU                              |
| `preprocess`  | `bool`         | `True`          | Aplicar pré-processamento             |

### Retorno

Retorna um `BatchResult` com os campos:

| Campo           | Tipo     | Descrição                         |
|-----------------|----------|-----------------------------------|
| `total_images`  | `int`    | Total de imagens                  |
| `successful`    | `int`    | Extrações bem-sucedidas           |
| `failed`        | `int`    | Extrações com falha               |
| `success_rate`  | `float`  | Taxa de sucesso (%)               |
| `total_time`    | `float`  | Tempo total em segundos           |
| `results`       | `list`   | Lista de `ExtractionResult`       |

## VisionEngine

Para controle mais fino, use a classe `VisionEngine`:

```python
from vision_text_engine import VisionEngine

engine = VisionEngine(lang=["pt", "en"], gpu=False)
result = engine.extract("imagem.jpg")
```
