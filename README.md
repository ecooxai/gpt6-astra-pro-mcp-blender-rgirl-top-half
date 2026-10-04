# RG.01 — Original Blender portrait bust

GPT-6 Astra Pro · MCP Colabdev · Blender 4.2.3 LTS / EEVEE · Three.js

A from-scratch interpretation of the user-provided portrait, with original facial geometry, masked eyes, layered curve hair, a white collared blouse, and a responsive comparison studio. No existing character model, hair asset, photographic texture, or environment map is imported. JavaScript frameworks are software dependencies, not character assets.

## Current state

This is an actively refined work in progress, **not a claimed 95/100 or AAA-quality match**. `preview/status.json` contains the actual visual review history and current score. Scores are manual subjective estimates; they are not automated image-similarity measurements. The user's requested 20,000-round budget is not represented as completed work.

The supplied front reference does not verify rear or profile appearance. Those surfaces are modeled as plausible interpretations.

## Rebuild

The Colab runtime provides `/home/dev/.local/opt/blender-4.2.3-linux-x64/blender`.

```sh
Xvfb :93 -screen 0 1440x1200x24 +extension GLX +render -noreset &
FAST_PREVIEW=1 ./src/render.sh 3 # use a fresh revision number for real edits
# Omit FAST_PREVIEW for the 768 x 1024 EEVEE render.
DISPLAY=:93 /home/dev/.local/opt/blender-4.2.3-linux-x64/blender \
  -b build/gpt6_astra_pro_mcp_blender_rgirl_top_half.blend \
  --python-exit-code 1 --python src/export_web.py
python3 -m http.server 8793 --directory preview
```

Only publish a score after visually inspecting the actual rendered result:

```sh
python3 src/publish_review.py REVISION SCORE 'Review title' 'Honest review notes'
```

`src/build_character.py` never opens the reference image. All meshes, strands, materials and color fields are defined in code. The GLB exporter omits the fine render-only groom and joins compatible geometry to reduce browser draw calls. The editable Blender source preserves the full procedural construction.

## Browser verification

```sh
npm ci
node tests/browser.mjs
# After the GLB is published:
TEST_MODEL=1 node tests/browser.mjs
```

The test runs headless Chromium at 1440 x 1100 and 390 x 844, checks overflow, script errors, reference enlargement and image loading, and optionally checks WebGL model loading and controls. Test evidence lives in `tests/`.

## Project layout

- `src/`: original builder, export and publication utilities.
- `build/`: editable Blender source, actual EEVEE outputs and GLB.
- `preview/`: self-contained static studio with locally vendored Three.js modules.
- `tests/`: reproducible browser tests and screenshots.
- `Agents.md`: next-agent handoff and remaining limitations.

Absolute project path: `/home/dev/project/3d/gpt6_astra_pro_mcp_blender_rgirl_top_half`.
