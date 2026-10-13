"""Weighted trait sampling with incompatibility enforcement."""

from __future__ import annotations

import random

from ai_nft_gen.lib.hashing import trait_fingerprint
from ai_nft_gen.models.trait import Trait, TraitPool
from ai_nft_gen.models.token import TokenRecord


def _weighted_pick(rng: random.Random, traits: list[Trait]) -> Trait:
    total = sum(t.weight for t in traits)
    if total <= 0:
        raise ValueError("layer has zero total weight")
    r = rng.uniform(0, total)
    upto = 0.0
    for t in traits:
        upto += t.weight
        if upto >= r:
            return t
    return traits[-1]


def _violates(combo: dict[str, str], rules: list[list[str]]) -> bool:
    for rule in rules:
        if all(combo.get(k.split(":", 1)[0]) == k.split(":", 1)[1] for k in rule if ":" in k):
            return True
    return False


def sample_token(
    rng: random.Random,
    pool: TraitPool,
    layer_order: list[str],
    incompatibilities: list[list[str]],
    token_id: int,
) -> TokenRecord:
    """Sample one token. Retries up to 64 times on incompatibility."""
    for _ in range(64):
        combo: dict[str, str] = {}
        for layer in layer_order:
            combo[layer] = _weighted_pick(rng, pool.layers[layer]).name
        if not _violates(combo, incompatibilities):
            return TokenRecord(
                token_id=token_id,
                traits=combo,
                fingerprint=trait_fingerprint(combo),
            )
    raise RuntimeError(f"could not sample token {token_id} after 64 attempts")