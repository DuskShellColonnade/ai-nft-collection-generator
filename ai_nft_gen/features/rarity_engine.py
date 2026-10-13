"""Rarity scoring. Three methods, one entrypoint."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from ai_nft_gen.lib.config_loader import AppConfig
from ai_nft_gen.lib.logging import get_logger
from ai_nft_gen.models.collection import RarityEntry, RarityReport
from ai_nft_gen.models.token import TokenRecord

log = get_logger(__name__)


def _load_renders(cfg: AppConfig) -> list[TokenRecord]:
    p = Path("outputs") / cfg.collection.symbol.lower() / "renders.json"
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [TokenRecord.model_validate(r) for r in raw]


def _trait_counts(tokens: list[TokenRecord]) -> dict[tuple[str, str], int]:
    c: Counter[tuple[str, str]] = Counter()
    for t in tokens:
        for layer, name in t.traits.items():
            c[(layer, name)] += 1
    return dict(c)


def _score_trait_count(tokens: list[TokenRecord], counts: dict[tuple[str, str], int]) -> list[float]:
    n = len(tokens)
    out: list[float] = []
    for t in tokens:
        s = 0.0
        for layer, name in t.traits.items():
            freq = counts[(layer, name)] / n
            s += 1.0 / freq
        out.append(s)
    return out


def _score_information_content(tokens: list[TokenRecord], counts: dict[tuple[str, str], int]) -> list[float]:
    n = len(tokens)
    out: list[float] = []
    for t in tokens:
        s = 0.0
        for layer, name in t.traits.items():
            p = counts[(layer, name)] / n
            s += -math.log(p)
        out.append(s)
    return out


def score_collection(cfg: AppConfig) -> RarityReport:
    tokens = _load_renders(cfg)
    counts = _trait_counts(tokens)
    method = cfg.rarity.method
    if method == "information_content":
        scores = _score_information_content(tokens, counts)
    else:
        scores = _score_trait_count(tokens, counts)
    if cfg.rarity.normalize and scores:
        lo, hi = min(scores), max(scores)
        rng = (hi - lo) or 1.0
        scores = [(s - lo) / rng for s in scores]
    ranked = sorted(zip(tokens, scores, strict=True), key=lambda x: x[1], reverse=True)
    entries = [
        RarityEntry(token_id=tok.token_id, score=score, rank=i + 1)
        for i, (tok, score) in enumerate(ranked)
    ]
    report = RarityReport(method=method, entries=entries)
    out = Path("collections") / cfg.collection.symbol.lower() / "rarity.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    log.info("scored %d tokens via %s", len(entries), method)
    return report