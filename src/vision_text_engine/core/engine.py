"""
Motor OCR principal do Vision Text Engine.

Wrapper sobre EasyOCR com pipeline de pré-processamento,
múltiplos backends e fallback automático.
"""

import os
import time
from collections.abc import Callable
from typing import Any

from .models import BatchResult, ImagePreprocessingConfig, OCRResult

try:
    import easyocr

    _HAS_EASYOCR = True
except (ImportError, RuntimeError):
    _HAS_EASYOCR = False

try:
    import cv2  # noqa: F401 — imported to detect availability (try/except pattern)

    _HAS_CV2 = True
except (ImportError, RuntimeError):
    _HAS_CV2 = False


class VisionEngine:
    """
    Motor de visão computacional para extração de texto.

    Características:
    - Pipeline preprocessing → OCR → filtragem
    - Cache de modelo EasyOCR (carrega uma vez)
    - Fallback automático entre backends
    - Suporte a múltiplos idiomas
    - Batch processing com progresso
    """

    def __init__(
        self,
        lang: list[str] | None = None,
        gpu: bool = False,
        preprocessor: Callable[..., Any] | None = None,
        filter_fn: Callable[..., Any] | None = None,
        model_storage_directory: str | None = None,
        download_enabled: bool = True,
    ):
        self.lang = lang or ["pt", "en"]
        self.gpu = gpu
        self._preprocessor = preprocessor
        self._filter_fn = filter_fn
        self._model_storage = model_storage_directory
        self._download_enabled = download_enabled
        self._reader: easyocr.Reader | None = None
        self._initialized = False

    def _ensure_reader(self) -> None:
        """Inicializa o reader EasyOCR (lazy load)."""
        if self._reader is not None:
            return
        if not _HAS_EASYOCR:
            raise RuntimeError("EasyOCR não está instalado. Execute: pip install easyocr")
        kwargs: dict[str, object] = {"gpu": self.gpu}
        if self._model_storage:
            kwargs["model_storage_directory"] = self._model_storage
        if not self._download_enabled:
            kwargs["download_enabled"] = False
        self._reader = easyocr.Reader(self.lang, **kwargs)
        self._initialized = True

    def extract(
        self,
        image_path: str,
        detail: int = 0,
        paragraph: bool = False,
        preprocess: bool = True,
        prep_config: ImagePreprocessingConfig | None = None,
    ) -> OCRResult:
        """
        Extrai texto de uma imagem.

        Args:
            image_path: Caminho da imagem.
            detail: 0 = só texto, 1 = texto + bounding box + confiança.
            paragraph: True = agrupa em parágrafos.
            preprocess: Aplica pré-processamento antes do OCR.
            prep_config: Configuração de pré-processamento.

        Returns:
            OCRResult com textos extraídos.

        """
        result = OCRResult(file_path=image_path)
        t_start = time.time()

        if not os.path.isfile(image_path):
            result.error = f"Arquivo não encontrado: {image_path}"
            result.total_time = time.time() - t_start
            return result

        try:
            self._ensure_reader()
        except RuntimeError as e:
            result.error = str(e)
            result.total_time = time.time() - t_start
            return result

        # Preprocessamento
        t_pre = time.time()
        try:
            if preprocess and self._preprocessor:
                img = self._preprocessor(image_path, prep_config)
            elif preprocess and _HAS_CV2:
                from ..preprocessing.pipeline import preprocess_image

                img = preprocess_image(image_path, prep_config)
            else:
                img = image_path
            result.preprocessing_time = time.time() - t_pre
        except Exception as e:
            result.error = f"Erro no pré-processamento: {e}"
            result.total_time = time.time() - t_start
            return result

        # OCR
        t_ocr = time.time()
        try:
            assert self._reader is not None
            raw = self._reader.readtext(img, detail=detail, paragraph=paragraph)
            result.ocr_time = time.time() - t_ocr
        except Exception as e:
            result.error = f"Erro no OCR: {e}"
            result.total_time = time.time() - t_start
            return result

        # Processar resultados
        if detail == 0:
            result.raw_texts = [t.strip() for t in raw if t and t.strip()]
        else:
            result.raw_texts = [t[1].strip() for t in raw if t[1] and t[1].strip()]
            result.confidence_scores = [float(t[2]) for t in raw if len(t) > 2]

        # Filtrar
        if self._filter_fn:
            result.filtered_texts = self._filter_fn(result.raw_texts)
        else:
            result.filtered_texts = result.raw_texts

        result.total_time = time.time() - t_start
        return result

    def extract_batch(
        self,
        image_paths: list[str],
        detail: int = 0,
        paragraph: bool = False,
        preprocess: bool = True,
        prep_config: ImagePreprocessingConfig | None = None,
        show_progress: bool = True,
    ) -> BatchResult:
        """
        Extrai texto de múltiplas imagens.

        Args:
            image_paths: Lista de caminhos de imagens.
            detail: 0 = só texto, 1 = com bounding boxes.
            paragraph: True = agrupa em parágrafos.
            preprocess: Aplica pré-processamento.
            prep_config: Configuração de pré-processamento.
            show_progress: Mostra barra de progresso.

        Returns:
            BatchResult com resultados de todas as imagens.

        """
        batch = BatchResult(total_images=len(image_paths))
        t_start = time.time()

        for i, path in enumerate(image_paths):
            if show_progress:
                print(f"[{i + 1}/{len(image_paths)}] {os.path.basename(path)}")

            result = self.extract(
                image_path=path,
                detail=detail,
                paragraph=paragraph,
                preprocess=preprocess,
                prep_config=prep_config,
            )
            batch.results.append(result)

            if result.success:
                batch.successful += 1
            else:
                batch.failed += 1

        batch.total_time = time.time() - t_start
        return batch

    def available_backends(self) -> dict[str, bool]:
        """Retorna status dos backends disponíveis."""
        return {
            "easyocr": _HAS_EASYOCR,
            "opencv": _HAS_CV2,
        }
