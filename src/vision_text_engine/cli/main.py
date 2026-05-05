"""
"""CLI do Vision Text Engine — uso interativo e scripting.

Comandos:
    vte extract <imagem>       Extrai texto de uma imagem
    vte batch <dir|glob>       Processa múltiplas imagens
    vte info                   Info do engine e backends
    vte serve                  Modo servidor HTTP (futuro)
"""

from __future__ import annotations

import glob
import json
import os
import sys

try:
    import click
except ImportError:
    click = None  # type: ignore[assignment]


def create_cli() -> "click.Group | None":
    """Cria CLI com Click. Retorna None se click não estiver instalado."""
    if click is None:
        return None

    @click.group()
    @click.option("--lang", default="pt,en", help="Idiomas separados por vírgula")
    @click.option("--gpu", is_flag=True, help="Usar GPU")
    @click.option("--no-preprocess", is_flag=True, help="Desabilitar pré-processamento")
    @click.pass_context
    def cli(ctx, lang, gpu, no_preprocess):
        """Vision Text Engine — extração inteligente de texto de imagens."""
        ctx.ensure_object(dict)
        ctx.obj["lang"] = [lang_code.strip() for lang_code in lang.split(",")]
        ctx.obj["gpu"] = gpu
        ctx.obj["preprocess"] = not no_preprocess

    @cli.command()
    @click.argument("image_path", type=click.Path(exists=True))
    @click.option("--json", "json_output", is_flag=True, help="Saída em JSON")
    @click.option("--handles", is_flag=True, help="Extrair apenas @handles")
    @click.option("--raw", is_flag=True, help="Mostrar texto bruto sem filtro")
    @click.pass_context
    def extract(ctx, image_path, json_output, handles, raw):
        """Extrai texto de uma imagem."""
        from ..api import extract_text
        from ..filters.smart_filter import extract_handles as get_handles

        result = extract_text(
            image_path=image_path,
            lang=ctx.obj["lang"],
            gpu=ctx.obj["gpu"],
            preprocess=ctx.obj["preprocess"],
        )

        if json_output:
            print(
                json.dumps(
                    {
                        "file": result.file_path,
                        "success": result.success,
                        "text": result.text,
                        "raw_texts": result.raw_texts,
                        "filtered_texts": result.filtered_texts,
                        "error": result.error,
                        "ocr_time_sec": round(result.ocr_time, 3),
                        "total_time_sec": round(result.total_time, 3),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif raw:
            print(result.raw_text)
        elif handles:
            handles_list = get_handles(result.raw_texts)
            for h in handles_list:
                print(h)
        else:
            if result.error:
                print(f"ERRO: {result.error}", file=sys.stderr)
                sys.exit(1)
            print(result.text)
            print(f"\n⏱  {result.total_time:.1f}s | {len(result.filtered_texts)} textos extraídos")

    @cli.command()
    @click.argument("pattern", type=str)
    @click.option("--json", "json_output", is_flag=True, help="Saída em JSON")
    @click.option("--recursive", is_flag=True, help="Buscar recursivamente")
    @click.option("--ext", default="jpg,jpeg,png", help="Extensões (separadas por vírgula)")
    @click.pass_context
    def batch(ctx, pattern, json_output, recursive, ext):
        """Processa múltiplas imagens (glob ou diretório)."""
        from ..api import extract_text_batch

        # Resolver arquivos
        if os.path.isdir(pattern):
            exts = [e.strip().lower() for e in ext.split(",")]
            pattern = os.path.join(pattern, "**" if recursive else "*")
            files = []
            for e in exts:
                files.extend(glob.glob(f"{pattern}.{e}", recursive=recursive))
        else:
            files = sorted(glob.glob(pattern, recursive=recursive))

        if not files:
            print(f"Nenhuma imagem encontrada: {pattern}", file=sys.stderr)
            sys.exit(1)

        batch_result = extract_text_batch(
            image_paths=files,
            lang=ctx.obj["lang"],
            gpu=ctx.obj["gpu"],
            preprocess=ctx.obj["preprocess"],
        )

        if json_output:
            print(
                json.dumps(
                    {
                        "total": batch_result.total_images,
                        "successful": batch_result.successful,
                        "failed": batch_result.failed,
                        "success_rate": round(batch_result.success_rate, 1),
                        "total_time_sec": round(batch_result.total_time, 3),
                        "results": [
                            {
                                "file": r.file_path,
                                "success": r.success,
                                "text": r.text,
                                "error": r.error,
                            }
                            for r in batch_result.results
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"Processando {len(files)} imagens...")
            print(
                f"\n✅ {batch_result.successful}/{batch_result.total_images} "
                f"({batch_result.success_rate:.0f}%) | "
                f"⏱  {batch_result.total_time:.1f}s"
            )
            for r in batch_result.results[:5]:
                status = "✅" if r.success else "❌"
                preview = r.text[:80].replace("\n", " | ") if r.text else r.error or "vazio"
                print(f"  {status} {os.path.basename(r.file_path)}: {preview}")

    @cli.command()
    @click.pass_context
    def info(ctx):
        """Informações do engine e backends disponíveis."""
        from ..core.engine import VisionEngine

        engine = VisionEngine(lang=ctx.obj["lang"], gpu=ctx.obj["gpu"])
        backends = engine.available_backends()
        print("Vision Text Engine v0.1.0")
        print(f"Idiomas: {', '.join(ctx.obj['lang'])}")
        print(f"GPU: {'sim' if ctx.obj['gpu'] else 'não'}")
        print(f"Pré-processamento: {'sim' if ctx.obj['preprocess'] else 'não'}")
        print("Backends:")
        for name, available in backends.items():
            print(f"  {'✅' if available else '❌'} {name}")

    return cli


def main() -> None:
    """Entry point para a CLI."""
    cli = create_cli()
    if cli is None:
        print("Erro: click não está instalado. pip install click", file=sys.stderr)
        sys.exit(1)
    cli()
