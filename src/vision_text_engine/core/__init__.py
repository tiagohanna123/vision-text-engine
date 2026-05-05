"""Módulo core do Vision Text Engine."""

# Lazy imports — evitar carregar easyocr/torchvision no import do módulo


def __getattr__(name):
    if name == "VisionEngine":
        from .engine import VisionEngine

        return VisionEngine
    if name in ("BatchResult", "ImagePreprocessingConfig", "OCRResult"):
        from .models import BatchResult, ImagePreprocessingConfig, OCRResult

        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["BatchResult", "ImagePreprocessingConfig", "OCRResult", "VisionEngine"]
