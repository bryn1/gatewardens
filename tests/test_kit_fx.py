"""v1.5 W-K kit-crossing presentation probe (MC 11876 / V15-PLAN-c2 §3
W-K) — engine matrix + structural source-truth pins. File history:
v1.4 P7 FINDING probe (MC 11857, V12-PLAN:297 debt) — the versioned
truth then was kit_presentation=NONE (pure state writers, fx_director
spawned ONLY from _observe_enemies/_observe_fires); its re-pin clause
("Any future kit presentation implementation MUST re-pin these rows —
it cannot false-green") is what this re-pin honors. The RE-PIN PROOF
(plan F-B leg 1) ran FIRST: the untouched old file on the new tree
went RED (probe KF-FAIL "sparks=2" rc1; per-assert driver: old
sparks_delta==0 RED). DECLARED honest reading: the old exact NONE-
string assert stays GREEN vacuously (its three print inputs are
structurally zero in the old probe) — the plan's §3 subclaim that
the string itself reddens is mechanically false; the full argument
and both transcripts stand in .audits/20261101-0843-v15-plan/
WK-wave.log (fleet law: nothing here rounds a RED up).

WHAT SHIPPED AT W-K (the new measured shape): fx_director._observe_kits
— an UNCONDITIONAL observer pass in fx_step (DA P1-B: kit assigns are
build-phase-only per mission_relics.gd:16, zero drops those frames, a
drops-guard would ship it dead) presenting relic_uid 0->uid crossings
with the ONE existing sheet (fx_spark_hit) through the ONE cap-
respecting _spawn_spark site. Unassign (uid->0) paints NOTHING —
symmetric poof DECLARED OUT (pinned by the KF-CAP una_sparks row).
Zero writer lines moved: _PRESENT_BAN leg untouched and green — the
observer-side proof (hard leg 5).

KIT NAMING (DoD "kits file + rows", reading DECLARED at v1.4, stands):
the kit data file is godot/data/items.json — 15 rows, the 3
slot=="relic" kits mark_of_fervor / orb_of_the_deep /
medallion_of_the_gate (the data leg below re-pins). mission.setup()
copies the bank's relic rows into the mission-local relic_pool
(mission.gd:149-151); the shipped writers are mission.assign_relic/
unassign_relic -> mission_relics (:15/:31, guards phase>uid>relic>
taken) -> defense_obj.assign_relic/clear_relic (:97/:102).

Legs (KF-* rows; in-probe KF-FAIL + quit(1) guards + KF-OK-LAST so a
silent skip cannot go green):
  KF-ASSIGN   assign kit -> state read back: relic_uid, bonuses
              hp:3.000 (items.json primary, scripted 3.0 F3-input),
              hp_max = tier hp + 3.0 EXACT, hp CLAMPED not healed
              (defense_obj :96), C5 mirror 1, pool 2 (C11 keeps).
  KF-PRESENT  v1.5 W-K shape: live 0 at assign (the observer is the
              painter), ONE hand-driven fx_step OBSERVES the crossing
              (kit live 1), the 2 s pump ends it; world node intact.
  KF-FINDING  re-declared shipped shape, exact string: fx_spark_hit,
              live 1 -> 0, sparks_delta 1, node unchanged.
  KF-CONTROL  non-vacuity on the SAME instrument + pump. Spark counter
              baseline RE-ANCHORED at the control start — since W-K
              the kit spark rides the shared spawned_sparks counter.
  KF-CAP      MAX_FX leg (plan §3 W-K): the cap is PLANTED with the
              shipped spawn site and DERIVED from behavior (fill 512,
              plateau cap; drop-past-cap observed, no literal); the
              same window pins una_sparks == 0 (uid->0 paints nothing
              — the DECLARED symmetric OUT).
  KF-STACK    stacking per the SHIPPED rule — one relic per defense:
              the second kit is REFUSED "taken" (mission_relics.gd:24),
              NOT replaced; state unmoved, ack delta 0.
  KF-INVALID  unknown kit uid -> refused "relic", state unmoved, ack 0.
  KF-UNASSIGN ok -> everything reverts (relic_uid 0, bonuses gone,
              hp_max back to the bare tier row, mirror 0, pool intact).
  KF-ACK      ZERO save writes across the whole matrix (boot ack 3 =
              set_deck + 2 bank_add, the shipped C13 seed writes).
  structural  dead-shape detector (the pass call is ONE one-tab line
              in fx_step; behind any guard it ships dead) + zero-write/
              cap-door source truth (no mutator, no injected write,
              ONE _spawn_spark site) + the UNMOVED _PRESENT_BAN leg.

F3 doctrine honored: NO duplicate legs — phase/uid refusals and the
same-relic DUP are already pinned by test_relic_negatives.py; this
file adds the presentation dimension, the CAP shape, the different-
kit STACK and the INVALID-kit-id gap only. PLANTED-REDs (transcripts
+ byte-verified reverts in .audits/20261101-0843-v15-plan/WK-wave.
log): (1) the W-K pass call deleted from fx_step -> KF-PRESENT RED;
(2) the pass behind a drops-guard (dead-shape, DA P1-B) -> KF-PRESENT
RED + structural detector RED. The v1.4 :24 taken-guard plant stands
in P7-wave.log as this file's first planted-red history.
"""

import json
import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for greps)

# Mutator/write shapes LOCAL per the repo rule (test_wave_telegraph
# home; no cross-test imports in tests/).
MUT_RE = re.compile(r"\b(?:add_|spend_|consume_|set_|equip|place_)\w*\s*\(")
PLUMBING = {"add_child"}
WRITE_RE = re.compile(
    r"\b(?:m|mission|state|game_state)\.[A-Za-z_]\w*"
    r"(?:\[[^\]]*\])?\s*(?:[+\-*/]?=[^=])")

GODOT = Path(conftest.repo_path("godot"))
_ITEMS = json.loads((GODOT / "data" / "items.json").read_text(
        encoding="utf-8"))
_TOWERS = json.loads((GODOT / "data" / "towers.json").read_text(
        encoding="utf-8"))
_TOWER_ROWS = _TOWERS["towers"] if isinstance(_TOWERS, dict) else _TOWERS

# Kit ids (items.json rows; the data leg below re-pins them).
KIT_HP = "orb_of_the_deep"       # primary "hp" -> a readable property
KIT_DMG = "mark_of_fervor"       # the STACK second kit (different kit)
KIT_SCRIPT_VALUE = 3.0           # scripted F3-shape fixture input, NOT
                                 # a balance literal

PROBE_SRC = '''
extends SceneTree
# gw kit-fx probe (v1.4 P7, MC 11857). Machine rows: KF-BOOT / -ASSIGN /
# -PRESENT / KF-FINDING / -CONTROL / -STACK / -INVALID / -UNASSIGN /
# -ACK / KF-OK (LAST print). Any failed check prints KF-FAIL <detail> +
# quit(1); a skipped leg can never reach KF-OK.
# E5: -s dispatches no _process — the pump is hand-driven through the
# SHIPPED public fx_step (its own header: "Public so the headless probe
# can drive it in lockstep"). DECLARED: fx._fx is read as the shipped
# live-effect state; the control leg drives the shipped _spawn_spark
# (the same call _observe_enemies makes on an hp drop) to prove this
# harness observes an effect BEGIN and reach its observable END.
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MISSION_RELICS := preload("res://scripts/mission_relics.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
# Kit seeds: items.json relic rows, F3 _scripted_relic shape verbatim
# (uid stamped by the bank_add mutator; rarity/ilvl/value 3.0 are
# fixture inputs, not balance literals). KIT_HP primary is "hp" (the
# tier row HAS an hp key -> the bonus lands on a readable property;
# items.json-pinned by the test).
const KIT_HP := "orb_of_the_deep"
const KIT_DMG := "mark_of_fervor"

var tables = null
var state = null


func _fail(why: String) -> void:
	print("KF-FAIL " + why)
	quit(1)


func _scripted_kit(base_id: String) -> Dictionary:
	var base: Dictionary = {}
	for row: Dictionary in tables.rows("items"):
		if String(row.get("id", "")) == base_id:
			base = row
	if base.is_empty():
		_fail("no items.json kit row " + base_id)
		return {}
	return {
		"uid": 0,
		"base_id": String(base["id"]),
		"slot": String(base["slot"]),
		"rarity": "powerful",
		"ilvl": 3,
		"primary": {"stat": String(base["primary"]), "value": 3.0},
		"secondary": null,
		"atk_speed": float(base["roll_ranges"]["atk_speed"][0]),
		"shot_type": null,
		"proj_count": int(base["roll_ranges"]["proj_count"][0]),
		"mods": [],
		"upgraded": 0,
	}


func _bonuses(obj) -> String:
	if obj.relic_bonuses.is_empty():
		return "none"
	var out := ""
	for stat: String in obj.relic_bonuses:
		if out != "":
			out += ","
		out += "%s:%.3f" % [stat, float(obj.relic_bonuses[stat])]
	return out


func _pump(fx) -> void:
	for _i: int in range(120):
		fx.fx_step(1.0 / 60.0)


func _init() -> void:
	tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	state = graph["state"]
	state.set_deck(DECK.duplicate())     # shipped C13 mutators only (F3)
	state.bank_add(_scripted_kit(KIT_HP))
	state.bank_add(_scripted_kit(KIT_DMG))
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11857
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	var p = m.get_node("DefensePanel")
	var fx = m.get_node("FxDirector")
	# Place one tower through the panel's own placer (F3/P1 reading).
	var placer = p.placer
	var cheap_id := ""
	var cheap_cost := 1 << 30
	for row: Dictionary in placer.tower_defs:
		if int(row["base_cost"]) < cheap_cost:
			cheap_cost = int(row["base_cost"])
			cheap_id = String(row["id"])
	var cres: Dictionary = placer.place_id(cheap_id, 1)
	if not bool(cres.get("ok", false)) or m.defense_list.size() != 1:
		_fail("boot control place refused " + str(cres))
		return
	var uid := int(m.defense_list[0]["uid"])
	var obj = MISSION_RELICS.defense_by_uid(m, uid)
	if obj == null:
		_fail("placed row not readable back")
		return
	var tier_hp := float(obj.tier_row()["hp"])
	var iid0 := int(obj.node.get_instance_id())
	var ack0 := int(state.saved_ack)
	var spark0 := int(fx.spawned_sparks)
	print("KF-BOOT kits=2 pool=%d tower=%s tier_hp=%.3f fx=0 sparks0=%d ack=%d list=%d mirror=%d" % [
			int(m.relic_pool.size()), cheap_id, tier_hp, spark0,
			ack0, int(m.defense_list.size()), int(m.relics_assigned)])
	if int(m.relic_pool.size()) != 2:
		_fail("relic pool did not copy the 2 bank kit rows")
		return
	var poolA := _kit_uid(m, KIT_HP)
	var poolB := _kit_uid(m, KIT_DMG)
	if poolA == 0 or poolB == 0:
		_fail("pool kit rows missing after setup")
		return

	# --- KF-ASSIGN: shipped crossing; property read-back. ---
	var ares: Dictionary = m.assign_relic(uid, poolA)
	if not bool(ares.get("ok", false)):
		_fail("assign refused " + str(ares))
		return
	var live_assign := int(fx._fx.size())
	print("KF-ASSIGN ok=true relic=%d bonuses=%s hp_max=%.3f hp=%.3f mirror=%d pool=%d ack=%d" % [
			int(obj.relic_uid), _bonuses(obj), float(obj.hp_max),
			float(obj.hp), int(m.relics_assigned),
			int(m.relic_pool.size()), int(state.saved_ack)])
	if int(obj.relic_uid) != poolA:
		_fail("relic_uid not on the row")
		return

	# --- KF-PRESENT (v1.5 W-K re-pin): live 0 at assign (observer is
	# the painter); ONE fx_step observes the crossing; pump ends it. ---
	fx.fx_step(1.0 / 60.0)
	var kit_live := int(fx._fx.size())
	var kit_sc0 := float(((fx._fx[0]["node"]) as Sprite3D).scale.x) if kit_live == 1 else 0.0
	fx.fx_step(1.0 / 60.0)
	var kit_sc1 := float(((fx._fx[0]["node"]) as Sprite3D).scale.x) if int(fx._fx.size()) >= 1 else 0.0
	var rtex := 1 if kit_live == 1 and String(((fx._fx[0]["node"]) as Sprite3D).texture.resource_path).contains("fx_spark_hit") else 0
	_pump(fx)
	var live_pump := int(fx._fx.size())
	var swapped := 0 if int(obj.node.get_instance_id()) == iid0 else 1
	var parented := 1 if (obj.node as Node).get_parent() != null else 0
	print("KF-PRESENT live_after_assign=%d kit_live=%d live_after_pump=%d swapped=%d parented=%d sparks_delta=%d ack=%d" % [
			live_assign, kit_live, live_pump, swapped, parented,
			int(fx.spawned_sparks) - spark0, int(state.saved_ack)])
	# FINDING row RE-DECLARED at v1.5 W-K (was =NONE at v1.4): the
	# shipped shape paints the spark sheet AT the crossing —
	# VERBATIM-pinned, a future change must re-pin or false-green.
	print("KF-FINDING kit_presentation=fx_spark_hit kit_fx_live=%d kit_fx_after_pump=%d kit_sparks_delta=%d kit_node_changed=%d kit_rtex=%d kit_tw=%d" % [
			kit_live, live_pump,
			int(fx.spawned_sparks) - spark0, swapped, rtex, int(kit_sc1 != kit_sc0)])

	# --- KF-CONTROL: same instrument, SAME pump, on a known shipped
	# effect: begin (live 1) -> observable end (live 0). Spark baseline
	# RE-ANCHORED here: the kit spark rides the shared counter (W-K). ---
	var spark_c := int(fx.spawned_sparks)
	fx._spawn_spark(obj.pos)
	var live_mid := int(fx._fx.size())
	var spark1 := int(fx.spawned_sparks) - spark_c
	if live_mid != 1 or spark1 != 1:
		_fail("control effect did not begin (live=%d sparks=%d)" % [live_mid, spark1])
		return
	_pump(fx)
	print("KF-CONTROL live_mid=%d live_end=%d spawned_delta=%d" % [
			live_mid, int(fx._fx.size()), spark1])
	if int(fx._fx.size()) != 0:
		_fail("control effect never reached its observable end")
		return

	# --- KF-CAP (v1.5 W-K, plan §3 MAX_FX leg): PLANT the cap with the
	# shipped spawn site, DERIVED from behavior (fill 512 -> plateau;
	# growth stopping IS the drop-past-cap read), then CROSS a fresh kit
	# crossing while FULL: dropped, never queued (symmetric OUT too). ---
	var una0 := int(fx.spawned_sparks)
	if not bool(m.unassign_relic(uid).get("ok", false)):
		_fail("cap-leg unassign refused")
		return
	fx.fx_step(1.0 / 60.0)
	var una_delta := int(fx.spawned_sparks) - una0
	var cap0 := int(fx.spawned_sparks)
	for _i: int in range(512):
		fx._spawn_spark(obj.pos)
	var cap := int(fx.spawned_sparks) - cap0
	var filled := int(fx._fx.size())
	var ares2: Dictionary = m.assign_relic(uid, poolA)
	fx.fx_step(1.0 / 60.0)
	var kit_at_cap := int(fx.spawned_sparks) - cap0 - cap
	_pump(fx)
	print("KF-CAP cap=%d filled=%d una_sparks=%d kit_at_cap=%d live_end=%d ok=%s" % [
			cap, filled, una_delta, kit_at_cap, int(fx._fx.size()),
			str(bool(ares2.get("ok", false)))])
	if not bool(ares2.get("ok", false)):
		_fail("cap-leg re-assign refused " + str(ares2))
		return
	if cap == 0 or cap >= 512 or filled != cap:
		_fail("cap plant not observed (cap=%d filled=%d)" % [cap, filled])
		return
	if una_delta != 0 or kit_at_cap != 0 or int(fx._fx.size()) != 0:
		_fail("cap/symmetric leg broken (una=%d kit=%d end=%d)" % [
				una_delta, kit_at_cap, int(fx._fx.size())])
		return

	# --- KF-STACK: second kit on an OCCUPIED row (shipped rule:
	# mission_relics.gd:24 refuses "taken", NOT replace). ---
	var sres: Dictionary = m.assign_relic(uid, poolB)
	print("KF-STACK ok=%s why=%s relic=%d mirror=%d ack=%d" % [
			str(bool(sres.get("ok", false))),
			String(sres.get("why", "NONE")), int(obj.relic_uid),
			int(m.relics_assigned), int(state.saved_ack)])
	if bool(sres.get("ok", false)) or String(sres.get("why", "NONE")) != "taken":
		_fail("stack leg: shipped rule is refuse-taken, got " + str(sres))
		return
	if int(obj.relic_uid) != poolA or int(m.relics_assigned) != 1:
		_fail("stack refusal moved state")
		return

	# --- KF-INVALID: unknown kit id -> "relic", nothing moved. ---
	var ires: Dictionary = m.assign_relic(uid, 900001)
	print("KF-INVALID ok=%s why=%s relic=%d mirror=%d pool=%d ack=%d" % [
			str(bool(ires.get("ok", false))),
			String(ires.get("why", "NONE")), int(obj.relic_uid),
			int(m.relics_assigned), int(m.relic_pool.size()),
			int(state.saved_ack)])
	if bool(ires.get("ok", false)) or String(ires.get("why", "NONE")) != "relic":
		_fail("invalid-kit leg accepted a non-pool uid " + str(ires))
		return

	# --- KF-UNASSIGN: revert read-back. ---
	var ures: Dictionary = m.unassign_relic(uid)
	if not bool(ures.get("ok", false)):
		_fail("unassign refused " + str(ures))
		return
	print("KF-UNASSIGN ok=true relic=%d bonuses=%s hp_max=%.3f hp=%.3f mirror=%d pool=%d ack=%d" % [
			int(obj.relic_uid), _bonuses(obj), float(obj.hp_max),
			float(obj.hp), int(m.relics_assigned),
			int(m.relic_pool.size()), int(state.saved_ack)])
	if int(obj.relic_uid) != 0 or not obj.relic_bonuses.is_empty():
		_fail("unassign did not clear the row")
		return
	if absf(float(obj.hp_max) - tier_hp) > 1e-9 or int(m.relics_assigned) != 0:
		_fail("unassign did not revert hp_max/mirror")
		return
	if int(m.relic_pool.size()) != 2:
		_fail("pool row left the pool (C11 clear-not-move)")
		return

	# --- KF-ACK: ZERO save writes across the whole kit matrix. ---
	print("KF-ACK start=%d end=%d delta=%d" % [ack0,
			int(state.saved_ack), int(state.saved_ack) - ack0])
	if int(state.saved_ack) != ack0:
		_fail("kit matrix emitted a save write")
		return
	print("KF-OK")
	quit(0)


func _kit_uid(m, base_id: String) -> int:
	for row: Dictionary in m.relic_pool:
		if String(row.get("base_id", "")) == base_id:
			return int(row.get("uid", 0))
	return 0
'''


def _run_probe(tmp_path, class_cache):
    probe = Path(tmp_path) / "gw_kit_fx_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (),
                                     tmp_path / "user_home")


def _only(out, tag):
    r = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(r) == 1, "expected exactly one %s row:\n%s" % (tag, out)
    return dict(x.split("=", 1) for x in r[0].split(" ")[1:])


def _row_tier_hp(tower_id):
    for r in _TOWER_ROWS:
        if str(r["id"]) == tower_id:
            return float(r["tiers"][0]["hp"])
    raise AssertionError("tower id %s not in towers.json" % tower_id)


def test_kit_fx_matrix(tmp_path, class_cache):
    """One engine probe: the full KF-* matrix (rows + asserts below)."""
    proc = _run_probe(tmp_path, class_cache)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "KF-FAIL" not in out, out
    assert out.rstrip().endswith("KF-OK"), \
        "KF-OK must be the LAST row (a skipped leg cannot reach it)"

    boot = _only(out, "KF-BOOT")
    assert boot["kits"] == "2" and int(boot["pool"]) == 2, boot
    assert int(boot["fx"]) == 0 and int(boot["mirror"]) == 0, boot
    assert int(boot["list"]) == 1, "boot control place did not land: %s" % boot
    # ack baseline: set_deck + 2 bank_add are the shipped C13 writes the
    # probe seeded with (P1 pins the same semantics at ack0==1 there).
    assert int(boot["ack"]) == 3, boot
    tier_hp = _row_tier_hp(boot["tower"])
    assert float(boot["tier_hp"]) == tier_hp, \
        "tier hp %s != towers.json tiers[0].hp %s for %s" % (
            boot["tier_hp"], tier_hp, boot["tower"])

    asg = _only(out, "KF-ASSIGN")
    assert asg["ok"] == "true" and int(asg["relic"]) > 0, asg
    assert asg["bonuses"] == "hp:%.3f" % KIT_SCRIPT_VALUE, \
        "kit bonus is not the items.json primary add: %s" % asg
    assert abs(float(asg["hp_max"]) - (tier_hp + KIT_SCRIPT_VALUE)) \
        < 1e-6, "hp_max did not ride the data add: %s (%s)" % (asg, tier_hp)
    # The declared clamp reading: a full-hp row is NOT healed by a kit.
    assert float(asg["hp"]) == tier_hp, asg
    assert int(asg["mirror"]) == 1 and int(asg["pool"]) == 2, asg
    assert int(asg["ack"]) == int(boot["ack"]), asg

    # The v1.5 W-K measured shape (re-pin transcripts in WK-wave.log):
    # nothing paints at assign (observer is the painter); ONE fx_step
    # observes the crossing, the pump ends it. kit_rtex=1 pins the BANK
    # sheet (WK2: runtime rebuild = WEB-breaker); kit_tw=1 the pulse.
    pres = _only(out, "KF-PRESENT")
    assert pres["live_after_assign"] == "0", \
        "kit fx painted synchronously — the observer is the painter: %s" % pres
    assert pres["kit_live"] == "1", \
        "kit crossing spawned no presentation (W-K shipped shape): %s" % pres
    assert pres["live_after_pump"] == "0", pres
    assert pres["swapped"] == "0" and pres["parented"] == "1", pres
    assert pres["sparks_delta"] == "1", pres
    assert int(pres["ack"]) == int(boot["ack"]), pres
    finding = [ln for ln in out.splitlines()
               if ln.startswith("KF-FINDING ")]
    assert finding == ["KF-FINDING kit_presentation=fx_spark_hit "
                       "kit_fx_live=1 kit_fx_after_pump=0 "
                       "kit_sparks_delta=1 kit_node_changed=0 "
                       "kit_rtex=1 kit_tw=1"], \
        "FINDING row drifted from the measured shipped shape: %s" % finding

    # Non-vacuity: the SAME read + pump observe a REAL shipped effect
    # begin and reach its observable end. Without this the all-zero
    # PRESENT row could not prove anything.
    ctl = _only(out, "KF-CONTROL")
    assert ctl["live_mid"] == "1" and ctl["live_end"] == "0" \
        and ctl["spawned_delta"] == "1", \
        "instrument failed to observe a shipped effect: %s" % ctl

    # W-K MAX_FX + symmetric-OUT legs (cap DERIVED from behavior in
    # the probe — no literal; drop-past-cap pinned by filled == cap).
    cp = _only(out, "KF-CAP")
    assert cp["ok"] == "true" and 0 < int(cp["cap"]) < 512 \
        and cp["filled"] == cp["cap"], \
        "cap plant did not observe drop-past-cap: %s" % cp
    assert cp["una_sparks"] == "0", \
        "unassign painted fx — symmetric poof is DECLARED OUT: %s" % cp
    assert cp["kit_at_cap"] == "0", \
        "kit fx past the cap queued — cap discipline broken: %s" % cp
    assert cp["live_end"] == "0", cp

    # Stacking per the shipped rule (mission_relics.gd:24): REFUSED,
    # not replaced. This pins what IS, honestly (the brief's reading).
    stk = _only(out, "KF-STACK")
    assert stk["ok"] == "false" and stk["why"] == "taken", stk
    assert int(stk["relic"]) == int(asg["relic"]) \
        and int(stk["mirror"]) == 1, "stacking moved state: %s" % stk
    assert int(stk["ack"]) == int(boot["ack"]), stk

    inv = _only(out, "KF-INVALID")
    assert inv["ok"] == "false" and inv["why"] == "relic", inv
    assert int(inv["relic"]) == int(asg["relic"]) \
        and int(inv["mirror"]) == 1 and int(inv["pool"]) == 2, \
        "invalid-kit refusal moved state: %s" % inv
    assert int(inv["ack"]) == int(boot["ack"]), inv

    una = _only(out, "KF-UNASSIGN")
    assert una["ok"] == "true" and int(una["relic"]) == 0, una
    assert una["bonuses"] == "none", una
    assert float(una["hp_max"]) == tier_hp and float(una["hp"]) == tier_hp, una
    assert int(una["mirror"]) == 0 and int(una["pool"]) == 2, \
        "unassign did not revert / pool row left the pool: %s" % una
    assert int(una["ack"]) == int(boot["ack"]), una

    ack = _only(out, "KF-ACK")
    assert int(ack["start"]) == int(boot["ack"]) \
        and int(ack["end"]) == int(boot["ack"]) \
        and int(ack["delta"]) == 0, (ack, boot)


# The FINDING's structural half: the named claim "the shipped kit
# assign/unassign writers spawn ZERO presentation-layer effects" goes
# false the moment ANY of these bodies calls the fx/sprite/text/child
# layer. This is what forces a future implementation to re-pin the
# KF-PRESENT/KF-FINDING rows instead of riding the green silently.
_PRESENT_BAN = ("_spawn", "fx_", "FxDirector", "make_sprite",
                "make_text", "SPRITE_BANK", "WORLD_TEXT", "add_child",
                "emit")

_WRITER_BODIES = (
    ("scripts/mission_relics.gd", ("assign", "unassign")),
    ("scripts/defense_obj.gd", ("assign_relic", "clear_relic")),
    ("scripts/mission.gd", ("assign_relic", "unassign_relic")),
)


def _func_body(text, name):
    start = text.index("func %s(" % name)
    nxt = text.find("\nfunc ", start + 1)
    return text[start:nxt if nxt > 0 else len(text)]


def test_kit_presentation_source_truth():
    for rel, funcs in _WRITER_BODIES:
        text = (GODOT / rel).read_text(encoding="utf-8")
        for fn in funcs:
            body = _func_body(text, fn)
            for token in _PRESENT_BAN:
                assert token not in body, \
                    "kit writer %s::%s now touches presentation (%r): " \
                    "re-pin the KF-PRESENT/KF-FINDING rows" % (rel, fn, token)
        if rel == "scripts/mission.gd":
            for fn in funcs:
                assert "MISSION_RELICS." in _func_body(text, fn), \
                    "mission.gd %s no longer delegates the crossing" % fn


def test_kit_observer_pass_is_unconditional():
    """Dead-shape detector (plan §3 W-K leg 2, DA P1-B): kit assigns
    are build-phase-only (mission_relics.gd:16) — ZERO drops those
    frames — so the pass call must sit at fx_step's TOP LEVEL; behind
    any guard (or in the guarded bodies) it ships dead."""
    text = (GODOT / "scripts" / "fx_director.gd").read_text(
        encoding="utf-8")
    step = _func_body(text, "fx_step")
    kit = [ln for ln in step.split("\n") if "_observe_kits(" in ln]
    assert kit == ["\t_observe_kits(m)"], \
        "kit pass moved off fx_step's top level — a guarded pass ships " \
        "dead (kit assigns are build-phase-only, DA P1-B): %r" % kit
    for guarded in ("_observe_fires", "_observe_enemies"):
        assert "_observe_kits" not in _func_body(text, guarded), \
            "kit pass moved into the guarded %s body" % guarded
    assert "drops" not in _func_body(text, "_observe_kits"), \
        "kit pass reads the drop map — dead-shape class"


def test_kit_observer_zero_writes_and_cap_door_source_truth():
    """F3 idiom (plan §3 W-K leg 4): the kit pass READS published
    rows, writes NO injected state (shapes per test_wave_telegraph),
    and its ONLY spawn path is the shipped _spawn_spark site — the
    cap lives in _spawn_fx below it, never bypassed."""
    text = (GODOT / "scripts" / "fx_director.gd").read_text(
        encoding="utf-8")
    code = hyg.blank_code(_func_body(text, "_observe_kits"), "gd")
    muts = [mm.group(0) for mm in MUT_RE.finditer(code)
            if mm.group(0).rstrip("(").strip() not in PLUMBING]
    assert muts == [], "kit pass calls a shipped mutator: %s" % muts
    writes = [mm.group(0) for mm in WRITE_RE.finditer(code)]
    assert writes == [], "kit pass writes injected state: %s" % writes
    for tok in ("assign_relic", "clear_relic", "bank_add", "add_child",
                "make_sprite", "SPRITE_BANK", "emit"):
        assert tok not in code, \
            "kit pass bypasses the observer shape (%r)" % tok
    assert code.count("_spawn_spark(") == 1, \
        "kit spark must ride the ONE shipped sheet spawn site"
    assert "_spawn_fx" not in code and "spawned_" not in code, \
        "kit pass bypasses _spawn_spark or counts on its own"


def test_kit_data_rows():
    # kits file + rows (DoD naming leg): items.json, 15 rows, the 3
    # slot=="relic" kits pinned by id and primary stat.
    assert len(_ITEMS) == 15, len(_ITEMS)
    kits = {r["id"]: r for r in _ITEMS if r["slot"] == "relic"}
    assert set(kits) == {"mark_of_fervor", "orb_of_the_deep",
                         "medallion_of_the_gate"}, sorted(kits)
    assert kits[KIT_HP]["primary"] == "hp"
    assert kits[KIT_DMG]["primary"] == "damage"
    assert kits["medallion_of_the_gate"]["primary"] == "fire_rate"
