"""Testes para o filtro inteligente do Vision Text Engine."""

from vision_text_engine.filters.smart_filter import (
    _is_noise,
    _matches_exclude_pattern,
    default_filter_rules,
    extract_emails,
    extract_handles,
    extract_hashtags,
    extract_urls,
    smart_filter,
)


class TestSmartFilter:
    """Testes para smart_filter()."""

    def test_empty_input(self):
        assert smart_filter([]) == []

    def test_all_noise(self):
        texts = ["seguidores", "curtir", "comentar", "22:30"]
        assert smart_filter(texts) == []

    def test_mixed_input(self):
        texts = ["@user1", "@user2", "seguidores", "curtir"]
        result = smart_filter(texts)
        assert "@user1" in result
        assert "@user2" in result
        assert "seguidores" not in result
        assert "curtir" not in result

    def test_dedup(self):
        texts = ["@user1", "@user1", "@user2", "@user2"]
        result = smart_filter(texts)
        assert len(result) == 2

    def test_handles_rule(self):
        texts = ["@victorcortez", "@gigioficial", "mensagem"]
        result = smart_filter(texts)
        assert "@victorcortez" in result
        assert "@gigioficial" in result
        assert "mensagem" not in result

    def test_minimum_length(self):
        texts = ["@a", "@ab", "@abc", "ab"]
        result = smart_filter(texts)
        assert "@abc" in result
        assert "@a" not in result  # Too short for handle
        assert "@ab" in result  # handle min_length is 3? No, default min_length=3

    def test_max_length(self):
        long_text = "a" * 200
        texts = [long_text]
        result = smart_filter(texts)
        assert long_text not in result

    def test_exclude_keywords_case_insensitive(self):
        texts = ["SEGUIDORES", "Curtir", "@user"]
        result = smart_filter(texts)
        assert "@user" in result

    def test_exclude_time_patterns(self):
        texts = ["22:30", "22h30", "@user"]
        result = smart_filter(texts)
        assert "22:30" not in result
        assert "22h30" not in result
        assert "@user" in result

    def test_exclude_dates(self):
        texts = ["2026-05-05", "@user"]
        result = smart_filter(texts)
        assert "2026-05-05" not in result

    def test_exclude_time_relative(self):
        texts = ["ontem", "hoje", "amanhã", "@user"]
        result = smart_filter(texts)
        assert "ontem" not in result
        assert "@user" in result

    def test_email_extraction(self):
        texts = ["user@example.com", "test@test.com.br", "seguidores"]
        result = smart_filter(texts)
        assert "user@example.com" in result
        assert "test@test.com.br" in result

    def test_url_extraction(self):
        texts = ["https://instagram.com/user", "http://example.com"]
        result = smart_filter(texts)
        assert "https://instagram.com/user" in result
        assert "http://example.com" in result

    def test_platform_instagram(self):
        texts = [
            "@user1",
            "@user2",
            "Voce mencionou @user1 no seu story",
            "seguidores 1.234",
            "ver perfil",
        ]
        result = smart_filter(texts)
        assert "@user1" in result
        assert "@user2" in result
        assert "ver perfil" not in result

    def test_no_short_responses(self):
        texts = ["sim", "não", "@user"]
        result = smart_filter(texts)
        assert "sim" not in result
        assert "@user" in result

    def test_whitespace_stripping(self):
        texts = ["  @user  ", "  ", "\t"]
        result = smart_filter(texts)
        assert "@user" in result

    def test_large_batch(self):
        texts = [f"@{i}" for i in range(100)]
        result = smart_filter(texts)
        assert len(result) == 90  # @0-@9 filtered (len <= 2)


class TestExtractHandles:
    """Testes para extract_handles()."""

    def test_basic_handles(self):
        texts = ["@victorcortez", "@gigioficial", "texto normal"]
        assert extract_handles(texts) == ["@gigioficial", "@victorcortez"]

    def test_handles_with_dots(self):
        texts = ["@user.name", "@user_name"]
        result = extract_handles(texts)
        assert "@user.name" in result
        assert "@user_name" in result

    def test_no_handles(self):
        assert extract_handles(["texto normal"]) == []

    def test_multiple_handles_in_one_text(self):
        texts = ["Mencionou @user1 e @user2 no story"]
        result = extract_handles(texts)
        assert "@user1" in result
        assert "@user2" in result

    def test_handle_dedup(self):
        texts = ["@user", "@user", "@user"]
        assert len(extract_handles(texts)) == 1

    def test_short_handles_excluded(self):
        texts = ["@a"]
        assert extract_handles(texts) == []

    def test_handles_with_numbers(self):
        texts = ["@user123", "@2mafia"]
        result = extract_handles(texts)
        assert "@user123" in result

    def test_handles_sorted(self):
        texts = ["@zebra", "@alpha"]
        assert extract_handles(texts) == ["@alpha", "@zebra"]


class TestExtractHashtags:
    """Testes para extract_hashtags()."""

    def test_basic_hashtags(self):
        texts = ["#tech", "#python"]
        assert extract_hashtags(texts) == ["#python", "#tech"]

    def test_no_hashtags(self):
        assert extract_hashtags(["texto normal"]) == []

    def test_mixed_content(self):
        texts = ["#python é melhor que #javascript"]
        result = extract_hashtags(texts)
        assert "#python" in result
        assert "#javascript" in result

    def test_short_tags_excluded(self):
        texts = ["#a"]
        assert extract_hashtags(texts) == []

    def test_dedup(self):
        texts = ["#python", "#python"]
        assert len(extract_hashtags(texts)) == 1


class TestExtractEmails:
    """Testes para extract_emails()."""

    def test_basic_email(self):
        texts = ["user@example.com"]
        assert extract_emails(texts) == ["user@example.com"]

    def test_no_emails(self):
        assert extract_emails(["texto"]) == []

    def test_multiple_emails(self):
        texts = ["a@b.com e c@d.com"]
        result = extract_emails(texts)
        assert len(result) == 2

    def test_invalid_emails_not_matched(self):
        texts = ["notanemail@"]
        assert extract_emails(texts) == []


class TestExtractUrls:
    """Testes para extract_urls()."""

    def test_basic_url(self):
        texts = ["https://example.com"]
        assert extract_urls(texts) == ["https://example.com"]

    def test_no_urls(self):
        assert extract_urls(["texto"]) == []

    def test_multiple_urls(self):
        texts = ["https://a.com e https://b.com"]
        result = extract_urls(texts)
        assert len(result) == 2

    def test_http_url(self):
        texts = ["http://example.com"]
        assert "http://example.com" in extract_urls(texts)


class TestIsNoise:
    """Testes para _is_noise()."""

    def test_phone_number(self):
        assert _is_noise("+5511999999999") is True

    def test_long_numbers(self):
        assert _is_noise("123456789") is True

    def test_exclude_keyword(self):
        assert _is_noise("seguidores") is True
        assert _is_noise("curtir") is True

    def test_short_text(self):
        assert _is_noise("ab") is True

    def test_valid_text(self):
        assert _is_noise("@user") is False
        assert _is_noise("nome válido") is False


class TestMatchesExcludePattern:
    """Testes para _matches_exclude_pattern()."""

    def test_time_format(self):
        assert _matches_exclude_pattern("22:30") is True
        assert _matches_exclude_pattern("22h30") is True

    def test_list_item(self):
        assert _matches_exclude_pattern("- item") is True
        assert _matches_exclude_pattern("— item") is True

    def test_ordinal(self):
        assert _matches_exclude_pattern("1º") is True

    def test_date(self):
        assert _matches_exclude_pattern("2026-05-05") is True

    def test_no_match(self):
        assert _matches_exclude_pattern("@user") is False
        assert _matches_exclude_pattern("nome válido") is False


class TestDefaultFilterRules:
    """Testes para default_filter_rules()."""

    def test_returns_list(self):
        rules = default_filter_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_all_have_names(self):
        rules = default_filter_rules()
        for rule in rules:
            assert rule.name

    def test_rules_have_exclude_keywords(self):
        rules = default_filter_rules()
        for rule in rules:
            assert rule.exclude_keywords


class TestMatchesRule:
    """Testes para _matches_rule — cobre linhas 191 e 203."""

    def test_matches_rule_min_length_edge(self):
        """_matches_rule retorna False quando len(text) < rule.min_length
        mas len(text) > 2 (não pego pelo _is_noise). Linha 191."""
        from vision_text_engine.core.models import FilterRule
        from vision_text_engine.filters.smart_filter import _matches_rule

        # Texto "abc" (len=3) com min_length=10 → deve falhar no length check
        rule = FilterRule(name="test", min_length=10, max_length=100)
        result = _matches_rule("abc", rule)
        assert result is False

    def test_matches_rule_require_handle_format(self):
        """_matches_rule com require_handle_format=True valida formato @user.
        Linha 203."""
        from vision_text_engine.core.models import FilterRule
        from vision_text_engine.filters.smart_filter import _matches_rule

        rule = FilterRule(
            name="test",
            min_length=3,
            max_length=50,
            require_handle_format=True,
        )

        # Formato inválido (tem espaço)
        assert _matches_rule("@user name", rule) is False
        # Formato inválido (caractere especial)
        assert _matches_rule("@user!name", rule) is False
        # Formato válido
        assert _matches_rule("@username", rule) is True
        # Formato válido sem @ (o regex aceita @? opcional)
        assert _matches_rule("username", rule) is True
        # Muito curto (len < min_length)
        assert _matches_rule("@a", rule) is False
