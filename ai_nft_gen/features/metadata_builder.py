"""Assemble ERC-721 metadata JSON from renders + rarity."""

from __future__ import annotations

import json
from pathlib import Path

from ai_nft_gen.lib.config_loader import AppConfig
from ai_nft_gen.lib.logging import get_logger
from ai_nft_gen.models.collection import RarityReport
from ai_nft_gen.models.token import TokenRecord

log = get_logger(__name__)


def _load_renders(cfg: AppConfig) -> list[TokenRecord]:
    p = Path("outputs") / cfg.collection.symbol.lower() / "renders.json"
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [TokenRecord.model_validate(r) for r in raw]


def _load_rarity(cfg: AppConfig) -> dict[int, int]:
    p = Path("collections") / cfg.collection.symbol.lower() / "rarity.json"
    if not p.exists():
        return {}
    rep = RarityReport.model_validate_json(p.read_text(encoding="utf-8"))
    return {e.token_id: e.rank for e in rep.entries}


def build_metadata(cfg: AppConfig) -> list[Path]:
    tokens = _load_renders(cfg)
    ranks = _load_rarity(cfg)
    out_dir = Path("collections") / cfg.collection.symbol.lower() / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for tok in tokens:
        image_uri = (
            f"{cfg.metadata.image_base}{tok.image_path.name}"
            if tok.image_path
            else f"{cfg.metadata.image_base}{tok.token_id}.png"
        )
        doc = {
            "name": f"{cfg.collection.name} #{tok.token_id}",
            "description": cfg.collection.description,
            "image": image_uri,
            "external_url": cfg.metadata.external_url,
            "attributes": [
                {"trait_type": layer, "value": name} for layer, name in tok.traits.items()
            ]
            + ([{"trait_type": "Rarity Rank", "value": ranks[tok.token_id]}]
               if tok.token_id in ranks else []),
        }
        path = out_dir / f"{tok.token_id}.json"
        path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        written.append(path)
    log.info("wrote %d metadata files -> %s", len(written), out_dir)
    return written