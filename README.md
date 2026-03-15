# pag — Pixel Art Generator

**pag** (pixel art generator) — a Python CLI tool for generating pixel art using the [Retro Diffusion](https://retrodiffusion.ai/) API.

## Features

- Generate pixel art from text prompts with 50+ style presets
- Three model tiers: RD_PRO (high quality), RD_FAST (speed), RD_PLUS (extended styles)
- Sprite sheet and GIF animation generation (walking, idle, VFX, rotations)
- Reference image support (up to 9 images for RD_PRO)
- Seamless tiling (X/Y axis)
- Background removal
- Custom style management (create, update, delete)
- Cost estimation before generating
- Installs globally via [uv](https://docs.astral.sh/uv/)

## Requirements

- Python 3.12+
- Ubuntu 25.10+ (or any Linux with uv support)
- A [Retro Diffusion API key](https://retrodiffusion.ai/)

## Installation

```bash
git clone git@github.com:Ymx1ZQ/pag.git
cd pag
chmod +x install.sh
./install.sh
```

The install script will:
1. Install `uv` if not already present
2. Install `pag` as a global CLI tool via `uv tool install`
3. Verify the installation with `pag --version`

### Manual installation

```bash
uv tool install .
```

## Configuration

Set your API key in one of these ways (in order of precedence):

1. CLI flag: `--api-key <key>`
2. Environment variable: `export RETRODIFFUSION_API_KEY=your_key`
3. `.env` file in the current directory

## Usage

### Generate pixel art

```bash
# Basic generation
pag generate "a cool corgi" --style rd_pro__default --size 128x128

# Multiple images with seed
pag generate "dungeon tileset" --style rd_pro__dungeon_map -n 4 --seed 42

# With background removal
pag generate "sword icon" --style rd_fast__item_sheet --size 64x64 --remove-bg

# With reference images
pag generate "a warrior" --style rd_pro__fantasy --ref image1.png --ref image2.png

# Seamless tiling
pag generate "grass texture" --style rd_pro__default --tile-x --tile-y

# Custom output directory
pag generate "a cat" --style rd_pro__default -o ./output/

# Pipe base64 to stdout
pag generate "a cat" --style rd_pro__default --stdout
```

### Animations

```bash
# Walking + idle animation (outputs GIF)
pag animate "walking knight" --style walking_and_idle

# As spritesheet (outputs PNG)
pag animate "walking knight" --style walking_and_idle --spritesheet

# VFX animation
pag animate "fire effect" --style vfx --size 48x48
```

Available animation styles:
- `any_animation` — 64x64, generic animation
- `8_dir_rotation` — 80x80, 8-direction rotation
- `four_angle_walking` — 48x48, 4-angle walk cycle
- `walking_and_idle` — 48x48, walk + idle
- `small_sprites` — 32x32, small animated sprites
- `vfx` — 24x24 to 96x96, visual effects

### Cost estimation

```bash
pag cost "a cool corgi" --style rd_pro__default --size 128x128
```

Outputs the credit cost without generating any image.

### Custom styles

```bash
# List your custom styles
pag styles list

# Create a new custom style
pag styles create --name "my style" --description "A dark fantasy style" --ref reference.png

# Update a style
pag styles update <style_id> --name "renamed style"

# Delete a style
pag styles delete <style_id>
```

### Other options

```bash
pag --version          # Show version
pag --help             # Show help
pag generate --help    # Show help for generate subcommand
pag --list-styles      # List all available built-in styles
```

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
# Unit tests only
uv run pytest tests/unit/

# Live tests (requires RETRODIFFUSION_API_KEY)
uv run pytest tests/live/

# All tests
uv run pytest
```

Live tests are automatically skipped when `RETRODIFFUSION_API_KEY` is not set.

### Project structure

```
pag/
├── pyproject.toml          # Package config (uv/pip compatible)
├── install.sh              # Global CLI installer
├── src/
│   └── pag/
│       ├── __init__.py
│       ├── __main__.py     # python -m pag entry point
│       ├── cli.py          # Click-based CLI
│       ├── client.py       # Retro Diffusion API client (httpx)
│       ├── models.py       # Pydantic request/response models
│       ├── styles.py       # Style registry and validation
│       ├── config.py       # API key resolution
│       └── output.py       # Base64 decoding and file saving
├── tests/
│   ├── unit/               # Mocked tests, no API calls
│   └── live/               # Real API tests, need API key
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `click` | CLI framework |
| `httpx` | HTTP client |
| `pydantic` | Input/output validation |
| `python-dotenv` | `.env` file loading |

Dev dependencies: `pytest`, `pytest-mock`, `respx`

## License

MIT
