"""
Funções de alto nível para extração de texto.

Uso rápido:
    >>> from vision_text_engine import extract_text
    >>> result = extract_text("foto.jpg")
    >>> print(result.text)
"""

from .core.engine import VisionEngine
from .core.models import BatchResult, OCRResult
from .filters.smart_filter import smart_filter

_global_engine: VisionEngine | None = None


def _get_engine(**kwargs) -> VisionEngine:
    """Retorna engine global (singleton)."""
    global _global_engine
    if _global_engine is None:
        _global_engine = VisionEngine(
            filter_fn=smart_filter,
            **kwargs,
        )
    return _global_engine


def extract_text(
    image_path: str,
    *,
    lang: list[str] | None = None,
    gpu: bool = False,
    preprocess: bool = True,
    paragraph: bool = False,
) -> OCRResult:
    """
    Extrai texto de uma imagem. Função de mais alto nível.

    Args:
        image_path: Caminho da imagem.
        lang: Idiomas para OCR (padrão: ['pt', 'en']).
        gpu: Usar GPU (padrão: False).
        preprocess: Aplicar pré-processamento.
        paragraph: Agrupar em parágrafos.

    Returns:
        OCRResult com texto extraído e filtrado.

    """
    engine = _get_engine(lang=lang, gpu=gpu)
    return engine.extract(
        image_path=image_path,
        preprocess=preprocess,
        paragraph=paragraph,
    )


def extract_text_batch(
    image_paths: list[str],
    *,
    lang: list[str] | None = None,
    gpu: bool = False,
    preprocess: bool = True,
    show_progress: bool = True,
) -> BatchResult:
    """
    Extrai texto de múltiplas imagens.

    Args:
        image_paths: Lista de caminhos.
        lang: Idiomas para OCR.
        gpu: Usar GPU.
        preprocess: Aplicar pré-processamento.
        show_progress: Mostrar progresso.

    Returns:
        BatchResult com todos os resultados.

    """
    engine = _get_engine(lang=lang, gpu=gpu)
    return engine.extract_batch(
        image_paths=image_paths,
        preprocess=preprocess,
        show_progress=show_progress,
    )
