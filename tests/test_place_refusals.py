"""v1.4 P1 place-refusal matrix (MC 11829 / V14-PLAN §3 P1, wave W1)
— TESTS-ONLY, zero production edits (pathspec commit proves).

The refusal dicts ship (defense_placer.gd phase/id/slot gates;
mission.place_defense cap/green) but the matrix was never run as ONE
F3-idiom set (v1.2 F3 test_relic_negatives.py is the harness precedent:
conftest.run_probe_script, probe generated into tmp_path — R5). Coverage
map honestly named (plan "no duplicate legs, gap legs only"):
  why:"green" ALREADY covered — test_family_picker FP-REFUSE row;
  why:"id"    ALREADY covered — test_family_picker FP-ID row;
  why:"phase" GAP — this card, BOTH shipped routes (a);
  why:"slot"  GAP — exhaustion (fill every slot, place again -> NO
              double-place) + off-list slot index — this card (b);
  why:"cap"   GAP — mission.gd's cap guard had NO test caller anywhere
              (gatefall cap 60 > the ground-waypoint slot count, so the
              shipped map never reaches it): the gap leg drives it with
              a harness cap write, restored right after (c);
  GREEN CONTROL — the same probe builds one tower in BUILD on a free
              slot, node read back valid+parented, green down by the
              towers.json cost EXACTLY: a refusal matrix without a
              passing build row proves nothing (d);
  ACK/SAVE — baseline honesty: state.set_deck is a shipped C13
              mutator, so exactly ONE boot write mirrors write_seq into
              saved_ack (the ack-counting test_return_hub pins). The
              ack-delta leg means ZERO further save writes across the
              whole refusal matrix: every refusal row carries the
              baseline saved_ack UNCHANGED, and the save file (user://
              path READ from save_store.gd, never hardcoded here) is
              found in the isolated XDG_DATA_HOME tree (BN4 lever of
              run_probe_script: the boot write landed in tmp, the
              developer's real save untouched) with ack never having
              moved since (a failed write would printerr — the EMPTY
              stderr guard covers it).

Routes (found in defense_placer.gd + mission.gd step_bookkeeping, the
main input routing): KEY = bridge.on_key rising edge -> drain_presses ->
DefensePanel.poll -> handle_press("KeyM") -> place_selected -> placer.
place -> {"why":"phase"}; CLICK = a picker row's own pressed receiver
(_on_family_pressed -> _arm, the button's signal target) then a
"MouseLeft" press routed through handle_press to _confirm -> placer.
place_id -> {"why":"phase"}. Every placer call rides THE panel's own
placer (F3 reading: "the panel's own placer, the call the button makes"
— mission injects none, defense_panel.setup builds it). The G5b combat
lock (poll's sync disarms the aim through the ONE cancel route and
disables the picker rows) gets its own row. DECLARED readings:
- Combat entry is the F3 precedent write (test_relic_negatives.py:235
  "drive-real-entry-points write", its :237 restore twin): phase_kind +
  in_combat set to the pair _enter_combat writes before its start_wave
  side-effects. NO world step runs while phase_kind lies — one step()
  would let the waveless combat state "finish" a wave that never
  started; the E2E press legs replay the shipped pump PAIR verbatim
  (m.bridge.drain_presses() + DefensePanel.poll, mission.gd
  step_bookkeeping :242-249) with zero world advance. Deterministic.
- The combat legs run BEFORE the fill (free slots exist + green above
  every table cost): phase is then the ONLY blocking gate — the "no
  tower node / no gold write" reads are non-vacuous, and the KEY route
  would have placed for real the instant the phase guard was missing.
  The slot legs run AFTER the fill (all slots taken): why=="phase" vs
  "slot" stays the refusal-CAUSE discriminator.
- The green top-up before the fill is a HARNESS WRITE (declared — the
  placer header itself names "harness callers"): the occupied gate, not
  the economy, is the leg under test; gatefall's start green cannot
  fill its slots. The arithmetic is data-derived in-probe and
  re-checked here against towers.json.
- A REFUSAL itself never disarms the panel (shipped _confirm reading)
  — during COMBAT it is the lock's refresh-pass that clears the aim,
  which the REFUSE-CONFIRM/LOCKUI rows read back as armed=0; the pump
  sync runs BEFORE the press drains, so the confirm cannot even reach
  the placer (the direct handle_press leg is the armed race the placer
  phase gate exists to answer).

IN-PROBE REFUSE-FAIL guards: every leg fails loudly (REFUSE-FAIL +
quit(1), E3 early-return) and REFUSE-OK is the LAST print — a silent
skip cannot go green. PLANTED-RED (tests-only card, the F3 rule
verbatim): the phase guard is deleted as throwaway scratch at BOTH
shipped sites (place() AND place_id() — the same rule lives at both and
place() delegates to place_id(), so dropping only one still refuses
and would false-green); pytest goes RED (REFUSE-KEYM answers accepted
or "slot", never the asserted "phase"), then `git checkout --` +
diff-vs-index byte-verified revert and the GREEN re-run; transcripts
(RED row beside the GREEN row) in
.audits/20261031-1830-v14-plan/P1-wave.log. No permanent argv plant is
embeddable — the bug lives in shipped code the probe must not fake.
"""

import json
import os
import re
from pathlib import Path

import conftest

GODOT = Path(conftest.repo_path("godot"))
SAVE_GD = GODOT / "scripts" / "save_store.gd"

_TOWERS = json.loads((GODOT / "data" / "towers.json").read_text(
        encoding="utf-8"))
_ROWS = _TOWERS["towers"] if isinstance(_TOWERS, dict) else _TOWERS
MIN_COST = min(int(r["base_cost"]) for r in _ROWS)


PROBE_SRC = '''
extends SceneTree
# gw place-refusal probe (v1.4 P1, MC 11829). Machine rows: REFUSE-BOOT
# / -CTRL (green control) / -CAP / -SLOTOUT / -KEYM / -KEYME2E /
# -CONFIRM / -LOCKUI / -FILL / -SLOT / -ACK / REFUSE-OK (LAST print).
# Any failed check prints REFUSE-FAIL <detail> + quit(1); a skipped leg
# can never reach REFUSE-OK. DECLARED (test docstring): the
# phase_kind/in_combat writes are the F3 :235/:237 drive-real-entry-
# points pair; the green top-up is the harness-caller write (the
# occupied gate, not the economy, is under test); the E2E legs replay
# the shipped pump pair (drain_presses + DefensePanel.poll) with NO
# world step, so the declared combat state can never "finish" a wave.
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]

var tables = null
var state = null
var placer = null            # THE panel's own placer (no mission twin)


func _fail(why: String) -> void:
	print("REFUSE-FAIL " + why)
	quit(1)


func _nodes_ok(m) -> int:
	# A real tower = a defense record whose node is valid AND parented
	# (place_defense add_child's it; a refused place grew no record).
	var n := 0
	for rec: Dictionary in m.defense_list:
		var node: Variant = (rec["obj"] as RefCounted).node
		if is_instance_valid(node) and (node as Node).get_parent() != null:
			n += 1
	return n


func _state(m, p) -> String:
	return "green=%d list=%d nodes=%d ack=%d ghost=%d armed=%d" % [
			int(m.green), int(m.defense_list.size()), _nodes_ok(m),
			int(state.saved_ack), int(placer.ghost),
			1 if bool(p.armed) else 0]


func _refused(res: Dictionary, want: String, leg: String) -> void:
	# THE REFUSE-FAIL guard: an accepted or wrong-why refusal is RED.
	if bool(res.get("ok", false)) or String(res.get("why", "NONE")) \
			!= want:
		_fail(leg + " wanted why=" + want + " got " + str(res))
		return


func _init() -> void:
	tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	state = graph["state"]
	state.set_deck(DECK.duplicate())     # starter deck via the C13 write
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		print("REFUSE-FAIL mission.tscn not loadable")
		quit(1)
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11829                     # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	var p = m.get_node("DefensePanel")
	placer = p.placer
	var cheap_id := ""
	var cheap_cost := 1 << 30
	for row: Dictionary in placer.tower_defs:
		if int(row["base_cost"]) < cheap_cost:
			cheap_cost = int(row["base_cost"])
			cheap_id = String(row["id"])
	var nslots: int = placer.slots.size()
	var cap0 := int(m.defense_cap)
	# ACK BASELINE: state.set_deck is a shipped C13 mutator, so ONE boot
	# write has already mirrored write_seq into saved_ack here (the same
	# ack-counting test_return_hub pins, WIN=3/LOSE=4). "ack-delta 0"
	# means ZERO further save writes across the refusal matrix — every
	# leg compares against THIS baseline (ack mirrors write_seq only on
	# a successful write; a failed one prints to stderr, EMPTY-guarded).
	var ack0 := int(state.saved_ack)
	print("REFUSE-BOOT slots=%d cap=%d green=%d list=%d ack=%d" % [
			nslots, cap0, int(m.green), int(m.defense_list.size()), ack0])
	if nslots < 2 or nslots >= cap0:
		_fail("matrix premise broken (slots=%d cap=%d)" % [nslots, cap0])
		return
	if ack0 != 1:
		_fail("boot ack %d not the one set_deck write" % ack0)
		return

	# (d) GREEN CONTROL: BUILD phase, a free slot -> a real tower.
	var g0 := int(m.green)
	var cres: Dictionary = placer.place_id(cheap_id, 1)
	print("REFUSE-CTRL ok=%s cost=%d %s" % [str(bool(
			cres.get("ok", false))), int(cres.get("cost", -1)),
			_state(m, p)])
	if not bool(cres.get("ok", false)) or int(cres.get("cost", -1)) \
			!= cheap_cost or int(m.green) != g0 - cheap_cost \\
			or m.defense_list.size() != 1 or _nodes_ok(m) != 1:
		_fail("green control: BUILD-phase place did not land " + str(cres))
		return
	var gkeep := int(m.green)            # NO later leg may move green

	# (c) why:"cap" — THE gap leg (mission.gd:331 had no test caller:
	# the shipped cap 60 is unreachable above the slot count). Harness
	# cap write to the current list size, refused, cap restored.
	m.defense_cap = m.defense_list.size()
	var capres: Dictionary = placer.place_id(cheap_id, 1)
	print("REFUSE-CAP ok=%s why=%s %s" % [str(bool(
			capres.get("ok", false))), String(capres.get("why", "NONE")),
			_state(m, p)])
	m.defense_cap = cap0
	_refused(capres, "cap", "cap leg")
	if int(m.green) != gkeep or m.defense_list.size() != 1 \\
			or int(state.saved_ack) != ack0:
		_fail("cap refusal moved state")
		return

	# (b1) why:"slot" — off-list slot index (occupied() answers out of
	# range; free slots still exist, so only the slot gate can refuse).
	var ores: Dictionary = placer.place_id(cheap_id, 1, nslots + 7)
	print("REFUSE-SLOTOUT ok=%s why=%s %s" % [str(bool(
			ores.get("ok", false))), String(ores.get("why", "NONE")),
			_state(m, p)])
	_refused(ores, "slot", "slot-off-list leg")
	if int(m.green) != gkeep or m.defense_list.size() != 1:
		_fail("slot-off-list refusal moved state")
		return

	# (a) COMBAT, BOTH shipped routes — before the fill: free slots and
	# green above every table cost, so phase is the ONLY blocker.
	m.phase_kind = "combat"              # F3 :235 drive-real-entry-points
	m.in_combat = true
	var kres: Dictionary = p.place_selected()   # the KeyM-unarmed route
	print("REFUSE-KEYM ok=%s why=%s %s" % [str(bool(
			kres.get("ok", false))), String(kres.get("why", "NONE")),
			_state(m, p)])
	_refused(kres, "phase", "key-route leg")
	if int(m.green) != gkeep or m.defense_list.size() != 1 \\
			or _nodes_ok(m) != 1 or int(state.saved_ack) != ack0:
		_fail("key-route refusal moved state")
		return
	# KEY route end-to-end: a REAL bridge press drained through the
	# shipped pump pair (mission.gd step_bookkeeping), zero world step.
	m.bridge.on_key("KeyM", true)
	m.bridge.on_key("KeyM", false)
	p.poll(m.bridge.drain_presses())
	print("REFUSE-KEYME2E %s" % _state(m, p))
	if m.defense_list.size() != 1 or int(m.green) != gkeep \\
			or int(state.saved_ack) != ack0:
		_fail("key-route E2E press moved state")
		return
	# CLICK route: a picker row's own pressed receiver ARMS (G5: press
	# arms, never places). The refusal dict is captured on the EXACT
	# _confirm call — placer.place_id(armed_id, 1), the same arguments
	# _confirm passes — BEFORE the routed press, because the routed
	# confirm's trailing refresh lets the combat lock disarm the aim
	# (REFUSE-CONFIRM armed=0; the refusal itself never disarms).
	p._on_family_pressed(cheap_id)
	if not bool(p.armed) or String(p.armed_id) != cheap_id:
		_fail("arm via the shipped pressed receiver did not arm")
		return
	var cfres: Dictionary = placer.place_id(String(p.armed_id), 1)
	p.handle_press("MouseLeft")          # the shipped router, poll's own
	print("REFUSE-CONFIRM ok=%s why=%s %s" % [str(bool(
			cfres.get("ok", false))), String(cfres.get("why", "NONE")),
			_state(m, p)])
	_refused(cfres, "phase", "click-confirm leg")
	if m.defense_list.size() != 1 or int(m.green) != gkeep \\
			or _nodes_ok(m) != 1 or int(state.saved_ack) != ack0:
		_fail("click-confirm refusal moved state")
		return
	# G5b combat lock through the FULL pump: arm again, then a real
	# MouseLeft press — poll's sync DISABLES the picker rows and
	# disarms the aim through the ONE cancel route BEFORE the press
	# drains, so the confirm never even reaches the placer.
	p._on_family_pressed(cheap_id)
	p.sync()
	var dis := 0
	for row: Dictionary in p.picker_rows:
		if bool((row["btn"] as Button).disabled):
			dis += 1
	m.bridge.on_key("MouseLeft", true)
	m.bridge.on_key("MouseLeft", false)
	p.poll(m.bridge.drain_presses())
	print("REFUSE-LOCKUI rows=%d disabled=%d %s" % [
			int(p.picker_rows.size()), dis, _state(m, p)])
	if dis != int(p.picker_rows.size()) or bool(p.armed) \\
			or m.defense_list.size() != 1 \\
			or int(m.green) != gkeep or int(state.saved_ack) != ack0:
		_fail("combat lock leaked a place, an armed row, or a write")
		return
	m.phase_kind = "build"               # F3 :237 restore twin
	m.in_combat = false

	# (b2) FILL every buildable slot, then place again. Harness green
	# (declared): the 300 start cannot fill the map; the occupied gate,
	# not the economy, is the leg. Arithmetic re-checked python-side.
	var need: int = (nslots - m.defense_list.size()) * cheap_cost
	m.green = int(m.green) + need + cheap_cost
	var gfill := int(m.green)
	var placed := 0
	while placer.first_free() >= 0:
		var fres: Dictionary = placer.place_id(cheap_id, 1)
		if not bool(fres.get("ok", false)):
			_fail("fill place refused " + str(fres) + " " + _state(m, p))
			return
		placed += 1
	print("REFUSE-FILL placed=%d %s" % [placed, _state(m, p)])
	if placed != nslots - 1 or m.defense_list.size() != nslots \\
			or _nodes_ok(m) != nslots \\
			or int(m.green) != gfill - (nslots - 1) * cheap_cost:
		_fail("fill arithmetic off (placed=%d slots=%d) %s" % [
				placed, nslots, _state(m, p)])
		return
	var gfull := int(m.green)

	# (b3) all slots taken: place AGAIN -> refused, NO double-place.
	var sres: Dictionary = placer.place_id(cheap_id, 1)
	var sres2: Dictionary = placer.place_id(cheap_id, 1)
	placer.cycle_ghost(1)                # zero-free cycle parks the ghost
	print("REFUSE-SLOT ok=%s why=%s why2=%s %s" % [
			str(bool(sres.get("ok", false))),
			String(sres.get("why", "NONE")),
			String(sres2.get("why", "NONE")), _state(m, p)])
	_refused(sres, "slot", "exhaustion leg")
	_refused(sres2, "slot", "exhaustion-twice leg")
	if m.defense_list.size() != nslots or _nodes_ok(m) != nslots \\
			or int(m.green) != gfull or int(placer.ghost) != -1 \\
			or int(state.saved_ack) != ack0:
		_fail("double-place or state write at exhaustion")
		return

	# (e) ACK row: no refusal (nor mission play) emitted a C13 mutated —
	# saved_ack never moved from the baseline the set_deck boot write
	# left (the save-file existence scan is python-side over the
	# isolated XDG_DATA_HOME tree).
	print("REFUSE-ACK start=%d end=%d delta=%d" % [ack0,
			int(state.saved_ack), int(state.saved_ack) - ack0])
	if int(state.saved_ack) != ack0:
		_fail("ack delta != 0 across the refusal matrix")
		return
	print("REFUSE-OK")
	quit(0)
'''


def _run_probe(tmp_path):
    probe = Path(tmp_path) / "gw_place_refusal_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (),
                                     tmp_path / "user_home")


def _only(out, tag):
    r = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(r) == 1, "expected exactly one %s row:\n%s" % (tag, out)
    return dict(x.split("=", 1) for x in r[0].split(" ")[1:])


def _save_name():
    m = re.search(r'user://([A-Za-z0-9._-]+)',
                  SAVE_GD.read_text(encoding="utf-8"))
    assert m, "save_store.gd exposes no user:// path"
    return m.group(1)


def test_place_refusal_matrix(tmp_path, class_cache):
    proc = _run_probe(tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "REFUSE-FAIL" not in out, out
    assert out.rstrip().endswith("REFUSE-OK"), \
        "REFUSE-OK must be the LAST row (a skipped leg cannot reach it)"

    boot = _only(out, "REFUSE-BOOT")
    # ack==1: the ONE set_deck boot write (shipped C13 mutator) already
    # mirrored write_seq before the matrix starts — the ack-delta 0
    # contract is ZERO FURTHER writes (test_return_hub ack semantics).
    assert int(boot["ack"]) == 1 and int(boot["list"]) == 0, boot
    nslots = int(boot["slots"])
    assert 2 <= nslots < int(boot["cap"]), \
        "matrix premise (fillable under cap) broken: %s" % boot

    # (d) GREEN CONTROL: the BUILD-phase place landed — the DATA cost.
    ctrl = _only(out, "REFUSE-CTRL")
    assert ctrl["ok"] == "true" and int(ctrl["cost"]) == MIN_COST, ctrl
    assert int(ctrl["nodes"]) == 1 and int(ctrl["list"]) == 1, ctrl
    assert int(ctrl["green"]) == int(boot["green"]) - MIN_COST, \
        (ctrl, boot)

    # Refusal rows: the plan's why-values, each re-checked against the
    # UNCHANGED reads (green/list/nodes/ack) python-side.
    capr = _only(out, "REFUSE-CAP")
    assert capr["ok"] == "false" and capr["why"] == "cap", capr
    assert int(capr["green"]) == int(ctrl["green"]), capr
    so = _only(out, "REFUSE-SLOTOUT")
    assert so["ok"] == "false" and so["why"] == "slot", so
    km = _only(out, "REFUSE-KEYM")
    assert km["ok"] == "false" and km["why"] == "phase", km
    assert int(km["nodes"]) == 1 and int(km["green"]) == \
        int(ctrl["green"]), "combat key refusal moved state: %s" % km
    ke = _only(out, "REFUSE-KEYME2E")
    assert int(ke["list"]) == 1 and int(ke["green"]) == \
        int(ctrl["green"]) and int(ke["ack"]) == int(boot["ack"]), ke
    cf = _only(out, "REFUSE-CONFIRM")
    assert cf["ok"] == "false" and cf["why"] == "phase", cf
    assert int(cf["nodes"]) == 1 and int(cf["green"]) == \
        int(ctrl["green"]), "combat click refusal moved state: %s" % cf
    lu = _only(out, "REFUSE-LOCKUI")
    assert int(lu["disabled"]) == int(lu["rows"]) > 0, lu
    assert int(lu["armed"]) == 0 and int(lu["list"]) == 1, lu

    # (b) exhaustion: every slot filled, place-again refused, no
    # double-place, zero-free ghost parked at -1.
    fill = _only(out, "REFUSE-FILL")
    assert int(fill["placed"]) == nslots - 1 and \
        int(fill["list"]) == nslots, (fill, boot)
    slot = _only(out, "REFUSE-SLOT")
    assert slot["ok"] == "false" and slot["why"] == "slot", slot
    assert slot["why2"] == "slot", "place-again double-placed: %s" % slot
    assert int(slot["list"]) == nslots and int(slot["nodes"]) == nslots, \
        "exhaustion grew a defense: %s" % slot
    assert int(slot["ghost"]) == -1, slot
    # green arithmetic: start 300, minus the CONTROL place, plus a
    # top-up of (nslots-1)*MIN_COST + MIN_COST, minus the FILL of
    # (nslots-1)*MIN_COST -> back to EXACTLY the start green. Every
    # refusal wrote zero gold or this trips.
    assert int(slot["green"]) == int(boot["green"]), slot

    # (e) ack-delta 0: the baseline never moved across the matrix.
    ack = _only(out, "REFUSE-ACK")
    assert int(ack["start"]) == int(boot["ack"]) \
        and int(ack["end"]) == int(boot["ack"]) and int(ack["delta"]) == 0, \
        (ack, boot)

    # The save file (name READ from save_store.gd) DID land in the
    # isolated data_home tree (the boot write proves the BN4 lever
    # works and the developer's real save was never the target); with
    # the ack-delta at 0 and stderr EMPTY (a failed write prints), NO
    # refusal, and no mission play, ever reached GWSaveStore.write.
    save = _save_name()
    hits = [os.path.join(dp, f) for dp, _, fs in
            os.walk(tmp_path / "user_home") for f in fs if f == save]
    assert hits, "isolated save tree never saw even the boot write: %s" % \
        ack
