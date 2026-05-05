"""Tests for vision_text_engine.core.models.

Tests OCRResult, BatchResult, FilterRule, ImagePreprocessingConfig
including properties, edge cases, and empty data scenarios.
"""

import pytest

from vision_text_engine.core.models import (
    BatchResult,
    FilterRule,
    ImagePreprocessingConfig,
    OCRResult,
)

# ── OCRResult ──────────────────────────────────────────────────────────


class TestOCRResult:
    def test_default_creation(self):
        """Create OCRResult with minimal args."""
        r = OCRResult(file_path="/img/test.png")
        assert r.file_path == "/img/test.png"
        assert r.raw_texts == []
        assert r.filtered_texts == []
        assert r.confidence_scores == []
        assert r.error is None
        assert r.preprocessing_time == 0.0
        assert r.ocr_time == 0.0
        assert r.total_time == 0.0

    def test_success_property(self):
        """success is True when error is None."""
        r = OCRResult(file_path="a.png")
        assert r.success is True

    def test_success_property_with_error(self):
        """success is False when error is set."""
        r = OCRResult(file_path="a.png", error="something went wrong")
        assert r.success is False

    def test_text_property(self):
        """text returns filtered_texts joined by newline."""
        r = OCRResult(
            file_path="a.png",
            filtered_texts=["hello", "world", "test"],
        )
        assert r.text == "hello\nworld\ntest"

    def test_text_property_empty(self):
        """text returns empty string when no filtered texts."""
        r = OCRResult(file_path="a.png", filtered_texts=[])
        assert r.text == ""

    def test_raw_text_property(self):
        """raw_text returns raw_texts joined by newline."""
        r = OCRResult(
            file_path="a.png",
            raw_texts=["foo", "bar"],
        )
        assert r.raw_text == "foo\nbar"

    def test_raw_text_property_empty(self):
        """raw_text returns empty string when no raw texts."""
        r = OCRResult(file_path="a.png", raw_texts=[])
        assert r.raw_text == ""

    def test_full_construction(self):
        """OCRResult with all fields populated."""
        r = OCRResult(
            file_path="/path/img.jpg",
            raw_texts=["raw1", "raw2"],
            filtered_texts=["filtered1"],
            confidence_scores=[0.95, 0.87],
            error=None,
            preprocessing_time=0.1,
            ocr_time=0.5,
            total_time=0.6,
        )
        assert r.file_path == "/path/img.jpg"
        assert r.raw_texts == ["raw1", "raw2"]
        assert r.filtered_texts == ["filtered1"]
        assert r.confidence_scores == [0.95, 0.87]
        assert r.error is None
        assert r.preprocessing_time == 0.1
        assert r.ocr_time == 0.5
        assert r.total_time == 0.6
        assert r.success is True
        assert r.text == "filtered1"
        assert r.raw_text == "raw1\nraw2"

    def test_single_item_texts(self):
        """Single item in filtered/raw lists."""
        r = OCRResult(
            file_path="a.png",
            raw_texts=["only_one"],
            filtered_texts=["only_filtered"],
        )
        assert r.raw_text == "only_one"
        assert r.text == "only_filtered"

    def test_text_with_newlines_in_items(self):
        """Items with embedded newlines."""
        r = OCRResult(
            file_path="a.png",
            filtered_texts=["line1\nline2", "line3"],
        )
        assert r.text == "line1\nline2\nline3"

    def test_error_edge_cases(self):
        """Error as empty string is still an error (success=False)."""
        r = OCRResult(file_path="a.png", error="")
        assert r.success is False
        assert r.error == ""


# ── BatchResult ────────────────────────────────────────────────────────


class TestBatchResult:
    def test_default_creation(self):
        """BatchResult with no args."""
        b = BatchResult()
        assert b.results == []
        assert b.total_images == 0
        assert b.successful == 0
        assert b.failed == 0
        assert b.total_time == 0.0

    def test_success_rate_zero_when_no_images(self):
        """success_rate is 0.0 when total_images == 0."""
        b = BatchResult()
        assert b.success_rate == 0.0

    def test_success_rate_all_successful(self):
        """success_rate is 100 when all succeed."""
        b = BatchResult(
            results=[OCRResult(file_path="a.png"), OCRResult(file_path="b.png")],
            total_images=2,
            successful=2,
            failed=0,
        )
        assert b.success_rate == 100.0

    def test_success_rate_partial(self):
        """success_rate reflects partial success."""
        b = BatchResult(
            total_images=4,
            successful=3,
            failed=1,
        )
        assert b.success_rate == 75.0

    def test_success_rate_none_successful(self):
        """success_rate is 0 when none succeed."""
        b = BatchResult(
            total_images=3,
            successful=0,
            failed=3,
        )
        assert b.success_rate == 0.0

    def test_success_rate_float_precision(self):
        """success_rate handles non-integer percentages."""
        b = BatchResult(
            total_images=3,
            successful=1,
            failed=2,
        )
        assert b.success_rate == pytest.approx(33.333333, rel=1e-5)

    def test_full_construction(self):
        """BatchResult with all fields."""
        results = [
            OCRResult(file_path="a.png", filtered_texts=["hello"]),
            OCRResult(file_path="b.png", error="fail"),
        ]
        b = BatchResult(
            results=results,
            total_images=2,
            successful=1,
            failed=1,
            total_time=1.5,
        )
        assert len(b.results) == 2
        assert b.results[0].text == "hello"
        assert b.results[1].error == "fail"
        assert b.total_time == 1.5

    def test_success_rate_large_numbers(self):
        """success_rate with large image counts."""
        b = BatchResult(total_images=1000, successful=1, failed=999)
        assert b.success_rate == 0.1


# ── FilterRule ─────────────────────────────────────────────────────────


class TestFilterRule:
    def test_default_creation(self):
        """FilterRule with only name."""
        rule = FilterRule(name="test_rule")
        assert rule.name == "test_rule"
        assert rule.keywords == []
        assert rule.min_length == 3
        assert rule.max_length == 100
        assert rule.require_at_symbol is False
        assert rule.require_handle_format is False
        assert rule.exclude_patterns == []
        assert rule.exclude_keywords == []

    def test_full_construction(self):
        """FilterRule with all fields."""
        rule = FilterRule(
            name="handles",
            keywords=["@user"],
            min_length=3,
            max_length=50,
            require_at_symbol=True,
            require_handle_format=True,
            exclude_patterns=[r"^\d+$"],
            exclude_keywords=["spam", "bot"],
        )
        assert rule.name == "handles"
        assert rule.keywords == ["@user"]
        assert rule.min_length == 3
        assert rule.max_length == 50
        assert rule.require_at_symbol is True
        assert rule.require_handle_format is True
        assert rule.exclude_patterns == [r"^\d+$"]
        assert rule.exclude_keywords == ["spam", "bot"]

    def test_custom_lengths(self):
        """FilterRule with different length constraints."""
        rule = FilterRule(name="short", min_length=1, max_length=10)
        assert rule.min_length == 1
        assert rule.max_length == 10

    def test_mutable_lists(self):
        """FilterRule lists are mutable (dataclass field defaults work)."""
        rule = FilterRule(name="test")
        rule.keywords.append("new_keyword")
        rule.exclude_patterns.append(r"pattern")
        assert "new_keyword" in rule.keywords
        assert "pattern" in rule.exclude_patterns


# ── ImagePreprocessingConfig ───────────────────────────────────────────


class TestImagePreprocessingConfig:
    def test_default_creation(self):
        """ImagePreprocessingConfig with defaults."""
        cfg = ImagePreprocessingConfig()
        assert cfg.contrast_limit == 0.5
        assert cfg.brightness_limit == 0.3
        assert cfg.denoise_strength == 10
        assert cfg.sharpen is True
        assert cfg.resize_max_width == 1920
        assert cfg.resize_max_height == 1920
        assert cfg.grayscale is True
        assert cfg.auto_rotate is True
        assert cfg.crop_margin == 0

    def test_custom_values(self):
        """ImagePreprocessingConfig with custom values."""
        cfg = ImagePreprocessingConfig(
            contrast_limit=1.0,
            brightness_limit=0.0,
            denoise_strength=5,
            sharpen=False,
            resize_max_width=800,
            resize_max_height=600,
            grayscale=False,
            auto_rotate=False,
            crop_margin=10,
        )
        assert cfg.contrast_limit == 1.0
        assert cfg.brightness_limit == 0.0
        assert cfg.denoise_strength == 5
        assert cfg.sharpen is False
        assert cfg.resize_max_width == 800
        assert cfg.resize_max_height == 600
        assert cfg.grayscale is False
        assert cfg.auto_rotate is False
        assert cfg.crop_margin == 10

    def test_grayscale_only(self):
        """ImagePreprocessingConfig with only grayscale=False."""
        cfg = ImagePreprocessingConfig(grayscale=False)
        assert cfg.grayscale is False
        # Other defaults unchanged
        assert cfg.contrast_limit == 0.5

    def test_zero_denoise(self):
        """ImagePreprocessingConfig with denoise_strength=0."""
        cfg = ImagePreprocessingConfig(denoise_strength=0)
        assert cfg.denoise_strength == 0

    def test_extreme_values(self):
        """ImagePreprocessingConfig with extreme values."""
        cfg = ImagePreprocessingConfig(
            contrast_limit=10.0,
            brightness_limit=-1.0,
            denoise_strength=100,
            resize_max_width=100,
            resize_max_height=100,
        )
        assert cfg.contrast_limit == 10.0
        assert cfg.brightness_limit == -1.0
        assert cfg.denoise_strength == 100
        assert cfg.resize_max_width == 100
        assert cfg.resize_max_height == 100
