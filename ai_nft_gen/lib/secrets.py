"""Env loading + redaction. Never log a raw JWT."""

from __future__ import annotations

import os
from dataclasses import dataclass

_REDACT_KEYS = {"PINATA_JWT", "PINATA_API_KEY", "PINATA_API_SECRET", "RPC_URL"}


@dataclass(frozen=True)
class Secrets:
    pinata_jwt: str | None
    rpc_url: str | None

    def __repr__(self) -> str:  # never leak
        def r(k: str, v: str | None) -> str:
            if v is None:
                return "None"
            return f"<redacted:{k}:len={len(v)}>"
        return f"Secrets(pinata_jwt={r('PINATA_JWT', self.pinata_jwt)}, rpc_url={r('RPC_URL', self.rpc_url)})"


def load_secrets() -> Secrets:
    return Secrets(
        pinata_jwt=os.environ.get("PINATA_JWT") or None,
        rpc_url=os.environ.get("RPC_URL") or None,
    )