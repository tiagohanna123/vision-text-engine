"""
Filtros inteligentes para texto extraído de imagens.

Estratégias de filtragem específicas por plataforma:
- Instagram: @handles, seguidores, menções
- Twitter/X: @handles, hashtags
- WhatsApp: números, nomes de contato
- Genérico: URLs, emails, números de telefone
"""

import re

from ..core.models import FilterRule

# Palavras de exclusão comuns (UI text, noise)
EXCLUDE_KEYWORDS = {
    "seguir", "seguindo", "seguidores", "publicações", "posts",
    "perfil", "editar", "compartilhar", "denunciar", "silenciar",
    "mensagem", "pesquisar", "configurações", "voltar", "fechar",
    "cancelar", "salvar", "excluir", "bloquear", "ver perfil",
    "mencionou", "marcou", "curtir", "comentar", "enviar",
    "instagram", "twitter", "facebook", "whatsapp", "telegram",
    "settings", "profile", "edit", "share", "report", "mute",
    "message", "search", "back", "close", "cancel", "save",
    "delete", "block", "view profile", "mention", "like",
    "comment", "send", "follow", "following", "followers",
    "publications",
}

# Padrões de exclusão
EXCLUDE_PATTERNS = [
    r"^\d{1,2}:\d{2}",           # Horários (22:30)
    r"^\d{1,2}h\d{2}",           # Horários (22h30)
    r"^[A-Za-z]{1,2}\.$",        # Iniciais (J.)
    r"^[-–—]\s",  # noqa: RUF001 — en/em dash intentional in regex
    r"^\d+[°º]",                 # Graus/números ordinais
    r"^(sim|não|talvez|ok)$",    # Respostas curtas
    r"^(yes|no|maybe|ok)$",      # Respostas curtas EN
    r"^\d{4}-\d{2}-\d{2}",       # Datas
    r"^(há|atrás|ontem|hoje|amanhã)$",  # Tempo relativo
]


def default_filter_rules() -> list[FilterRule]:
    """Regras de filtragem padrão."""
    return [
        FilterRule(
            name="handles",
            min_length=3,
            max_length=50,
            require_at_symbol=True,
            require_handle_format=True,
            exclude_keywords=list(EXCLUDE_KEYWORDS),
        ),
        FilterRule(
            name="hashtags",
            min_length=3,
            max_length=100,
            require_prefix="#",
            exclude_keywords=list(EXCLUDE_KEYWORDS),
        ),
        FilterRule(
            name="emails",
            min_length=6,
            max_length=254,
            require_at_symbol=True,
            exclude_keywords=list(EXCLUDE_KEYWORDS),
        ),
        FilterRule(
            name="urls",
            min_length=10,
            max_length=2000,
            require_prefix="http",
            exclude_keywords=list(EXCLUDE_KEYWORDS),
        ),
    ]


def smart_filter(
    texts: list[str],
    rules: list[FilterRule] | None = None,
    platform: str | None = None,
) -> list[str]:
    """
    Filtra texto extraído usando regras inteligentes.

    Args:
        texts: Lista de textos extraídos.
        rules: Regras de filtragem (usa padrão se None).
        platform: Plataforma específica ('instagram', 'twitter', 'whatsapp').

    Returns:
        Lista de textos filtrados, ordenados por relevância.

    """
    rules = rules or default_filter_rules()
    filtered = []
    seen = set()

    for text in texts:
        text = text.strip()
        if not text:
            continue

        # Dedup
        lower = text.lower()
        if lower in seen:
            continue
        seen.add(lower)

        # Verificar exclusão por padrão
        if _matches_exclude_pattern(text):
            continue

        # Ruído SEMPRE é removido — mesmo se regra bater
        if _is_noise(text):
            continue

        # Verificar cada regra
        matched = False
        for rule in rules:
            if _matches_rule(text, rule):
                filtered.append(text)
                matched = True
                break

        # Se não match em nenhuma regra, mas passou noise, incluir
        if not matched:
            filtered.append(text)

    return filtered


def _matches_exclude_pattern(text: str) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if re.match(pattern, text):
            return True
    return False  # noqa: SIM110 — explicit loop clearer for regex patterns


def _matches_rule(text: str, rule: FilterRule) -> bool:
    """Verifica se texto corresponde a uma regra."""
    text_lower = text.lower()

    # Comprimento
    if len(text) < rule.min_length or len(text) > rule.max_length:
        return False

    # @ required
    if rule.require_at_symbol and "@" not in text:
        return False

    # Handle format (@user)
    if rule.require_handle_format and not re.match(r"^@?[\w.]{2,30}$", text):
        return False

    # Exclude keywords
    for kw in rule.exclude_keywords:
        if kw.lower() in text_lower:
            return False

    # Require prefix
    if rule.require_prefix is not None and not text_lower.startswith(rule.require_prefix):
        return False

    # Exclude patterns
    for pat in rule.exclude_patterns:
        if re.search(pat, text_lower):
            return False
    return True  # noqa: SIM110 — explicit loop clearer for regex patterns
    return True


def _is_noise(text: str) -> bool:
    """Verifica se texto é ruído (UI elements, etc)."""
    # Muito longo (provavelmente lixo OCR)
    if len(text) > 100:
        return True

    # Números de telefone completos
    if re.match(r"^\+?\d{10,15}$", text):
        return True

    # Apenas números
    if re.match(r"^\d+$", text) and len(text) > 4:
        return True

    # Palavras de exclusão
    if text.lower() in EXCLUDE_KEYWORDS:
        return True

    # Muito curto
    if len(text) <= 2:
        return True

    return False


def extract_handles(texts: list[str]) -> list[str]:
    """Extrai apenas @handles de uma lista de textos."""
    handles = set()
    for text in texts:
        found = re.findall(r"@([\w.]{1,30})", text)
        for handle in found:
            if len(handle) >= 2:
                handles.add(f"@{handle}")
    return sorted(handles)


def extract_hashtags(texts: list[str]) -> list[str]:
    """Extrai apenas hashtags de uma lista de textos."""
    tags = set()
    for text in texts:
        found = re.findall(r"#(\w+)", text)
        for tag in found:
            if len(tag) >= 2:
                tags.add(f"#{tag}")
    return sorted(tags)


def extract_emails(texts: list[str]) -> list[str]:
    """Extrai emails de uma lista de textos."""
    emails = set()
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    for text in texts:
        found = re.findall(pattern, text)
        emails.update(found)
    return sorted(emails)


def extract_urls(texts: list[str]) -> list[str]:
    """Extrai URLs de uma lista de textos."""
    urls = set()
    pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[-\w/?#&%=~.;,:@]"
    for text in texts:
        found = re.findall(pattern, text)
        urls.update(found)
    return sorted(urls)
