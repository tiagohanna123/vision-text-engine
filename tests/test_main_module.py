"""Testes para __main__.py — execução via python -m vision_text_engine."""

import runpy
from unittest.mock import patch


class TestMainModule:
    """Testa a execução do módulo __main__."""

    @patch("vision_text_engine.cli.main.main")
    def test_main_module_calls_main(self, mock_main):
        """Executar o módulo com run_name='__main__' chama main()."""
        runpy.run_module(
            "vision_text_engine.__main__",
            run_name="__main__",
            alter_sys=True,
        )
        mock_main.assert_called_once()
