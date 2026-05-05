"""
Vision Text Engine — Extração inteligente de texto de imagens.

Uso:
    python -m vision_text_engine extract foto.jpg
    python -m vision_text_engine batch ./imagens/ --recursive
    python -m vision_text_engine info
"""

from .cli.main import main

if __name__ == "__main__":
    main()
