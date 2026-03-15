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

## M9 — API key management ✅

- [x] Update `config.py` — key resolution: `--api-key` flag > `~/.pag/.env` (removed env var and cwd .env)
- [x] Add `save_api_key(key)`, `get_saved_key()`, `mask_key()` to config module
- [x] Interactive prompt in `install.sh` — asks to configure API key after install, handles existing key with `[y/N]` confirmation
- [x] Add `pag config set-key` — interactive or with argument
- [x] Add `pag config show` — shows masked key and source
- [x] Unit tests for config resolution, save, mask, CLI config commands
- [x] Update README — configuration section, quickstart

## M10 — Animate enhancements ✅

- [x] Add `--remove-bg` flag to `pag animate`
- [x] Add `--input-image` option to `pag animate` — base64-encodes a reference image and passes it as `input_image` to the API
- [x] Unit tests for both new options
- [x] Update README animate section

## M11 — Auto-open generated files ✅

- [x] Add `--open` flag to `pag generate` and `pag animate`
- [x] Opens the generated file(s) with `xdg-open` after saving
- [x] No-op when `--stdout` is used (stdout path skips file saving entirely)
- [x] Unit tests (2 new tests)
- [x] Update README

## M12 — Shell completions ✅

- [x] Add `pag completions` command that outputs shell completion script
- [x] Support bash and zsh (`pag completions bash`, `pag completions zsh`)
- [x] Document installation in README

## M13 — Fix style names and size limits ✅

- [x] Fix RD_FAST style names (removed minecraft_block/mob, renamed minecraft_item→mc_item, added mc_texture)
- [x] Fix RD_PLUS style names (topdown_map, topdown_asset, isometric, isometric_asset, mc_item, mc_texture, removed minecraft_mob)
- [x] Fix per-style size limits (low_res, mc_item, mc_texture → 16-128; classic → 32-192)
- [x] Added factory kwargs min_s/max_s to _fast() and _plus() for per-style overrides
- [x] Updated README "Available styles and size limits" section
- [x] Added 25 new unit tests for name/size validation (124 total, all green)

## M14 — Fix InferenceRequest field constraints ✅

- [x] `InferenceRequest.width`: `ge=24` → `ge=16`
- [x] `InferenceRequest.height`: `ge=24` → `ge=16`
- [x] Added test for minimum size 16 acceptance

## M15 — Aggiungere parametri API mancanti a InferenceRequest ✅

- [x] Added all 10 missing fields: strength, input_palette, return_pre_palette, bypass_prompt_expansion, include_downloadable_data, return_non_bg_removed, upscale_output_factor, extra_prompt, extra_input_image, frames_duration
- [x] Added 6 new unit tests covering all new fields

## M16 — Fix InferenceResponse e StyleResponse ✅

- [x] Added output_images, output_urls, downloadable_data to InferenceResponse
- [x] Added prompt_style, type, created_at, updated_at, deleted to StyleResponse
- [x] CLI shows prompt_style after style creation
- [x] Added 5 new unit tests (136 total)

## M17 — Aggiungere stili Tileset (rd_tile) ✅

- [x] Added 6 rd_tile styles with correct size limits
- [x] Added `pag tileset` command with --extra-prompt, --input-image, --extra-input-image
- [x] Added `rd_tile` to `pag list-styles --model` filter
- [x] Added 11 new unit tests (147 total)

## M18 — Aggiungere Advanced Animations (rd_advanced_animation) ✅

- [x] Added 8 advanced animation styles (attack, crouch, custom_action, destroy, idle, jump, subtle_motion, walking)
- [x] Integrated into `pag animate` with auto-detection (animation__ vs rd_advanced_animation__)
- [x] Added --frames-duration option (4, 6, 8, 10, 12, 16)
- [x] --input-image required for advanced styles (enforced with error)
- [x] Added rd_advanced_animation to list-styles --model filter
- [x] 5 new unit tests (152 total)

## M19 — Aggiungere endpoint Edit (POST /v1/edit) ✅

- [x] Added EditRequest and EditResponse models
- [x] Added edit() method to RetroClient
- [x] Added `pag edit` CLI command with -o, -d, --name-pattern, --stdout, --open
- [x] 3 new unit tests (155 total)

## M20 — Aggiungere endpoint Balance (GET /v1/inferences/credits) ✅

- [x] Added get_balance() method to RetroClient
- [x] Added `pag balance` CLI command
- [x] 1 new unit test (156 total)

## M21 — Aggiungere opzioni CLI mancanti per generate ✅

- [x] Added --input-image + --strength (img2img)
- [x] Added --input-palette + --return-pre-palette
- [x] Added --bypass-prompt-expansion, --upscale-output-factor
- [x] Added --include-downloadable-data, --return-non-bg-removed
- [x] 2 new unit tests (158 total)

## M22 — Audit e fix README finale ✅

- [x] Complete README rewrite covering all 6 model tiers
- [x] Documented all new commands: tileset, edit, balance
- [x] Documented all new generate options: img2img, palette, bypass-prompt-expansion, upscale, downloadable-data
- [x] Documented advanced animations with --frames-duration
- [x] All style names and size limits match official API
- [x] Updated project structure and test counts
- [x] All 158 unit tests pass
