"""Módulo core do Vision Text Engine."""
from .engine import VisionEngine
from .models import BatchResult, ImagePreprocessingConfig, OCRResult

__all__ = ["BatchResult", "ImagePreprocessingConfig", "OCRResult", "VisionEngine"]
