"""
Vision Text Engine — Motor de extração de texto de imagens.

Pipeline completo: preprocessing → OCR → filtragem inteligente.
Múltiplos backends: EasyOCR (primário), Tesseract (fallback), API (fallback final).
"""

__version__ = "0.1.0"

from .api import extract_text, extract_text_batch
from .core.engine import VisionEngine

__all__ = ["VisionEngine", "extract_text", "extract_text_batch"]
