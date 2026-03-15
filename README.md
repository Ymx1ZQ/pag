# pag — Pixel Art Generator

**pag** (pixel art generator) — a Python CLI tool for generating pixel art using the [Retro Diffusion](https://retrodiffusion.ai/) API.

## Features

- Generate pixel art from text prompts with 60+ style presets
- Three model tiers: **RD_PRO** (high quality), **RD_FAST** (speed), **RD_PLUS** (extended styles)
- Sprite sheet and GIF animation generation (walking, idle, VFX, rotations)
- Reference image support (up to 9 images for RD_PRO)
- Seamless tiling (X/Y axis)
- Background removal
- Custom style management (create, update, delete)
- Cost estimation before generating
- Flexible output naming: exact path, directory + auto-name, or custom pattern
- Installs globally via [uv](https://docs.astral.sh/uv/)

## Requirements

- Python 3.12+
- Ubuntu 25.10+ (or any Linux with uv support)
- A [Retro Diffusion API key](https://retrodiffusion.ai/)

## Quickstart

```bash
# 1. Clone and install
git clone git@github.com:Ymx1ZQ/pag.git
cd pag
chmod +x install.sh
./install.sh

# 2. Set your API key
export RETRODIFFUSION_API_KEY=your_key_here

# 3. Generate your first pixel art image
pag generate "a cute red mushroom" --style rd_fast__simple --size 64x64

# 4. Check the output — the PNG is saved in your current directory
ls *.png
```

That's it! The image is saved as `a_cute_red_mushroom_<timestamp>.png` in your current directory.

## Installation

### Via install.sh (recommended)

```bash
git clone git@github.com:Ymx1ZQ/pag.git
cd pag
chmod +x install.sh
./install.sh
```

The install script will:
1. Check that Python 3.12+ is installed
2. Install `uv` if not already present
3. Install `pag` as a global CLI tool via `uv tool install`
4. Verify the installation with `pag --version`

### Manual installation

```bash
uv tool install .
```

## Configuration

Set your API key in one of these ways (in order of precedence):

| Method | Example |
|--------|---------|
| CLI flag | `pag generate "a cat" --style rd_pro__default --api-key YOUR_KEY` |
| Environment variable | `export RETRODIFFUSION_API_KEY=your_key` |
| `.env` file | Create a `.env` file with `RETRODIFFUSION_API_KEY=your_key` |

## Usage

### `pag generate` — Generate pixel art

Generate one or more pixel art images from a text prompt.

```bash
# Basic generation (uses style's default size)
pag generate "a cool corgi" --style rd_pro__default

# Specify exact size
pag generate "a cool corgi" --style rd_pro__default --size 128x128

# Multiple images with a fixed seed
pag generate "dungeon tileset" --style rd_pro__dungeon_map -n 4 --seed 42

# With background removal
pag generate "sword icon" --style rd_fast__item_sheet --size 64x64 --remove-bg

# With reference images (RD_PRO supports up to 9)
pag generate "a warrior" --style rd_pro__fantasy --ref image1.png --ref image2.png

# Seamless tiling (for textures)
pag generate "grass texture" --style rd_pro__default --tile-x --tile-y
```

**All `generate` options:**

| Option | Description |
|--------|-------------|
| `PROMPT` | Text description of the image (required) |
| `--style` | Style key, e.g. `rd_pro__default` (required). See `pag list-styles` |
| `--size WxH` | Image dimensions, e.g. `128x128`. Defaults to style minimum |
| `-n, --num-images` | Number of images to generate (default: 1) |
| `--seed` | Seed for generation |
| `--ref PATH` | Reference image file (repeatable) |
| `--tile-x` | Enable horizontal seamless tiling |
| `--tile-y` | Enable vertical seamless tiling |
| `--remove-bg` | Remove image background |
| `-o, --output` | Exact output file path |
| `-d, --output-dir` | Output directory (auto-names files) |
| `--name-pattern` | Custom filename template (see [Filename patterns](#filename-patterns)) |
| `--stdout` | Write base64 to stdout instead of saving files |
| `--api-key` | Override API key for this command |

### Verbose mode and spinner

All API calls show an animated spinner with elapsed time:

```
⠹ Generating... 3.2s
Generating... done (12.4s)
```

Use `-v` / `--verbose` (before the subcommand) to see full request and response payloads:

```bash
pag -v generate "a cat" --style rd_pro__default --size 128x128
```

This prints the JSON request body and response to stderr, with base64 fields truncated for readability.

### `pag animate` — Generate animations

Generate animated sprites as GIF or PNG spritesheet.

```bash
# Walking + idle animation (outputs GIF)
pag animate "walking knight" --style walking_and_idle

# As spritesheet (outputs PNG)
pag animate "walking knight" --style walking_and_idle --spritesheet

# VFX animation with custom size
pag animate "fire effect" --style vfx --size 48x48
```

You can use either the short name (`walking_and_idle`) or the full key (`animation__walking_and_idle`).

**Available animation styles:**

| Style | Default size | Description |
|-------|-------------|-------------|
| `any_animation` | 64x64 | Generic animation |
| `8_dir_rotation` | 80x80 | 8-direction rotation |
| `four_angle_walking` | 48x48 | 4-angle walk cycle |
| `walking_and_idle` | 48x48 | Walk + idle |
| `small_sprites` | 32x32 | Small animated sprites |
| `vfx` | 24x24 → 96x96 | Visual effects (square only) |

**All `animate` options:**

| Option | Description |
|--------|-------------|
| `PROMPT` | Text description (required) |
| `--style` | Animation style (required) |
| `--size WxH` | Override default size |
| `--spritesheet` | Output PNG spritesheet instead of GIF |
| `-o, --output` | Exact output file path |
| `-d, --output-dir` | Output directory |
| `--name-pattern` | Custom filename template |
| `--stdout` | Write base64 to stdout |
| `--api-key` | Override API key |

### `pag cost` — Estimate credit cost

Check how many credits a generation would cost without actually generating images.

```bash
pag cost "a cool corgi" --style rd_pro__default --size 128x128
pag cost "tileset" --style rd_pro__dungeon_map -n 4
```

**Options:** `PROMPT`, `--style`, `--size`, `-n`, `--api-key`

### `pag list-styles` — Browse available styles

List all built-in styles with their size ranges.

```bash
# All styles
pag list-styles

# Filter by model
pag list-styles --model rd_pro
pag list-styles --model rd_fast
pag list-styles --model rd_plus
pag list-styles --model animation
```

### `pag styles` — Manage custom styles

Create, update, and delete custom RD_PRO styles.

```bash
# Create a new custom style
pag styles create --name "my style" --description "A dark fantasy style" --ref reference.png --icon skull

# Update a style
pag styles update <style_id> --name "renamed style" --description "Updated description"

# Delete a style
pag styles delete <style_id>

# List built-in styles (same as pag list-styles)
pag styles list
```

**`styles create` options:**

| Option | Description |
|--------|-------------|
| `--name` | Style name (required) |
| `--description` | Style description |
| `--ref PATH` | Reference image file |
| `--icon` | Icon name (e.g. `skull`, `sparkles`, `fire`, `sword`) |
| `--api-key` | Override API key |

### Filename patterns

Control how output files are named using `--name-pattern` with these placeholders:

| Placeholder | Description |
|-------------|-------------|
| `{prompt_slug}` | First 48 chars of prompt, lowercased, special chars → `_` |
| `{prompt}` | Same as `{prompt_slug}` |
| `{style}` | Style key with `__` replaced by `_` |
| `{seed}` | Seed value, or `noseed` if not set |
| `{n}` | Image index (0-based) |
| `{timestamp}` | Unix timestamp |

**Examples:**

```bash
# Custom pattern
pag generate "a cat" --style rd_pro__default --name-pattern "{prompt_slug}_{style}_{seed}"
# → a_cat_rd_pro_default_noseed.png

# Exact output path
pag generate "a cat" --style rd_pro__default -o my_cat.png
# → my_cat.png

# Output to directory with auto-naming
pag generate "a cat" --style rd_pro__default -d ./output/
# → ./output/a_cat_1700000000.png

# Multiple images get index suffix automatically
pag generate "gems" --style rd_pro__default -n 3 -d ./output/
# → ./output/gems_1700000000_0.png, gems_1700000000_1.png, gems_1700000000_2.png
```

**Default pattern:** `{prompt_slug}_{timestamp}.png` (single image) or `{prompt_slug}_{timestamp}_{n}.png` (multiple). Animations use `.gif` unless `--spritesheet` is set.

## Available styles

### RD_PRO (96x96 → 256x256)

`default`, `painterly`, `fantasy`, `ui_panel`, `horror`, `scifi`, `simple`, `isometric`, `topdown`, `platformer`, `dungeon_map`, `edit`, `pixelate`, `spritesheet`, `typography`, `hexagonal_tiles`, `fps_weapon`, `inventory_items`

### RD_FAST (64x64 → 384x384)

`default`, `retro`, `simple`, `detailed`, `anime`, `game_asset`, `portrait`, `texture`, `ui`, `item_sheet`, `character_turnaround`, `1_bit`, `low_res`, `minecraft_block`, `minecraft_item`, `minecraft_mob`, `no_style`

### RD_PLUS (varies by style)

`default`, `retro`, `watercolor`, `textured`, `cartoon`, `ui_element`, `item_sheet`, `character_turnaround`, `environment`, `topdown_character`, `topdown_tileset`, `isometric_object`, `isometric_environment`, `classic`, `low_res`, `minecraft_block`, `minecraft_item`, `minecraft_mob`, `topdown_item`, `skill_icon`

## Development

### Setup

```bash
git clone git@github.com:Ymx1ZQ/pag.git
cd pag
uv sync
```

### Running tests

```bash
# Unit tests only (no API key needed)
uv run pytest tests/unit/ -v

# Live tests (requires RETRODIFFUSION_API_KEY)
uv run pytest tests/live/ -v

# All tests
uv run pytest -v
```

Live tests are automatically skipped when `RETRODIFFUSION_API_KEY` is not set.

### Project structure

```
pag/
├── pyproject.toml          # Package metadata and dependencies
├── install.sh              # Global CLI installer
├── src/
│   └── pag/
│       ├── __init__.py     # Version
│       ├── __main__.py     # python -m pag entry point
│       ├── cli.py          # Click-based CLI (generate, animate, cost, styles)
│       ├── client.py       # Retro Diffusion API client (httpx)
│       ├── models.py       # Pydantic request/response models
│       ├── styles.py       # Style registry and validation
│       ├── config.py       # API key resolution
│       └── output.py       # Base64 decoding, file saving, filename resolution
├── tests/
│   ├── unit/               # 82 tests — mocked, no API calls
│   └── live/               # 10 tests — real API, need RETRODIFFUSION_API_KEY
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `click` | CLI framework |
| `httpx` | HTTP client |
| `pydantic` | Input/output validation |
| `python-dotenv` | `.env` file loading |

Dev: `pytest`, `pytest-mock`, `respx`

## License

MIT
