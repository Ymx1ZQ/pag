# pag — Development Plan

## M1 — Project scaffolding ✅

- [x] Create `pyproject.toml` with metadata, dependencies, and `[project.scripts]` entry point
- [x] Create `src/pag/__init__.py` with version
- [x] Create `src/pag/__main__.py`
- [x] Create `install.sh`
- [x] Create `.env.example`
- [x] Verify `uv sync` and `uv run pag --version` work

## M2 — Configuration and models ✅

- [x] Implement `config.py` — API key resolution (flag > env var > .env)
- [x] Implement `models.py` — Pydantic models for InferenceRequest, InferenceResponse, StyleCreateRequest, StyleUpdateRequest, StyleResponse
- [x] Implement `styles.py` — Static registry of all styles per model (RD_PRO, RD_FAST, RD_PLUS, animations) with valid size ranges
- [x] Unit tests for config, models, styles

## M3 — API client ✅

- [x] Implement `client.py` — httpx-based client for `/v1/inferences` (generate, animate, cost check) and `/v1/styles` (CRUD)
- [x] Handle errors, timeouts, retries
- [x] Unit tests with respx mocks

## M4 — Output handling ✅

- [x] Implement `output.py` — base64 decode, save PNG/GIF, `--stdout` mode
- [x] Filename resolution logic:
  - [x] `--output` / `-o` → exact file path (e.g. `pag generate "cat" -o cat.png`)
  - [x] `--output-dir` / `-d` → directory with auto-generated name
  - [x] `--name-pattern` → custom template using `{prompt}`, `{style}`, `{seed}`, `{n}`, `{timestamp}` placeholders
  - [x] Default pattern: `{prompt_slug}_{timestamp}_{n}.png` (`.gif` for animations)
  - [x] `{prompt_slug}` = first 48 chars of prompt, lowercased, non-alnum replaced with `_`, trailing `_` stripped
  - [x] `{n}` = image index (0-based), only appended when `num_images > 1` or pattern explicitly includes it
- [x] Unit tests for output and filename resolution

## M5 — CLI ✅

- [x] Implement `cli.py` with Click:
  - [x] `pag generate` — prompt, --style, --size, -n, --seed, --ref, --tile-x, --tile-y, --remove-bg, -o, -d, --name-pattern, --stdout, --api-key
  - [x] `pag animate` — prompt, --style, --size, --spritesheet, -o, -d, --name-pattern, --stdout, --api-key
  - [x] `pag cost` — prompt, --style, --size, -n
  - [x] `pag styles list|create|update|delete`
  - [x] `pag --version`, `pag list-styles [--model]`
- [x] Unit tests for CLI (click.testing.CliRunner) — 21 tests

## M6 — Live tests ✅

- [x] `tests/live/conftest.py` — skip if no API key, shared fixtures
- [x] `test_generate.py` — basic generation, multiple images, seed, tiling, bg removal
- [x] `test_animate.py` — GIF and spritesheet output
- [x] `test_styles_api.py` — create, update, delete custom style lifecycle
- [x] `test_cost_check.py` — verify cost check returns expected fields

Note: Removed `list_styles` (GET /v1/styles) — API returns 405 Method Not Allowed. `styles list` now shows built-in styles instead. Seed reproducibility test relaxed — API does not guarantee identical output for same seed.

## M7 — Install script and final polish ✅

- [x] Finalize `install.sh` — Python 3.12+ check, uv detection/install, `uv tool install .`, verification
- [x] Comprehensive README with quickstart, all commands/options documented, filename patterns
- [x] Verify all unit (82) and live (10) tests pass

## M8 — Spinner e verbose mode ✅

- [x] Spinner animato durante le chiamate API (elapsed time visibile)
- [x] Flag `--verbose` / `-v` globale che mostra request payload e response payload (JSON pretty-printed)
- [x] Il verbose tronca i campi base64 (reference_images, base64_images) per leggibilità
- [x] Unit tests per spinner e verbose (12 test)
- [x] Aggiornare README
