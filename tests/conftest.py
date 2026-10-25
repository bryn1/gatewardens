"""Shared pytest helpers for Gatewardens.

Number-layer tests never touch the engine; engine-tier tests call
ensure_class_cache() first (F14): once per session Godot imports the
project so class_name scripts resolve under any later `-s` run. The
pinned binary is overridable with the GW_GODOT env var.
"""

import os
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GODOT = os.environ.get(
    "GW_GODOT",
    "/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64")


def repo_path(*parts):
    return os.path.join(REPO_ROOT, *parts)


_class_cache_ready = False


def ensure_class_cache():
    """`godot --headless --import godot/` exactly once per session (F14)."""
    global _class_cache_ready
    if _class_cache_ready:
        return
    proc = subprocess.run(
        [GODOT, "--headless", "--import", repo_path("godot")],
        capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(
            "godot --headless --import failed (%d):\n%s%s"
            % (proc.returncode, proc.stdout, proc.stderr))
    _class_cache_ready = True


@pytest.fixture(scope="session")
def class_cache():
    ensure_class_cache()
    return GODOT
