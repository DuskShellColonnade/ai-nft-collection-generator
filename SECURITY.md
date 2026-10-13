# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security only |
| < 0.5   | no        |

## Reporting a vulnerability

Open a private security advisory on GitHub. Do not file a public issue for
anything that could leak a Pinata JWT, an IPFS pinning key, or a wallet
private key used by the mint adapter.

Expected first response: 72 hours. Fix window for critical: 14 days.

## Scope

In scope:
- `ai_nft_gen/services/pinata_client.py` — credential handling
- `ai_nft_gen/services/ipfs_gateway.py` — gateway SSRF surface
- `ai_nft_gen/features/mint_adapter.py` — unsigned tx construction
- `ai_nft_gen/lib/secrets.py` — env loading

Out of scope:
- Model weights supplied by the user
- Third-party RPC endpoints
- Anything in `outputs/` or `collections/`

## Hardening notes

- Never log a JWT. `pinata_client` redacts on `__repr__`.
- RPC URLs must be validated against an allowlist in `config/rpc.yaml`.
- Mint adapter never signs. It returns an unsigned payload for the user's wallet.