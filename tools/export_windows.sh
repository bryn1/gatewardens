#!/usr/bin/env bash
# Gatewardens Windows desktop export wrapper (W18, MC 11274 / card 11437).
# Runs the SHIPPED export_presets.cfg preset "Windows Desktop" (x86_64-only,
# binary_format/embed_pck=true — ONE self-contained .exe, no sidecar .pck)
# headless; cross-generates the .exe on Linux. Built artifacts are
# evidence-side, never product-side: build/ is .gitignore'd (same law as
# static/). GW_GODOT overrides the pinned binary (conftest idiom, as in
# export_web.sh). Echoes the exe sha256 at the end.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT="${GW_GODOT:-/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64}"
mkdir -p "$REPO/build"
"$GODOT" --headless --path "$REPO/godot" --export-release "Windows Desktop" \
    "$REPO/build/Gatewardens.exe"
sha256sum "$REPO/build/Gatewardens.exe"
