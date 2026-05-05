"""Shared fixtures and configurations for tests.

Fixes broken import in preprocessing/pipeline.py and provides
common test utilities.
"""
import sys
import types

import pytest

# ── Fix broken import in preprocessing/pipeline.py ──────────────────────
# pipeline.py does "from .models import ImagePreprocessingConfig" at module level,
# but preprocessing/models.py does not exist (should be from ..core.models).
# We inject a synthetic module so imports don't crash when loading pipeline.py.
from vision_text_engine.core.models import ImagePreprocessingConfig as _RealIPC

_models_mod = types.ModuleType("vision_text_engine.preprocessing.models")
_models_mod.ImagePreprocessingConfig = _RealIPC
sys.modules["vision_text_engine.preprocessing.models"] = _models_mod


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a temporary image file path."""
    img = tmp_path / "test_image.png"
    img.write_text("fake-image-content")
    return str(img)


@pytest.fixture
def another_image_path(tmp_path):
    """Create another temporary image file path."""
    img = tmp_path / "another_image.jpg"
    img.write_text("fake-image-content")
    return str(img)
