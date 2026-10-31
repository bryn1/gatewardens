# Gatewardens

Clean-room, forever-free action tower defense in the Dungeon Defenders vein (Godot 4, web export).

**No shop. No loot boxes. No timers. No monetization, ever — by owner ruling 2026-10-25.**

Web client build (DECLARED W12 one-liner): `bash tools/export_web.sh` → `static/` (build artifacts, never committed), served by `python3 server/server.py` (GW_PORT, default 8124).

Status: **v1.3 (zoom)** — mouse-wheel camera zoom on the v1.2.1 readability base: scroll out to a 2× overview, scroll in to a floor derived from the shipped framing gate that never crops a path corner, the default view byte-identical to v1.2.1 (pixel-identical capture), wheel-only with no HUD change — the camera ships exactly as granted, "Go 1 and zoom control for 2" (owner, 2026-10-30, MC 11719): distance only, pan/rotate/pitch stay NOT granted, the LOCKED frustum pin #3 stays SPENT — plus the clean-code wave the v1.2.1 close ordered (audit 0 hard size findings; the duplicate material builder + air-grouping folded to one home each; the dead selected_tier retired; docs de-staled; byte-identical probe transcripts = zero behavior change) (287 pytest green, hygiene gate 0 hits, golden fixtures byte-identical). What shipped + the honest known-limits list: RELEASE_NOTES.md; acceptance list with evidence levels: LEDGER.md.

Windows desktop build (W18, built by `bash tools/export_windows.sh` → `build/`, artifacts never committed): the double-click `Gatewardens.exe` asset ships on the [release page](https://github.com/bryn1/gatewardens/releases); saves live in `%APPDATA%\Godot\app_userdata\Gatewardens`.
