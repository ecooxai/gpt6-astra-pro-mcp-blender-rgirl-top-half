# RGirl top-half bust — GPT-6 Astra Pro / MCP / Blender
Project: /home/dev/project/3d/gpt6_astra_pro_mcp_blender_rgirl_top_half
Branch: gpt6-astra-pro/mcp-blender-bust
User reference: reference/reference.png, downloaded from the exact user URL.
Do not reuse existing character meshes, textures, hair assets, or generators. All character geometry and materials are authored in src/build_character.py. Reference is for human visual comparison only; never sample it into a model texture or analyze its pixels.
Use Blender headless EEVEE for previews. Runtime initially reports Blender 4.0.2; render on Xvfb :93 if needed.
Build artifacts belong in build/. Web app lives in preview/ and serves only this project. Record actual reviewed edit/render iterations in preview/status.json. Scores are subjective visual estimates, not externally measured likeness. Never claim 20,000 iterations or >95 quality without evidence.
Current state: environment restored, reference visually inspected, no character render completed yet.
Reference appearance: pale warm skin, dark-brown long swept hair and wispy bangs, brown eyes, subtle pink lips, white collared button shirt, head leaning slightly toward screen right. Back and sides must be inferred as plausible anatomy, not claimed as reference-verified.

## Milestone update
Actual complete toolchain: Blender 4.2.3 portable at /home/dev/.local/opt/blender-4.2.3-linux-x64/blender. The `blender` command on PATH is a broken restored 4.0.2 sysroot launcher; do not use it.
Working Xvfb display: :93. Preview HTTP server: port 8793, root preview/. Cloudflared URL at this milestone: https://namely-packed-batman-columns.trycloudflare.com . Runtime process IDs are only in ignored logs/*.pid.
Visual review 1: 38/100; visible white eye leaks, intersecting scalp, lumpy jaw interpolation, rigid hair.
Visual review 2: 52/100; major defects repaired, but eyelid-ring blending, scalp fibers, fuller hair and clothing opening still need substantial improvement.
Iteration 3 is being rendered with FAST_PREVIEW=1 (512x684, 12 samples). This is a real reduced-resolution EEVEE preview, not a generated illustration.
Desktop/mobile UI test passed: no page errors or horizontal overflow, reference modal works. Full GLB interaction test is still pending export.
Terminal pool can hit 32 sessions: stop only this task's completed terminal records with webterm stop ID. Never terminate unrelated terminals. Long-running render commands must be read, not relaunched.
