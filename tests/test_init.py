"""Tests for the __init__ and __main__ module entry points.

Covers lazy import via __getattr__ and python -m execution.
"""

import subprocess
import sys

from vision_text_engine import __all__ as pkg_all
from vision_text_engine import __getattr__, __version__
from vision_text_engine.core import __all__ as core_all


class TestPackageInit:
    """Tests for vision_text_engine.__init__ lazy imports."""

    def test_package_exports(self):
        """Package __all__ exports expected names."""
        assert "VisionEngine" in pkg_all
        assert "extract_text" in pkg_all
        assert "extract_text_batch" in pkg_all

    def test_getattr_vision_engine(self):
        """__getattr__ lazy-loads VisionEngine."""
        from vision_text_engine import VisionEngine

        assert VisionEngine is not None

    def test_getattr_extract_text(self):
        """__getattr__ lazy-loads extract_text."""
        from vision_text_engine import extract_text

        assert callable(extract_text)

    def test_getattr_extract_text_batch(self):
        """__getattr__ lazy-loads extract_text_batch."""
        from vision_text_engine import extract_text_batch

        assert callable(extract_text_batch)

    def test_getattr_raises(self):
        """__getattr__ raises for unknown names."""
        import pytest

        with pytest.raises(AttributeError):
            __getattr__("NonExistentThing")  # type: ignore[no-untyped-call]

    def test_version(self):
        """Package has a version string."""
        assert isinstance(__version__, str)
        assert __version__ == "0.2.0"


class TestCoreInit:
    """Tests for vision_text_engine.core.__init__ lazy imports."""

    def test_core_exports(self):
        """Core __all__ exports expected names."""
        assert "VisionEngine" in core_all
        assert "OCRResult" in core_all
        assert "BatchResult" in core_all
        assert "ImagePreprocessingConfig" in core_all

    def test_core_getattr_vision_engine(self):
        """Core __getattr__ lazy-loads VisionEngine."""
        from vision_text_engine.core import VisionEngine

        assert VisionEngine is not None

    def test_core_getattr_models(self):
        """Core __getattr__ lazy-loads model classes."""
        from vision_text_engine.core import BatchResult, ImagePreprocessingConfig, OCRResult

        assert OCRResult is not None
        assert BatchResult is not None
        assert ImagePreprocessingConfig is not None

    def test_core_getattr_raises(self):
        """Core __getattr__ raises for unknown names."""
        import pytest

        from vision_text_engine.core import __getattr__ as core_getattr

        with pytest.raises(AttributeError):
            core_getattr("NonExistentThing")  # type: ignore[no-untyped-call]


class TestMainModule:
    """Tests for __main__.py (python -m vision_text_engine)."""

    def test_module_runnable(self):
        """python -m vision_text_engine exits cleanly or with expected error."""
        result = subprocess.run(
            [sys.executable, "-m", "vision_text_engine"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Should either exit with code 1 (no CLI args) or show help
        assert result.returncode in (0, 1, 2)
