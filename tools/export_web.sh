#!/usr/bin/env bash
# Gatewardens Web export wrapper (W12, MC 11274.1.21 / card 11331).
# Runs the SHIPPED export_presets.cfg preset "Web" (thread_support=false,
# custom_html_shell=res://web_shell.html, export_path ../static/index.html)
# headless. Built artifacts are evidence-side, never product-side: static/
# is .gitignore'd (only static/.gitkeep is committed). GW_GODOT overrides
# the pinned binary (conftest idiom). Reproducible: same file set + same
# index.html sha256 from a clean static/ (pck byte-identity not asserted).
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT="${GW_GODOT:-/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64}"
mkdir -p "$REPO/static"
"$GODOT" --headless --path "$REPO/godot" --export-release Web \
    "$REPO/static/index.html"
