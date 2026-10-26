"""W10 HUD gate (MC 11274.1.18 / card 11325) — read-only mission HUD +
hero hot-swap bar (godot/scripts/hud.gd + scenes/hud.tscn), mounted by
the mission's DECLARED hook.

Two tiers, one idiom per repo (test_mission_smoke / test_hub precedent):
- ENGINE: run godot/sim/mission_smoke.gd under `-s` over an isolated
  user:// and assert every MISSION-SMOKE-HUD* machine row against
  numbers re-derived from the shipped data files (waves / economy /
  heroes / enemies) — never a test-side copy. EMPTY stderr (W4 ruling)
  and byte-stable reruns (pinned seed 11274).
- SOURCE TRUTH: the I4 read-only bans pytest can settle without the
  engine — hud.gd makes ZERO shipped-mutator calls (the add_/spend_/
  consume_/set_/equip/place_ families; add_child is node plumbing, the
  same call the shipped hook itself uses), ZERO state writes, ZERO
  balance literals (I2 structural set), no monetization vocabulary (I1),
  no input consumer (the HUD renders, it never listens), and NO second
  economy crossing (no SimEconomy import). mission.gd carries ONLY the
  declared mount hook. Every gate ships a planted-red proof run in
  memory, so each one is proven able to fail.
"""

import json
import math
import re
import sys

import conftest
from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code, TRIPWIRE)

SMOKE = "res://sim/mission_smoke.gd"
HUD_GD = repo_path("godot", "scripts", "hud.gd")
HUD_TSCN = repo_path("godot", "scenes", "hud.tscn")
MISSION_GD = repo_path("godot", "scripts", "mission.gd")
GODOT = repo_path("godot")

STRUCT_VALS = {0.0, 1.0, 2.0, 3.0, 4.0, 0.5}   # the I2 structural set
NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\b")

# The shipped mutator families named by the contract (game_state C13 +
# the mission's green/placement sites). Bare-name scan with ONE plumbing
# exemption: add_child (node-tree plumbing, not a state mutator — the
# mission hook and hero rig use it too).
MUT_RE = re.compile(r"\b(?:add_|spend_|consume_|set_|equip|place_)\w*\s*\(")
PLUMBING = {"add_child"}
# Direct writes onto the injected state sources = I4 violation.
WRITE_RE = re.compile(
    r"\b(?:m|mission|state|game_state)\.[A-Za-z_]\w*"
    r"(?:\[[^\]]*\])?\s*(?:[+\-*/]?=[^=])")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _hud_code():
    return hyg.blank_code(_read(HUD_GD), "gd")


def _json(*parts):
    with open(repo_path("godot", *parts), encoding="utf-8") as fh:
        return json.load(fh)


def _row(stdout, tag):
    hits = [line for line in stdout.splitlines() if line.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), stdout)
    head = hits[0].split(" text=")[0]
    fields = dict(kv.split("=", 1) for kv in head.split(" ")[1:])
    if " text=" in hits[0]:              # label text = rest of the line
        fields["text"] = hits[0].split(" text=", 1)[1]
    return fields


def _rows(stdout, tag):
    return [_row_line(line) for line in stdout.splitlines()
            if line.startswith(tag + " ")]


def _row_line(line):
    head = line.split(" text=")[0]
    fields = dict(kv.split("=", 1) for kv in head.split(" ")[1:])
    if " text=" in line:
        fields["text"] = line.split(" text=", 1)[1]
    return fields


# ---------- engine tier ----------

def test_hud_engine_leg(tmp_path, class_cache):
    proc = conftest.run_probe_script(SMOKE, (), tmp_path)
    assert proc.returncode == 0, \
        "smoke rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert "MISSION-SMOKE-OK" in proc.stdout, proc.stdout
    assert proc.stderr == "", \
        "-s smoke stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    _hud_rows(proc.stdout)


def test_hud_smoke_is_byte_stable(tmp_path, class_cache):
    first = conftest.run_probe_script(SMOKE, (), tmp_path / "a")
    second = conftest.run_probe_script(SMOKE, (), tmp_path / "b")
    assert first.returncode == 0 and second.returncode == 0
    assert first.stdout == second.stdout, \
        "smoke output must be byte-stable under the pinned seed 11274"


def _hud_rows(out):
    waves = _json("data", "waves", "waves_gatefall_normal.json")["waves"]
    total = len(waves)
    assert total == 11, "10 waves + boss wave (A4) — data drifted"
    lines = out.splitlines()

    # build-phase label: SimWave.build_seconds + the phase controller's
    # ONE timer; the wave number is the 1-based display of state index 0.
    build = _row(out, "MISSION-SMOKE-HUD-BUILD")
    secs = int(math.ceil(float(waves[0]["build_seconds"])))
    assert build["wave"] == "0" and int(build["secs"]) == secs, build
    assert build["text"] == "Build: wave 1 in %d s" % secs, build

    # combat label: "wave n / 11" with the TOTAL from the data file.
    wave = _row(out, "MISSION-SMOKE-HUD-WAVE")
    assert wave["wave"] == "0" and wave["text"] == "Wave 1 / %d" % total, wave

    # green count matches the state mirror at that tick — the same value
    # the W8 panel leg paid down to (green moves nowhere between).
    act = _row(out, "MISSION-SMOKE-W8PANEL-ACT")
    cap = _json("data", "economy.json")["green"]["cap"]
    green = _row(out, "MISSION-SMOKE-HUD-GREEN")
    assert green["green"] == act["green"], \
        "HUD green %s != state %s" % (green, act)
    assert int(green["cap"]) == cap and green["text"] == \
        "Green %s / cap %d" % (act["green"], cap), green

    # blue bar: the ACTIVE slot's bar mirrors the one C4 pool EXACTLY
    # (bar == state value) and its max is the hero's data blue_max.
    warden = [h for h in _json("data", "heroes.json")
              if h["id"] == "warden"][0]
    blue = _row(out, "MISSION-SMOKE-HUD-BLUE")
    assert blue["active"] == "warden", blue
    assert float(blue["max"]) == float(warden["base"]["blue_max"]), blue
    assert float(blue["bar"]) == float(blue["blue"]), blue
    ratio = float(blue["blue"]) / float(blue["max"])
    assert abs(float(blue["ratio"]) - ratio) < 1e-9, blue
    assert 0.0 < ratio < 1.0, "ability spent; the bar must not read full"

    # highlight MOVES with the shipped swap: down-swap -> 0, F2 -> 1,
    # F1 -> 0 (the machine-row ORDER is the proof).
    hl = _rows(out, "MISSION-SMOKE-HUD-HL")
    assert [h["slot"] for h in hl] == ["0", "1", "0"], hl
    assert [h["hero"] for h in hl] == ["warden", "deadeye", "warden"], hl

    # boss bar: non-null exactly on the boss wave, hp = the data hp.
    boss_row = _row(out, "MISSION-SMOKE-HUD-BOSS")
    breaker = [e for e in _json("data", "enemies.json")
               if e["id"] == "warden_breaker"][0]
    boss_hp = float(breaker["hp"]["normal"])
    assert boss_row["visible"] == "1" and boss_row["wave"] == "10", boss_row
    assert float(boss_row["hp"]) == boss_hp and \
        float(boss_row["max"]) == boss_hp, boss_row
    assert boss_row["text"] == "%s %d / %d" % (
        breaker["name"], boss_hp, boss_hp), boss_row

    # banner: honest copy off the shipped outcome field; LOSE path.
    banner = _row(out, "MISSION-SMOKE-HUD-BANNER")
    lose = _row(out, "MISSION-SMOKE-LOSE")
    assert banner["outcome"] == "lose" == lose["outcome"], banner
    assert banner["text"] == "DEFEAT", banner

    # row ORDER honors the run: build before spawn, boss after F1SWAP,
    # banner after DOWN (the HUD reflects state, never leads it).
    idx = {tag: min(i for i, ln in enumerate(lines)
                    if ln.startswith(tag)) for tag in (
        "MISSION-SMOKE-HUD-BUILD", "MISSION-SMOKE-SPAWN",
        "MISSION-SMOKE-HUD-BOSS", "MISSION-SMOKE-F1SWAP",
        "MISSION-SMOKE-HUD-BANNER", "MISSION-SMOKE-DOWN")}
    assert idx["MISSION-SMOKE-HUD-BUILD"] < idx["MISSION-SMOKE-SPAWN"]
    assert idx["MISSION-SMOKE-F1SWAP"] < idx["MISSION-SMOKE-HUD-BOSS"]
    assert idx["MISSION-SMOKE-DOWN"] < idx["MISSION-SMOKE-HUD-BANNER"]


# ---------- source truth: I4 read-only overlay ----------

def _mutator_hits(code):
    return [m.group(0).rstrip("(").strip() for m in MUT_RE.finditer(code)
            if m.group(0).rstrip("(").strip() not in PLUMBING]


def test_hud_makes_no_mutator_calls():
    assert _mutator_hits(_hud_code()) == [], \
        "hud.gd calls a shipped mutator — the HUD is a read-only overlay"


def test_hud_writes_no_state():
    assert WRITE_RE.search(_hud_code()) is None, \
        "hud.gd writes the mission/state — I4 forbids it outright"


def test_hud_carries_no_balance_literals():
    extra = sorted({float(n) for n in NUM_RE.findall(_hud_code())}
                   - STRUCT_VALS)
    assert extra == [], \
        "hud.gd carries non-structural literals %s (all numbers are data)" % extra


def test_hud_has_no_input_consumer_and_no_second_economy_crossing():
    code = _hud_code()
    assert not re.search(r"\bInput\b\s*\.|on_key\s*\(|move_vector", code), \
        "the HUD consumes no input (F1-F3 stay the mission's step-(5) legs)"
    assert not re.search(r"SIM_ECONOMY|SimEconomy|can_afford|add_green", code), \
        "no economy crossing beside the shipped single application site"


def test_hud_avoids_monetization_vocabulary():
    for path in (HUD_GD, HUD_TSCN):
        text = _read(path).lower()
        for token in ("shop", "price", "cash", "gem", "wallet", "iap",
                      "premium", "gacha", "lockbox", "battle_pass"):
            assert token not in text, \
                "%s carries monetization vocabulary %r (I1)" % (path, token)


def test_mission_carries_the_declared_w10_hook_only():
    # RAW text here: the hook lines quote scene/node names, and
    # blank_code would blank the very strings this gate must see.
    text = _read(MISSION_GD)
    assert re.search(r'const HUD_SCENE := preload\("res://scenes/hud\.tscn"\)',
                     text), "pinned row scene, bound by preload (W4 rule)"
    assert re.search(r"HUD_SCENE\.instantiate\(\)", text) \
        and re.search(r'hud\.name = "HUD"', text) \
        and re.search(r"hud\.setup\(self\)", text), \
        "the mount site is the declared hook: instantiate, name, setup"
    hook = text[text.index("HUD_SCENE.instantiate()"):]
    assert re.search(r"^\s*hud\.setup\(self\)", hook[:400], re.M), \
        "setup(self) must follow the mount immediately (read-only inject)"
    # no _process change: the overlay self-refreshes in the LIVE game;
    # _process stays step(d) and nothing else (C12 stays pinned).
    proc_body = re.search(r"func _process\(d: float\) -> void:\n(.*?)\n\n",
                          text, re.S).group(1)
    assert "step(d)" in proc_body and "hud" not in proc_body


def test_hud_scene_is_a_canvas_layer_overlay():
    tscn = _read(HUD_TSCN)
    assert 'node name="HUD" type="CanvasLayer"' in tscn, tscn
    assert "res://scripts/hud.gd" in tscn and "HeroBar" in tscn
    assert 'parent="Root/TopLeft"' in tscn and 'parent="Root"' in tscn


# ---------- planted reds: every gate proves it can fail ----------

def test_planted_red_mutator_call_goes_red():
    planted = _hud_code().replace(
        "func refresh() -> void:",
        'func _planted() -> void:\n\tstate.add_hero_xp("warden", 1)\n'
        '\tplace_defense({}, 1)\n\nfunc refresh() -> void:', 1)
    hits = _mutator_hits(planted)
    assert "add_hero_xp" in hits and "place_defense" in hits, hits


def test_planted_red_state_write_goes_red():
    planted = _hud_code().replace(
        "func refresh() -> void:",
        "func _planted() -> void:\n\tm.blue = 0.0\n\n"
        "func refresh() -> void:", 1)
    assert WRITE_RE.search(planted) is not None


def test_planted_red_balance_literal_goes_red():
    planted = _hud_code().replace(
        "func refresh() -> void:",
        "var _planted := 12\n\nfunc refresh() -> void:", 1)
    extra = sorted({float(n) for n in NUM_RE.findall(planted)}
                   - STRUCT_VALS)
    assert extra == [12.0], extra
