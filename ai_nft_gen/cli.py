"""Bootstrap entrypoint. Typer app wired to feature modules."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ai_nft_gen.features.collection_planner import plan_collection
from ai_nft_gen.features.render_pipeline import render_collection
from ai_nft_gen.features.metadata_builder import build_metadata
from ai_nft_gen.features.rarity_engine import score_collection
from ai_nft_gen.lib.config_loader import load_config
from ai_nft_gen.lib.logging import get_logger

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()
log = get_logger(__name__)


@app.command()
def plan(config: Path = typer.Option(Path("config/default.yaml"), "--config", "-c")) -> None:
    """Plan a collection: resolve traits, dedupe, write plan.json."""
    cfg = load_config(config)
    plan_obj = plan_collection(cfg)
    console.print(f"[green]planned[/green] {len(plan_obj.items)} tokens -> {plan_obj.out_path}")


@app.command()
def render(
    config: Path = typer.Option(Path("config/default.yaml"), "--config", "-c"),
    limit: int = typer.Option(0, help="0 = all"),
) -> None:
    """Render images for a planned collection."""
    cfg = load_config(config)
    render_collection(cfg, limit=limit or None)


@app.command()
def rarity(config: Path = typer.Option(Path("config/default.yaml"), "--config", "-c")) -> None:
    """Score rarity across a rendered collection."""
    cfg = load_config(config)
    report = score_collection(cfg)
    console.print(f"[green]scored[/green] {len(report.entries)} tokens")


@app.command()
def metadata(config: Path = typer.Option(Path("config/default.yaml"), "--config", "-c")) -> None:
    """Assemble ERC-721 metadata from renders + rarity."""
    cfg = load_config(config)
    build_metadata(cfg)


if __name__ == "__main__":
    app()