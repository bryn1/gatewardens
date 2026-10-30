"""G5 build-confirm UX (v1.2.1, MC 11700 / V121-PLAN §1 G5 + §4 G5 card).

THE SHIPPED UX SWAP (declared by the plan; the W17f "panel press =
instant place at first free" copy RETIRED — docs/ARCHITECTURE.md row
rewritten the same commit, grep-to-zero in the wave log):
  - a tower/family button PRESS ARMS that row + sets the ghost on the
    first buildable slot — placement does NOT happen (defense count +
    green unchanged: the DoD negative leg);
  - ArrowLeft/ArrowRight (the EXISTING held-key relay, rising edge)
    cycle the ghost over placer.buildable();
  - MouseLeft CONFIRMS: places ONCE through the ONE m.place_defense
    site (count +1, green -cost, then DISARMED); a second press places
    nothing more;
  - MouseRight/Escape CANCEL (never place);
  - KeyM WHILE ARMED = the confirm route at the ghost slot; KeyM
    UNARMED = the legacy first-free instant place, UNCHANGED (pinned
    standing behavior, plan Rev 2 / DA A4.3 — the smoke/harness callers
    ride it untouched). Sim untouched (fixtures EMPTY, C-3).

ENGINE LEG: the shipped kit godot/sim/g5_build_confirm_probe.gd (new
sim kit per the card) boots the REAL mission and drives the real step
(5) pump (bridge on_key -> mission.step -> panel.poll, the smoke KeyM
idiom). Rows re-checked here with the green drop re-derived FROM
towers.json (no cost literal in this file).

PLANTED-RED: in-suite source mutations below (cancel-code removed ->
the cancel pins go RED; arm that also places -> the arm-no-place pins
go RED); the ENGINE transcripts (real .gd mutation + probe re-run, red
beside green) ride the wave log .audits/20261029-2100-v121-plan/
G5-wave.log per the card.
"""

import json
import os
import sys

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code greps)

PROBE = "res://sim/g5_build_confirm_probe.gd"
PANEL_GD = conftest.repo_path("godot", "scripts", "defense_panel.gd")
PLACER_GD = conftest.repo_path("godot", "scripts", "defense_placer.gd")
SCRIPTS_DIR = conftest.repo_path("godot", "scripts")

TOWERS = json.load(open(conftest.repo_path("godot", "data", "towers.json"),
                        encoding="utf-8"))
BY_ID = {row["id"]: int(row["base_cost"]) for row in TOWERS}
BALLISTA = BY_ID["ballista"]        # the class-winner the probe arms


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _rows(out, tag):
    return [ln for ln in out.splitlines() if ln.startswith(tag + " ")]


def _kv(line):
    return dict(x.split("=", 1) for x in line.split(" ")[1:])


def _body(text, header):
    start = text.index(header)
    rest = text[start + len(header):]
    end = rest.find("\nfunc ")
    return rest if end < 0 else rest[:end]


# ---------- engine tier: the shipped g5 kit, real relay, real step -----

def test_g5_build_confirm_engine_leg(tmp_path, class_cache):
    proc = conftest.run_probe_script(PROBE, (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "G5B-FAIL" not in out, out
    assert out.rstrip().endswith("G5B-OK"), out

    # ARM: press armed WITHOUT placing — on a fresh map the defense
    # count is still ZERO (the plan DoD negative leg) and the ghost sits
    # on the first buildable slot (index 0: nothing occupies anything).
    arm = _kv(_rows(out, "G5B-ARM")[0])
    assert arm["armed"] == "1" and arm["count"] == "0", arm
    assert int(arm["ghost"]) >= 0, arm

    # CYCLE: forward one buildable slot and back, over the shipped
    # buildable() list the probe itself walked.
    cyc = _kv(_rows(out, "G5B-CYCLE")[0])
    assert int(cyc["size"]) >= 2, cyc
    assert int(cyc["fwd"]) > int(arm["ghost"]), cyc
    assert cyc["back"] == arm["ghost"], cyc

    # LMB: placed ONCE, green drop EXACTLY the towers.json base_cost,
    # disarmed (ghost -1); the second press placed nothing more.
    lmb = _kv(_rows(out, "G5B-LMB")[0])
    assert lmb["count"] == "1" and lmb["armed"] == "0" \
        and lmb["ghost"] == "-1", lmb
    assert int(lmb["green_drop"]) == BALLISTA, \
        "confirm charged off the shipped base_cost: %s != %d" % (
            lmb["green_drop"], BALLISTA)
    assert _kv(_rows(out, "G5B-LMB2")[0])["count"] == "1", \
        "a second MouseLeft placed twice"

    # RMB: cancel — disarmed, ghost gone, still the ONE defense.
    rmb = _kv(_rows(out, "G5B-RMB")[0])
    assert rmb["armed"] == "0" and rmb["ghost"] == "-1" \
        and rmb["count"] == "1", rmb

    # KeyM armed placed AT the ghost slot; KeyM unarmed kept the legacy
    # first-free instant place (both legs assert in-probe; rows = the
    # count walk 2 -> 3 with the flags).
    ka = _kv(_rows(out, "G5B-KEYMA")[0])
    assert ka["count"] == "2" and ka["at_ghost"] == "1" \
        and ka["disarmed"] == "1", ka
    ku = _kv(_rows(out, "G5B-KEYMU")[0])
    assert ku["count"] == "3" and ku["first_free"] == "1" \
        and ku["armed"] == "0", ku


# ---------- source truth: the ONE site + the planned ghost callers -----

def _violations(panel_code):
    """The G5 mechanism pins over defense_panel.gd RAW text (the PRESS
    tokens are STRING literals — blank_code blanks strings, and here the
    strings ARE the mechanism; the shipped test_family_picker source pin
    reads raw text by the same precedent; comment prose never names the
    counted call sites, VERIFIED): the PRESS map carries the
    confirm/cancel codes beside the shipped three; the ghost API has
    EXACTLY its planned callers (set_ghost: the one arm; cancel_ghost:
    confirm-success + cancel; cycle_ghost: the arrow relay); placement
    still flows through place_id exactly ONCE, from _confirm — the arm
    route carries NO placement (the DoD negative, in-suite); the
    KeyM-UNARMED legacy route stays wired."""
    bad = []
    for token in ('"KeyM": "place"', '"MouseLeft": "confirm"',
                  '"MouseRight": "cancel"', '"Escape": "cancel"'):
        if token not in panel_code:
            bad.append("PRESS map lost %s" % token)
    if panel_code.count("set_ghost(") != 1:
        bad.append("set_ghost callers=%d (planned: 1 — the arm route)"
                   % panel_code.count("set_ghost("))
    if panel_code.count("cancel_ghost(") != 2:
        bad.append("cancel_ghost callers=%d (planned: 2 — confirm + "
                   "cancel)" % panel_code.count("cancel_ghost("))
    if panel_code.count("cycle_ghost(") != 1:
        bad.append("cycle_ghost callers=%d (planned: 1 — the arrow "
                   "relay)" % panel_code.count("cycle_ghost("))
    if panel_code.count("placer.place_id(") != 1:
        bad.append("place_id calls=%d (planned: 1 — _confirm only)"
                   % panel_code.count("placer.place_id("))
    arm_body = _body(panel_code, "func _arm(tower_id: String) -> void:")
    # comment lines stripped: the slice runs up to the NEXT def, and
    # _confirm's prose naming place_id must not false-flip this negative
    arm_code = "\n".join(ln for ln in arm_body.splitlines()
                         if not ln.lstrip().startswith("#"))
    if "place_id" in arm_code or "place_selected" in arm_code:
        bad.append("the ARM route places (press must arm, not place)")
    hp_body = _body(panel_code, "func handle_press(code: String) -> void:")
    if "place_selected()" not in hp_body:
        bad.append("KeyM-unarmed legacy route detached (place_selected)")
    ga_body = _body(panel_code, "func _ghost_arrows() -> void:")
    if "armed" not in ga_body or "held" not in ga_body:
        bad.append("the arrow cycle left the held relay / armed gate")
    return bad


def test_g5_panel_source_truth():
    bad = _violations(read(PANEL_GD))
    assert not bad, "defense_panel.gd lost the G5 build-confirm " \
                    "mechanism: %r" % bad


def test_g5_one_place_site_source_truth():
    """The DoD contract grep: the whole production scripts/ tree calls
    m.place_defense( from EXACTLY one place (the placer's confirm
    route), and place_id resolves the ghost INSIDE it."""
    hits = []
    for name in sorted(os.listdir(SCRIPTS_DIR)):
        if name.endswith(".gd"):
            text = hyg.blank_code(read(os.path.join(SCRIPTS_DIR, name)),
                                 "gd")
            if "m.place_defense(" in text:
                hits.append(name)
    assert hits == ["defense_placer.gd"], \
        "the ONE application site grew a second caller: %r" % hits
    body = _body(hyg.blank_code(read(PLACER_GD), "gd"),
                 "func place_id(tower_id: String, ")
    assert "at = ghost" in body, "place_id must resolve the armed ghost"


# ---------- planted-red: the mechanism gates prove they can fail --------

def test_g5_planted_red_cancel_removed_goes_red():
    code = read(PANEL_GD)
    planted = code.replace('"MouseRight": "cancel",', "")
    bad = _violations(planted)
    assert bad, "planted-red: RMB cancel removed slipped the source gate"


def test_g5_planted_red_arm_also_places_goes_red():
    code = read(PANEL_GD)
    planted = code.replace(
        "placer.set_ghost(placer.first_free())",
        "placer.place_id(armed_id, 1)")
    bad = _violations(planted)
    assert bad, "planted-red: an arm that also places slipped the gate"


# ---------- served-path tier: the REAL main.gd forwarder + web dedup ----
# The served-browser retest (orchestrator, 19715d4 export) reached what
# direct on_key injection could not: on web EVERY physical key arrives
# at GWBridge.on_key TWICE (the shell's JS keydown/keyup relay AND
# Godot's own canvas pipeline via main.gd's _unhandled_input) — served
# measurement: ONE KeyM press placed TWO. The shipped kit
# godot/sim/g5_real_relay_probe.gd now boots the real mission, mounts
# the real main.gd script as the relay object and feeds it SYNTHESIZED
# InputEventKey/InputEventMouseButton (+ the JS entry _on_js_key):
# the closest production analogue runnable under -s.

RELAY_PROBE = "res://sim/g5_real_relay_probe.gd"
RELAY_GD = conftest.repo_path("godot", "sim", "g5_real_relay_probe.gd")
BRIDGE_GD = conftest.repo_path("godot", "scripts", "bridge.gd")


def test_g5_real_relay_engine_leg(tmp_path, class_cache):
    proc = conftest.run_probe_script(RELAY_PROBE, (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "G5R-FAIL" not in out, out
    assert out.rstrip().endswith("G5R-OK"), out
    kv = {ln.split(" ")[0]: _kv(ln) for ln in out.splitlines()
          if ln.startswith("G5R-")}
    assert kv["G5R-ARM"]["armed"] == "1" and kv["G5R-ARM"]["count"] == "0"
    keym = kv["G5R-KEYM"]
    assert keym["count"] == "1" and keym["disarmed"] == "1", keym
    assert int(keym["green_drop"]) == BALLISTA, keym   # data-derived cost
    # ONE physical press, BOTH live feeds (JS relay + engine pipeline):
    # exactly ONE place — the served double-feed gate.
    assert kv["G5R-DEDUP"]["placed"] == "1", kv["G5R-DEDUP"]
    lmb = kv["G5R-LMB"]
    assert lmb["count"] == "3" and lmb["disarmed"] == "1" \
        and lmb["ghost"] == "-1" and int(lmb["green_drop"]) == BALLISTA, lmb
    assert kv["G5R-RMB"]["armed"] == "0" and kv["G5R-RMB"]["ghost"] == "-1" \
        and kv["G5R-RMB"]["count"] == "3", kv["G5R-RMB"]
    assert int(kv["G5R-CYCLE"]["fwd"]) >= 0, kv["G5R-CYCLE"]
    # combat locks the rows WHILE AFFORDABLE and nothing places;
    # build unlocks them again (the served silent-refusal trap's gate).
    assert kv["G5R-LOCK"]["disabled"] == "1" \
        and kv["G5R-LOCK"]["armed"] == "0" \
        and kv["G5R-LOCK"]["placed"] == "0", kv["G5R-LOCK"]
    assert kv["G5R-UNLOCK"]["disabled"] == "0" \
        and kv["G5R-UNLOCK"]["armed"] == "1", kv["G5R-UNLOCK"]


def test_g5_planted_red_web_doublefeed_goes_red(tmp_path, class_cache):
    """LEGACY-BRIDGE plant: emulate on_key WITHOUT the edge guard (the
    pre-fix down path: held set + press appended unconditionally) by
    replacing the JS-relay line in a copy of the shipped kit — the DEDUP
    leg MUST go RED (two places from one physical press)."""
    src = read(RELAY_GD).replace(
        '_main._on_js_key(["KeyM", true])',
        '_m.bridge.held["KeyM"] = true\n\t_m.bridge.presses.append("KeyM")')
    assert src != read(RELAY_GD), "plant anchor lost"
    probe = tmp_path / "g5_relay_legacy.gd"
    probe.write_text(src, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), (), tmp_path)
    assert proc.returncode == 1, \
        "planted-red: an unguarded double feed slipped the DEDUP leg\n%s" \
        % proc.stdout
    assert "G5R-FAIL DEDUP" in proc.stdout, proc.stdout


# ---------- source truth: the edge guard + the combat lock -------------

def _bridge_body(text):
    return _body(text, "func on_key(code: String, down: bool) -> void:")


def test_g5_dedup_and_lock_source_truth():
    bad = []
    bbody = _bridge_body(read(BRIDGE_GD))
    if "held.has(code)" not in bbody or "presses.append" not in bbody:
        bad.append("bridge.on_key lost the rising-edge guard "
                   "(web double-feed re-opens)")
    sbody = _body(read(PANEL_GD), "func sync() -> void:")
    if "locked or not SIM_ECONOMY.can_afford(" not in sbody \
            or "_cancel_arm()" not in sbody:
        bad.append("panel.sync lost the combat phase-lock (rows arm into "
                   "combat and silently refuse)")
    assert not bad, "served-path gates lost: %r" % bad


def test_g5_planted_red_dedup_guard_removed_goes_red():
    code = read(BRIDGE_GD)
    planted = code.replace("if held.has(code):", "if false:")
    body = _bridge_body(planted)
    assert "held.has(code)" not in body, \
        "plant missed the on_key body"


def test_g5_planted_red_lock_removed_goes_red():
    code = read(PANEL_GD)
    planted = code.replace("btn.disabled = locked or not "
                           "SIM_ECONOMY.can_afford(",
                           "btn.disabled = not SIM_ECONOMY.can_afford(")
    sbody = _body(planted, "func sync() -> void:")
    assert "locked or not SIM_ECONOMY.can_afford(" not in sbody, \
        "plant missed sync()"
    # the source-truth gate must notice (cancel route still present,
    # so the gate keys on the disabled condition):
    bad = []
    if "locked or not SIM_ECONOMY.can_afford(" not in sbody \
            or "_cancel_arm()" not in sbody:
        bad.append("lock")
    assert bad, "planted-red: lock removal slipped the source gate"
