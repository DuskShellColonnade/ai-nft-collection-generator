"""Plan a collection: sample N unique tokens, write plan.json."""

from __future__ import annotations

import json
import random
from pathlib import Path

import yaml

from ai_nft_gen.features.trait_sampler import sample_token
from ai_nft_gen.lib.config_loader import AppConfig
from ai_nft_gen.lib.logging import get_logger
from ai_nft_gen.models.collection import CollectionPlan
from ai_nft_gen.models.trait import Trait, TraitPool

log = get_logger(__name__)


def _load_pool(path: Path) -> TraitPool:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    layers: dict[str, list[Trait]] = {}
    for layer, entries in raw.items():
        layers[layer] = [Trait(layer=layer, name=e["name"], weight=int(e["weight"])) for e in entries]
    return TraitPool(layers=layers)


def plan_collection(cfg: AppConfig, seed: int = 6767) -> CollectionPlan:
    pool = _load_pool(cfg.traits.source)
    rng = random.Random(seed)
    seen: set[str] = set()
    items = []
    attempts = 0
    while len(items) < cfg.collection.size and attempts < cfg.collection.size * 20:
        attempts += 1
        rec = sample_token(
            rng, pool, cfg.traits.layer_order, cfg.traits.incompatibilities, len(items)
        )
        if rec.fingerprint in seen:
            continue
        seen.add(rec.fingerprint)
        items.append(rec)
    if len(items) < cfg.collection.size:
        raise RuntimeError(
            f"only {len(items)}/{cfg.collection.size} unique tokens after {attempts} attempts; "
            "widen trait weights or reduce size"
        )
    out_path = Path("collections") / cfg.collection.symbol.lower() / "plan.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {"name": cfg.collection.name, "size": len(items), "seed": seed,
             "items": [i.model_dump(mode="json") for i in items]},
            indent=2,
        ),
        encoding="utf-8",
    )
    log.info("planned %d tokens -> %s", len(items), out_path)
    return CollectionPlan(
        name=cfg.collection.name, size=len(items), items=items, out_path=out_path, seed=seed
    )