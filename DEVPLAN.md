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

## M3 — API client

- [ ] Implement `client.py` — httpx-based client for `/v1/inferences` (generate, animate, cost check) and `/v1/styles` (CRUD)
- [ ] Handle errors, timeouts, retries
- [ ] Unit tests with respx mocks

## M4 — Output handling

- [ ] Implement `output.py` — base64 decode, save PNG/GIF, `--stdout` mode
- [ ] Filename resolution logic:
  - [ ] `--output` / `-o` → exact file path (e.g. `pag generate "cat" -o cat.png`)
  - [ ] `--output-dir` / `-d` → directory with auto-generated name
  - [ ] `--name-pattern` → custom template using `{prompt}`, `{style}`, `{seed}`, `{n}`, `{timestamp}` placeholders
  - [ ] Default pattern: `{prompt_slug}_{timestamp}_{n}.png` (`.gif` for animations)
  - [ ] `{prompt_slug}` = first 48 chars of prompt, lowercased, non-alnum replaced with `_`, trailing `_` stripped
  - [ ] `{n}` = image index (0-based), only appended when `num_images > 1` or pattern explicitly includes it
- [ ] Unit tests for output and filename resolution

## M5 — CLI

- [ ] Implement `cli.py` with Click:
  - [ ] `pag generate` — prompt, --style, --size, -n, --seed, --ref, --tile-x, --tile-y, --remove-bg, -o, --stdout, --format, --api-key
  - [ ] `pag animate` — prompt, --style, --size, --spritesheet, -o, --api-key
  - [ ] `pag cost` — prompt, --style, --size, -n
  - [ ] `pag styles list|create|update|delete`
  - [ ] `pag --version`, `pag --list-styles`
- [ ] Unit tests for CLI (click.testing.CliRunner)

## M6 — Live tests

- [ ] `tests/live/conftest.py` — skip if no API key, shared fixtures
- [ ] `test_generate.py` — basic generation, multiple images, reference images, tiling, bg removal
- [ ] `test_animate.py` — GIF and spritesheet output
- [ ] `test_styles_api.py` — create, update, delete custom style
- [ ] `test_cost_check.py` — verify cost check returns expected fields

## M7 — Install script and final polish

- [ ] Finalize `install.sh` — uv detection/install, `uv tool install .`, verification
- [ ] Test install flow on clean environment
- [ ] Verify all unit and live tests pass
