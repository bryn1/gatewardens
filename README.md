# Gatewardens

Clean-room, forever-free action tower defense in the Dungeon Defenders vein (Godot 4, web export).

**No shop. No loot boxes. No timers. No monetization, ever — by owner ruling 2026-10-25.**

Web client build (DECLARED W12 one-liner): `bash tools/export_web.sh` → `static/` (build artifacts, never committed), served by `python3 server/server.py` (GW_PORT, default 8124).

Status: **v1.1 (visuals)** — since v1 (GA, W1–W17g): original stylized sprites, T1–T3 tower art, arena world, HUD badges, combat FX and menu motion, all knut-VERIFIED with pixel proof served AND on a native Windows/RTX 2060 run at 60 FPS (222 pytest green, hygiene gate 0 hits, golden fixtures byte-identical). What shipped + the honest known-limits list: RELEASE_NOTES.md; acceptance list with evidence levels: LEDGER.md.

Windows desktop build (W18, built by `bash tools/export_windows.sh` → `build/`, artifacts never committed): the double-click `Gatewardens.exe` asset ships on the [release page](https://github.com/bryn1/gatewardens/releases); saves live in `%APPDATA%\Godot\app_userdata\Gatewardens`.
