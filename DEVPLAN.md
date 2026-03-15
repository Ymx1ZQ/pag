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

## M14 — Fix InferenceRequest field constraints

Il model Pydantic ha vincoli sbagliati che impediscono l'uso di stili a bassa risoluzione.

- [ ] `InferenceRequest.width`: `ge=24` → `ge=16` (stili low_res/mc vanno fino a 16)
- [ ] `InferenceRequest.height`: `ge=24` → `ge=16`
- [ ] Aggiornare unit test che validano i bounds

## M15 — Aggiungere parametri API mancanti a InferenceRequest

Parametri supportati dall'API che il nostro model non include.

- [ ] `strength: float | None` (0.0–1.0, per img2img)
- [ ] `input_palette: str | None` (base64, riferimento palette colori)
- [ ] `return_pre_palette: bool` (ricevere immagine pre-palette)
- [ ] `bypass_prompt_expansion: bool` (disabilitare prompt expansion)
- [ ] `include_downloadable_data: bool` (per inventory_items e simili)
- [ ] `return_non_bg_removed: bool` (ricevere immagine originale quando remove_bg=True)
- [ ] `upscale_output_factor: int | None` (1 = risoluzione nativa, null = default)
- [ ] `extra_prompt: str | None` (per tileset_advanced)
- [ ] `extra_input_image: str | None` (per tileset_advanced)
- [ ] `frames_duration: int | None` (per advanced animations: 4, 6, 8, 10, 12, 16)
- [ ] Aggiornare unit test

## M16 — Fix InferenceResponse e StyleResponse

I model di risposta non catturano tutti i campi restituiti dall'API.

**InferenceResponse — campi mancanti:**
- [ ] `output_images: list[str]` (default `[]`)
- [ ] `output_urls: list[str]` (default `[]`)
- [ ] `downloadable_data: dict | None` (quando include_downloadable_data è usato)

**StyleResponse — campi mancanti:**
- [ ] `prompt_style: str | None` (la chiave da usare nelle inference)
- [ ] `type: str | None` (es. "user")
- [ ] `created_at: int | None`
- [ ] `updated_at: int | None`
- [ ] `deleted: bool | None` (restituito dal delete)

- [ ] Aggiornare `cli.py` per mostrare `prompt_style` dopo la creazione (è il valore che l'utente deve usare)
- [ ] Aggiornare unit test

## M17 — Aggiungere stili Tileset (rd_tile)

L'API supporta 6 stili tileset che non sono nel nostro registry e non hanno un comando CLI.

**Stili da aggiungere a `styles.py`:**
- [ ] `rd_tile__tileset` (16→32)
- [ ] `rd_tile__tileset_advanced` (16→32)
- [ ] `rd_tile__single_tile` (16→64)
- [ ] `rd_tile__tile_variation` (16→128)
- [ ] `rd_tile__tile_object` (16→96)
- [ ] `rd_tile__scene_object` (64→384)

**CLI:**
- [ ] Aggiungere comando `pag tileset` (o integrare in `pag generate` con model detection)
- [ ] Supportare `extra_prompt` e `extra_input_image` per `tileset_advanced`
- [ ] Aggiungere `rd_tile` come opzione in `pag list-styles --model`
- [ ] Unit test

## M18 — Aggiungere Advanced Animations (rd_advanced_animation)

L'API supporta 8 stili di animazione avanzata che richiedono un input_image e supportano frames_duration.

**Stili da aggiungere a `styles.py`:**
- [ ] `rd_advanced_animation__attack` (32→256)
- [ ] `rd_advanced_animation__crouch` (32→256)
- [ ] `rd_advanced_animation__custom_action` (32→256)
- [ ] `rd_advanced_animation__destroy` (32→256)
- [ ] `rd_advanced_animation__idle` (32→256)
- [ ] `rd_advanced_animation__jump` (32→256)
- [ ] `rd_advanced_animation__subtle_motion` (32→256)
- [ ] `rd_advanced_animation__walking` (32→256)

**CLI:**
- [ ] Integrare in `pag animate` o creare `pag animate-advanced`
- [ ] `--input-image` obbligatorio per questi stili
- [ ] `--frames-duration` opzione (4, 6, 8, 10, 12, 16)
- [ ] Aggiungere `rd_advanced_animation` come opzione in `pag list-styles --model`
- [ ] Unit test

## M19 — Aggiungere endpoint Edit (POST /v1/edit)

L'API ha un endpoint di editing separato che non supportiamo.

- [ ] Aggiungere `EditRequest` e `EditResponse` a `models.py`
  - Request: `prompt: str`, `inputImageBase64: str`
  - Response: `outputImageBase64: str`, `remaining_credits: float`
  - Size supportata: 16x16→256x256
- [ ] Aggiungere metodo `edit()` a `RetroClient`
- [ ] Aggiungere comando `pag edit` al CLI
  - `pag edit "add a hat" --input-image sprite.png`
  - Supportare `-o`, `-d`, `--name-pattern`, `--stdout`, `--open`
- [ ] Unit test

## M20 — Aggiungere endpoint Balance (GET /v1/inferences/credits)

L'API permette di controllare il saldo crediti.

- [ ] Aggiungere metodo `get_balance()` a `RetroClient`
- [ ] Aggiungere comando `pag balance` al CLI
- [ ] Unit test

## M21 — Aggiungere opzioni CLI mancanti per generate

Esporre i parametri API aggiunti in M15 come opzioni CLI in `pag generate`.

- [ ] `--input-image PATH` + `--strength FLOAT` (img2img)
- [ ] `--input-palette PATH` (palette reference)
- [ ] `--bypass-prompt-expansion` (flag)
- [ ] `--upscale-output-factor INT` (1 = nativo)
- [ ] `--include-downloadable-data` (flag, salva JSON aggiuntivo)
- [ ] `--return-non-bg-removed` (flag, salva anche l'immagine senza bg removal)
- [ ] `--return-pre-palette` (flag, salva anche l'immagine pre-palette)
- [ ] Unit test

## M22 — Audit e fix README finale

Revisione completa del README per allinearlo a tutti i fix precedenti.

- [ ] Sezione "Available styles and size limits" — aggiornare nomi, tabelle, range, includere tileset e advanced animations
- [ ] Sezione animate — aggiungere advanced animations
- [ ] Aggiungere sezione tileset
- [ ] Aggiungere sezione edit
- [ ] Aggiungere sezione balance
- [ ] Aggiungere documentazione nuove opzioni generate (img2img, palette, ecc.)
- [ ] Verificare che ogni stile e parametro listato corrisponda esattamente all'API
