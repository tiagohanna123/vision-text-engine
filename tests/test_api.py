"""Tests for vision_text_engine.api.

Tests the high-level extract_text() and extract_text_batch()
functions exported from vision_text_engine.__init__.
"""


from unittest.mock import MagicMock, patch

from vision_text_engine.core.models import BatchResult, OCRResult


class TestExtractText:
    """Tests for the extract_text() high-level function."""

    @patch("vision_text_engine.api._get_engine")
    def test_extract_text_basic(self, mock_get_engine, sample_image_path):
        """extract_text calls engine.extract and returns OCRResult."""
        mock_engine = MagicMock()
        expected_result = OCRResult(
            file_path=sample_image_path,
            raw_texts=["hello world"],
            filtered_texts=["hello world"],
        )
        mock_engine.extract.return_value = expected_result
        mock_get_engine.return_value = mock_engine

        from vision_text_engine.api import extract_text

        result = extract_text(sample_image_path)

        assert result.file_path == sample_image_path
        assert result.text == "hello world"
        mock_engine.extract.assert_called_once_with(
            image_path=sample_image_path,
            preprocess=True,
            paragraph=False,
        )

    @patch("vision_text_engine.api._get_engine")
    def test_extract_text_with_params(self, mock_get_engine):
        """extract_text passes all parameters to engine.extract."""
        mock_engine = MagicMock()
        mock_engine.extract.return_value = OCRResult(file_path="test.png")
        mock_get_engine.return_value = mock_engine

        from vision_text_engine.api import extract_text

        result = extract_text(
            "test.png",
            lang=["fr"],
            gpu=True,
            preprocess=False,
            paragraph=True,
        )

        mock_engine.extract.assert_called_once_with(
            image_path="test.png",
            preprocess=False,
            paragraph=True,
        )
        # Verify engine was created with correct params
        mock_get_engine.assert_called_once_with(lang=["fr"], gpu=True)

    @patch("vision_text_engine.api._get_engine")
    def test_extract_text_error_handling(self, mock_get_engine):
        """extract_text propagates engine errors."""
        mock_engine = MagicMock()
        error_result = OCRResult(
            file_path="missing.png", error="Arquivo não encontrado: missing.png"
        )
        mock_engine.extract.return_value = error_result
        mock_get_engine.return_value = mock_engine

        from vision_text_engine.api import extract_text

        result = extract_text("missing.png")
        assert result.success is False
        assert "Arquivo não encontrado" in result.error


class TestExtractTextBatch:
    """Tests for the extract_text_batch() high-level function."""

    @patch("vision_text_engine.api._get_engine")
    def test_extract_text_batch_basic(self, mock_get_engine):
        """extract_text_batch calls engine.extract_batch and returns BatchResult."""
        mock_engine = MagicMock()
        paths = ["img1.png", "img2.png"]
        expected_batch = BatchResult(
            results=[
                OCRResult(file_path="img1.png", filtered_texts=["text1"]),
                OCRResult(file_path="img2.png", filtered_texts=["text2"]),
            ],
            total_images=2,
            successful=2,
            failed=0,
        )
        mock_engine.extract_batch.return_value = expected_batch
        mock_get_engine.return_value = mock_engine

        from vision_text_engine.api import extract_text_batch

        batch = extract_text_batch(paths)

        assert batch.total_images == 2
        assert batch.successful == 2
        assert batch.results[0].text == "text1"
        mock_engine.extract_batch.assert_called_once_with(
            image_paths=paths,
            preprocess=True,
            show_progress=True,
        )

    @patch("vision_text_engine.api._get_engine")
    def test_extract_text_batch_with_params(self, mock_get_engine):
        """extract_text_batch passes all parameters."""
        mock_engine = MagicMock()
        mock_engine.extract_batch.return_value = BatchResult()
        mock_get_engine.return_value = mock_engine

        from vision_text_engine.api import extract_text_batch

        batch = extract_text_batch(
            ["a.png"],
            lang=["en"],
            gpu=False,
            preprocess=False,
            show_progress=False,
        )

        mock_engine.extract_batch.assert_called_once_with(
            image_paths=["a.png"],
            preprocess=False,
            show_progress=False,
        )
        mock_get_engine.assert_called_once_with(lang=["en"], gpu=False)


class TestGlobalEngine:
    """Tests for the singleton engine pattern."""

    def tear_down(self):
        """Reset global engine after each test."""
        import vision_text_engine.api

        vision_text_engine.api._global_engine = None

    @patch("vision_text_engine.api.VisionEngine")
    def test_singleton_pattern(self, MockEngine):
        """_get_engine returns the same instance on second call."""
        import vision_text_engine.api

        vision_text_engine.api._global_engine = None

        engine1 = vision_text_engine.api._get_engine()
        engine2 = vision_text_engine.api._get_engine()

        assert engine1 is engine2
        MockEngine.assert_called_once()

    @patch("vision_text_engine.api.VisionEngine")
    def test_engine_created_with_filter_fn(self, MockEngine):
        """Engine is created with smart_filter as filter_fn."""
        import vision_text_engine.api

        vision_text_engine.api._global_engine = None

        engine = vision_text_engine.api._get_engine()
        assert MockEngine.called

        # Verify smart_filter was passed as filter_fn
        call_kwargs = MockEngine.call_args[1]
        assert "filter_fn" in call_kwargs
        assert call_kwargs["filter_fn"] is not None

    @patch("vision_text_engine.api.VisionEngine")
    def test_engine_created_with_custom_kwargs(self, MockEngine):
        """Engine is created with custom kwargs."""
        import vision_text_engine.api

        vision_text_engine.api._global_engine = None

        engine = vision_text_engine.api._get_engine(lang=["de"], gpu=True)
        call_kwargs = MockEngine.call_args[1]
        assert call_kwargs["lang"] == ["de"]
        assert call_kwargs["gpu"] is True
