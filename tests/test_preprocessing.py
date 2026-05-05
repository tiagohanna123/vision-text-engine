"""Tests for vision_text_engine.preprocessing.pipeline.

Tests preprocess_image() with mocked cv2 and without cv2 (fallback).
Uses unittest.mock to avoid needing real opencv-python.
"""

from unittest.mock import MagicMock, patch

import pytest

from vision_text_engine.core.models import ImagePreprocessingConfig


class TestPreprocessImageNoCV2:
    """Tests when cv2 is NOT available (fallback path)."""

    def test_fallback_returns_none(self, sample_image_path):
        """Without cv2, fallback returns None."""
        with patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", False):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            result = preprocess_image(sample_image_path)
        assert result is None

    def test_fallback_with_config(self, sample_image_path):
        """Config is accepted but ignored when cv2 unavailable."""
        with patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", False):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            cfg = ImagePreprocessingConfig(sharpen=False)
            result = preprocess_image(sample_image_path, config=cfg)
        assert result is None


class TestPreprocessImageWithCV2:
    """Tests when cv2 is available (mocked).

    IMPORTANT: pipeline.py does `import numpy as np`, so the module
    attribute is `np`, NOT `numpy`.  We patch `np`.
    """

    def test_basic_grayscale_processing(self, sample_image_path):
        """Basic pipeline: read, grayscale, CLAHE, denoise, sharpen."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_img = MagicMock(spec=object)
            mock_img.shape = (200, 100, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (200, 100)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path)

            mock_cv2.imread.assert_called_once_with(sample_image_path)
            mock_cv2.cvtColor.assert_called_once_with(mock_img, mock_cv2.COLOR_BGR2GRAY)
            mock_cv2.createCLAHE.assert_called_once()
            assert result is not None

    def test_resize_when_too_large(self, sample_image_path):
        """Image is resized when exceeds max dimensions."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_img = MagicMock(spec=object)
            mock_img.shape = (3000, 3000, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (3000, 3000)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path)

            mock_cv2.resize.assert_called_once()
            call_args = mock_cv2.resize.call_args[0]
            assert call_args[1] == (1920, 1920)

    def test_denoise_disabled(self, sample_image_path):
        """No denoising when denoise_strength=0."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            cfg = ImagePreprocessingConfig(denoise_strength=0)
            mock_img = MagicMock(spec=object)
            mock_img.shape = (100, 100, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (100, 100)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path, config=cfg)

            mock_cv2.fastNlMeansDenoising.assert_not_called()

    def test_sharpen_disabled(self, sample_image_path):
        """No sharpening when sharpen=False."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            cfg = ImagePreprocessingConfig(sharpen=False)
            mock_img = MagicMock(spec=object)
            mock_img.shape = (100, 100, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (100, 100)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path, config=cfg)

            mock_cv2.filter2D.assert_not_called()

    def test_non_grayscale_path(self, sample_image_path):
        """Non-grayscale pipeline: convertScaleAbs instead of CLAHE."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            cfg = ImagePreprocessingConfig(grayscale=False)
            mock_img = MagicMock(spec=object)
            mock_img.shape = (100, 100, 3)
            mock_cv2.imread.return_value = mock_img
            result = preprocess_image(sample_image_path, config=cfg)

            mock_cv2.cvtColor.assert_not_called()
            mock_cv2.createCLAHE.assert_not_called()
            mock_cv2.convertScaleAbs.assert_called_once()

    def test_cv2_imread_returns_none(self, sample_image_path):
        """When cv2.imread returns None, fallback is used."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_cv2.imread.side_effect = [None, None]
            result = preprocess_image(sample_image_path)

            assert result is None

    def test_sharpen_applied(self, sample_image_path):
        """Sharpening kernel is applied."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_img = MagicMock(spec=object)
            mock_img.shape = (100, 100, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (100, 100)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path)

            mock_cv2.filter2D.assert_called_once()

    def test_denoise_applied(self, sample_image_path):
        """Denoising is applied when denoise_strength > 0."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_img = MagicMock(spec=object)
            mock_img.shape = (100, 100, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (100, 100)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path)

            mock_cv2.fastNlMeansDenoising.assert_called_once_with(gray_img, None, 10, 7, 21)

    def test_resize_width_only(self, sample_image_path):
        """Only width exceeds max, height within bounds."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_img = MagicMock(spec=object)
            mock_img.shape = (500, 3000, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (500, 3000)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path)

            mock_cv2.resize.assert_called_once()
            call_args = mock_cv2.resize.call_args[0]
            assert call_args[1][0] == 1920
            assert call_args[1][1] == 320

    def test_no_resize_when_within_bounds(self, sample_image_path):
        """Image within bounds is not resized."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_img = MagicMock(spec=object)
            mock_img.shape = (500, 800, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (500, 800)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path)

            mock_cv2.resize.assert_not_called()

    def test_custom_config(self, sample_image_path):
        """Custom config parameters are used."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            cfg = ImagePreprocessingConfig(
                contrast_limit=1.0,
                denoise_strength=5,
                sharpen=True,
                resize_max_width=800,
                resize_max_height=600,
                grayscale=True,
            )
            mock_img = MagicMock(spec=object)
            mock_img.shape = (100, 100, 3)
            mock_cv2.imread.return_value = mock_img
            gray_img = MagicMock(spec=object)
            gray_img.shape = (100, 100)
            mock_cv2.cvtColor.return_value = gray_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = gray_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path, config=cfg)

            mock_cv2.createCLAHE.assert_called_with(clipLimit=4.0, tileGridSize=(8, 8))
            mock_cv2.fastNlMeansDenoising.assert_called_once_with(gray_img, None, 5, 7, 21)

    def test_grayscale_image_already_gray(self, sample_image_path):
        """If image is already grayscale (2D), cv2.cvtColor is skipped."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_img = MagicMock(spec=object)
            mock_img.shape = (100, 100)
            mock_cv2.imread.return_value = mock_img
            clahe_instance = MagicMock()
            clahe_instance.apply.return_value = mock_img
            mock_cv2.createCLAHE.return_value = clahe_instance
            result = preprocess_image(sample_image_path)

            mock_cv2.cvtColor.assert_not_called()
            mock_cv2.createCLAHE.assert_called_once()


class TestPreprocessImageEdgeCases:
    """Edge cases for preprocess_image."""

    def test_empty_image_path(self):
        """Empty string path returns fallback."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_cv2.imread.side_effect = [None, None]
            result = preprocess_image("")
            assert result is None

    def test_cv2_error_handled(self, sample_image_path):
        """cv2 operation raises exception."""
        with (
            patch("vision_text_engine.preprocessing.pipeline.np", new_callable=MagicMock),
            patch("vision_text_engine.preprocessing.pipeline.cv2") as mock_cv2,
            patch("vision_text_engine.preprocessing.pipeline._HAS_CV2", True),
        ):
            from vision_text_engine.preprocessing.pipeline import preprocess_image

            mock_cv2.imread.side_effect = RuntimeError("CV2 error")
            with pytest.raises(RuntimeError):
                preprocess_image(sample_image_path)
