"""Load and validate collection config. Pydantic v2 models, strict types."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator


class CollectionCfg(BaseModel):
    name: str
    symbol: str
    description: str
    size: int = Field(gt=0, le=100_000)
    chain: str
    royalty_bps: int = Field(ge=0, le=10_000)


class TraitsCfg(BaseModel):
    source: Path
    layer_order: list[str]
    incompatibilities: list[list[str]] = Field(default_factory=list)


class RenderCfg(BaseModel):
    backend: Literal["diffusers", "stub"]
    model_id: str
    steps: int = Field(ge=1, le=150)
    guidance: float = Field(ge=0.0, le=20.0)
    width: int = Field(ge=256, le=4096)
    height: int = Field(ge=256, le=4096)
    seed_offset: int
    batch_size: int = Field(ge=1, le=64)
    device: Literal["cuda", "cpu", "mps"]


class RarityCfg(BaseModel):
    method: Literal["trait_count", "rarity_score", "information_content"]
    normalize: bool
    min_unique_ratio: float = Field(ge=0.0, le=1.0)


class MetadataCfg(BaseModel):
    schema_: str = Field(alias="schema")
    image_base: str
    external_url: str


class PinCfg(BaseModel):
    provider: Literal["pinata", "none"]
    pin_images: bool
    pin_metadata: bool
    concurrency: int = Field(ge=1, le=32)


class AppConfig(BaseModel):
    collection: CollectionCfg
    traits: TraitsCfg
    render: RenderCfg
    rarity: RarityCfg
    metadata: MetadataCfg
    pin: PinCfg

    @field_validator("traits")
    @classmethod
    def _layer_order_nonempty(cls, v: TraitsCfg) -> TraitsCfg:
        if not v.layer_order:
            raise ValueError("traits.layer_order must not be empty")
        return v


def load_config(path: Path) -> AppConfig:
    """Read YAML from disk and validate. Raises pydantic.ValidationError on bad input."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return AppConfig.model_validate(raw)