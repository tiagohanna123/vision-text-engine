"""Shared fixtures and configurations for tests.

Fixes broken import in preprocessing/pipeline.py and provides
common test utilities.
"""

import sys
from unittest.mock import MagicMock

import pytest

# ── Mock easyocr BEFORE any import that touches engine.py ────────────
# engine.py does `import easyocr` at module level, which loads torch,
# which can crash with SIGBUS due to CUDA version mismatch on this machine.
# We inject a mock into sys.modules so the import succeeds silently.
_easyocr_mock = MagicMock()
_easyocr_mock.Reader = MagicMock
sys.modules["easyocr"] = _easyocr_mock


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
