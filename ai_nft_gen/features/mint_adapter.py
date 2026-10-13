"""Unsigned mint payload builder. Never signs. Never broadcasts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MintPayload:
    token_uri: str
    to: str
    chain: str
    royalty_bps: int
    unsigned_tx: dict[str, object]


def build_mint_payload(
    metadata_cid: str,
    to: str,
    chain: str,
    royalty_bps: int,
    contract: str,
) -> MintPayload:
    """Return an unsigned payload for the user's own wallet to sign.

    Caller is responsible for RPC submission. This module does not hold keys.
    """
    uri = f"ipfs://{metadata_cid}"
    tx = {
        "to": contract,
        "data": f"0xSAFE_MINT_CALLDATA_PLACEHOLDER:{uri}:{to}",
        "value": "0x0",
    }
    return MintPayload(
        token_uri=uri, to=to, chain=chain, royalty_bps=royalty_bps, unsigned_tx=tx
    )


def load_metadata_cids(collection_dir: Path) -> dict[int, str]:
    """Read cid sidecar written by the pin step."""
    import json
    sidecar = collection_dir / "metadata_cids.json"
    if not sidecar.exists():
        return {}
    return {int(k): v for k, v in json.loads(sidecar.read_text(encoding="utf-8")).items()}