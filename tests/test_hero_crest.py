"""v1.2.1 G7 — hero identity at the shipped rig (MC 11695 / V121-PLAN G7).

Contract (V121-PLAN §G7, camera LOCKED — pin #3 SPENT, zero rig edits):
(a) sprite_bank gains WORLD_H_HERO (> WORLD_H_UNIT); hero pawns scale
    their sheet to it so the hero reads bigger than the 2u mobs — the
    enemies keep WORLD_H_UNIT (negative leg: enemy sheet height pinned
    byte-unchanged at 2.0). (b) every pawn carries a name CREST child —
    the hero's own sheet miniature + its heroes.json name through
    world_text.make_text (Label3D camera-facing by default), parented
    in hero_pawn.setup_pawn. The crest rides the pawn visibility swap
    (hero_controller._sync_pawns, UNTOUCHED — no new mechanism): exactly
    the active hero's crest is visible, and an F1-F3 press through the
    shipped swap path moves the visible crest to the NEW active name.

ENGINE LEG (conftest.run_probe_script idiom, G6's tmp-probe shape — the
probe is generated into tmp_path, so the repo stays G6-clean: world_text
is still the only Label3D site): boots the REAL mission under -s, and
drives ONLY shipped entries — bridge presses, mission.step, the rig's
own _sync_pawns. Rows: CREST (per pawn: text/sheet/billboard/visible),
HEIGHT (hero vs enemy world heights read off live nodes), FOLLOW (the
crest's offset above the rig before/after a bridge-driven move, EPS
declared here at 0.01), SWAP + SWAPBACK (F2 then F1 through the shipped
path; NEG: non-active names absent from the visible set).

DATA LEGS re-derive from the shipped JSON — crest text == heroes.json
"name" per id; WORLD_H_HERO/WORLD_H_UNIT parsed from sprite_bank.gd.
SOURCE-TRUTH LEGS: the crest mounts exactly once in setup_pawn, rides
make_text (never a hand-rolled Label3D), resolves the name through the
GWTables array door (no name literals in hero_pawn.gd), and the hero
call is the ONLY caller of WORLD_H_HERO (enemies untouched).

PLANTED-RED (fleet gate rule) rides G7-wave.log: the shipped swap hook
(hero_controller.step's _sync_pawns call) removed -> the SWAP leg goes
RED; transcript beside the green one, hero_controller.gd restored.
"""

import json
import re
import sys

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: the gate's blank_code)

BANK_GD = conftest.repo_path("godot", "scripts", "sprite_bank.gd")
PAWN_GD = conftest.repo_path("godot", "scripts", "hero_pawn.gd")
RUNNER_GD = conftest.repo_path("godot", "scripts", "enemy_runner.gd")
HEROES = json.load(open(conftest.repo_path(
    "godot", "data", "heroes.json"), encoding="utf-8"))
NAMES = {r["id"]: r["name"] for r in HEROES}
DECK = ["warden", "deadeye", "embercaller"]   # the probe deck seed (v11/g1)
EPS = 0.01          # declared eps for the FOLLOW/height comparisons

# key=value fields whose values may contain spaces (crest names) — a
# value runs until the next ` key=` or end of row.
FIELD_RE = re.compile(r"([A-Za-z_]\w*)=((?:(?!\s[A-Za-z_]\w*=).)*)")

PROBE_SRC = '''\
# v121_g7_hero_identity probe — hero scale + name crest under -s.
# Boot idiom = g1_gate_eye_probe (mission.tscn, _ready + setup driven
# directly, pinned seed) AND ITS FRAME-4 _process LEG HOME: under -s
# nothing is inside the tree during _init (measured: is_inside_tree()
# false for root-added nodes until the tree activates), so global
# transforms and is_visible_in_tree() are read from frame 4 onward —
# the G6 tmp-probe never needed tree state, this one does (declared).
# Drives ONLY shipped entries: bridge.on_key (F2/F1 swap, KeyD held
# move), mission.step (manual deterministic sub-legs), the rig's
# shipped _sync_pawns. Rows: CREST HEIGHT FOLLOW SWAP SWAPBACK OK;
# any failure prints G7C-FAIL <why>, quit 1, and the _failed flag
# skips every later leg (a late quit(0) can never overwrite the 1).
# CREST_Y read from the pawn script's OWN const (the g1 GATE_EYE_Y
# pattern) — the offsets are presentation consts, the contract legs
# are the eps offsets and the deck-driven names.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")
const HERO_PAWN := preload("res://scripts/hero_pawn.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const HERO_IDS := ["warden", "deadeye", "embercaller"]   # deck seed (v11)
const EPS := 0.01                      # declared eps (mirrors the test)
const BILLBOARD_ENABLED := 1           # BaseMaterial3D.BillboardMode pin
const MOVE_FRAMES := 30                # KeyD held: 0.5 s of a real move

var _m = null
var _rig = null
var _failed := false
var _frames := 0


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(HERO_IDS.duplicate())
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	_m = packed.instantiate()
	root.add_child(_m)
	_m._ready()
	var rng := RandomNumberGenerator.new()
	rng.seed = 11695
	_m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(_m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	_rig = _m.get_node_or_null("HeroRig")
	if _rig == null:
		_fail("mission does not ship HeroRig")
		return


func _process(_delta: float) -> bool:
	if _failed:
		return true                       # quit(1) already fired
	_frames += 1
	if _frames == 4:                      # g1 idiom: tree is active now
		_crest_leg()
		if not _failed:
			_height_leg()
		if not _failed:
			_follow_leg()
		if not _failed:
			_swap_leg()
		if not _failed:
			print("G7C-OK")
			quit(0)
	return false


func _crest(id: String):
	return _rig.pawns[id].get_node_or_null("Crest")


func _labels(node: Node) -> Array:
	var out: Array = []
	for c: Node in node.get_children():
		if c is Label3D:
			out.append(c)
	return out


func _visible_names() -> Array:
	var out: Array = []
	for hid: Variant in _rig.pawns:
		var crest = _crest(String(hid))
		if crest != null and crest.is_visible_in_tree():
			for lb: Node in _labels(crest):
				out.append(String((lb as Label3D).text))
	return out


func _crest_leg() -> void:
	for hid: String in HERO_IDS:
		var pawn = _rig.pawns[hid]
		var crest = _crest(hid)
		if crest == null:
			_fail("pawn %s has no Crest child" % hid)
			return
		var lbs := _labels(crest)
		if lbs.size() != 1:
			_fail("crest %s labels = %d (want exactly 1)" % [hid, lbs.size()])
			return
		var lb: Label3D = lbs[0]
		if String(lb.text) == "":
			_fail("crest %s text empty" % hid)
			return
		if int(lb.billboard) != BILLBOARD_ENABLED:
			_fail("crest %s not camera-facing: %d" % [hid, int(lb.billboard)])
			return
		var sheet := crest.get_node_or_null("CrestSheet") as Sprite3D
		print(("G7C-CREST id=%s text=%s sheet=%d labels=1 billboard=1 " \
				+ "visible=%d") % [hid, String(lb.text),
				1 if sheet != null else 0,
				1 if crest.is_visible_in_tree() else 0])
	var vis := _visible_names()
	if vis.size() != 1:
		_fail("visible crests at boot = %s (want exactly 1)" % str(vis))
		return
	print("G7C-ACTIVE active=%s names=%s" \
			% [String(_m.deck[int(_m.active)]), String(vis[0])])


func _eff_h(spr: Sprite3D) -> float:
	return float(spr.texture.get_height()) * float(spr.pixel_size) \
			* float(spr.scale.y)


func _height_leg() -> void:
	var spr: Sprite3D = _rig.pawns[HERO_IDS[0]].get_node("Sprite")
	if spr == null:
		_fail("hero pawn has no Sprite (greybox never sprited)")
		return
	var hero_h := _eff_h(spr)
	var espr := SPRITE_BANK.make_sprite("skitterling",
			SPRITE_BANK.WORLD_H_UNIT)
	if espr == null:
		_fail("bank has no enemy sheet to measure")
		return
	var enemy_h := _eff_h(espr)
	espr.free()
	if hero_h <= enemy_h + EPS:
		_fail("hero does not read bigger: hero=%s enemy=%s" \
				% [str(hero_h), str(enemy_h)])
		return
	print("G7C-HEIGHT hero_h=%.6f enemy_h=%.6f" % [hero_h, enemy_h])


func _active_crest():
	return _crest(String(_m.deck[int(_m.active)]))


func _off(crest) -> Vector3:
	return crest.global_position - _rig.global_position


func _follow_leg() -> void:
	var crest = _active_crest()
	var o0 := _off(crest)
	if absf(o0.x) > EPS or absf(o0.z) > EPS \
			or absf(o0.y - float(HERO_PAWN.CREST_Y)) > EPS:
		_fail("crest not straight above the hero: off=%s" % str(o0))
		return
	var x0 := float(_rig.global_position.x)
	_m.bridge.on_key("KeyD", true)
	for _i: int in MOVE_FRAMES:
		_m.step(1.0 / 60.0)
	_m.bridge.on_key("KeyD", false)
	_m.step(1.0 / 60.0)
	var o1 := _off(crest)
	if absf(o1.x) > EPS or absf(o1.z) > EPS:
		_fail("crest did not ride the move: off=%s" % str(o1))
		return
	print("G7C-FOLLOW moved=%.6f off_x=%.6f off_y=%.6f off_z=%.6f" \
			% [float(_rig.global_position.x) - x0, o1.x, o1.y, o1.z])


func _swap_leg() -> void:
	_m.bridge.on_key("F2", true)
	_m.bridge.on_key("F2", false)
	_m.step(1.0 / 60.0)      # step (5) records the swap ...
	_m.step(1.0 / 60.0)      # ... the next slot-(2) tick paints it
	if int(_m.active) != 1:
		_fail("F2 never swapped: active=%d" % int(_m.active))
		return
	var vis := _visible_names()
	if vis.size() != 1:
		_fail("visible crests after swap = %s" % str(vis))
		return
	print("G7C-SWAP active=%s names=%s" \
			% [String(_m.deck[1]), String(vis[0])])
	_m.bridge.on_key("F1", true)
	_m.bridge.on_key("F1", false)
	_m.step(1.0 / 60.0)
	_m.step(1.0 / 60.0)
	if int(_m.active) != 0:
		_fail("F1 never swapped back: active=%d" % int(_m.active))
		return
	var vis2 := _visible_names()
	if vis2.size() != 1:
		_fail("visible crests after swapback = %s" % str(vis2))
		return
	print("G7C-SWAPBACK active=%s names=%s" \
			% [String(_m.deck[0]), String(vis2[0])])


func _fail(why: String) -> void:
	_failed = true
	print("G7C-FAIL " + why)
	quit(1)
'''


def _run_probe(tmp_path):
    probe = tmp_path / "v121_g7_hero_identity.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (), tmp_path / "user_home")


def _rows(out, tag):
    return [_fields(ln) for ln in out.splitlines()
            if ln.startswith(tag + " ")]


def _fields(line):
    return {k: v.strip() for k, v in FIELD_RE.findall(line)}


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _const(path, name):
    m = re.search(r"^const %s := (\d+(?:\.\d+)?)" % name, _read(path), re.M)
    assert m, "const %s missing in %s" % (name, path)
    return float(m.group(1))


def test_crest_mount_height_follow_swap_engine(tmp_path, class_cache):
    proc = _run_probe(tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "G7C-FAIL" not in out, out
    assert out.rstrip().splitlines()[-1].startswith("G7C-OK"), out

    # CREST leg + DATA leg: one crest per pawn, exactly one Label3D,
    # camera-facing, sheet on every deck hero, and the text EQUALS the
    # heroes.json name for THAT pawn (names re-derived, never copied).
    crest = {r["id"]: r for r in _rows(out, "G7C-CREST")}
    assert set(crest) == set(DECK), out
    for hid, row in crest.items():
        assert row["text"] == NAMES[hid], (hid, row)
        assert (row["sheet"], row["labels"], row["billboard"]) == \
            ("1", "1", "1"), (hid, row)
    # the boot ACTIVE leg: exactly the deck[0] crest visible — the NEG
    # reading: the two non-active names are absent from the visible set
    # (only one visible crest exists, and it carries deck[0]'s name).
    act = _rows(out, "G7C-ACTIVE")[0]
    assert act["active"] == DECK[0] and act["names"] == NAMES[DECK[0]], out
    assert (crest[DECK[0]]["visible"], crest[DECK[1]]["visible"],
            crest[DECK[2]]["visible"]) == ("1", "0", "0"), out

    # HEIGHT leg: the hero's live world height == WORLD_H_HERO and the
    # enemy sheet height == WORLD_H_UNIT, both parsed from sprite_bank
    # (NEG: the enemy read stays the byte-pinned 2.0).
    h = _rows(out, "G7C-HEIGHT")[0]
    hero_c = _const(BANK_GD, "WORLD_H_HERO")
    unit_c = _const(BANK_GD, "WORLD_H_UNIT")
    assert hero_c > unit_c, (hero_c, unit_c)
    assert abs(float(h["hero_h"]) - hero_c) < EPS, h
    assert abs(float(h["enemy_h"]) - 2.0) < EPS, \
        "enemy sheet height drifted off the byte-pinned 2.0: %s" % h

    # FOLLOW leg (eps-declared): after a bridge-driven move the crest
    # still sits straight above the rig at its mount height — the crest
    # rides the hero node it is parented under.
    f = _rows(out, "G7C-FOLLOW")[0]
    assert float(f["moved"]) > 0.05, f          # the hero really moved
    assert abs(float(f["off_x"])) < EPS and abs(float(f["off_z"])) < EPS, f
    assert abs(float(f["off_y"]) - _const(PAWN_GD, "CREST_Y")) < EPS, f

    # SWAP legs through the SHIPPED path (bridge presses -> mission
    # step (5) -> _sync_pawns): after F2 the ONLY visible crest carries
    # deck[1]'s heroes.json name; after F1 deck[0]'s. NEG: the other
    # two names are absent from the visible set every step.
    sw = _rows(out, "G7C-SWAP")[0]
    assert sw["active"] == DECK[1] and sw["names"] == NAMES[DECK[1]], out
    assert NAMES[DECK[0]] not in sw["names"] and \
        NAMES[DECK[2]] not in sw["names"], out
    sb = _rows(out, "G7C-SWAPBACK")[0]
    assert sb["active"] == DECK[0] and sb["names"] == NAMES[DECK[0]], out
    assert NAMES[DECK[1]] not in sb["names"] and \
        NAMES[DECK[2]] not in sb["names"], out


def test_hero_scale_is_a_presentation_only_swap():
    """(a)-row source truth: hero_pawn scales its sheet with the NEW
    heroes-only const; WORLD_H_UNIT keeps its byte-pinned 2.0 value and
    the enemy caller is unchanged — enemies keep the 2u read (plan
    negative leg: 'enemy sheet heights byte-unchanged')."""
    assert re.search(r"^const WORLD_H_UNIT := 2\.0\b", _read(BANK_GD), re.M), \
        "WORLD_H_UNIT drifted off the byte-pinned 2.0"
    pawn = _read(PAWN_GD)
    assert pawn.count("SPRITE_BANK.WORLD_H_HERO") == 1, pawn
    assert "SPRITE_BANK.WORLD_H_UNIT" not in pawn, \
        "the pawn must not read the enemy/unit const"
    assert "SPRITE_BANK.WORLD_H_UNIT" in _read(RUNNER_GD), \
        "enemy_runner no longer mounts at WORLD_H_UNIT"


def test_crest_rides_shipped_factories_source_truth():
    """(b)-row source truth: exactly ONE crest per pawn, mounted in
    setup_pawn; the name line rides world_text.make_text (world_text
    stays the ONLY Label3D site — hero_pawn never hand-rolls one) and
    the name is data read through the GWTables array door — no name
    literals in hero_pawn.gd (I2-safe strings)."""
    pawn = _read(PAWN_GD)
    assert pawn.count("add_child(_make_crest(id))") == 1, pawn
    body = pawn[pawn.index("func _make_crest("):]
    assert body.count("WORLD_TEXT.make_text(") == 1, body
    assert "Label3D" not in hyg.blank_code(pawn, "gd"), \
        "hero_pawn must not touch Label3D — world_text is the one site"
    assert 'GW_TABLES.new().rows("heroes")' in pawn, pawn
    for name in NAMES.values():
        assert name not in pawn, "crest name literal in hero_pawn: %s" % name

