"""
Vision Text Engine — Motor de extração de texto de imagens.

Pipeline completo: preprocessing → OCR → filtragem inteligente.
Múltiplos backends: EasyOCR (primário), Tesseract (fallback), API (fallback final).
"""

__version__ = "0.1.0"

# Lazy imports — easyocr/torchvision têm dependências pesadas
# que podem causar crash (CUDA mismatch). Importar apenas quando usado.


def __getattr__(name):
    if name == "VisionEngine":
        from .core.engine import VisionEngine

        return VisionEngine
    if name in ("extract_text", "extract_text_batch"):
        from .api import extract_text, extract_text_batch

        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["VisionEngine", "extract_text", "extract_text_batch"]
