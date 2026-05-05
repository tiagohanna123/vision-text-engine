"""Tests for vision_text_engine.core.engine.

Tests VisionEngine: initialization, extract(), extract_batch(),
error handling (file not found, reader not installed), preprocessing,
and available_backends().
"""

import sys
from unittest.mock import MagicMock, patch

from vision_text_engine.core.engine import VisionEngine
from vision_text_engine.core.models import BatchResult


class TestVisionEngineInit:
    """VisionEngine construction and configuration."""

    def test_default_init(self):
        """Default initialization."""
        engine = VisionEngine()
        assert engine.lang == ["pt", "en"]
        assert engine.gpu is False
        assert engine._preprocessor is None
        assert engine._filter_fn is None
        assert engine._model_storage is None
        assert engine._download_enabled is True
        assert engine._reader is None
        assert engine._initialized is False

    def test_custom_lang(self):
        """Custom language list."""
        engine = VisionEngine(lang=["en", "fr"])
        assert engine.lang == ["en", "fr"]

    def test_gpu_enabled(self):
        """GPU enabled."""
        engine = VisionEngine(gpu=True)
        assert engine.gpu is True

    def test_custom_preprocessor(self):
        """Custom preprocessor function."""
        fn = lambda x: x  # noqa: E731
        engine = VisionEngine(preprocessor=fn)
        assert engine._preprocessor is fn

    def test_custom_filter(self):
        """Custom filter function."""
        fn = lambda x: x  # noqa: E731
        engine = VisionEngine(filter_fn=fn)
        assert engine._filter_fn is fn

    def test_model_storage(self):
        """Custom model storage directory."""
        engine = VisionEngine(model_storage_directory="/tmp/models")
        assert engine._model_storage == "/tmp/models"

    def test_download_disabled(self):
        """Download disabled."""
        engine = VisionEngine(download_enabled=False)
        assert engine._download_enabled is False


class TestExtract:
    """VisionEngine.extract() method."""

    def test_file_not_found(self, sample_image_path):
        """Returns error when file does not exist."""
        engine = VisionEngine()
        result = engine.extract(image_path="/nonexistent/file.png")
        assert result.success is False
        assert "Arquivo não encontrado" in result.error
        assert result.file_path == "/nonexistent/file.png"
        assert result.total_time >= 0

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", False)
    def test_reader_not_installed(self, sample_image_path):
        """Returns error when easyocr is not available."""
        engine = VisionEngine()
        result = engine.extract(image_path=sample_image_path)
        assert result.success is False
        assert "EasyOCR não está instalado" in result.error

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_successful_extract_detail_0(self, sample_image_path):
        """Successful OCR with detail=0 (text only)."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["hello ", " world ", "  test  "]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, detail=0, preprocess=False)
        assert result.success is True
        assert result.raw_texts == ["hello", "world", "test"]
        assert result.file_path == sample_image_path

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_successful_extract_detail_1(self, sample_image_path):
        """Successful OCR with detail=1 (with bounding boxes)."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = [
            ([[0, 0], [10, 0], [10, 10], [0, 10]], "hello", 0.95),
            ([[0, 0], [20, 0], [20, 10], [0, 10]], "world", 0.87),
        ]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, detail=1, preprocess=False)
        assert result.success is True
        assert result.raw_texts == ["hello", "world"]
        assert result.confidence_scores == [0.95, 0.87]

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_empty_result(self, sample_image_path):
        """OCR returns empty result."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = []

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, detail=0, preprocess=False)
        assert result.success is True
        assert result.raw_texts == []

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_ocr_whitespace_only(self, sample_image_path):
        """OCR returns only whitespace strings — should be stripped."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["   ", "  ", ""]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, detail=0, preprocess=False)
        assert result.success is True
        assert result.raw_texts == []

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_ocr_error(self, sample_image_path):
        """OCR raises an exception."""
        mock_reader = MagicMock()
        mock_reader.readtext.side_effect = RuntimeError("OCR failed horribly")

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, preprocess=False)
        assert result.success is False
        assert "Erro no OCR" in result.error

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_with_filter_fn(self, sample_image_path):
        """Filter function applied to raw texts."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["hello @user", "check this out"]

        def dummy_filter(texts):
            return [t for t in texts if "@" in t]

        engine = VisionEngine(filter_fn=dummy_filter)
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, detail=0, preprocess=False)
        assert result.raw_texts == ["hello @user", "check this out"]
        assert result.filtered_texts == ["hello @user"]

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_without_filter_fn(self, sample_image_path):
        """Without filter fn, filtered_texts == raw_texts."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["some text"]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, detail=0, preprocess=False)
        assert result.filtered_texts == result.raw_texts

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    @patch("vision_text_engine.core.engine._HAS_CV2", True)
    def test_with_preprocessing_default(self, sample_image_path):
        """Preprocessing enabled, cv2 available."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["preprocessed text"]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        # Patch the pipeline import inside extract()
        with patch(
            "vision_text_engine.preprocessing.pipeline.preprocess_image",
        ) as mock_preprocess:
            mock_preprocess.return_value = "processed_img_array"
            result = engine.extract(image_path=sample_image_path, detail=0, preprocess=True)
            assert result.success is True
            mock_preprocess.assert_called_once()
            assert result.raw_texts == ["preprocessed text"]

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_with_custom_preprocessor(self, sample_image_path):
        """Custom preprocessor is used instead of default pipeline."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["custom preprocessed"]

        custom_prep = MagicMock(return_value="custom_img")

        engine = VisionEngine(preprocessor=custom_prep)
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, detail=0, preprocess=True)
        assert result.success is True
        custom_prep.assert_called_once_with(sample_image_path, None)
        assert result.raw_texts == ["custom preprocessed"]

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_preprocessing_error(self, sample_image_path):
        """Preprocessing raises exception."""
        mock_reader = MagicMock()

        def bad_preprocessor(*args, **kwargs):
            raise ValueError("Preprocessing failed")

        engine = VisionEngine(preprocessor=bad_preprocessor)
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, preprocess=True)
        assert result.success is False
        assert "Erro no pré-processamento" in result.error

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_preprocess_disabled(self, sample_image_path):
        """When preprocess=False, image_path is passed directly to reader."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["no preprocessing"]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(image_path=sample_image_path, detail=0, preprocess=False)
        assert result.success is True
        # When preprocess=False, the path string is passed as-is
        mock_reader.readtext.assert_called_with(sample_image_path, detail=0, paragraph=False)

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_paragraph_parameter(self, sample_image_path):
        """paragraph=True is passed through to reader."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["paragraph text"]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        result = engine.extract(
            image_path=sample_image_path, detail=0, paragraph=True, preprocess=False
        )
        assert result.success is True
        mock_reader.readtext.assert_called_with(sample_image_path, detail=0, paragraph=True)

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_consecutive_calls(self, sample_image_path, another_image_path):
        """Multiple extract calls work correctly."""
        mock_reader = MagicMock()
        mock_reader.readtext.side_effect = [
            ["first image text"],
            ["second image text"],
        ]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        r1 = engine.extract(image_path=sample_image_path, detail=0, preprocess=False)
        r2 = engine.extract(image_path=another_image_path, detail=0, preprocess=False)

        assert r1.success is True
        assert r1.raw_texts == ["first image text"]
        assert r2.success is True
        assert r2.raw_texts == ["second image text"]
        assert mock_reader.readtext.call_count == 2


class TestExtractBatch:
    """VisionEngine.extract_batch() method."""

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_batch_two_images(self, sample_image_path, another_image_path):
        """Batch processing with two images."""
        mock_reader = MagicMock()
        mock_reader.readtext.side_effect = [
            ["img1 text"],
            ["img2 text"],
        ]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        batch = engine.extract_batch(
            image_paths=[sample_image_path, another_image_path],
            detail=0,
            preprocess=False,
            show_progress=False,
        )

        assert isinstance(batch, BatchResult)
        assert batch.total_images == 2
        assert batch.successful == 2
        assert batch.failed == 0
        assert len(batch.results) == 2
        assert batch.results[0].raw_texts == ["img1 text"]
        assert batch.results[1].raw_texts == ["img2 text"]

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_batch_with_failures(self, sample_image_path, another_image_path):
        """Batch processing with some failures."""
        mock_reader = MagicMock()
        mock_reader.readtext.side_effect = [
            ["success text"],
            RuntimeError("OCR error"),
        ]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        batch = engine.extract_batch(
            image_paths=[sample_image_path, another_image_path],
            detail=0,
            preprocess=False,
            show_progress=False,
        )

        assert batch.total_images == 2
        assert batch.successful == 1
        assert batch.failed == 1
        assert batch.results[0].success is True
        assert batch.results[1].success is False

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_batch_empty_list(self):
        """Batch processing with empty list."""
        engine = VisionEngine()
        engine._reader = MagicMock()
        engine._initialized = True

        batch = engine.extract_batch(image_paths=[], preprocess=False, show_progress=False)

        assert batch.total_images == 0
        assert batch.successful == 0
        assert batch.failed == 0
        assert batch.results == []
        assert batch.total_time >= 0

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    def test_batch_with_progress(self, capsys, sample_image_path):
        """Batch processing shows progress."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["text"]

        engine = VisionEngine()
        engine._reader = mock_reader
        engine._initialized = True

        batch = engine.extract_batch(
            image_paths=[sample_image_path],
            detail=0,
            preprocess=False,
            show_progress=True,
        )

        captured = capsys.readouterr()
        assert "test_image.png" in captured.out
        assert "[1/1]" in captured.out


class TestAvailableBackends:
    """VisionEngine.available_backends() method."""

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    @patch("vision_text_engine.core.engine._HAS_CV2", True)
    def test_both_available(self):
        """Both backends available."""
        engine = VisionEngine()
        backends = engine.available_backends()
        assert backends["easyocr"] is True
        assert backends["opencv"] is True

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", False)
    @patch("vision_text_engine.core.engine._HAS_CV2", False)
    def test_none_available(self):
        """No backends available."""
        engine = VisionEngine()
        backends = engine.available_backends()
        assert backends["easyocr"] is False
        assert backends["opencv"] is False

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    @patch("vision_text_engine.core.engine._HAS_CV2", False)
    def test_only_easyocr(self):
        """Only easyocr available."""
        engine = VisionEngine()
        backends = engine.available_backends()
        assert backends["easyocr"] is True
        assert backends["opencv"] is False

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", False)
    @patch("vision_text_engine.core.engine._HAS_CV2", True)
    def test_only_opencv(self):
        """Only opencv available."""
        engine = VisionEngine()
        backends = engine.available_backends()
        assert backends["easyocr"] is False
        assert backends["opencv"] is True


class TestEngineImportFailures:
    """Cobre os except blocks nos imports do módulo engine (linhas 19-20, 26-27)."""

    def test_easyocr_import_error_triggers_except(self):
        """O except (ImportError, RuntimeError) em engine.py linha 19-20 é executado
        quando easyocr não pode ser importado."""
        orig_modules = {}
        for key in ("easyocr", "vision_text_engine.core.engine"):
            if key in sys.modules:
                orig_modules[key] = sys.modules[key]

        try:
            sys.modules.pop("easyocr", None)
            sys.modules.pop("vision_text_engine.core.engine", None)

            # None sentinel: Python levanta ImportError quando o módulo
            # está em sys.modules com valor None (evita patch do __import__)
            sys.modules["easyocr"] = None

            import vision_text_engine.core.engine as eng

            assert eng._HAS_EASYOCR is False
        finally:
            for key, mod in orig_modules.items():
                sys.modules[key] = mod

    def test_cv2_import_error_triggers_except(self):
        """O except (ImportError, RuntimeError) em engine.py linha 26-27 é executado
        quando cv2 não pode ser importado."""
        orig_modules = {}
        for key in ("cv2", "vision_text_engine.core.engine"):
            if key in sys.modules:
                orig_modules[key] = sys.modules[key]

        try:
            sys.modules.pop("cv2", None)
            sys.modules.pop("vision_text_engine.core.engine", None)

            # None sentinel: Python levanta ImportError quando o módulo
            # está em sys.modules com valor None (evita patch do __import__)
            sys.modules["cv2"] = None

            import vision_text_engine.core.engine as eng

            assert eng._HAS_CV2 is False
        finally:
            for key, mod in orig_modules.items():
                sys.modules[key] = mod


class TestEnsureReader:
    """Cobre _ensure_reader com model_storage e download_enabled (linhas 66-72)."""

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    @patch("vision_text_engine.core.engine.easyocr")
    def test_ensure_reader_model_storage(self, mock_easyocr, sample_image_path):
        """_ensure_reader passa model_storage_directory ao Reader."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["text"]
        mock_easyocr.Reader.return_value = mock_reader

        engine = VisionEngine(
            model_storage_directory="/tmp/custom_models",
            download_enabled=False,
        )
        result = engine.extract(image_path=sample_image_path, preprocess=False)
        assert result.success is True
        mock_easyocr.Reader.assert_called_once_with(
            ["pt", "en"],
            gpu=False,
            model_storage_directory="/tmp/custom_models",
            download_enabled=False,
        )

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    @patch("vision_text_engine.core.engine.easyocr")
    def test_ensure_reader_download_disabled(self, mock_easyocr, sample_image_path):
        """_ensure_reader passa download_enabled=False ao Reader."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["text"]
        mock_easyocr.Reader.return_value = mock_reader

        engine = VisionEngine(download_enabled=False)
        result = engine.extract(image_path=sample_image_path, preprocess=False)
        assert result.success is True
        mock_easyocr.Reader.assert_called_once_with(
            ["pt", "en"],
            gpu=False,
            download_enabled=False,
        )

    @patch("vision_text_engine.core.engine._HAS_EASYOCR", True)
    @patch("vision_text_engine.core.engine.easyocr")
    def test_ensure_reader_model_storage_only(self, mock_easyocr, sample_image_path):
        """_ensure_reader com model_storage_directory mas download habilitado."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = ["text"]
        mock_easyocr.Reader.return_value = mock_reader

        engine = VisionEngine(model_storage_directory="/tmp/models")
        result = engine.extract(image_path=sample_image_path, preprocess=False)
        assert result.success is True
        mock_easyocr.Reader.assert_called_once_with(
            ["pt", "en"],
            gpu=False,
            model_storage_directory="/tmp/models",
        )
        kwargs = mock_easyocr.Reader.call_args[1]
        assert "download_enabled" not in kwargs
