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


def run_probe_script(res_path, args=(), data_home=None, timeout=300):
    """One `-s` probe invocation: godot --headless --path godot/ -s
    <res_path> -- <args>. With data_home the desktop user:// redirect
    (XDG_DATA_HOME temp dir, the save_probe/BN4 idiom) is applied, so a
    probe never touches the developer's real save."""
    env = dict(os.environ)
    if data_home is not None:
        env["XDG_DATA_HOME"] = str(data_home)
    return subprocess.run(
        [GODOT, "--headless", "--path", repo_path("godot"),
         "-s", res_path, "--"] + list(args),
        capture_output=True, text=True, timeout=timeout, env=env)


@pytest.fixture(scope="session")
def class_cache():
    ensure_class_cache()
    return GODOT
