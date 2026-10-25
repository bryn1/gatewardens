"""W5 bridge contract (MC 11274.1.12 / card 11304), per the pinned test
row: cfg html/head_include == "" + custom_html_shell = res://web_shell.
html; GW names present in web_shell.html AND main.gd (gwHost,
__gwSnapshot, GW_STATE); the retired-bridge names = 0 raw hits in the I8
scope; the F2-3 engine-bootstrap asserts (web_shell.html contains
$GODOT_URL + $GODOT_CONFIG + `new Engine` + <canvas) — the dead-shell
trap can never pass again; and the boot_probe leg via the conftest
engine tier: boot the REAL main flow headless on a temp user:// pre-
seeded through the shipped save_probe write leg (so from_save runs on a
REAL save), asserting BOOT-PROBE-OK + EMPTY stderr (the W4 parse-leg
ruling: stderr is the true signal, not the OK rows).

The I8 grep reuses the hygiene gate's OWN walk, name list and scope
(one mechanism per concern — never a second grep implementation; the
gate's shipped scope is godot/ server/ static/ + README.md, and this
leg mirrors it exactly).
"""

import json
import os
import sys
import tempfile

import pytest

import conftest
from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: walk, VS_NAMES, read)

CFG = repo_path("godot", "export_presets.cfg")
SHELL = repo_path("godot", "web_shell.html")
MAIN = repo_path("godot", "scripts", "main.gd")
BOOT_PROBE = "res://sim/boot_probe.gd"
SAVE_PROBE = "res://sim/save_probe.gd"

# The pinned GW bridge trio (I8 present-side); the retired names the
# 0-hit side mirrors live in hyg.VS_NAMES (one list, never a copy).
GW_NAMES = ("gwHost", "__gwSnapshot", "GW_STATE")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def test_export_preset_single_source_shell():
    cfg = read(CFG)
    assert 'html/head_include=""' in cfg, \
        "head_include must be EMPTY (F9 single source)"
    assert 'html/custom_html_shell="res://web_shell.html"' in cfg, \
        "custom_html_shell must point at res://web_shell.html (F2-3)"


def test_gw_names_present_in_shell_and_main():
    shell = read(SHELL)
    main = read(MAIN)
    for name in GW_NAMES:
        assert name in shell, "GW name %r missing in web_shell.html" % name
        assert name in main, "GW name %r missing in main.gd" % name


def test_retired_bridge_names_zero_raw_hits_in_i8_scope():
    hits = []
    all_exts = {""} | set(hyg.CODE_EXTS)
    for top in hyg.I8_DIRS:
        for path in hyg.walk(os.path.join(hyg.REPO, top), all_exts):
            text = hyg.read(path)
            for name in hyg.VS_NAMES:
                if name in text:
                    hits.append("%s:%s" % (hyg.rel(path), name))
    readme = os.path.join(hyg.REPO, "README.md")
    if os.path.isfile(readme):
        readme_text = hyg.read(readme)
        for name in hyg.VS_NAMES:
            if name in readme_text:
                hits.append("README.md:%s" % name)
    assert hits == [], "I8 rename incomplete: %r" % hits


def test_f2_3_shell_carries_engine_bootstrap():
    shell = read(SHELL)
    for token in ("$GODOT_URL", "$GODOT_CONFIG", "new Engine", "<canvas"):
        assert token in shell, \
            "F2-3 engine-bootstrap token %r missing from web_shell.html" \
            % token


# ---------- engine leg: boot probe over the real main flow ----------

def test_boot_probe_boots_main_flow_headless():
    if not os.path.exists(conftest.GODOT):
        pytest.skip("Godot binary not installed")
    conftest.ensure_class_cache()
    with tempfile.TemporaryDirectory() as home:
        seed = conftest.run_probe_script(SAVE_PROBE, ["write"], home)
        assert seed.returncode == 0, "save seed write rc=%d\n%s\n%s" % (
            seed.returncode, seed.stdout, seed.stderr)
        proc = conftest.run_probe_script(BOOT_PROBE, (), home)
        assert proc.returncode == 0, "boot probe rc=%d\n%s\n%s" % (
            proc.returncode, proc.stdout, proc.stderr)
        assert proc.stderr == "", \
            "boot leg stderr must be EMPTY (true signal):\n%s" % proc.stderr
        assert "BOOT-PROBE-OK" in proc.stdout, proc.stdout
        rows = [line for line in proc.stdout.splitlines()
                if line.startswith("BOOT-PROBE-SNAP ")]
        assert len(rows) == 1, proc.stdout
        snap = json.loads(rows[0][len("BOOT-PROBE-SNAP "):])
        # C5 shape on the hub boot + REAL from_save legs (the save
        # written above: +50 gold, -20 spent, one bank row, deck of 3).
        assert snap["schema"] == 1, snap
        assert snap["phase"] == "hub", snap
        assert snap["gold"] == 30, "from_save gold leg: %r" % snap
        assert snap["bank_count"] == 1, "from_save bank leg: %r" % snap
        assert len(snap["deck"]) == 3, "from_save deck leg: %r" % snap
        # Boot never mutates: no C13 write fires on boot, mirror at 0.
        assert snap["saved_ack"] == 0, \
            "boot must not spam save writes: %r" % snap
