"""
Pré-processamento de imagem para OCR.

Pipeline de melhoramento: contraste → brilho → denoise → sharpen → redimensionamento.
"""


from ..core.models import ImagePreprocessingConfig

try:
    import cv2
    import numpy as np
    _HAS_CV2 = True
except ImportError:
    _HAS_CV2 = False


def preprocess_image(
    image_path: str,
    config: ImagePreprocessingConfig | None = None,
) -> "np.ndarray | None":
    """
    Pré-processa uma imagem para melhorar qualidade OCR.

    Args:
        image_path: Caminho da imagem.
        config: Configuração de pré-processamento.

    Returns:
        Imagem processada como numpy array, ou None se falhar.

    """
    if not _HAS_CV2:
        return _load_image_fallback(image_path)

    cfg = config or ImagePreprocessingConfig()
    img = cv2.imread(image_path)
    if img is None:
        return _load_image_fallback(image_path)

    # Grayscale
    if cfg.grayscale and len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Redimensionar se maior que o máximo
    h, w = img.shape[:2]
    if w > cfg.resize_max_width or h > cfg.resize_max_height:
        scale = min(cfg.resize_max_width / w, cfg.resize_max_height / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Contraste e brilho (CLAHE para grayscale)
    if cfg.grayscale:
        clahe = cv2.createCLAHE(clipLimit=cfg.contrast_limit * 4, tileGridSize=(8, 8))
        img = clahe.apply(img)
    else:
        img = cv2.convertScaleAbs(img, alpha=1 + cfg.contrast_limit, beta=cfg.brightness_limit * 255)

    # Denoise
    if cfg.denoise_strength > 0:
        img = cv2.fastNlMeansDenoising(img, None, cfg.denoise_strength, 7, 21)

    # Sharpen
    if cfg.sharpen:
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        img = cv2.filter2D(img, -1, kernel)

    return img


def _load_image_fallback(image_path: str):
    """Fallback: carrega imagem sem processamento."""
    if not _HAS_CV2:
        return None
    return cv2.imread(image_path)
