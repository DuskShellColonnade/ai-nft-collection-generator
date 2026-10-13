"""Render images for a planned collection. Pluggable backend."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from ai_nft_gen.lib.config_loader import AppConfig
from ai_nft_gen.lib.logging import get_logger
from ai_nft_gen.models.token import TokenRecord

log = get_logger(__name__)


class RenderBackend(Protocol):
    def render(self, token: TokenRecord, prompt: str, seed: int) -> Path: ...


def _prompt_for(token: TokenRecord, base: str) -> str:
    bits = ", ".join(f"{k}={v}" for k, v in token.traits.items())
    return f"{base}. traits: {bits}. consistent style, centered, square."


def _load_plan(cfg: AppConfig) -> list[TokenRecord]:
    plan_path = Path("collections") / cfg.collection.symbol.lower() / "plan.json"
    raw = json.loads(plan_path.read_text(encoding="utf-8"))
    return [TokenRecord.model_validate(i) for i in raw["items"]]


def _get_backend(cfg: AppConfig) -> RenderBackend:
    if cfg.render.backend == "diffusers":
        from ai_nft_gen.services.diffusers_backend import DiffusersBackend
        return DiffusersBackend(cfg.render)
    from ai_nft_gen.services.stub_backend import StubBackend
    return StubBackend(cfg.render)


def render_collection(cfg: AppConfig, limit: int | None = None) -> list[TokenRecord]:
    backend = _get_backend(cfg)
    out_dir = Path("outputs") / cfg.collection.symbol.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    items = _load_plan(cfg)
    if limit:
        items = items[:limit]
    base = cfg.collection.description
    done: list[TokenRecord] = []
    for tok in items:
        seed = cfg.render.seed_offset + tok.token_id
        path = backend.render(tok, _prompt_for(tok, base), seed)
        tok.image_path = path
        done.append(tok)
        if tok.token_id % 25 == 0:
            log.info("rendered %d/%d", tok.token_id, len(items))
    (out_dir / "renders.json").write_text(
        json.dumps([t.model_dump(mode="json") for t in done], indent=2), encoding="utf-8"
    )
    return done