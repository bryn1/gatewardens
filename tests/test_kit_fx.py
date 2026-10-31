"""v1.4 P7 kit-presentation probe (MC 11857 / V14-PLAN §2 row "v5_fx_probe
tracer kit leg (V12-PLAN:297, never executed)", wave W4) — TESTS-ONLY,
ZERO production edits (pathspec commit proves).

THE DEBT: V12-PLAN:297 promised the kit leg of the F5 row; the planner
verified it NEVER ran (V14-PLAN §2: "never executed"; §Verification kits
grep 0 hits). This card pays it as the PROBE this DoD names: the shipped
kit (C11 relic) crossing's presentation dimension, exercised as RUNNING
behavior over the real mission.tscn — the conftest.run_probe_script
tmp-probe idiom (R5; test_place_refusals.py P1 + test_relic_negatives.py
F3 are the harness precedents; E5: _ready + the fx pump are HAND-driven
in headless — fx_step is public exactly for this).

KIT NAMING (DoD "kits file + rows", reading DECLARED): the kit data file
is godot/data/items.json — 15 rows, the 3 slot=="relic" kits are
mark_of_fervor / orb_of_the_deep / medallion_of_the_gate (test_kit_data
rows names + pins it). mission.setup() copies the bank's slot=="relic"
rows into the mission-local relic_pool (mission.gd:149-151); the shipped
writers are mission.assign_relic/unassign_relic -> mission_relics
(:15/:31, guards phase>uid>relic>taken) -> defense_obj.assign_relic/
clear_relic (:97/:102, the pinned bonus application site).

THE FINDING (the deliverable per the V12 debt; production NOT touched,
HONEST ROUTE of the brief): the promised kit PRESENTATION effect is NOT
implemented in shipped code. The assign/unassign writers are PURE STATE
crossings (relic_uid, relic_bonuses, hp_max/hp clamp, C5 mirror) and the
one presentation director (fx_director.gd) spawns ONLY from _observe_
enemies/_observe_fires (hp-drop sparks, despawn poofs, shot tracers,
damage numbers) — no kit path feeds it (VERIFIED: zero fx calls in the
writer bodies; source-truth leg below pins it STRUCTURALLY). The probe
pins this honestly: KF-PRESENT + the KF-FINDING row assert the MEASURED
shipped shape (live fx 0 -> 0 across the assign window AND a hand-driven
2 s pump; world node untouched), while KF-CONTROL proves the instrument
is NOT blind — the same _fx read + the same pump take a REAL shipped
effect (_spawn_spark, the call _observe_enemies itself makes) from
BEGIN (live=1) to observable END (live=0). Any future kit presentation
implementation MUST re-pin these rows — it cannot false-green.

Legs (KF-* rows; in-probe KF-FAIL + quit(1) guards + KF-OK-LAST so a
silent skip cannot go green):
  KF-ASSIGN   assign kit -> state read back: relic_uid, bonuses
              hp:3.000 (items.json primary, scripted 3.0 F3-input),
              hp_max = tier row hp + 3.0 EXACT, hp CLAMPED not healed
              (defense_obj :96 declared reading), C5 mirror 1, pool 2
              (C11 clear-not-move), saved_ack unmoved.
  KF-PRESENT  presentation dimension through the shipped pump: live fx
              0 at assign, 0 after 120 hand-driven fx_step frames
              (2 s > the 0.5 s longest lifetime); world node same
              instance, still parented; sparks counter unmoved.
  KF-FINDING  the pinned FINDING row (exact-string asserted).
  KF-CONTROL  non-vacuity: the SAME instrument sees a shipped spark
              begin (1) and reach its observable end (0).
  KF-STACK    stacking per the SHIPPED rule — one relic per defense:
              the second kit is REFUSED "taken" (mission_relics.gd:24),
              NOT replaced; state unmoved, ack delta 0.
  KF-INVALID  unknown kit uid -> refused "relic", state unmoved, ack 0.
  KF-UNASSIGN ok -> everything reverts (relic_uid 0, bonuses gone,
              hp_max back to the bare tier row, mirror 0, pool intact).
  KF-ACK      ZERO save writes across the whole matrix (the boot ack
              3 = set_deck + 2 bank_add, the shipped C13 mutators the
              probe seeded with — P1 pins the same ack semantics).

F3 doctrine honored: NO duplicate legs — phase/uid refusals and the
same-relic DUP are already pinned by test_relic_negatives.py; this file
adds the presentation dimension, the different-kit STACK and the
INVALID-kit-id gap only. PLANTED-RED x1: the :24 taken-guard is broken
by scratch line-sed (guard -> false) -> KF-STACK goes RED (second kit
ACCEPTED) -> same-sed revert, byte-verified (git diff vs HEAD EMPTY +
sha256) -> green re-run; transcripts in .audits/20261031-1830-v14-plan/
P7-wave.log.
"""

import json
from pathlib import Path

import conftest

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

	# --- KF-PRESENT: presentation effect through the hand-driven pump. ---
	_pump(fx)
	var live_pump := int(fx._fx.size())
	var swapped := 0 if int(obj.node.get_instance_id()) == iid0 else 1
	var parented := 1 if (obj.node as Node).get_parent() != null else 0
	print("KF-PRESENT live_after_assign=%d live_after_pump=%d swapped=%d parented=%d sparks_delta=%d ack=%d" % [
			live_assign, live_pump, swapped, parented,
			int(fx.spawned_sparks) - spark0, int(state.saved_ack)])
	# FINDING row (V12-PLAN:297 debt): the promised kit presentation is
	# NOT implemented in shipped code — this row is the measured proof,
	# expected VERBATIM by the test (a future implementation MUST trip
	# it and re-pin, it cannot false-green).
	print("KF-FINDING kit_presentation=NONE kit_fx_delta=%d kit_live_after_pump=%d kit_node_changed=%d" % [
			live_assign, live_pump, swapped])

	# --- KF-CONTROL: same instrument, SAME pump, on a known shipped
	# effect: begin (live 1) -> observable end (live 0). Non-vacuity. ---
	fx._spawn_spark(obj.pos)
	var live_mid := int(fx._fx.size())
	var spark1 := int(fx.spawned_sparks) - spark0
	if live_mid != 1 or spark1 != 1:
		_fail("control effect did not begin (live=%d sparks=%d)" % [live_mid, spark1])
		return
	_pump(fx)
	print("KF-CONTROL live_mid=%d live_end=%d spawned_delta=%d" % [
			live_mid, int(fx._fx.size()), spark1])
	if int(fx._fx.size()) != 0:
		_fail("control effect never reached its observable end")
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

    # THE FINDING leg (pinned to ACTUAL shipped behavior): the kit
    # assign spawns NO presentation effect and the hand-driven pump
    # ends nothing because nothing began; the world node is untouched.
    pres = _only(out, "KF-PRESENT")
    assert pres["live_after_assign"] == "0", \
        "a kit presentation effect spawned — re-pin the KF-FINDING row: %s" % pres
    assert pres["live_after_pump"] == "0", pres
    assert pres["swapped"] == "0" and pres["parented"] == "1", pres
    assert pres["sparks_delta"] == "0", pres
    assert int(pres["ack"]) == int(boot["ack"]), pres
    finding = [ln for ln in out.splitlines()
               if ln.startswith("KF-FINDING ")]
    assert finding == ["KF-FINDING kit_presentation=NONE "
                       "kit_fx_delta=0 kit_live_after_pump=0 "
                       "kit_node_changed=0"], \
        "FINDING row drifted from the measured shipped shape: %s" % finding

    # Non-vacuity: the SAME read + pump observe a REAL shipped effect
    # begin and reach its observable end. Without this the all-zero
    # PRESENT row could not prove anything.
    ctl = _only(out, "KF-CONTROL")
    assert ctl["live_mid"] == "1" and ctl["live_end"] == "0" \
        and ctl["spawned_delta"] == "1", \
        "instrument failed to observe a shipped effect: %s" % ctl

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
