"""v1.6 V-A fortress plateau (MC card 12081 / V16-PLAN-c2 §3 W1 V-A —
the look-and-feel HEART): the flat checkered board in a void becomes a
fortress on stone.

THE CONTRACT (plan row 1 + row 1b): the play plane stays the FORTRESS
TOP — height lives OUTSIDE/BELOW the grid (cliff-skirt plateau mass,
rim walls + corner towers, one gatehouse per spawner, a keep under the
main core) so placement coords/cells/ranges NEVER move (slots are
discrete candidates from defense_placer._build_slots; zero raycasts
exist — DA N1 keeps the :47 comment word VESTIGIAL). Geometry is
engine-managed PrimitiveMesh ONLY (BoxMesh/CylinderMesh — the G2
web-raster law, kb 2d5274003; the committed core BoxMesh already
proves that class rasterizes on web). Fortress budget <= 30 primitives
(DA F-2, the scene's first shadow-casting geometry). The ground
albedo id `ground_arena` REMAPS (replace-not-add) to the clean-room
flagstone sheet; fortress_stone.png is the masonry sheet with diorama.gd
its only consumer. The row-1b icons (icon_core / icon_gate_eye /
icon_gate_eye_air) are IN-PLACE redraws: SAME paths, ids and 512x512
sizes, so test_gate_eye's id->PATH pins stay green WITHOUT re-pin.

ENGINE LEG: the embedded kit probe (test_kit_fx R5 tmp-probe idiom —
godot/sim/ is FROZEN, L7, so the probe lands with this file, not there)
boots mission.tscn (E5, pinned seed) and asserts, DG-* rows with
in-probe DG-FAIL guards + DG-OK-LAST + a completion flag (the G2
silent-abort lesson): CONTAINER exactly one "Fortress" node at the
origin; COUNT the pinned primitive census AND the <=30 budget; CLASS
every mesh is a BoxMesh/CylinderMesh AND a PrimitiveMesh (the
web-proof proxy); LIT the DECLARED shadow ruling — nothing casts, every
node carries the emission floor (env_greybox ambient is DISABLED: the
scene's first shaded geometry would paint black faces/shadows on web;
V-E owns the env re-tune and the flip-back); PLATEAU top face byte-flush
with the play plane y 0;
GROUND the node transform + mesh AABB byte-pinned (THE grid-frozen
proof — pre == the scene's own values); FLOOR the remapped flagstone
albedo path pinned by committed resource path, repeat OFF, modulate
pinned; GATE one tower pair + lintel per spawner (spawners, not lanes —
the exact-count pin is the NEG leg: a loop over the 5 lane rows instead
of the 3 spawners changes the census and cannot ride the green);
KEEP the keep box at the main-core pos + 4 turrets; AABB the container
union inside declared bounds; SCREEN the keep and gate centers project
INSIDE the served viewport through the SHIPPED Camera3D.

SOURCE-TRUTH LEGS (pytest cannot exec GDScript — the test_lane_bands/
test_kit_fx idiom parses the .gd text after blanking comments): ONE
build_fortress call in build_cores; diorama.gd assigns NOTHING onto m
(visual-only), ONE add_child site, ONE construction site per primitive
class, no retired ArrayMesh/raw-array/get_image tokens, no RNG; the
bank row remap is the one replace-not-add line; the committed PNGs keep
their pinned pixel sizes (PNG header read, stdlib struct).

PLANTED-REDs (L3, transcripts in VA-wave.log, byte-verified reverts):
(1) hook removed from build_cores -> container leg DG-FAIL rc1;
(2) budget plant 31 -> COUNT leg DG-FAIL rc1.
"""

import re
import struct
from pathlib import Path

import conftest

GODOT = Path(conftest.repo_path("godot"))
WORLD_GD = GODOT / "scripts" / "mission_world.gd"
DIO_GD = GODOT / "scripts" / "diorama.gd"
BANK_GD = GODOT / "scripts" / "sprite_bank.gd"
V11 = GODOT / "assets" / "v11"

FLOOR_PATH = "res://assets/v11/ground_fortress.png"
STONE_PATH = "res://assets/v11/fortress_stone.png"
SPAWNERS = {"spawn_a", "spawn_b", "spawn_c"}
N_PRIM = 23          # the pinned census: 9 boxes + 14 cylinders
MAX_PRIM = 30        # DA F-2 budget (diorama.gd's own const, re-pinned)
ARENA_MOD = (0.9, 0.9, 0.95)     # ARENA_MODULATE, literal-pinned (the
                                 # v1 probe "bank-never-oracle" rule)
# The ground invariants v1_world_probe pinned from mesh_plane.tres —
# THE grid-frozen byte-pin (numeric compare, never a string compare):
GND_POS = (0.0, 0.0, 0.0)
GND_ROT = (0.0, 0.0, 0.0)
GND_SCALE = (1.0, 1.0, 1.0)
GND_AABB_MIN = (-80.0, 0.0, -80.0)
GND_AABB_SIZE = (160.0, 0.0, 160.0)
# Fortress union bounds (rim/plateau reach x,z +-84; keep turrets top
# 7.5; plateau bottom -22) — EPS-wide, the union is a sanity bound, the
# per-node transforms are what the pins above nail.
AABB_MIN = (-84.5, -22.5, -84.5)
AABB_MAX = (84.5, 7.6, 84.5)

WRITE_RE = re.compile(
    r"(?<![\w.])m\.[\w.\[\]\"']*\s*(?:[+\-*/]?=[^=])")
MUT_RE = re.compile(r"\b(?:add_|spend_|consume_|set_|equip|place_)\w*\s*\(")
PLUMBING = {"add_child"}

PROBE_SRC = '''
extends SceneTree
# gw diorama probe (v1.6 V-A, MC 12081). Boot idiom = g2_lane_band_probe
# (itself g1/v1_world): mission.tscn instantiated, _ready + setup driven
# directly (E5), pinned seed, root.size = the served canvas. Machine
# rows DG-CONTAINER/-COUNT/-CLASS/-PLATEAU/-GROUND/-FLOOR/-GATE/-KEEP/
# -AABB/-SCREEN, any failed check prints DG-FAIL <detail> + quit(1); a
# skipped leg can never reach DG-OK (LAST print, completion-flag guarded).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DIORAMA := preload("res://scripts/diorama.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const VIEW := Vector2i(1280, 720)
const N_PRIM := 23                 # pinned census (9 box + 14 cyl)
const GROUND_PATH := "res://assets/v11/ground_fortress.png"
const REPEAT_OFF := false          # 4.7.2 BOOL property (pinned literal)
const MOD := Color(0.9, 0.9, 0.95) # ARENA_MODULATE pinned LITERAL
const GND_AABB_MIN := Vector3(-80, 0, -80)
const GND_AABB_SIZE := Vector3(160, 0, 160)
const EPS := 0.05

var _failed := false
var _done := false
var _frames := 0
var _m = null


func _init() -> void:
	root.size = VIEW
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(DECK.duplicate())
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()
	var rng := RandomNumberGenerator.new()
	rng.seed = 12081
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	_m = m


func _process(_delta: float) -> bool:
	if _failed:
		return true
	_frames += 1
	if _frames == 2:
		root.size = VIEW
		return false
	if _frames == 4:
		_pass(_m)
		if not _failed:
			if not _done:
				_fail("diorama pass aborted mid-way (completion flag unset)")
			else:
				print("DG-OK")
				quit(0)
	return false


func _corners(mi: MeshInstance3D) -> Array:
	var la: AABB = mi.mesh.get_aabb()
	var gt: Transform3D = mi.global_transform
	var out: Array = []
	for i: int in 8:
		var c := Vector3(la.end.x if i & 1 == 1 else la.position.x,
				la.end.y if i & 2 == 2 else la.position.y,
				la.end.z if i & 4 == 4 else la.position.z)
		out.append(gt * c)
	return out


func _meshes(fort) -> Array:
	var out: Array = []
	for c: Node in fort.get_children():
		var mi := c as MeshInstance3D
		if mi == null:
			_fail("Fortress child %s is not a MeshInstance3D" % str(c.name))
			return out
		out.append(mi)
	return out


func _pass(m) -> void:
	# CONTAINER: exactly ONE Fortress node, at the mission origin.
	var forts: Array = []
	for c: Node in m.get_children():
		if String(c.name) == DIORAMA.FORTRESS_NAME:
			forts.append(c)
	if forts.size() != 1:
		_fail("CONTAINER Fortress nodes = %d (want 1)" % forts.size())
		return
	var fort := forts[0] as Node3D
	if fort == null or fort.position != Vector3.ZERO \\
			or fort.scale != Vector3.ONE:
		_fail("CONTAINER Fortress not at identity transform")
		return
	print("DG-CONTAINER n=1")
	# COUNT + CLASS: pinned census, budget, PrimitiveMesh-only (the web
	# law: the G2 runtime ArrayMesh never rasterized; BoxMesh/CylinderMesh
	# are engine-managed and the committed core BoxMesh already paints).
	var meshes := _meshes(fort)
	if _failed:
		return
	var n := meshes.size()
	if n != N_PRIM or n > DIORAMA.MAX_PRIMITIVES:
		_fail("COUNT primitives = %d (want %d pinned, budget %d)" % [
				n, N_PRIM, DIORAMA.MAX_PRIMITIVES])
		return
	var boxes := 0
	var cyls := 0
	for mi: MeshInstance3D in meshes:
		if mi.mesh is BoxMesh:
			boxes += 1
		elif mi.mesh is CylinderMesh:
			cyls += 1
		else:
			_fail("CLASS %s mesh %s not BoxMesh/CylinderMesh" % [
					str(mi.name), str(mi.mesh.get_class())])
			return
		if not mi.mesh is PrimitiveMesh:
			_fail("CLASS %s not PrimitiveMesh (web-dead class)" \
					% str(mi.name))
			return
	print("DG-COUNT n=%d max=%d" % [n, DIORAMA.MAX_PRIMITIVES])
	print("DG-CLASS boxes=%d cyls=%d prim=1" % [boxes, cyls])
	# LIT: the DECLARED shadow ruling (env_greybox ambient is DISABLED —
	# the served-leg contradiction): NO fortress node casts shadows and
	# EVERY material carries the emission floor (no black faces on web).
	var cast_on := 0
	var emit_ok := 0
	for mi: MeshInstance3D in meshes:
		if mi.cast_shadow != 0:      # GeometryInstance3D OFF literal
			cast_on += 1
		var mo := mi.material_override as StandardMaterial3D
		if mo != null and mo.emission_enabled:
			emit_ok += 1
	if cast_on != 0 or emit_ok != n:
		_fail("LIT cast_on=%d emit=%d (want 0/%d)" % [cast_on, emit_ok, n])
		return
	print("DG-LIT cast_off=1 emission=%d" % emit_ok)
	# PLATEAU: the cliff mass TOP FACE flush with the play plane y 0 —
	# the fortress is the board, the ground node itself is untouched.
	var plate := fort.get_node_or_null("Plateau") as MeshInstance3D
	if plate == null:
		_fail("PLATEAU missing")
		return
	var ptop := -1000.0
	for c: Vector3 in _corners(plate):
		ptop = maxf(ptop, c.y)
	if absf(ptop) > EPS:
		_fail("PLATEAU top y = %s (want flush 0 within %s)" % [str(ptop),
				str(EPS)])
		return
	print("DG-PLATEAU top=%.3f" % ptop)
	# GROUND: the grid-frozen byte-pin — the scene's own transform and
	# the mesh-plane AABB (mesh_plane.tres 160x160 at the origin),
	# component-wise numeric compare (the v1_world_probe pin).
	var ground := m.get_node_or_null("Ground") as MeshInstance3D
	if ground == null:
		_fail("Ground node missing")
		return
	var pos := ground.position
	var rot := ground.rotation
	var scl := ground.scale
	var aabb: AABB = ground.mesh.get_aabb()
	var ok: bool = _near(pos, Vector3.ZERO) and _near(rot, Vector3.ZERO) \\
			and _near(scl, Vector3.ONE) and m.transform.origin \\
			== Vector3.ZERO \\
			and _near(aabb.position, GND_AABB_MIN) \\
			and _near(aabb.size, GND_AABB_SIZE)
	if not ok:
		_fail("GROUND moved: pos=%s rot=%s scale=%s aabb=%s+%s " % [
				str(pos), str(rot), str(scl), str(aabb.position),
				str(aabb.size)] + "(grid-frozen pin — fortress may not " \\
				+ "touch the ground node)")
		return
	print("DG-GROUND pos=0,0,0 scale=1,1,1 aabb_min=-80,0,-80 size=160,0,160")
	# FLOOR: the remapped flagstone albedo (committed path pin, never
	# through the bank — the v11_sprite_probe bank-never-oracle lesson),
	# repeat OFF, pinned modulate.
	var mat := ground.material_override as StandardMaterial3D
	if mat == null or mat.albedo_texture == null \\
			or String(mat.albedo_texture.resource_path) != GROUND_PATH:
		_fail("FLOOR albedo not the pinned flagstone sheet: %s" % [
				str(mat.albedo_texture.resource_path) if mat != null \\
						and mat.albedo_texture != null else "null"])
		return
	if mat.texture_repeat != REPEAT_OFF:
		_fail("FLOOR flagstone repeats (framed board stays 1:1)")
		return
	if absf(mat.albedo_color.r - MOD.r) > EPS \\
			or absf(mat.albedo_color.g - MOD.g) > EPS \\
			or absf(mat.albedo_color.b - MOD.b) > EPS:
		_fail("FLOOR modulate %s != pinned %s" % [str(mat.albedo_color),
				str(MOD)])
		return
	print("DG-FLOOR tex=%s repeat=0 mod=%.3f,%.3f,%.3f" % [GROUND_PATH,
			mat.albedo_color.r, mat.albedo_color.g, mat.albedo_color.b])
	# GATE + NEG census: EXACTLY one tower-pair + lintel per SPAWNER row
	# (a loop over the 5 lane rows instead of the 3 spawners shifts the
	# census — the exact names are the negative leg).
	var gated := {}
	var extras := 0
	for mi: MeshInstance3D in meshes:
		var nm := String(mi.name)
		if not nm.begins_with("Gate_"):
			continue
		var sid := ""
		for suffix: String in ["_tower_a", "_tower_b", "_lintel"]:
			if nm.ends_with(suffix):
				sid = nm.trim_prefix("Gate_").trim_suffix(suffix)
		if sid == "" or not m.map_def.get("spawners", {}).has(sid):
			extras += 1
			continue
		gated[sid] = gated.get(sid, 0) + 1
	if extras != 0:
		_fail("NEG gate primitives at non-spawner ids: %d" % extras)
		return
	if gated.size() != m.map_def["spawners"].size() or gated.size() != 3:
		_fail("GATE gated=%d spawners=%d (want 3/3)" % [gated.size(),
				m.map_def["spawners"].size()])
		return
	for sid: String in gated:
		if int(gated[sid]) != 3:
			_fail("GATE %s parts=%s (want tower_a+tower_b+lintel)" % [
					sid, str(gated[sid])])
			return
	print("DG-GATE gated=%d spawners=%d extra=0" % [gated.size(),
			m.map_def["spawners"].size()])
	# KEEP: the keep box at the main-core pos + exactly 4 turrets.
	var keep := fort.get_node_or_null("Keep") as MeshInstance3D
	if keep == null:
		_fail("KEEP missing")
		return
	var cp: Array = m.map_def["cores"]["main"]["pos"]
	var kpos := keep.position
	if absf(kpos.x - float(cp[0])) > EPS \\
			or absf(kpos.z - float(cp[2])) > EPS:
		_fail("KEEP at %s (want main-core xz %s)" % [str(kpos), str(cp)])
		return
	var turrets := 0
	for mi: MeshInstance3D in meshes:
		if String(mi.name).begins_with("KeepTurret_"):
			turrets += 1
	if turrets != 4:
		_fail("KEEP turrets=%d (want 4)" % turrets)
		return
	print("DG-KEEP keep=%s turrets=4" % str(kpos))
	# AABB: the container union inside declared bounds (rim reach,
	# plateau bottom, turret tops) — nothing outside the declared box.
	var uni := AABB()
	var first := true
	for mi: MeshInstance3D in meshes:
		for c: Vector3 in _corners(mi):
			uni = AABB(c, Vector3.ZERO) if first \\
					else uni.merge(AABB(c, Vector3.ZERO))
			first = false
	if uni.position.x < -84.5 or uni.position.z < -84.5 \\
			or uni.position.y < -22.5 or uni.end.x > 84.5 \\
			or uni.end.z > 84.5 or uni.end.y > 7.6:
		_fail("AABB union %s+%s outside declared bounds" % [
				str(uni.position), str(uni.size)])
		return
	print("DG-AABB min=%.1f,%.1f,%.1f max=%.1f,%.1f,%.1f" % [
			uni.position.x, uni.position.y, uni.position.z,
			uni.end.x, uni.end.y, uni.end.z])
	# SCREEN: keep + gate centers project INSIDE the served viewport
	# through the SHIPPED Camera3D (unproject_position — the v1 FRAME
	# idiom; margin >= 40).
	var cam := m.get_node("CameraRig/Camera3D") as Camera3D
	if cam == null or not cam.is_current():
		_fail("SCREEN Camera3D missing or not current")
		return
	var pts := {"keep": Vector3(0, float(DIORAMA.KEEP.y), 0)}
	for sid: String in m.map_def["spawners"]:
		var p: Array = m.map_def["spawners"][sid]
		pts[sid] = Vector3(float(p[0]), float(DIORAMA.GATE_TOWER_H),
				float(p[2]))
	for key: String in pts:
		var s := cam.unproject_position(pts[key])
		if s.x < 40.0 or s.y < 40.0 or s.x > float(VIEW.x - 40) \\
				or s.y > float(VIEW.y - 40):
			_fail("SCREEN %s projects at %s outside the 40px margin" % [
					key, str(s)])
			return
		print("DG-SCREEN %s at=%.1f,%.1f margin=40" % [key, s.x, s.y])
	_done = true


func _near(v: Vector3, want: Vector3) -> bool:
	return absf(v.x - want.x) <= EPS and absf(v.y - want.y) <= EPS \\
			and absf(v.z - want.z) <= EPS


func _fail(why: String) -> void:
	_failed = true
	print("DG-FAIL " + why)
	quit(1)
'''


def _run_probe(tmp_path, class_cache):
    probe = Path(tmp_path) / "gw_diorama_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (), tmp_path / "user_home")


def _row(out, prefix):
    rows = [ln for ln in out.splitlines() if ln.startswith(prefix)]
    assert len(rows) == 1, "want exactly one %s row:\n%s" % (prefix, out)
    return rows[0]


def _nums(row, after):
    """Parse the printed 'key=a,b,c' triple from a machine row."""
    tail = row[row.index(after) + len(after):].split()[0]
    return tuple(float(x) for x in tail.split(","))


def test_diorama_engine_probe(tmp_path, class_cache):
    proc = _run_probe(tmp_path, class_cache)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "DG-FAIL" not in out, out
    assert out.splitlines()[-1] == "DG-OK", \
        "DG-OK must be the LAST transcript row (completion, not rc)"
    assert _row(out, "DG-CONTAINER") == "DG-CONTAINER n=1"
    count = _row(out, "DG-COUNT")
    n = int(count.split()[1][2:])
    assert n == N_PRIM and n <= MAX_PRIM, count   # pinned + budget leg
    cls = _row(out, "DG-CLASS")
    assert "boxes=9 cyls=14 prim=1" in cls, cls    # 9+14 == N_PRIM
    # The DECLARED shadow ruling, machine-pinned (see diorama.gd's
    # SHADOW RULING block): nothing casts, every node carries the floor.
    assert _row(out, "DG-LIT") == "DG-LIT cast_off=1 emission=%d" % N_PRIM
    assert abs(_nums(_row(out, "DG-PLATEAU"), "top=")[0]) <= 0.05
    # THE grid-frozen byte-pin: the probe only prints this row after the
    # numeric component-wise compare passed; the row pins what passed.
    assert _row(out, "DG-GROUND") == \
        ("DG-GROUND pos=0,0,0 scale=1,1,1 aabb_min=-80,0,-80 "
         "size=160,0,160"), out
    floor = _row(out, "DG-FLOOR")
    assert "tex=%s " % FLOOR_PATH in floor, floor
    assert "repeat=0" in floor, floor
    mod = _nums(floor, "mod=")
    for got, want in zip(mod, ARENA_MOD):
        assert abs(got - want) <= 0.001, floor      # pinned literal
    gate = _row(out, "DG-GATE")
    assert "gated=3 spawners=3 extra=0" in gate, gate
    keep = _row(out, "DG-KEEP")
    assert "turrets=4" in keep, keep
    mn = _nums(_row(out, "DG-AABB"), "min=")
    mx = _nums(_row(out, "DG-AABB"), "max=")
    for got, want in zip(mn, AABB_MIN):
        assert got >= want, (mn, AABB_MIN)
    for got, want in zip(mx, AABB_MAX):
        assert got <= want, (mx, AABB_MAX)
    screens = [ln for ln in out.splitlines()
               if ln.startswith("DG-SCREEN ")]
    assert len(screens) == 4 and \
        {ln.split()[1] for ln in screens} == {"keep"} | SPAWNERS, out


def test_bank_ground_remap_and_stone_row_source_truth():
    """Replace-not-add law: the ONE id `ground_arena` now points at the
    clean-room flagstone sheet (the old sheet id may not survive beside
    it, no second ground id exists), and `fortress_stone` joins the
    SAME map — diorama.gd is its only consumer."""
    bank = BANK_GD.read_text(encoding="utf-8")
    textures = bank[bank.index("const TEXTURES"):bank.index(
        "const TIER_TEXTURES")]
    m = re.search(r'"ground_arena":\s*preload\("([^"]+)"\)', textures)
    assert m and m.group(1) == FLOOR_PATH, \
        "ground_arena id must remap to the flagstone sheet"
    assert "ground_arena.png" not in textures, \
        "replace-not-add: the old framed-board path must be gone"
    s = re.search(r'"fortress_stone":\s*preload\("([^"]+)"\)', textures)
    assert s and s.group(1) == STONE_PATH, textures


def test_hook_one_call_in_build_cores_source_truth():
    world = WORLD_GD.read_text(encoding="utf-8")
    assert 'const DIORAMA := preload("res://scripts/diorama.gd")' \
        in world, "builder preloaded on the const block (G1 idiom)"
    cores = _fn_body(world, "static func build_cores(")
    # count the LIVE call shape (tab-indented statement): a commented
    # hook is not a mount (proven by the card's planted-red 1).
    assert cores.count("\n\tDIORAMA.build_fortress(m)") == 1, cores
    assert "paint_arena(m)" in cores, cores       # the hook home unchanged
    assert "LANE_BANDS.paint_lane_bands(m)" in cores, cores


def test_diorama_builder_zero_writes_primitive_only_source_truth():
    """Visual-only + the retired-mesh ban (the test_lane_bands G2-FIX
    idiom): comments blanked first, then — diorama.gd WRITES nothing on
    m, calls no shipped mutator (add_child is plumbing), mounts exactly
    ONE container onto m, builds each primitive class at exactly ONE
    site, and NONE of the web-dead mechanism's tokens survive (the G2
    ArrayMesh lesson; the W-K get_image lesson, kb ab9e1c8b). No RNG
    (bare-rand law)."""
    src = DIO_GD.read_text(encoding="utf-8")
    code = re.sub(r"#.*", "", src)
    for banned in ("ArrayMesh", "add_surface_from_arrays", "ARRAY_VERTEX",
                   "ARRAY_INDEX", "get_image", "PackedVector3Array",
                   "PackedInt32Array"):
        assert banned not in code, \
            "web-dead mechanism crept back: %s" % banned
    assert re.search(r"\b(?:randf|randi)\s*\(", code) is None, \
        "decor layout must be deterministic (bare-rand ban)"
    assert code.count("BoxMesh.new()") == 1, "ONE BoxMesh site"
    assert code.count("CylinderMesh.new()") == 1, "ONE CylinderMesh site"
    assert code.count("Node3D.new()") == 1, "ONE container node"
    assert code.count("m.add_child(") == 1, "exactly one mount site"
    assert WRITE_RE.search(code) is None, \
        "diorama must assign NOTHING onto m (visual-only)"
    muts = [mm.group(0) for mm in MUT_RE.finditer(code)
            if mm.group(0).rstrip("(").strip() not in PLUMBING]
    assert muts == [], "diorama calls a shipped mutator: %s" % muts
    # the budget const the probe pins is 30 (DA F-2)
    assert re.search(r"const MAX_PRIMITIVES\s*:=\s*30\b", src), src


def test_committed_sheets_keep_their_pinned_sizes():
    """Row-1b + art law: every committed v1.6 sheet keeps its pinned
    pixel size (PNG IHDR read — stdlib): the three redrawn icons stay
    512x512 (the CORE_EMBLEM_H/GATE_EYE_H make_sprite math and
    test_gate_eye's id->PATH pins ride those sizes), the flagstone and
    masonry sheets stay 1024x1024 (the framed-board precedent)."""
    want = {"icon_core.png": (512, 512), "icon_gate_eye.png": (512, 512),
            "icon_gate_eye_air.png": (512, 512),
            "ground_fortress.png": (1024, 1024),
            "fortress_stone.png": (1024, 1024)}
    for name, size in want.items():
        raw = (V11 / name).read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n", name
        wh = struct.unpack(">II", raw[16:24])
        assert wh == size, "%s is %dx%d, pinned %s" % (name, wh[0],
                                                       wh[1], size)
        assert (V11 / (name + ".import")).is_file(), \
            "%s must ship its .import sidecar in the same commit" % name


def _fn_body(text, header):
    start = text.index(header)
    rest = text[start + len(header):]
    end = rest.find("\nstatic func ")
    return rest if end < 0 else rest[:end]
