"""Token record: the unit that flows through the pipeline."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from ai_nft_gen.models.trait import Trait


class TokenRecord(BaseModel):
    token_id: int = Field(ge=0)
    traits: dict[str, str]
    fingerprint: str
    image_path: Path | None = None
    image_cid: str | None = None
    metadata_path: Path | None = None
    metadata_cid: str | None = None
    rarity_rank: int | None = None
    rarity_score: float | None = None

    def trait_objs(self, pool: dict[str, list[Trait]]) -> list[Trait]:
        out: list[Trait] = []
        for layer, name in self.traits.items():
            for t in pool.get(layer, []):
                if t.name == name:
                    out.append(t)
                    break
        return out