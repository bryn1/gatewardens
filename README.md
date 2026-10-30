# Gatewardens

Clean-room, forever-free action tower defense in the Dungeon Defenders vein (Godot 4, web export).

**No shop. No loot boxes. No timers. No monetization, ever — by owner ruling 2026-10-25.**

Web client build (DECLARED W12 one-liner): `bash tools/export_web.sh` → `static/` (build artifacts, never committed), served by `python3 server/server.py` (GW_PORT, default 8124).

Status: **v1.2.1 (readability)** — on the v1.2 quality-of-life set (end-only RETURN TO HUB on both mission-end screens, SELL ALL behind one total-gold confirm, the shop family picker, procedural enemy walk motion and the deeper, steeper camera D=64/pitch-48 — the ONE documented re-pin of the locked frustum pin #3, owner grant 2026-10-28; further moves need a NEW ruling) on the v1.1 visual base (original stylized sprites — boss included, greybox fully retired —, T1–T3 tower art, arena world, HUD badges, combat FX and menu motion, knut-VERIFIED with pixel proof served AND a deterministic 1280×720 @ 60 FPS native capture on a Windows 11 / RTX 2060 machine; the interactive-frame-rate figure on web is honest-by-instrument: see RELEASE_NOTES known limits), v1.2.1 makes the battlefield readable at a glance: eye billboards over every spawn gate (winged on the air gates), lit lane bands along every ground lane, per-gate wave telegraphs during the build phase, a bigger hero wearing a name crest, a first-mission coach banner telling you what to do now, floating damage numbers on every hit (the kill-blow number is a declared lower bound), a press-to-arm / click-to-place / right-click-cancel build flow with a yellow range ring on the armed ghost, and the web-build rendering fix that makes the bands and the ring paint in the browser (283 pytest green, hygiene gate 0 hits, golden fixtures byte-identical). What shipped + the honest known-limits list: RELEASE_NOTES.md; acceptance list with evidence levels: LEDGER.md.

Windows desktop build (W18, built by `bash tools/export_windows.sh` → `build/`, artifacts never committed): the double-click `Gatewardens.exe` asset ships on the [release page](https://github.com/bryn1/gatewardens/releases); saves live in `%APPDATA%\Godot\app_userdata\Gatewardens`.
