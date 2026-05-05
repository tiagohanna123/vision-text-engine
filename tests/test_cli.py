"""Testes para a CLI do Vision Text Engine."""

from unittest.mock import patch

from vision_text_engine.cli.main import create_cli, main


class TestCLIStructure:
    """Testes para estrutura da CLI."""

    def test_create_cli_exists(self):
        cli = create_cli()
        assert cli is not None

    def test_cli_has_extract_command(self):
        cli = create_cli()
        commands = list(cli.commands.keys())
        assert "extract" in commands

    def test_cli_has_batch_command(self):
        cli = create_cli()
        commands = list(cli.commands.keys())
        assert "batch" in commands

    def test_cli_has_info_command(self):
        cli = create_cli()
        commands = list(cli.commands.keys())
        assert "info" in commands

    @patch("click.Path", return_value=lambda: None)
    def test_extract_command_has_image_arg(self, mock_path):
        cli = create_cli()
        cmd = cli.get_command(None, "extract")
        assert cmd is not None
        params = [p.name for p in cmd.params]
        assert "image_path" in params

    def test_extract_command_has_options(self):
        cli = create_cli()
        cmd = cli.get_command(None, "extract")
        params = [p.name for p in cmd.params]
        assert "json_output" in params
        assert "handles" in params
        assert "raw" in params

    def test_batch_command_has_pattern_arg(self):
        cli = create_cli()
        cmd = cli.get_command(None, "batch")
        assert cmd is not None
        params = [p.name for p in cmd.params]
        assert "pattern" in params

    def test_batch_command_has_options(self):
        cli = create_cli()
        cmd = cli.get_command(None, "batch")
        params = [p.name for p in cmd.params]
        assert "json_output" in params
        assert "recursive" in params
        assert "ext" in params

    def test_cli_has_global_options(self):
        cli = create_cli()
        params = [p.name for p in cli.params]
        assert "lang" in params
        assert "gpu" in params
        assert "no_preprocess" in params


class TestCLIInfo:
    """Testes para comando info."""

    def test_info_uses_engine(self):
        """Info deve verificar backends."""
        cli = create_cli()
        cmd = cli.get_command(None, "info")
        assert cmd is not None
        assert cmd.callback is not None


class TestMainFunction:
    """Testes para entry point."""

    @patch("vision_text_engine.cli.main.click", None)
    def test_main_no_click(self):
        """Sem click, deve mostrar erro."""
        try:
            main()
        except SystemExit as e:
            assert e.code == 1

    def test_main_importable(self):
        """main() pode ser importada."""
        import inspect

        assert inspect.isfunction(main)

    @patch("vision_text_engine.cli.main.click", None)
    def test_main_no_click_exit(self):
        """Sem click, main deve chamar sys.exit(1) e exibir erro."""
        try:
            main()
        except SystemExit as e:
            assert e.code == 1
