"""v1.6 V-F WORLD DECOR (MC card 12111 / V16-PLAN-c2 §3 W2 V-F, pillar
P6): static instanced trees/rocks along the V-A rim walls sell scale at
the board edge (F-BUILD: the only scale sellers were baked grass specks
in the ground texture).

THE CONTRACT (plan row 9 + §3 V-F): decor is STATIC (zero per-frame
code — the perf budget IS "no frame code"), the layout is a pure const
table (zero RNG — the bare-rand ban; determinism is a leg: two builds
byte-identical), the budget is <= 40 props (MAX_PROPS; part census 38
pinned), and the geometry law (kb 2d5274003, L5) holds: engine-managed
PrimitiveMesh ONLY (the CylinderMesh/BoxMesh classes V-A's fortress
already proves rasterize on web) as the source mesh of each MultiMesh.
MultiMeshInstance3D itself is the pillar's word but was UNPROVEN on
web — the plan's leg 1 is the served raster proof (VF-wave.log); the
builder seam (fill(container)) is the declared fallback shape (one
MeshInstance3D per prop, the lane_bands idiom) behind the SAME hook,
should that proof ever fail. Decor mounts by ONE DECOR.build_decor(m)
call in build_cores (the paint_arena/G1/G2/V-A precedent; mission.gd at
the 400 ceiling adds ZERO lines) and stands OUTSIDE the play plane:
every part origin max(|x|,|z|) >= 80 (the board edge) at or above the
rim-wall top — the grid never moves (the fortress DG-GROUND byte-pin
leg keeps proving that each suite run).

ENGINE LEG: embedded kit probe (test_diorama/test_kit_fx R5 idiom —
godot/sim/ is FROZEN, L7), boots mission.tscn (E5, pinned seed),
DC-* machine rows with in-probe DC-FAIL guards + DC-OK-LAST + a
completion flag. CONTAINER one "Decor" at identity, three
MultiMeshInstance3D children; COUNT props/parts vs the pinned census
AND the budget; CLASS the PrimitiveMesh sources (the web-proof proxy);
LIT the V-A shadow ruling (nothing casts, every material carries the
emission floor); RIM the outside-the-board law over every instance
origin; DET three builds (live + two re-fills) serialize byte-identical;
SCREEN the six north-rim canopy tops project INSIDE the declared DECOR
census region through the SHIPPED Camera3D (the crop the served leg
counts — a census that cannot see its subject is not one); DC-TF dumps
the whole build for the cross-process compare. The authored build reads
the nodes' XFORMS_META stamp: runtime MultiMesh instance transforms
live server-side (4.7 set/get round-trips through the RenderingServer
— headless answers ZERO for every instance, VERIFIED this session), so
the engine legs read the builder's CPU-side stamp, and the SERVED leg
is what proves the server-side copy paints them at these exact places
(plan leg 1, the MultiMesh web-raster proof).

SOURCE-TRUTH LEGS (pytest cannot exec GDScript — the test_lane_bands
idiom, comments blanked first): ONE hook call in build_cores; ZERO
writes on m / no shipped mutator / no "Ground" reference; ZERO
per-frame surface (_process/_physics_process/Timer/tween/await) and
zero randf/randi; the web-dead tokens (ArrayMesh/get_image family) are
banned; ONE mount/add_child site; the const tables parse to EXACTLY
the pinned prop/part census under MAX_PROPS with every row on a rim
line (a silent row added reddens the data leg with no engine at all).

PLANTED-REDs (L3, transcripts in VF-wave.log, byte-verified reverts):
(1) hook removed -> DC-CONTAINER rc1 + hook leg RED; (2) budget plant
41 props -> DC-COUNT rc1 + data leg RED (the plan's declared plant);
(3) a stateful builder counter -> DC-DET rc1 + the two-builds compare
RED.
"""

import re
from pathlib import Path

import conftest

GODOT = Path(conftest.repo_path("godot"))
WORLD_GD = GODOT / "scripts" / "mission_world.gd"
DEC_GD = GODOT / "scripts" / "decor.gd"

MAX_PROPS = 40          # the pinned budget const (re-derived below)
N_TREES = 14
N_ROCKS = 10
N_PROPS = N_TREES + N_ROCKS
N_PARTS = N_TREES * 2 + N_ROCKS
RIM_LINE = 82.0         # diorama.BOARD_HALF + RIM_T/2 (wall centerline)
BOARD_EDGE = 80.0       # the play plane ends here; decor lives outside
# The DECOR census region (served crop, VF-wave.log): the north rim
# band where the six north-rim canopy tops project at the shipped D=64
# rig — the DC-SCREEN leg pins that they are INSIDE this rect.
REGION = (340.0, 40.0, 900.0, 160.0)

WRITE_RE = re.compile(
    r"(?<![\w.])m\.[\w.\[\]\"']*\s*(?:[+\-*/]?=[^=])")
MUT_RE = re.compile(r"\b(?:add_|spend_|consume_|set_|equip|place_)\w*\s*\(")
# add_child is mount plumbing; set_instance_transform / set_meta are the
# builder's OWN resource/node writes (MultiMesh API + the authored-
# transform stamp), never shipped mutators — the fx_director read-only
# doctrine's writer-side twin.
PLUMBING = {"add_child", "set_instance_transform", "set_meta"}

PROBE_SRC = '''
extends SceneTree
# gw decor probe (v1.6 V-F, MC 12111). Boot idiom = the diorama probe
# (itself g2/v1_world): mission.tscn instantiated, _ready + setup driven
# directly (E5), pinned seed, root.size = the served canvas. Machine
# rows DC-CONTAINER/-COUNT/-CLASS/-LIT/-RIM/-DET/-SCREEN plus 41 DC-TF
# dump rows; any failed check prints DC-FAIL <detail> + quit(1); a
# skipped leg can never reach DC-OK (LAST print, completion-flag
# guarded).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DECOR := preload("res://scripts/decor.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const VIEW := Vector2i(1280, 720)
const N_PROPS := 24                # pinned census: 14 trees + 10 rocks
const N_PARTS := 38                # trees carry trunk+canopy
const BOARD_EDGE := 80.0           # play-plane edge (decor sits outside)
const REGION := Vector4(340.0, 40.0, 900.0, 160.0)  # census crop
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
	rng.seed = 12111
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
		root.size = VIEW
		_pass(_m)
		if not _failed:
			if not _done:
				_fail("decor pass aborted mid-way (completion flag unset)")
			else:
				print("DC-OK")
				quit(0)
	return false


# Serialize a decor container: one M| header row per instanced node +
# one I| row per instance (origin + full basis, %.5f — byte-stable).
# The rows read the node's XFORMS_META stamp — the builder's authored
# copy (runtime get_instance_transform is server-side-only and answers
# ZERO for every instance under headless, VERIFIED this session; the
# served leg proves the server copy PAINTS what was authored).
func _dump(container: Node) -> Array:
	var out: Array = []
	for c: Node in container.get_children():
		var mmi := c as MultiMeshInstance3D
		if mmi == null:
			_fail("container child %s is not a MultiMeshInstance3D" \\
					% str(c.name))
			return []
		var mm: MultiMesh = mmi.multimesh
		var xf: Array = mmi.get_meta(DECOR.XFORMS_META)
		if xf.size() != mm.instance_count:
			_fail("META stamp %d drifted from server count %d on %s"
					% [xf.size(), mm.instance_count, str(c.name)])
			return []
		out.append("M|%s|%s|%d" % [str(c.name),
				str(mm.mesh.get_class()), mm.instance_count])
		for i: int in xf.size():
			var t: Transform3D = xf[i]
			var shape := "I|%s|%d|%.5f,%.5f,%.5f|" \\
					+ "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f"
			out.append(shape % [str(c.name), i, t.origin.x, t.origin.y,
					t.origin.z, t.basis.x.x, t.basis.x.y, t.basis.x.z,
					t.basis.y.x, t.basis.y.y, t.basis.y.z,
					t.basis.z.x, t.basis.z.y, t.basis.z.z])
	return out


func _pass(m) -> void:
	# CONTAINER: exactly ONE Decor node, at the mission origin, carrying
	# the three instanced part-nodes.
	var decs: Array = []
	for c: Node in m.get_children():
		if String(c.name) == DECOR.DECOR_NAME:
			decs.append(c)
	if decs.size() != 1:
		_fail("CONTAINER Decor nodes = %d (want 1)" % decs.size())
		return
	var decor := decs[0] as Node3D
	if decor == null or decor.position != Vector3.ZERO \\
			or decor.scale != Vector3.ONE:
		_fail("CONTAINER Decor not at identity transform")
		return
	var mms: Array = []
	for c: Node in decor.get_children():
		var mmi := c as MultiMeshInstance3D
		if mmi == null:
			_fail("CONTAINER child %s not MultiMeshInstance3D" \\
					% str(c.name))
			return
		mms.append(mmi)
	if mms.size() != 3:
		_fail("CONTAINER instanced nodes = %d (want 3)" % mms.size())
		return
	print("DC-CONTAINER n=1 inst_nodes=3")
	# COUNT: pinned prop/part census AND the budget (props are DATA —
	# read live off the const tables, never re-typed here).
	var props: int = DECOR.TREES.size() + DECOR.ROCKS.size()
	var parts := 0
	for mmi: MultiMeshInstance3D in mms:
		parts += mmi.multimesh.instance_count
	if props != N_PROPS or parts != N_PARTS or props > DECOR.MAX_PROPS \\
			or parts > DECOR.MAX_PROPS:
		_fail("COUNT props=%d parts=%d (want %d/%d, budget %d)" % [
				props, parts, N_PROPS, N_PARTS, DECOR.MAX_PROPS])
		return
	print("DC-COUNT props=%d parts=%d max=%d" % [props, parts,
			DECOR.MAX_PROPS])
	# CLASS: every MultiMesh source is the pinned PrimitiveMesh class
	# (the web law, kb 2d5274003 — engine-managed geometry; runtime
	# ArrayMesh NEVER rasterizes on web).
	var want := {"PropTrunks": "CylinderMesh",
			"PropCanopies": "CylinderMesh", "PropRocks": "BoxMesh"}
	for mmi: MultiMeshInstance3D in mms:
		var nm := String(mmi.name)
		if not want.has(nm) or str(mmi.multimesh.mesh.get_class()) \\
				!= String(want[nm]):
			_fail("CLASS %s mesh %s (want %s)" % [nm, str(
					mmi.multimesh.mesh.get_class()), str(want[nm])])
			return
		if not mmi.multimesh.mesh is PrimitiveMesh:
			_fail("CLASS %s source not PrimitiveMesh (web-dead class)"
					% nm)
			return
	print("DC-CLASS trunks=cyl canopies=cyl rocks=box prim=1")
	# LIT: the V-A shadow ruling reused verbatim — ambient is DISABLED
	# at the scene row, so NOTHING casts and EVERY material carries the
	# emission floor (no black faces on web).
	var cast_on := 0
	var emit_ok := 0
	for mmi: MultiMeshInstance3D in mms:
		if mmi.cast_shadow != 0:      # GeometryInstance3D OFF literal
			cast_on += 1
		var mo := mmi.material_override as StandardMaterial3D
		if mo != null and mo.emission_enabled:
			emit_ok += 1
	if cast_on != 0 or emit_ok != 3:
		_fail("LIT cast_on=%d emit=%d (want 0/3)" % [cast_on, emit_ok])
		return
	print("DC-LIT cast_off=1 emission=3")
	# RIM: every part origin OUTSIDE the play plane (max(|x|,|z|) on or
	# beyond the board edge) and AT OR ABOVE the rim-wall top — decor
	# can never stand on the grid the sim owns.
	var outside := 0
	var floored := 0
	for mmi: MultiMeshInstance3D in mms:
		var xf: Array = mmi.get_meta(DECOR.XFORMS_META)
		for i: int in xf.size():
			var o: Vector3 = (xf[i] as Transform3D).origin
			if maxf(absf(o.x), absf(o.z)) >= BOARD_EDGE - EPS:
				outside += 1
			if o.y >= DECOR.RIM_Y - EPS:
				floored += 1
	if outside != N_PARTS or floored != N_PARTS:
		_fail("RIM outside=%d floored=%d (want %d/%d)" % [
				outside, floored, N_PARTS, N_PARTS])
		return
	print("DC-RIM outside=%d floored=%d" % [outside, floored])
	# DET: three builds — the live one plus two re-fills — serialize
	# byte-identical (const table, zero RNG, zero time- or
	# state-dependence; the plan's "two builds identical" leg +1).
	var live := _dump(decor)
	if _failed:
		return
	var a := Node3D.new()
	DECOR.fill(a)
	var da := _dump(a)
	a.free()
	var b := Node3D.new()
	DECOR.fill(b)
	var db := _dump(b)
	b.free()
	if _failed:
		return
	if da != live or db != live:
		_fail("DET: re-fill dumps differ from the live build " \\
				+ "(layout must be pure const data)")
		return
	print("DC-DET builds=3 identical=1")
	# DC-TF: the full serialized live build (cross-process compare).
	for row: String in live:
		print("DC-TF " + row)
	# SCREEN: the north-rim canopy tops project INSIDE the declared
	# DECOR census region through the SHIPPED Camera3D — the served
	# pixel leg counts exactly this rect, so the census cannot be
	# pointed at empty sky.
	var cam := m.get_node("CameraRig/Camera3D") as Camera3D
	if cam == null or not cam.is_current():
		_fail("SCREEN Camera3D missing or not current")
		return
	var inside := 0
	var north := 0
	for row: Array in DECOR.TREES:
		var z := float(row[1])
		if absf(z + DECOR.RIM_LINE) > 0.01:
			continue                     # north rim wall rows only
		north += 1
		var s: float = float(row[2])
		var top := Vector3(float(row[0]), DECOR.RIM_Y \\
				+ s * (DECOR.TRUNK_H + DECOR.CANOPY_H), z)
		var p := cam.unproject_position(top)
		if p.x < REGION.x - EPS or p.x > REGION.z + EPS \\
				or p.y < REGION.y - EPS or p.y > REGION.w + EPS:
			var why := "SCREEN canopy top projects at %s outside the " \\
					+ "DECOR region %s"
			_fail(why % [str(p), str(REGION)])
			return
		inside += 1
	if north != 6 or inside != 6:
		_fail("SCREEN north-rim trees = %d inside = %d (want 6/6)" \\
				% [north, inside])
		return
	print("DC-SCREEN north=6 inside=6 region=340,40,900,160")
	_done = true


func _fail(why: String) -> void:
	_failed = true
	print("DC-FAIL " + why)
	quit(1)
'''


def _run_probe(tmp_path):
    Path(tmp_path).mkdir(parents=True, exist_ok=True)
    probe = Path(tmp_path) / "gw_decor_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (),
                                     Path(tmp_path) / "user_home")


def _rows(out, prefix):
    rows = [ln for ln in out.splitlines() if ln.startswith(prefix)]
    return rows


def test_decor_engine_probe(tmp_path, class_cache):
    proc = _run_probe(tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    out = proc.stdout
    assert "DC-FAIL" not in out, out
    assert out.splitlines()[-1] == "DC-OK", \
        "DC-OK must be the LAST transcript row (completion, not rc)"
    row = _rows(out, "DC-CONTAINER")
    assert len(row) == 1 and row[0] == "DC-CONTAINER n=1 inst_nodes=3", out
    count = _rows(out, "DC-COUNT")
    assert len(count) == 1, out
    assert count[0] == "DC-COUNT props=%d parts=%d max=%d" % (
        N_PROPS, N_PARTS, MAX_PROPS), count[0]
    assert _rows(out, "DC-CLASS") == \
        ["DC-CLASS trunks=cyl canopies=cyl rocks=box prim=1"], out
    assert _rows(out, "DC-LIT") == ["DC-LIT cast_off=1 emission=3"], out
    assert _rows(out, "DC-RIM") == \
        ["DC-RIM outside=%d floored=%d" % (N_PARTS, N_PARTS)], out
    assert _rows(out, "DC-DET") == ["DC-DET builds=3 identical=1"], out
    screens = _rows(out, "DC-SCREEN")
    assert screens == ["DC-SCREEN north=6 inside=6 region=340,40,900,160"], \
        out
    # 3 M| headers + 38 I| rows: the full build is on the transcript.
    tf = _rows(out, "DC-TF ")
    assert len(tf) == 3 + N_PARTS, len(tf)
    assert sum(1 for ln in tf if ln.startswith("DC-TF I|")) == N_PARTS


def test_decor_two_builds_byte_identical(tmp_path, class_cache):
    """Determinism ACROSS PROCESSES (the plan leg "two builds
    identical"): two independent boots of the same probe print
    byte-identical transcripts — no RNG, no time, no order-dependence
    survived the const-table law."""
    a = _run_probe(tmp_path / "a")
    b = _run_probe(tmp_path / "b")
    for p in (a, b):
        assert p.returncode == 0 and "DC-FAIL" not in p.stdout, \
            "OUT:%s\nERR:%s" % (p.stdout, p.stderr)
    assert a.stdout == b.stdout, \
        "two boots printed different builds (determinism broken)"


def test_hook_one_call_in_build_cores_source_truth():
    world = WORLD_GD.read_text(encoding="utf-8")
    assert 'const DECOR := preload("res://scripts/decor.gd")' \
        in world, "builder preloaded on the const block (G1 idiom)"
    cores = _fn_body(world, "static func build_cores(")
    # count the LIVE call shape (tab-indented statement): a commented
    # hook is not a mount (the diorama planted-red closed that class).
    assert cores.count("\n\tDECOR.build_decor(m)") == 1, cores
    assert "\n\tDIORAMA.build_fortress(m)" in cores, cores  # unchanged
    assert "paint_arena(m)" in cores, cores


def test_decor_builder_laws_source_truth():
    """Static, deterministic, visual-only + the retired-mesh ban (the
    test_lane_bands/test_diorama idiom): comments blanked, then —
    decor.gd writes NOTHING on m, touches no "Ground", calls no shipped
    mutator (add_child is plumbing), owns ONE mount site and ONE
    construction site per instanced class, carries ZERO per-frame
    surface (the perf budget IS "no frame code"), ZERO RNG tokens, and
    none of the web-dead mechanism's tokens (kb 2d5274003, ab9e1c8b)."""
    src = DEC_GD.read_text(encoding="utf-8")
    code = re.sub(r"#.*", "", src)
    for banned in ("ArrayMesh", "add_surface_from_arrays", "ARRAY_VERTEX",
                   "ARRAY_INDEX", "get_image", "PackedVector3Array",
                   "PackedInt32Array"):
        assert banned not in code, \
            "web-dead mechanism crept back: %s" % banned
    assert re.search(r"\b(?:randf|randi)\s*\(", code) is None, \
        "decor layout must be deterministic (bare-rand ban)"
    for per_frame in ("_process", "_physics_process", "Timer", "tween",
                      "await", "set_process"):
        assert per_frame not in code, \
            "decor owns a per-frame surface (%s) — static-only law" \
            % per_frame
    assert "Ground" not in code, "decor must never touch the ground node"
    assert code.count("MultiMesh.new()") == 1, "ONE MultiMesh site"
    assert code.count("MultiMeshInstance3D.new()") == 1, "ONE node site"
    assert code.count("Node3D.new()") == 1, "ONE container node"
    assert code.count("m.add_child(") == 1, "exactly one mount site"
    assert WRITE_RE.search(code) is None, \
        "decor must assign NOTHING onto m (visual-only)"
    muts = [mm.group(0) for mm in MUT_RE.finditer(code)
            if mm.group(0).rstrip("(").strip() not in PLUMBING]
    assert muts == [], "decor calls a shipped mutator: %s" % muts
    assert re.search(r"const MAX_PROPS\s*:=\s*40\b", src), src


def test_layout_tables_are_pinned_census_on_the_rim():
    """Data leg (no engine): the const tables parse to EXACTLY the
    pinned prop/part census under the budget, and EVERY row stands on
    a rim-wall centerline (max(|x|,|z|) >= the board edge + the wall
    inset) — adding a row silently reddens this leg even in a checkout
    that never ran Godot."""
    src = DEC_GD.read_text(encoding="utf-8")
    trees = _table_rows(src, "TREES")
    rocks = _table_rows(src, "ROCKS")
    assert (len(trees), len(rocks)) == (N_TREES, N_ROCKS), \
        "layout tables drifted from the pinned census"
    for kind, rows, parts in (("tree", trees, 2), ("rock", rocks, 1)):
        for r in rows:
            x, z = r[0], r[1]
            assert max(abs(x), abs(z)) >= BOARD_EDGE, \
                "%s row %r stands inside the play plane" % (kind, r)
            assert abs(abs(x) - RIM_LINE) < 0.01 or \
                abs(abs(z) - RIM_LINE) < 0.01, \
                "%s row %r is not on a rim-wall centerline" % (kind, r)
            assert 0.5 <= r[2] <= 1.4, "%s row %r scale off-door" % (
                kind, r)
        assert len(rows) * parts <= MAX_PROPS
    assert len(trees) * 2 + len(rocks) == N_PARTS
    assert N_PROPS <= MAX_PROPS


def _table_rows(src, name):
    head = "const %s := [" % name
    block = src[src.index(head) + len(head):]
    block = block[:block.index("\n]")]
    rows = []
    for m in re.finditer(r"\[([^\]]+)\]", block):
        fields = [f.strip() for f in m.group(1).split(",")]
        vals = []
        for f in fields:
            if f in ("RIM_LINE", "-RIM_LINE"):
                vals.append(RIM_LINE if f == "RIM_LINE" else -RIM_LINE)
            else:
                vals.append(float(f))
        rows.append(vals)
    assert len(rows) >= 1, name
    return rows


def _fn_body(text, header):
    start = text.index(header)
    rest = text[start + len(header):]
    end = rest.find("\nstatic func ")
    return rest if end < 0 else rest[:end]
