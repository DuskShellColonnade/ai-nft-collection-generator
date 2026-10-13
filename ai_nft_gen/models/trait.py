"""Trait primitives."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Trait(BaseModel):
    layer: str
    name: str
    weight: int = Field(ge=0)

    @property
    def key(self) -> str:
        return f"{self.layer}:{self.name}"


class TraitPool(BaseModel):
    """All traits for a collection, indexed by layer."""

    layers: dict[str, list[Trait]]

    def layer_names(self) -> list[str]:
        return list(self.layers.keys())

    def total_weight(self, layer: str) -> int:
        return sum(t.weight for t in self.layers[layer])