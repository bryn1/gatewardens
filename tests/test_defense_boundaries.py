"""W11b — defense_placer lifecycle boundary legs (MC 11274.1.20 / card
11330). P2 (LEDGER "Findings open", W11-discovered): upgrade()/repair()
crashed under -s on unknown uids — the not-found sentinel is NON-empty,
so the old rec.is_empty() guard never fired and rec["obj"] was a SCRIPT
ERROR. sell() already had the correct shape; the fix matches it.

Two tiers, one idiom per repo (test_hub/test_mission_smoke precedent):
- ENGINE: the boundary probe (embedded below, written to tmp_path at
  runtime) boots the REAL mission under `-s` and drives the shipped
  placer: upgrade(unknown)/repair(unknown) refused with green + the
  live tower's tier + defense_list count UNCHANGED; a sold uid rides the
  same not-found path; the known-good upgrade still works (the fix must
  not silently disable the path). rc 0 + EMPTY stderr (W4 ruling: stderr
  is the true parse/crash signal — the unfixed placer fails exactly
  here, RED transcript on the card) + machine-row numbers re-derived
  from the shipped data files, never from literals here.
- SOURCE TRUTH (no engine): the shipped upgrade()/repair() bodies carry
  the sentinel handling (no bare is_empty() guard can reappear as the
  not-found gate). Shipped planted-red: the same matcher over an
  in-memory copy with the OLD broken guard restored MUST report red.

Readings (R-list, card trail):
- R1 PINNED Modules row (docs/ARCHITECTURE.md): "scripts/
  defense_placer.gd | build-phase placement: ghost, validity
  (range/overlap), confirm/cancel, cost via SimEconomy | validity from
  injected tables; calls mission.place_defense" — it pins the
  interface, not a per-method refusal value, so the pinned refusal
  shape is the shipped sell() one (R2).
- R2 Shipped sell() not-found return is {"ok": false, "why": "uid"} —
  the governing refusal value. _rec ALREADY returns exactly that; only
  the guard was wrong, so the fix is the guard (one mechanism, no new
  sentinel).
- R3 Sold-then-used leg is allowed by the record shape: sell() REMOVES
  the record from m.defense_list (shipped), so the sold uid hits the
  same not-found path — asserted refused, green unchanged.
- R4 Found records are {uid, obj, tick} (mission.place_defense) and
  carry NO "ok" key; the refusal does — rec.has("obj") guards the
  routing without inventing a second sentinel.
- R5 The probe is generated into tmp_path from this file (absolute `-s`
  path; preload resolves res:// inside the --path project — verified):
  the W11b file constraint is defense_placer.gd + tests/ + evidence,
  so the godot/sim/ probe home cannot take a new file.
- R6 E3/E5 honored: failure paths early-return; _ready/setup are driven
  directly under -s.
"""

import json
import os
import re

import conftest

ECONOMY = json.load(open(conftest.repo_path("godot", "data", "economy.json"),
                         encoding="utf-8"))
TOWERS = json.load(open(conftest.repo_path("godot", "data", "towers.json"),
                        encoding="utf-8"))
GATEFALL = json.load(open(conftest.repo_path("godot", "data", "maps",
                                             "gatefall.json"),
                          encoding="utf-8"))
TOWER_BASE_COST = next(int(r["base_cost"]) for r in TOWERS
                       if r["class"] == "tower")
START_GREEN = int(GATEFALL["start_green"])

PLACER_GD = conftest.repo_path("godot", "scripts", "defense_placer.gd")

# The boundary probe, verbatim (R5). Machine rows are asserted here;
# every refusal is checked IN-PROBE too, so a failure prints a named
# BOUND FAIL row and quits 1 before the stderr leg even matters.
PROBE_SRC = '''\
# defense_boundaries probe — W11b P2 fix (MC 11274.1.20 / card 11330).
# Test asset under -s (boot_probe/mission_smoke precedent, E5: _ready
# and setup driven directly). E3: quit() does not abort the running
# frame — failure paths early-return. Rows (pytest re-derives numbers):
#   BOUND-PLACE ok=1 uid=<u> green=<g>       (live tower, green down by base_cost)
#   BOUND-UPG-UNKNOWN ok=0 why=<w> green=<g> tier=<t>  (refused, no state change)
#   BOUND-REP-UNKNOWN ok=0 why=<w> green=<g> tier=<t>
#   BOUND-UPG-OK ok=1 cost=<c> green=<g> tier=<t>      (positive control)
#   BOUND-SELL ok=1 refund=<r> green=<g>     (record removed)
#   BOUND-UPG-SOLD ok=0 why=<w> green=<g>    (sold-then-used, R3)
#   BOUND-REP-SOLD ok=0 why=<w> green=<g>
#   BOUND-OK
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DEF_PLACER := preload("res://scripts/defense_placer.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const UNKNOWN_UID := 999999


func _init() -> void:
\tvar tables = GW_TABLES.new("res://data")
\tvar graph: Dictionary = GW_COMPOSE.build_graph(tables)
\tvar state = graph["state"]
\tstate.set_deck(DECK.duplicate())
\tvar packed = ResourceLoader.load(MISSION_SCENE)
\tif packed == null:
\t\t_fail("mission.tscn not loadable")
\t\treturn
\tvar m = packed.instantiate()
\troot.add_child(m)
\tm._ready()
\tvar rng := RandomNumberGenerator.new()
\trng.seed = 11330
\tm.setup(tables, state, graph["save"], graph["bridge"], "gatefall", "normal", rng)
\tvar placer = DEF_PLACER.new()
\tplacer.setup(m)
\tvar slot := placer.first_free()
\tvar pres := placer.place("tower", 1, slot)
\tif not bool(pres.get("ok", false)):
\t\t_fail("place: %s" % str(pres))
\t\treturn
\tvar uid := int(pres["uid"])
\tprint("BOUND-PLACE ok=1 uid=%d green=%d" % [uid, int(m.green)])
\tvar g0 := int(m.green)
\tvar live = _live_obj(m)
\tvar t0 := int(live.tier)
\tvar ures: Dictionary = placer.upgrade(UNKNOWN_UID)
\tprint("BOUND-UPG-UNKNOWN ok=%d why=%s green=%d tier=%d" % [
\t\t\t0 if _refused(ures) else 1, String(ures.get("why", "")),
\t\t\tint(m.green), int(live.tier)])
\tif not _refused(ures) or int(m.green) != g0 \\
\t\t\tor int(live.tier) != t0 or m.defense_list.size() != 1:
\t\t_fail("UPG-UNKNOWN %s green=%d tier=%d count=%d" % [
\t\t\t\tstr(ures), int(m.green), int(live.tier), m.defense_list.size()])
\t\treturn
\tvar rres: Dictionary = placer.repair(UNKNOWN_UID)
\tprint("BOUND-REP-UNKNOWN ok=%d why=%s green=%d tier=%d" % [
\t\t\t0 if _refused(rres) else 1, String(rres.get("why", "")),
\t\t\tint(m.green), int(live.tier)])
\tif not _refused(rres) or int(m.green) != g0 \\
\t\t\tor int(live.tier) != t0 or m.defense_list.size() != 1:
\t\t_fail("REP-UNKNOWN %s green=%d tier=%d count=%d" % [
\t\t\t\tstr(rres), int(m.green), int(live.tier), m.defense_list.size()])
\t\treturn
\tvar ures2: Dictionary = placer.upgrade(uid)
\tprint("BOUND-UPG-OK ok=%d cost=%d green=%d tier=%d" % [
\t\t\t1 if bool(ures2.get("ok", false)) else 0,
\t\t\tint(ures2.get("cost", -1)), int(m.green), int(live.tier)])
\tif not bool(ures2.get("ok", false)) \\
\t\t\tor int(m.green) != g0 - int(ures2.get("cost", 0)):
\t\t_fail("UPG-OK %s green=%d" % [str(ures2), int(m.green)])
\t\treturn
\tvar sres: Dictionary = placer.sell(uid)
\tif not bool(sres.get("ok", false)) or m.defense_list.size() != 0:
\t\t_fail("SELL %s count=%d" % [str(sres), m.defense_list.size()])
\t\treturn
\tvar g1 := int(m.green)
\tprint("BOUND-SELL ok=1 refund=%d green=%d" % [
\t\t\tint(sres.get("refund", 0)), g1])
\tvar ures3: Dictionary = placer.upgrade(uid)
\tprint("BOUND-UPG-SOLD ok=%d why=%s green=%d" % [
\t\t\t0 if _refused(ures3) else 1, String(ures3.get("why", "")),
\t\t\tint(m.green)])
\tif not _refused(ures3) or int(m.green) != g1:
\t\t_fail("UPG-SOLD %s green=%d" % [str(ures3), int(m.green)])
\t\treturn
\tvar rres2: Dictionary = placer.repair(uid)
\tprint("BOUND-REP-SOLD ok=%d why=%s green=%d" % [
\t\t\t0 if _refused(rres2) else 1, String(rres2.get("why", "")),
\t\t\tint(m.green)])
\tif not _refused(rres2) or int(m.green) != g1:
\t\t_fail("REP-SOLD %s green=%d" % [str(rres2), int(m.green)])
\t\treturn
\tprint("BOUND-OK")
\tquit(0)


func _refused(res: Dictionary) -> bool:
\treturn not bool(res.get("ok", true)) and String(res.get("why", "")) == "uid"


func _live_obj(m):
\treturn (m.defense_list[0] as Dictionary)["obj"]


func _fail(why: String) -> void:
\tprint("BOUND FAIL " + why)
\tquit(1)
'''


def _rows(out, tag):
    hits = [line for line in out.splitlines() if line.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), out)
    return dict(kv.split("=", 1) for kv in hits[0].split(" ")[1:])


def check_rows(out):
    """All machine-row asserts, over probe stdout. Shared with the
    planted-red leg: the SAME checks must reject a mutated row set."""
    place = _rows(out, "BOUND-PLACE")
    assert place["ok"] == "1", place
    # place charged EXACTLY towers.json base_cost off start_green.
    assert int(place["green"]) == START_GREEN - TOWER_BASE_COST, place
    uid = int(place["uid"])
    assert uid > 0, place

    upg_u = _rows(out, "BOUND-UPG-UNKNOWN")
    rep_u = _rows(out, "BOUND-REP-UNKNOWN")
    # Refusal per the shipped sell() shape (R2), green + tier untouched.
    for row in (upg_u, rep_u):
        assert row["ok"] == "0" and row["why"] == "uid", row
        assert int(row["green"]) == int(place["green"]), row
    assert upg_u["tier"] == rep_u["tier"], (upg_u, rep_u)

    upg_ok = _rows(out, "BOUND-UPG-OK")
    # Positive control: the known-good path still runs, priced by the
    # pinned C3 ladder base x ratios[0] (T1->T2), green drops exactly it.
    want_cost = round(TOWER_BASE_COST * float(ECONOMY["upgrade_ratios"][0]))
    assert upg_ok["ok"] == "1", upg_ok
    assert int(upg_ok["cost"]) == want_cost, upg_ok
    assert int(upg_ok["green"]) == int(place["green"]) - want_cost, upg_ok
    assert int(upg_ok["tier"]) == int(upg_u["tier"]) + 1, upg_ok

    sell = _rows(out, "BOUND-SELL")
    assert sell["ok"] == "1", sell
    # Healthy (full-hp) defense: sell = total_spent x sell_ratio x 0 = 0
    # (R1 pinned formula; the non-zero refund path is mission_smoke's).
    assert int(sell["refund"]) == 0, sell
    assert int(sell["green"]) == int(upg_ok["green"]) + int(sell["refund"]), \
        sell

    for tag in ("BOUND-UPG-SOLD", "BOUND-REP-SOLD"):
        row = _rows(out, tag)
        assert row["ok"] == "0" and row["why"] == "uid", row
        assert int(row["green"]) == int(sell["green"]), row

    assert "BOUND-OK" in out.splitlines(), out


def test_placer_boundaries_engine_leg(tmp_path, class_cache):
    probe = tmp_path / "defense_boundaries_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal; the " \
        "unfixed placer fails HERE):\n%s" % proc.stderr
    assert "BOUND FAIL" not in proc.stdout, proc.stdout
    check_rows(proc.stdout)


def _lifecycle_body(text, name):
    m = re.search(r"func %s\(uid: int\) -> Dictionary:\n(.*?)(?=\n(?:@|func|var) )"
                  % name, text + "\nfunc var_sentinel() -> void:\n\tpass\n",
                  re.S)
    assert m, "defense_placer.gd exposes no func %s(uid: int)" % name
    return m.group(1)


def placer_guard_ok(text):
    """Source truth: both lifecycle routes gate the not-found refusal
    structurally (has("obj"), R4) — a bare is_empty() gate on the _rec
    result can never fire (that WAS the bug)."""
    ok = True
    for name in ("upgrade", "repair"):
        body = _lifecycle_body(text, name)
        if re.search(r"_rec\(uid\)[\s\S]{0,80}?is_empty\(\)", body):
            ok = False
        if 'has("obj")' not in body:
            ok = False
    return ok


def test_sentinel_guard_source_truth_with_planted_red():
    with open(PLACER_GD, encoding="utf-8") as fh:
        text = fh.read()
    assert placer_guard_ok(text), \
        "upgrade/repair must refuse via the not-found sentinel shape"
    # Shipped planted-red: restore the OLD broken guard in an in-memory
    # copy — the gate MUST report red (no file is touched).
    broken = text.replace(
        '\tif not rec.has("obj"):\n\t\treturn rec\n\treturn (rec["obj"]'
        ' as RefCounted).upgrade()',
        '\treturn rec if rec.is_empty() else (rec["obj"]'
        ' as RefCounted).upgrade()')
    assert broken != text, "planted-red anchor drifted — update this leg"
    assert not placer_guard_ok(broken), \
        "gate stayed green on the restored broken guard"


def test_probe_home_stays_outside_shipped_tree():
    # R5 bookkeeping: the probe is generated at runtime, so nothing W11b
    # added may squat under godot/ — the shipped probe homes are frozen.
    assert not os.path.exists(conftest.repo_path(
        "godot", "sim", "defense_boundaries_probe.gd"))
