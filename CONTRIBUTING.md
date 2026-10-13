# Contributing to ai-nft-collection-generator

Thanks for wanting to peel a layer. This repo is a modular Python toolkit for
generating AI-driven NFT collections: trait synthesis, diffusion rendering,
rarity scoring, metadata assembly, and IPFS pinning.

## Ground rules

- One feature per PR. Feature modules live under `ai_nft_gen/features/`.
- Shared helpers go in `ai_nft_gen/lib/`. Do not import feature modules from lib.
- Config schema changes require a migration note in `docs/config_migration.md`.
- Every new feature module ships with a test under `tests/`.
- Type hints required. `mypy --strict` must pass on `ai_nft_gen/`.
- Follow the existing naming: `render_*.py`, `trait_*.py`, `meta_*.py`.

## Dev setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
pytest -q
```

## Style

- Ruff for lint + format. Line length 100.
- No bare `except:`. Catch specific exceptions.
- Logging via `ai_nft_gen.lib.logging.get_logger(__name__)`.
- Do not commit model weights. Reference them by hash in `config/models.yaml`.

## Community vocabulary

We use the real terms. "render", "trait", "rarity", "mint", "pin",
"collection", "provenance". Do not rename these to softer synonyms inside
code or docs — downstream tooling greps for them.