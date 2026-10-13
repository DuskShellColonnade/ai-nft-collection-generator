"""Collection plan + report shapes."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from ai_nft_gen.models.token import TokenRecord


class CollectionPlan(BaseModel):
    name: str
    size: int
    items: list[TokenRecord]
    out_path: Path
    seed: int


class RarityEntry(BaseModel):
    token_id: int
    score: float
    rank: int


class RarityReport(BaseModel):
    method: str
    entries: list[RarityEntry] = Field(default_factory=list)

    def by_token(self) -> dict[int, RarityEntry]:
        return {e.token_id: e for e in self.entries}