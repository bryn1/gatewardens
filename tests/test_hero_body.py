"""v1.6 P4a — the hero is a readable primitive-composed body (MC 12083,
V16-PLAN §3 V-D / §1 A4).

Contract: at the FROZEN rig (camera_zoom.gd / mission.tscn ZERO lines —
OD1 ANSWERED DEFER, fixed framing) the ~8-px billboard speck of the
F-BUILD frame becomes a body per ARCHETYPE: BoxMesh/CylinderMesh parts
(L5 — zero runtime ArrayMesh), tinted by the shipped mat_hero_<id>.tres
REUSED, silhouette inside the WORLD_H_HERO 3u door with feet on the
origin. The main sheet hides through the shipped visibility-swap idiom
(the declared P4a composition after the SERVED TRUTH that a pawn at the
origin renders INSIDE the 3x4x3 core box — the figure stands BODY_-
OFFSET camera-side, the crest miniature rides the origin as its medall-
ion backdrop; the sheet survives visibly only in that 1.2u miniature
and its G7 eff_h pin stays green on the hidden node — test_hero_crest.py
stands UNTOUCHED). The crest block is the
P8 shipped contract: BYTE-PINNED here (consts + the verbatim
_make_crest body), zero sim writes (L7 — a source-truth leg).

ENGINE LEG = conftest.run_probe_script (G7/P1 tmp-probe idiom, seed
12083 declared; frame-4 tree reads per the g1/G7 lesson; HB-* rows,
in-probe HB-FAIL guards, HB-OK LAST). Albedos and archetypes are
re-derived PYTHON-SIDE from the .tres files and heroes.json so a plant
cannot agree green. PLANTED-RED (fleet L3, rides VD-wave.log): the body
builder returns null -> HB-BODY RED; byte-verified revert.
"""

import json
import re
import sys

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: the gate's blank_code)

PAWN_GD = conftest.repo_path("godot", "scripts", "hero_pawn.gd")
BANK_GD = conftest.repo_path("godot", "scripts", "sprite_bank.gd")
HEROES = json.load(open(conftest.repo_path(
    "godot", "data", "heroes.json"), encoding="utf-8"))
ARCH = {r["id"]: r["archetype"] for r in HEROES}
DECK = ["warden", "deadeye", "embercaller"]   # the probe deck seed
EPS = 0.01                    # declared eps (mirrors the probe's)


def _tres_albedo(hero_id):
    """The shipped .tres tint parsed from the committed asset — the
    reuse control: the body's live albedo must EQUAL these bytes."""
    src = open(conftest.repo_path("godot", "assets",
                                  "mat_hero_%s.tres" % hero_id),
               encoding="utf-8").read()
    m = re.search(r"albedo_color = Color\(([^)]*)\)", src)
    assert m, "no albedo_color in mat_hero_%s.tres" % hero_id
    return [float(v) for v in m.group(1).split(",")[:3]]


# The verbatim P8 crest factory — byte-pinned: this card edits NOTHING
# inside it (V16-PLAN V-D "crest block byte-untouched").
CREST_BLOCK = (
    'func _make_crest(id: String) -> Node3D:\n'
    '\tvar crest := Node3D.new()\n'
    '\tcrest.name = "Crest"\n'
    '\tcrest.position = Vector3(0.0, CREST_Y, 0.0)\n'
    '\tvar sheet := SPRITE_BANK.make_sprite(id, CREST_SHEET_H)\n'
    '\tif sheet != null:\n'
    '\t\tsheet.name = "CrestSheet"\n'
    '\t\tcrest.add_child(sheet)\n'
    '\tvar label := WORLD_TEXT.make_text(hero_name(id),\n'
    '\t\t\tVector3(0.0, CREST_NAME_DY, 0.0), CREST_NAME_H,\n'
    '\t\t\tCREST_NAME_OUTLINE)\n'
    '\tlabel.name = "CrestName"\n'
    '\tcrest.add_child(label)\n'
    '\treturn crest')

PROBE_SRC = '''\
# v16_vd_hero_body probe — the P4a composed body under -s. Boot idiom =
# test_hero_crest's G7 shape (mission.tscn, _ready + setup driven, pinned
# seed 12083 — declared); frame-4 tree reads (under -s nothing is inside
# the tree before the tree activates — the g1/G7 lesson). Drives ZERO
# sim mutators: reads only node state + the heroes.json array door.
# Rows: BODY SPRITE OK; any failure prints HB-FAIL <why>, quit(1), and
# the completion flag skips every later leg (a late quit(0) can never
# overwrite the 1).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const HERO_PAWN := preload("res://scripts/hero_pawn.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const HERO_IDS := ["warden", "deadeye", "embercaller"]   # deck seed
const EPS := 0.01

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
	rng.seed = 12083
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
	if _frames == 4:                      # g1/G7 idiom: tree is active
		_body_leg()
		if not _failed:
			_sprite_leg()
		if not _failed:
			print("HB-OK")
			quit(0)
	return false


func _body_leg() -> void:
	for hid: String in HERO_IDS:
		var pawn = _rig.pawns[hid]
		var body = pawn.get_node_or_null("Body")
		if body == null:
			_fail("pawn %s has no Body child" % hid)
			return
		var parts: Array = []
		for c: Node in body.get_children():
			if c is MeshInstance3D:
				parts.append(c)
		if parts.size() < 3:
			_fail("body %s parts = %d (want >= 3, composed)" \\
					% [hid, parts.size()])
			return
		var want: Color = HERO_PAWN.MATS[hid].albedo_color
		var mism := 0
		var top := -1000.0
		var bot := 1000.0
		var finger := ""
		for i: int in parts.size():
			var mi: MeshInstance3D = parts[i]
			if mi.material_override == null:
				mism += 1
			elif (absf(mi.material_override.albedo_color.r - want.r) > EPS
					or absf(mi.material_override.albedo_color.g - want.g) \\
					> EPS or absf(mi.material_override.albedo_color.b \\
					- want.b) > EPS):
				mism += 1
			var a: AABB = mi.global_transform * mi.get_aabb()
			top = maxf(top, float(a.end.y) - float(_rig.global_position.y))
			bot = minf(bot, float(a.position.y) \\
					- float(_rig.global_position.y))
			if i > 0:
				finger += "|"
			finger += "%s:%.2f,%.2f,%.2f" % [mi.mesh.get_class(),
					mi.position.x, mi.position.y, mi.position.z]
		print(("HB-BODY id=%s arch=%s parts=%d mat=%d alb=%.5f,%.5f,%.5f" \\
				+ " bpos=%.5f,%.5f,%.5f top=%.5f bot=%.5f finger=%s") \\
				% [hid, HERO_PAWN.hero_archetype(hid), parts.size(),
					1 if mism == 0 else 0, want.r, want.g, want.b,
					body.global_position.x, body.global_position.y,
					body.global_position.z, top, bot, finger])


func _sprite_leg() -> void:
	for hid: String in HERO_IDS:
		var spr: Sprite3D = _rig.pawns[hid].get_node_or_null("Sprite")
		if spr == null:
			_fail("pawn %s lost its Sprite node (G7 pin)" % hid)
			return
		var eff := float(spr.texture.get_height()) * float(spr.pixel_size) \\
				* float(spr.scale.y)
		var crest = _rig.pawns[hid].get_node_or_null("Crest/CrestSheet")
		print("HB-SPRITE id=%s eff=%.6f vis=%d sheet=%d" \\
				% [hid, eff, 1 if spr.visible else 0,
					1 if crest != null else 0])


func _fail(why: String) -> void:
	_failed = true
	print("HB-FAIL " + why)
	quit(1)
'''


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _const(path, name):
    m = re.search(r"^const %s := (\d+(?:\.\d+)?)" % name, _read(path), re.M)
    assert m, "const %s missing in %s" % (name, path)
    return float(m.group(1))


def _body_offset():
    m = re.search(r"const BODY_OFFSET := Vector3\(([^)]*)\)", _read(PAWN_GD))
    assert m, "const BODY_OFFSET missing in hero_pawn.gd"
    return [float(v) for v in m.group(1).split(",")]


def _rows(out, tag):
    rows = {}
    for ln in out.splitlines():
        if ln.startswith(tag + " "):
            fields = dict(p.split("=", 1) for p in ln.split()[1:])
            rows[fields["id"]] = fields
    return rows


def test_hero_body_engine_probe(tmp_path, class_cache):
    probe = tmp_path / "v16_vd_hero_body.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), (),
                                     tmp_path / "user_home")
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "HB-FAIL" not in out, out
    assert out.rstrip().splitlines()[-1].startswith("HB-OK"), out

    body = _rows(out, "HB-BODY")
    assert set(body) == set(DECK), out
    door = _const(BANK_GD, "WORLD_H_HERO")
    fingers = set()
    for hid in DECK:
        row = body[hid]
        # ARCHETYPE leg: shape selection is DATA — the printed archetype
        # equals heroes.json for THIS id (re-derived, never copied).
        assert row["arch"] == ARCH[hid], (hid, row)
        assert int(row["parts"]) >= 3, (hid, row)
        # TINT-REUSE leg: every part carries the shipped .tres albedo
        # (values parsed from the committed asset, EPS-declared).
        assert row["mat"] == "1", (hid, row)
        want = _tres_albedo(hid)
        got = [float(v) for v in row["alb"].split(",")]
        assert all(abs(g - w) < EPS for g, w in zip(got, want)), (hid, row)
        # DOOR leg: the silhouette stands on the origin inside the
        # WORLD_H_HERO gate (feet ~0, top >= 2.0u readable floor —
        # declared: a flat blob reddens).
        assert -EPS <= float(row["bot"]) <= 0.25, (hid, row)
        assert 2.0 <= float(row["top"]) <= door + EPS, (hid, row)
        # OFFSET leg: the figure stands BODY_OFFSET (parsed from
        # hero_pawn.gd itself) camera-side of the pawn origin — the
        # served truth (§COMPOSITION: the 3x4x3 core box swallows a
        # pawn at the origin). x/y must stay 0 (visual offset ONLY).
        off = _body_offset()
        got_off = [float(v) for v in row["bpos"].split(",")]
        assert all(abs(g - w) < EPS for g, w in zip(got_off, off)), (hid, row)
        assert off[2] > 0.0, "figure must stand camera-side"
        # PRIMITIVE LAW leg (L5): only engine-managed part classes.
        for tok in row["finger"].split("|"):
            assert tok.split(":")[0] in ("BoxMesh", "CylinderMesh"), row
        fingers.add(row["finger"])
    # PER-ARCHETYPE leg: three distinct composed silhouettes.
    assert len(fingers) == 3, out

    # FACE-MARK leg (declared composition): the G7 sheet node stays
    # byte-pinned at WORLD_H_HERO eff-height but rides HIDDEN; the
    # crest's 1.2u sheet miniature is the surviving visible sheet
    # instance (medallion backdrop at the origin).
    spr = _rows(out, "HB-SPRITE")
    assert set(spr) == set(DECK), out
    for hid in DECK:
        row = spr[hid]
        assert abs(float(row["eff"]) - door) < EPS, (hid, row)
        assert row["vis"] == "0", (hid, row)
        assert row["sheet"] == "1", (hid, row)


def test_crest_byte_pinned_and_zero_sim_writes():
    """The V-D byte-laws, source-side: the crest consts and the verbatim
    _make_crest body are byte-untouched (P8 shipped); the body mounts
    exactly once per pawn; the sheet hide is the shipped swap idiom;
    hero_pawn.gd writes ZERO sim state and breaks no mesh/texture law
    (L5/L7 source truth — the file stays read-only over the sim)."""
    pawn = _read(PAWN_GD)
    for name, value in (("CREST_Y", "2.4"), ("CREST_SHEET_H", "1.2"),
                        ("CREST_NAME_DY", "2.55"), ("CREST_NAME_H", "1.1"),
                        ("CREST_NAME_OUTLINE", "10")):
        assert re.search(r"^const %s := %s[ \t]*(?:#.*)?$"
                         % (name, re.escape(value)),
                         pawn, re.M), "crest const drifted: %s" % name
    assert CREST_BLOCK in pawn, "_make_crest body is not byte-identical"
    assert pawn.count("add_child(_make_crest(id))") == 1, pawn
    # body: mounted once, sheet hidden through the shipped swap idiom,
    # archetype read through the ONE array door (G7's WORLD_H_HERO pin
    # stays single-call).
    assert pawn.count("add_child(body)") == 1, pawn
    assert pawn.count("sprite.visible = false") == 1, pawn
    assert pawn.count("SPRITE_BANK.WORLD_H_HERO") == 1, pawn   # G7 pin
    assert 'GW_TABLES.new().rows("heroes")' in pawn, pawn
    # ZERO-SIM-WRITES + mesh law (L5/L7), blanked to the SAME code
    # universe check_hygiene walks.
    code = hyg.blank_code(pawn, "gd")
    for banned in ("mission", "hero_state", "hero_defs", "deck",
                   "bridge", "phase", "gold", "step(", "ArrayMesh",
                   "get_image", "SurfaceTool", "randf", "randi"):
        assert banned not in code, "sim/mesh token in pawn code: %s" % banned
