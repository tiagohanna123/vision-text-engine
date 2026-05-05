.PHONY: install install-dev test lint typecheck build clean

# ─── Instalação ────────────────────────────────────────────────────────────────

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[all]"

# ─── Qualidade de código ──────────────────────────────────────────────────────

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

lint-fix:
	ruff check --fix src/ tests/
	ruff format src/ tests/

typecheck:
	mypy src/ --ignore-missing-imports 2>&1 | tail -20

# ─── Testes ────────────────────────────────────────────────────────────────────

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ --cov=src/vision_text_engine --cov-report=term-missing --cov-report=html

test-fast:
	python -m pytest tests/ -x --tb=short -q

coverage:
	python -m pytest tests/ --cov=src/vision_text_engine --cov-report=term --cov-fail-under=70

# ─── Build ──────────────────────────────────────────────────────────────────────

build:
	python -m build

# ─── Limpeza ───────────────────────────────────────────────────────────────────

clean:
	rm -rf dist/ build/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ coverage/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# ─── Utilitários ──────────────────────────────────────────────────────────────

info:
	python -c "from vision_text_engine import VisionEngine, __version__; print(f'v{__version__}'); print(VisionEngine().available_backends())"
