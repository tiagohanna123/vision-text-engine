"""Testes de integração para CLI usando CliRunner.

Cobre linhas 18-19, 34-37, 47-85, 95-152, 158-168, 179 do cli/main.py.

NOTA: As funções extract_text, extract_text_batch e VisionEngine são
importadas DENTRO dos corpos das funções (lazy imports), então os patches
devem mirar nos módulos de ORIGEM (api, core.engine), não no cli.main.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from vision_text_engine.cli.main import create_cli, main


class TestCLIIntegration:
    """Testes com CliRunner para comandos reais."""

    def setup_method(self):
        self.runner = CliRunner()
        self.cli = create_cli()

    # ── info command (linhas 158-168) ─────────────────────────────────────

    @patch("vision_text_engine.core.engine.VisionEngine")
    def test_info_command(self, MockEngine):
        """vte info mostra informações do engine."""
        mock_engine = MagicMock()
        mock_engine.available_backends.return_value = {
            "easyocr": True,
            "opencv": False,
        }
        MockEngine.return_value = mock_engine

        result = self.runner.invoke(self.cli, ["info"])
        assert result.exit_code == 0
        assert "Vision Text Engine" in result.output
        assert "Idiomas:" in result.output
        assert "GPU:" in result.output
        assert "Pré-processamento:" in result.output
        assert "✅ easyocr" in result.output
        assert "❌ opencv" in result.output

    # ── extract command (linhas 47-85) ────────────────────────────────────

    @patch("vision_text_engine.api.extract_text")
    def test_extract_basic(self, mock_extract, sample_image_path):
        """vte extract <path> mostra texto extraído."""
        mock_result = MagicMock()
        mock_result.file_path = sample_image_path
        mock_result.success = True
        mock_result.text = "hello world\nline 2"
        mock_result.raw_text = "hello world\nline 2"
        mock_result.raw_texts = ["hello world", "line 2"]
        mock_result.filtered_texts = ["hello world", "line 2"]
        mock_result.error = None
        mock_result.ocr_time = 0.3
        mock_result.total_time = 0.5
        mock_extract.return_value = mock_result

        result = self.runner.invoke(self.cli, ["extract", sample_image_path])
        assert result.exit_code == 0
        assert "hello world" in result.output

    @patch("vision_text_engine.api.extract_text")
    def test_extract_json(self, mock_extract, sample_image_path):
        """vte extract --json <path> retorna JSON."""
        mock_result = MagicMock()
        mock_result.file_path = sample_image_path
        mock_result.success = True
        mock_result.text = "json text"
        mock_result.raw_text = "json text"
        mock_result.raw_texts = ["json text"]
        mock_result.filtered_texts = ["json text"]
        mock_result.error = None
        mock_result.ocr_time = 0.2
        mock_result.total_time = 0.4
        mock_extract.return_value = mock_result

        result = self.runner.invoke(self.cli, ["extract", sample_image_path, "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["text"] == "json text"

    @patch("vision_text_engine.api.extract_text")
    @patch("vision_text_engine.filters.smart_filter.extract_handles")
    def test_extract_handles(self, mock_get_handles, mock_extract, sample_image_path):
        """vte extract --handles <path> extrai apenas handles."""
        mock_result = MagicMock()
        mock_result.raw_texts = ["@user1", "@user2", "texto normal"]
        mock_result.success = True
        mock_result.text = ""
        mock_extract.return_value = mock_result
        mock_get_handles.return_value = ["@user1", "@user2"]

        result = self.runner.invoke(self.cli, ["extract", sample_image_path, "--handles"])
        assert result.exit_code == 0
        assert "@user1" in result.output
        assert "@user2" in result.output

    @patch("vision_text_engine.api.extract_text")
    def test_extract_raw(self, mock_extract, sample_image_path):
        """vte extract --raw <path> mostra texto bruto."""
        mock_result = MagicMock()
        mock_result.raw_text = "raw\nunfiltered\ntext"
        mock_result.success = True
        mock_extract.return_value = mock_result

        result = self.runner.invoke(self.cli, ["extract", sample_image_path, "--raw"])
        assert result.exit_code == 0
        assert "raw" in result.output

    @patch("vision_text_engine.api.extract_text")
    def test_extract_error(self, mock_extract, sample_image_path):
        """vte extract <path> mostra erro quando falha."""
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Arquivo não encontrado"
        mock_result.text = ""
        mock_extract.return_value = mock_result

        result = self.runner.invoke(self.cli, ["extract", sample_image_path])
        assert result.exit_code == 1
        assert "ERRO" in result.output
        assert "Arquivo não encontrado" in result.output

    # ── batch command (linhas 95-152) ─────────────────────────────────────

    @patch("vision_text_engine.api.extract_text_batch")
    def test_batch_basic(self, mock_batch, tmp_path):
        """vte batch <glob> processa múltiplas imagens."""
        img1 = tmp_path / "img1.png"
        img1.write_text("fake")
        img2 = tmp_path / "img2.png"
        img2.write_text("fake")

        mock_batch_result = MagicMock()
        mock_batch_result.total_images = 2
        mock_batch_result.successful = 2
        mock_batch_result.failed = 0
        mock_batch_result.success_rate = 100.0
        mock_batch_result.total_time = 1.0

        r1 = MagicMock()
        r1.success = True
        r1.text = "text from img1"
        r1.file_path = str(img1)
        r1.error = None
        r2 = MagicMock()
        r2.success = True
        r2.text = "text from img2"
        r2.file_path = str(img2)
        r2.error = None
        mock_batch_result.results = [r1, r2]
        mock_batch.return_value = mock_batch_result

        result = self.runner.invoke(self.cli, ["batch", str(tmp_path / "*.png")])
        assert result.exit_code == 0
        assert "2" in result.output or "100" in result.output

    @patch("vision_text_engine.api.extract_text_batch")
    def test_batch_json(self, mock_batch, tmp_path):
        """vte batch --json <glob> retorna JSON."""
        img1 = tmp_path / "img1.png"
        img1.write_text("fake")

        mock_batch_result = MagicMock()
        mock_batch_result.total_images = 1
        mock_batch_result.successful = 1
        mock_batch_result.failed = 0
        mock_batch_result.success_rate = 100.0
        mock_batch_result.total_time = 0.5

        r1 = MagicMock()
        r1.success = True
        r1.text = "json output"
        r1.file_path = str(img1)
        r1.error = None
        mock_batch_result.results = [r1]
        mock_batch.return_value = mock_batch_result

        result = self.runner.invoke(self.cli, ["batch", str(tmp_path / "*.png"), "--json"])
        assert result.exit_code == 0
        # JSON output appears after the "Processando" header line
        # Find first '{' and parse from there (JSON is pretty-printed multi-line)
        json_start = result.output.index("{")
        data = json.loads(result.output[json_start:])
        assert data["total"] == 1
        assert data["successful"] == 1

    @patch("vision_text_engine.api.extract_text_batch")
    def test_batch_directory(self, mock_batch, tmp_path):
        """vte batch <dir> com diretório encontra arquivos."""
        imgdir = tmp_path / "images"
        imgdir.mkdir()
        (imgdir / "foto1.jpg").write_text("fake")
        (imgdir / "foto2.jpeg").write_text("fake")

        mock_batch_result = MagicMock()
        mock_batch_result.total_images = 2
        mock_batch_result.successful = 2
        mock_batch_result.failed = 0
        mock_batch_result.success_rate = 100.0
        mock_batch_result.total_time = 0.8
        mock_batch_result.results = []
        mock_batch.return_value = mock_batch_result

        result = self.runner.invoke(self.cli, ["batch", str(imgdir)])
        assert result.exit_code == 0
        assert "2" in result.output

    @patch("vision_text_engine.api.extract_text_batch")
    def test_batch_no_files(self, mock_batch):
        """vte batch com padrão sem matches exibe erro."""
        mock_batch.return_value = MagicMock()
        result = self.runner.invoke(self.cli, ["batch", "/nonexistent/*.xyz"])
        assert result.exit_code == 1
        assert "Nenhuma imagem encontrada" in result.output

    # ── Global options (linhas 34-37) ─────────────────────────────────────

    @patch("vision_text_engine.core.engine.VisionEngine")
    def test_global_options_lang(self, MockEngine):
        """--lang é passado como lista para o engine."""
        mock_engine = MagicMock()
        mock_engine.available_backends.return_value = {"easyocr": True}
        MockEngine.return_value = mock_engine

        # --lang é opção GLOBAL, deve vir ANTES do subcomando
        result = self.runner.invoke(self.cli, ["--lang", "en,fr", "info"])
        assert result.exit_code == 0
        assert MockEngine.called
        call_kwargs = MockEngine.call_args[1]
        assert call_kwargs["lang"] == ["en", "fr"]

    @patch("vision_text_engine.core.engine.VisionEngine")
    def test_global_options_gpu(self, MockEngine):
        """--gpu flag é repassada."""
        mock_engine = MagicMock()
        mock_engine.available_backends.return_value = {"easyocr": True}
        MockEngine.return_value = mock_engine

        result = self.runner.invoke(self.cli, ["--gpu", "info"])
        assert result.exit_code == 0
        assert MockEngine.called
        assert MockEngine.call_args[1]["gpu"] is True

    @patch("vision_text_engine.core.engine.VisionEngine")
    def test_global_options_no_preprocess(self, MockEngine):
        """--no-preprocess desabilita preprocessamento."""
        mock_engine = MagicMock()
        mock_engine.available_backends.return_value = {"easyocr": True}
        MockEngine.return_value = mock_engine

        result = self.runner.invoke(self.cli, ["--no-preprocess", "info"])
        assert result.exit_code == 0
        assert "Pré-processamento: não" in result.output

    # ── No-click scenario (linhas 18-19, 179) ─────────────────────────────

    def test_main_no_click_scenario(self):
        """main() sem click instalado exibe erro e sai com código 1."""
        with patch("vision_text_engine.cli.main.click", None):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
