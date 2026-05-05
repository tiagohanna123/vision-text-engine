"""Modelos de dados do Vision Text Engine."""

from dataclasses import dataclass, field


@dataclass
class OCRResult:
    """Resultado de OCR para uma imagem."""

    file_path: str
    raw_texts: list[str] = field(default_factory=list)
    filtered_texts: list[str] = field(default_factory=list)
    confidence_scores: list[float] = field(default_factory=list)
    error: str | None = None
    preprocessing_time: float = 0.0
    ocr_time: float = 0.0
    total_time: float = 0.0

    @property
    def success(self) -> bool:
        """True when error is None — operation completed without failures."""
        return self.error is None

    @property
    def text(self) -> str:
        """Texto filtrado como string única."""
        return "\n".join(self.filtered_texts)

    @property
    def raw_text(self) -> str:
        """Texto bruto como string única."""
        return "\n".join(self.raw_texts)


@dataclass
class BatchResult:
    """Resultado de OCR para múltiplas imagens."""

    results: list[OCRResult] = field(default_factory=list)
    total_images: int = 0
    successful: int = 0
    failed: int = 0
    total_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Percentage of successful images (0.0-100.0)."""
        if self.total_images == 0:
            return 0.0
        return self.successful / self.total_images * 100


@dataclass
class FilterRule:
    """Regra de filtragem para texto extraído."""

    name: str
    keywords: list[str] = field(default_factory=list)
    min_length: int = 3
    max_length: int = 100
    require_at_symbol: bool = False
    require_handle_format: bool = False
    require_prefix: str | None = None
    exclude_patterns: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)


class ImagePreprocessingConfig:
    """Configuração de pré-processamento de imagem."""

    def __init__(
        self,
        contrast_limit: float = 0.5,
        brightness_limit: float = 0.3,
        denoise_strength: int = 10,
        sharpen: bool = True,
        resize_max_width: int = 1920,
        resize_max_height: int = 1920,
        grayscale: bool = True,
        auto_rotate: bool = True,
        crop_margin: int = 0,
    ):
        self.contrast_limit = contrast_limit
        self.brightness_limit = brightness_limit
        self.denoise_strength = denoise_strength
        self.sharpen = sharpen
        self.resize_max_width = resize_max_width
        self.resize_max_height = resize_max_height
        self.grayscale = grayscale
        self.auto_rotate = auto_rotate
        self.crop_margin = crop_margin
