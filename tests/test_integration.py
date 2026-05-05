"""Testes de integração para o Vision Text Engine.

Testa o pipeline completo: dados → filtro → resultado.
"""

from vision_text_engine.core.models import BatchResult, OCRResult
from vision_text_engine.filters.smart_filter import (
    extract_handles,
    extract_hashtags,
    smart_filter,
)


class TestInstagramScreenshotPipeline:
    """Pipeline completo: extração de handles do Instagram."""

    def test_extract_multiple_handles(self):
        """Cenário real: Instagram DM com múltiplas menções."""
        texts = [
            "@victorcortez",
            "@gigioficial",
            "Você mencionou @victorcortez no seu story",
            "Mencionou você no próprio story",
            "@_joaosilva_",
            "Ver perfil",
            "seguidores 1.234",
            "22:30",
        ]
        filtered = smart_filter(texts)
        handles = extract_handles(filtered)
        assert "@victorcortez" in handles
        assert "@gigioficial" in handles
        assert "@_joaosilva_" in handles
        assert len(handles) == 3

    def test_handle_with_trailing_noise(self):
        """Handle com ruído deve ser filtrado, mas o @handle puro extraído."""
        texts = [
            "@_victorcortez_no",  # Trailing noise from layout misread
            "Normal text",
        ]
        handles = extract_handles(texts)
        assert "@_victorcortez_no" in handles

    def test_noise_removed(self):
        """UI text e timestamps removidos."""
        texts = [
            "seguidores",
            "curtir",
            "comentar",
            "22:30",
            "22h30",
            "ontem",
            "há 2 horas",
            "@real_user",
        ]
        filtered = smart_filter(texts)
        assert "@real_user" in filtered
        assert "seguidores" not in filtered
        assert "22:30" not in filtered

    def test_empty_result_after_filter(self):
        """Se tudo for ruído, resultado filtrado vazio."""
        texts = ["seguidores", "curtir", "22:30"]
        filtered = smart_filter(texts)
        assert filtered == []


class TestTwitterScreenshotPipeline:
    """Pipeline para Twitter/X screenshots."""

    def test_twitter_handles_and_hashtags(self):
        texts = [
            "@elonmusk",
            "#tech",
            "#python",
            "Curtir",
            "Compartilhar",
        ]
        filtered = smart_filter(texts)
        assert "@elonmusk" in filtered
        assert "#tech" in filtered
        assert "#python" in filtered
        assert "Curtir" not in filtered

    def test_hashtag_extraction(self):
        texts = ["#python é melhor", "#javascript também"]
        tags = extract_hashtags(texts)
        assert "#python" in tags
        assert "#javascript" in tags


class TestEmailAndUrlPipeline:
    """Pipeline para extração de emails e URLs."""

    def test_email_in_text(self):
        texts = [
            "contato@empresa.com.br",
            "suporte@example.com",
            "seguidores",
        ]
        filtered = smart_filter(texts)
        assert "contato@empresa.com.br" in filtered
        assert "suporte@example.com" in filtered

    def test_urls_in_text(self):
        texts = [
            "https://instagram.com/user",
            "http://example.com/page",
        ]
        filtered = smart_filter(texts)
        assert "https://instagram.com/user" in filtered
        assert "http://example.com/page" in filtered


class TestEdgeCases:
    """Casos de borda do pipeline."""

    def test_special_characters(self):
        """Caracteres especiais em handles."""
        texts = ["@user.name_123", "@user-name"]
        handles = extract_handles(texts)
        assert "@user.name_123" in handles
        assert "@user-name" not in handles  # hífen não é permitido em handle

    def test_mixed_language_portuguese(self):
        """Português com acentos."""
        texts = ["@usuário", "Você mencionou @usuario", "ação"]
        handles = extract_handles(texts)
        assert "@usuário" in handles

    def test_large_batch_filter(self):
        """Batch grande — handles com 1 dígito são ruído (len ≤ 2)."""
        texts = [f"@{i}" for i in range(50)]
        result = smart_filter(texts)
        assert len(result) == 40  # @0-@9 filtrados por is_noise, @10-@49 passam

    def test_unicode_text(self):
        """Texto com unicode."""
        texts = ["@usuario", "coração", "✨"]
        result = smart_filter(texts)
        assert "@usuario" in result

    def test_empty_texts_ignored(self):
        """Textos vazios ignorados."""
        texts = ["", "  ", "\n", "@user"]
        result = smart_filter(texts)
        assert "@user" in result
        assert len(result) == 1

    def test_case_insensitive_dedup(self):
        """Dedup case insensitive."""
        texts = ["@User", "@user"]
        result = smart_filter(texts)
        assert len(result) == 1  # Normalização: lower

    def test_numeric_only_filtered(self):
        """Apenas números é ruído."""
        texts = ["12345", "42", "@user"]
        result = smart_filter(texts)
        assert "12345" not in result
        assert "@user" in result


class TestOCRResultPipeline:
    """Testes de integração com OCRResult."""

    def test_result_creation(self):
        result = OCRResult(
            file_path="test.jpg",
            raw_texts=["@user", "seguidores", "@user2"],
            filtered_texts=["@user", "@user2"],
            ocr_time=1.5,
            total_time=2.0,
        )
        assert result.success is True
        assert result.text == "@user\n@user2"
        assert "@user" in result.filtered_texts

    def test_result_with_confidence(self):
        result = OCRResult(
            file_path="test.jpg",
            raw_texts=["@user", "texto"],
            confidence_scores=[0.95, 0.80],
        )
        assert len(result.confidence_scores) == 2
        assert result.confidence_scores[0] == 0.95


class TestBatchResultPipeline:
    """Testes de integração com BatchResult."""

    def test_batch_with_mixed_results(self):
        batch = BatchResult(
            results=[
                OCRResult(file_path="a.jpg", filtered_texts=["@user1"]),
                OCRResult(file_path="b.jpg", error="fail"),
                OCRResult(file_path="c.jpg", filtered_texts=["@user3"]),
            ],
            total_images=3,
            successful=2,
            failed=1,
            total_time=5.0,
        )
        assert batch.success_rate == 2 / 3 * 100
        assert len(batch.results) == 3

    def test_batch_all_successful(self):
        batch = BatchResult(
            results=[OCRResult(file_path="a.jpg") for _ in range(5)],
            total_images=5,
            successful=5,
        )
        assert batch.success_rate == 100.0

    def test_batch_all_failed(self):
        batch = BatchResult(
            results=[OCRResult(file_path="a.jpg", error="e") for _ in range(3)],
            total_images=3,
            failed=3,
        )
        assert batch.success_rate == 0.0
