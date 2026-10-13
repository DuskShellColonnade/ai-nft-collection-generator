"""Deterministic hashing for provenance and dedupe."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def trait_fingerprint(traits: dict[str, str]) -> str:
    """Stable fingerprint for a trait combo. Used for dedupe."""
    return sha256_bytes(canonical_json(traits))[:16]