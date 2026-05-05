"""Testes para lazy imports via __getattr__ no __init__.py do pacote."""

import pytest


class TestPackageGetattr:
    """Testa __getattr__ para lazy imports no pacote vision_text_engine."""

    def test_getattr_vision_engine(self):
        """Acessar VisionEngine via __getattr__."""
        import vision_text_engine

        engine_cls = vision_text_engine.__getattr__("VisionEngine")
        from vision_text_engine.core.engine import VisionEngine as Real

        assert engine_cls is Real

    def test_getattr_extract_text(self):
        """Acessar extract_text via __getattr__."""
        import vision_text_engine

        fn = vision_text_engine.__getattr__("extract_text")
        from vision_text_engine.api import extract_text as real

        assert fn is real

    def test_getattr_extract_text_batch(self):
        """Acessar extract_text_batch via __getattr__."""
        import vision_text_engine

        fn = vision_text_engine.__getattr__("extract_text_batch")
        from vision_text_engine.api import extract_text_batch as real

        assert fn is real

    def test_getattr_unknown_raises(self):
        """Acessar atributo inexistente levanta AttributeError."""
        import vision_text_engine

        with pytest.raises(AttributeError, match="has no attribute"):
            vision_text_engine.__getattr__("unknown_attr")
