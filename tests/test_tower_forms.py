"""v1.6 V-B tower structures + aim (MC 12082 / V16-PLAN-c2 §3 W1 V-B).

The contract (plan row 2/3 + brief): the placed-defense WORLD visual is
the primitive-composed 3D form (scripts/tower_forms.gd — BoxMesh /
CylinderMesh only, the L5 web-raster law; every size const lives THERE,
ungoverned) — defense_obj._make_visual delegates in ONE line with ZERO
literals (GOVERNED honored, BN1) — and a root-mounted OBSERVER
(scripts/tower_aim.gd, the fx_director/selection_ring doctrine REUSED,
code-mounted from mission_world.build_cores since mission.gd sits at
its 400 ceiling) yaws each shooter's "Turret" child at the nearest live
entity inside the defense's OWN bonus_row().range door — READS published
state only, WRITES its own visual's transform only, ZERO-WRITE idle with
no target (an untouched turret keeps its yaw). The medallions RETIRE
from the world path only; the panel/HUD icons ride the separate icon_*
bank ids (plan P2b — asserted untouched here).

Harness = the P5/selection_ring idiom: conftest.run_probe_script with
the probe GENERATED into tmp_path (R5), REAL mission.tscn boot + setup
through the shipped injection door, placements through the shipped
mission.place_defense / defense_obj.upgrade entries (green top-up is the
harness license — mission_smoke precedent), spawns through the shipped
runner.spawn, the driver hand-driven via aim_step() (E5: -s dispatches
no _process — the fx_step/ring_step idiom, deterministic zero-wave
flakiness). Rows: TF-MOUNT/TF-FORM/TF-TIER/TF-FALLBACK + TF-IDLE/
TF-AIM/TF-SIMCALM/TF-TRACK, *-OK LAST (a silent skip cannot go green),
EMPTY stderr. Expected yaws are re-computed by PYTHON from the printed
positions + towers.json ranges (DATA leg — the probe is never its own
oracle). GDScript continuation inside these probes rides PARENTHESES,
never a backslash: python string-literal-eats "\\n" joins and silently
rewrites GDScript lines (the first-run lesson, VB-wave.log).

PLANTED-RED committed (mutation gate, pierce_splash shape): the yaw
expression inverted / argument-swapped on a COPY reddens the matcher
with zero file touched; the RUNTIME plant (yaw inverted in the real
file) is shown RED against test_aim_probe + byte-verified reverted in
VB-wave.log (L3). Node-CLASS re-pin sweep (L3/plan risk 6): the only
world-node pins the SUITE holds are shape-based (test_place_refusals
is_instance_valid+parented; test_kit_fx position/id based) — measured
green against the TowerForm container in the card's suite run, nothing
re-pinned (the sprite-era v11_sprite_probe is artifact-only: NO test
drives it; named as a stale-asset finding in VB-wave.log).
"""

import json
import math
import re
import sys

import conftest
from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code, literal scan)

AIM_GD = repo_path("godot", "scripts", "tower_aim.gd")
FORMS_GD = repo_path("godot", "scripts", "tower_forms.gd")
OBJ_GD = repo_path("godot", "scripts", "defense_obj.gd")
WORLD_GD = repo_path("godot", "scripts", "mission_world.gd")
BANK_GD = repo_path("godot", "scripts", "sprite_bank.gd")
FX_GD = repo_path("godot", "scripts", "fx_director.gd")
MISSION_GD = repo_path("godot", "scripts", "mission.gd")
TOWERS_JSON = repo_path("godot", "data", "towers.json")

BOOT = '''	root.size = Vector2i(1280, 720)
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(DECK.duplicate())
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return null
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()
	var rng := RandomNumberGenerator.new()
	rng.seed = 12082
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	m.green = 100000    # harness license (mission_smoke precedent)
	return m
'''

FORMS_PROBE = '''
extends SceneTree
# gw V-B tower-FORMS probe (MC 12082). Rows: TF-MOUNT / TF-FORM (x5) /
# TF-TIER / TF-FALLBACK / TF-FORMS-OK (LAST). Any failed check prints
# TF-FAIL <detail> + quit(1). Real-boot + shipped-entry idiom (P5 probe).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const DEF_OBJ := preload("res://scripts/defense_obj.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const IDS := ["ballista", "bombard", "hailspire_tower", "gate_blockade",
		"barbed_snare"]

var _failed := false


func _fail(why: String) -> void:
	_failed = true
	print("TF-FAIL " + why)
	quit(1)


func _turret_y(nd) -> float:
	var tur = nd.get_node_or_null(NodePath("Turret"))
	return float(tur.position.y) if tur != null else -1.0


func _boot():
''' + BOOT + '''

func _init() -> void:
	var m = _boot()
	if m == null:
		return
	# MOUNT leg: the SHIPPED setup mounted the aim driver on the root.
	var aim = m.get_node_or_null(NodePath("TowerAim"))
	if aim == null:
		_fail("MOUNT: build_cores mounted no TowerAim")
		return
	print("TF-MOUNT mounted=1")
	var trows := {}
	for row: Dictionary in m.tables.rows("towers"):
		trows[String(row["id"])] = row
	# FORM legs: one placed defense per world id, through the SHIPPED
	# place_defense entry — container shape + PrimitiveMesh-only meshes
	# (the L5 web-raster proxy) + the Turret contract on shooters ONLY.
	var i := 0
	for tid: String in IDS:
		var pl: Dictionary = m.place_defense(
				trows[tid], 1, Vector3(60 + i, 0.0, 0.0))
		if not bool(pl["ok"]):
			_fail("place refused %s: %s" % [tid, str(pl)])
			return
		var obj = (m.defense_list[-1] as Dictionary)["obj"]
		var nd = obj.node
		if (nd == null or not is_instance_valid(nd)
				or nd.get_parent() == null):
			_fail("form node invalid/unparented: %s" % tid)
			return
		if (not String(nd.name).begins_with("TowerForm")
				or nd.get_child_count() == 0):
			_fail("form container wrong: %s kids=%d"
					% [String(nd.name), nd.get_child_count()])
			return
		var meshes := 0
		var prim := 0
		for c: Node in nd.get_children():
			var mi := c as MeshInstance3D
			if mi == null:
				continue
			meshes += 1
			if mi.mesh is PrimitiveMesh:
				prim += 1
		if meshes == 0 or prim != meshes:
			_fail("form meshes %d prim %d: %s" % [meshes, prim, tid])
			return
		var tur = nd.get_node_or_null(NodePath("Turret"))
		var ty := _turret_y(nd)
		if tur != null and (tur.get_child_count() == 0 or ty <= 0.0):
			_fail("turret bare or sunk: %s y=%.2f" % [tid, ty])
			return
		var line := ("TF-FORM id=%s class=%s meshes=%d prim=%d "
				+ "turret=%d ty=%.2f")
		print(line % [tid, String(obj.class_id), meshes, prim,
				1 if tur != null else 0, ty])
		i += 1
	# TIER leg: the SHIPPED upgrade() entry swap-rebuilds the form and
	# the ladder GROWS (turret lift rides body_height; v11_sprite_probe
	# upgrade-license precedent).
	var obj0 = m.defense_list[0]["obj"]
	var y0 := _turret_y(obj0.node)
	var iid0 := int(obj0.node.get_instance_id())
	var y1 := -1.0
	for u: int in range(2):
		var up: Dictionary = obj0.upgrade()
		if not bool(up["ok"]):
			_fail("upgrade refused: %s" % str(up))
			return
		var nd2 = obj0.node
		if not String(nd2.name).begins_with("TowerForm"):
			_fail("tier swap produced no TowerForm")
			return
		if u == 0:
			y1 = _turret_y(nd2)
	var y2 := _turret_y(obj0.node)
	if y0 <= 0.0 or y1 <= y0 or y2 <= y1:
		_fail("tier ladder not growing: %.2f %.2f %.2f" % [y0, y1, y2])
		return
	var swapped := 1 if int(obj0.node.get_instance_id()) != iid0 else 0
	print("TF-TIER id=ballista y0=%.2f y1=%.2f y2=%.2f swapped=%d"
			% [y0, y1, y2, swapped])
	# FALLBACK leg: an id with no form yet still lands a TowerForm greybox
	# (the bank-null contract carried: never null on the slot). Synth row
	# through defense_obj directly (test_damage_numbers shape).
	var synth := {"id": "zz_future_tower", "class": "tower",
			"base_cost": 1, "tiers": [{"hp": 10.0, "damage": 1.0,
					"fire_rate": 1.0, "range": 5.0, "effect": "none"}]}
	var obj2 = DEF_OBJ.new()
	obj2.init_defense(m, synth, Vector3(70, 0, 0), 9001)
	var fb = obj2.node
	if (fb == null or not String(fb.name).begins_with("TowerForm")
			or fb.get_child_count() == 0):
		_fail("fallback form missing for unformed id")
		return
	print("TF-FALLBACK kids=%d turret=%d" % [fb.get_child_count(),
			1 if fb.get_node_or_null(NodePath("Turret")) != null
			else 0])
	fb.free()
	if _failed:
		return
	print("TF-FORMS-OK")
	quit(0)
'''

AIM_PROBE = '''
extends SceneTree
# gw V-B turret-AIM probe (MC 12082). Rows: TF-IDLE / TF-AIM (x2) /
# TF-SIMCALM / TF-TRACK / TF-AIM-OK (LAST). Driver hand-driven
# (aim_step, the fx_step/ring_step E5 idiom); entities planted through
# the SHIPPED runner.spawn; yaw + positions PRINTED for the python DATA
# leg to recompute (the probe is never its own oracle).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const SENTINEL := 1.234   # probe-write (harness license): the observable
                          # "untouched" marker on a fresh turret

var _failed := false


func _fail(why: String) -> void:
	_failed = true
	print("TF-FAIL " + why)
	quit(1)


func _boot():
''' + BOOT + '''

func _yaw(nd) -> float:
	var tur = nd.get_node_or_null(NodePath("Turret"))
	return float(tur.rotation.y) if tur != null else -99.0


func _place(m, tid: String, at: Vector3):
	for row: Dictionary in m.tables.rows("towers"):
		if String(row["id"]) == tid:
			var pl: Dictionary = m.place_defense(row, 1, at)
			if not bool(pl["ok"]):
				_fail("place refused %s: %s" % [tid, str(pl)])
				return null
			return (m.defense_list[-1] as Dictionary)["obj"]
	_fail("towers.json lost %s" % tid)
	return null


func _init() -> void:
	var m = _boot()
	if m == null:
		return
	var aim = m.get_node_or_null(NodePath("TowerAim"))
	if aim == null:
		_fail("MOUNT: build_cores mounted no TowerAim")
		return
	var bal = _place(m, "ballista", Vector3(-36, 0, 3))
	var hail = _place(m, "hailspire_tower", Vector3(-3, 0, -36))
	var bomb = _place(m, "bombard", Vector3(34, 0, 26))
	if bal == null or hail == null or bomb == null:
		return
	# IDLE leg: NO entities exist — sentinels written, driver run, every
	# turret must stand EXACTLY where the probe left it (zero writes).
	for obj in [bal, hail, bomb]:
		obj.node.get_node(NodePath("Turret")).rotation.y = SENTINEL
	aim.aim_step()
	var kept := 0
	var ys: Array = []
	for obj in [bal, hail, bomb]:
		var y := _yaw(obj.node)
		if absf(y - SENTINEL) < 1e-4:  # float32 storage eps
			kept += 1
		ys.append(y)
	print("TF-IDLE idle=3 kept=%d y0=%.4f y1=%.4f y2=%.4f"
			% [kept, ys[0], ys[1], ys[2]])
	# AIM legs: plant one ground mob at the spawn_a mouth (nearest to the
	# ballista) and one air mob at spawn_b (nearest to the hailspire);
	# the bombard stands far from both (out-of-range idle).
	var runner = m.get_node("EnemyRunner")
	runner.spawn({"enemy_id": "skitterling", "count": 1},
			m.lanes["lane_g1"], m.enemy_defs, m.rng)
	runner.spawn({"enemy_id": "gale_harpy", "count": 1},
			m.lanes["lane_a2"], m.enemy_defs, m.rng)
	aim.aim_step()
	for pair: Array in [[bal, runner.entities[0]],
			[hail, runner.entities[1]]]:
		var obj = pair[0]
		var ent: Dictionary = pair[1]
		var p: Vector3 = obj.pos
		var e: Vector3 = ent["pos"]
		print(("TF-AIM id=%s tx=%.4f tz=%.4f px=%.4f pz=%.4f got=%.4f"
				% [String(obj.trow["id"]), e.x, e.z, p.x, p.z,
				_yaw(obj.node)]))
	# SIMCALM: five driver passes move NOTHING in the sim (the observer
	# doctrine at runtime, beside the source-truth leg in python).
	var kept_bomb := 1 if absf(_yaw(bomb.node) - SENTINEL) < 1e-4 else 0
	var g0 := int(m.green)
	var hp0 := float(bal.hp)
	var ehp0 := float(runner.entities[0]["hp"])
	var ne0 := int(runner.entities.size())
	var dl0 := int(m.defense_list.size())
	for _i: int in range(5):
		aim.aim_step()
	var same := 1 if (int(m.green) == g0
			and absf(float(bal.hp) - hp0) < 1e-9
			and absf(float(runner.entities[0]["hp"]) - ehp0) < 1e-9
			and int(runner.entities.size()) == ne0
			and int(m.defense_list.size()) == dl0) else 0
	print("TF-SIMCALM same=%d bomb_kept=%d" % [same, kept_bomb])
	# TRACK leg: step the REAL sim — the mob walks, the driver re-reads
	# and the yaw MOVES onto the new position (printed for python).
	for _s: int in range(30):
		m.step(1.0 / 60.0)
		aim.aim_step()
	var p1: Vector3 = bal.pos
	var e1: Vector3 = runner.entities[0]["pos"]
	print("TF-TRACK tx=%.4f tz=%.4f px=%.4f pz=%.4f got=%.4f"
			% [e1.x, e1.z, p1.x, p1.z, _yaw(bal.node)])
	if _failed:
		return
	print("TF-AIM-OK")
	quit(0)
'''


def _rows(out, tag):
    return [ln for ln in out.splitlines() if ln.startswith(tag + " ")]


def _kv(line):
    return dict(x.split("=", 1) for x in line.split(" ")[1:])


def _run(tmp_path, src, name):
    probe = tmp_path / name
    probe.write_text(src, encoding="utf-8")
    return conftest.run_probe_script(str(probe), (),
                                     tmp_path / "user_home")


def _common(proc):
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    assert "TF-FAIL" not in proc.stdout, proc.stdout


def _tower_rows():
    rows = json.loads(open(TOWERS_JSON, encoding="utf-8").read())
    rows = rows["towers"] if isinstance(rows, dict) else rows
    return {row["id"]: row for row in rows}


def test_forms_probe(tmp_path, class_cache):
    """Form per world class id + the Turret contract (shooters ONLY) +
    PrimitiveMesh-only geometry (L5) + tier growth + the mounted driver
    — through the shipped place/upgrade entries."""
    proc = _run(tmp_path, FORMS_PROBE, "vb_forms_probe.gd")
    _common(proc)
    out = proc.stdout
    assert out.rstrip().endswith("TF-FORMS-OK"), \
        "TF-FORMS-OK must be the LAST row (a skipped leg cannot reach it)"
    assert _kv(_rows(out, "TF-MOUNT")[0])["mounted"] == "1", \
        "build_cores did not mount the aim driver"

    rows = _tower_rows()
    forms = [_kv(ln) for ln in _rows(out, "TF-FORM")]
    assert [f["id"] for f in forms] == \
        ["ballista", "bombard", "hailspire_tower", "gate_blockade",
         "barbed_snare"], forms
    for f in forms:
        assert f["prim"] == f["meshes"] and int(f["meshes"]) >= 1, f
        # Turret iff tower-class row (the data decides, not this test):
        assert f["turret"] == ("1" if rows[f["id"]]["class"] == "tower"
                               else "0"), (f, rows[f["id"]]["class"])
        if f["turret"] == "1":
            assert float(f["ty"]) > 0.0, f
    t = _kv(_rows(out, "TF-TIER")[0])
    assert t["swapped"] == "1", t
    assert float(t["y0"]) < float(t["y1"]) < float(t["y2"]), t
    fb = _kv(_rows(out, "TF-FALLBACK")[0])
    assert int(fb["kids"]) >= 1 and fb["turret"] == "1", fb


def test_aim_probe(tmp_path, class_cache):
    """Yaw tracks the planted entity inside the range door (ground AND
    air), zero-writes idle when no target (sentinel), the bombard with
    live-but-out-of-range entities keeps its yaw, five driver passes
    move NO sim field, and the yaw re-tracks after real sim steps."""
    proc = _run(tmp_path, AIM_PROBE, "vb_aim_probe.gd")
    _common(proc)
    out = proc.stdout
    assert out.rstrip().endswith("TF-AIM-OK"), out

    idle = _kv(_rows(out, "TF-IDLE")[0])
    assert idle["kept"] == "3", \
        "zero-writes idle broken: turret touched with NO entities\n%s" \
        % idle

    aims = [_kv(ln) for ln in _rows(out, "TF-AIM")]
    assert [a["id"] for a in aims] == ["ballista", "hailspire_tower"], aims
    ranges = _tower_rows()
    for a in aims:
        want = math.atan2(float(a["tx"]) - float(a["px"]),
                          float(a["tz"]) - float(a["pz"]))
        assert abs(want - float(a["got"])) < 1e-3, \
            "yaw does not face the planted entity: %s (want %.4f)" % (
                a, want)
        # the planted target really is inside that row's own T1 range
        # (DATA leg vs towers.json: the door the driver is pinned to).
        d = math.hypot(float(a["tx"]) - float(a["px"]),
                       float(a["tz"]) - float(a["pz"]))
        r = float(ranges[a["id"]]["tiers"][0]["range"])
        assert d <= r, (a, d, r)

    calm = _kv(_rows(out, "TF-SIMCALM")[0])
    assert calm["same"] == "1", \
        "the observer wrote sim state:\n%s" % calm
    assert calm["bomb_kept"] == "1", \
        "out-of-range turret was touched: %s" % calm

    tr = _kv(_rows(out, "TF-TRACK")[0])
    want = math.atan2(float(tr["tx"]) - float(tr["px"]),
                      float(tr["tz"]) - float(tr["pz"]))
    assert abs(want - float(tr["got"])) < 1e-3, \
        "yaw did not re-track after real sim steps: %s" % tr
    # movement actually happened (the TRACK leg is not the AIM row twice)
    a0 = aims[0]
    assert (float(a0["tx"]), float(a0["tz"])) != \
        (float(tr["tx"]), float(tr["tz"])), tr


def _fn_body(text, header):
    start = text.index(header)
    rest = text[start + len(header):]
    end = rest.find("\nfunc ")
    return rest if end < 0 else rest[:end]


def test_source_truth_and_planted_gates():
    """Observer discipline + delegation shape, mechanically: the driver
    constructs nothing and mutates nothing (the selection_ring source-
    truth shape — the ONLY assignment is its own visual's yaw); the
    defense_obj delegation is the one line with ZERO literals; the
    medallion retirement touches the WORLD path only (mission.gd and
    fx_director.gd carry ZERO V-B lines; the icon bank survives); the
    build_cores mount is exactly one; and committed PLANTED-RED mutation
    gates prove the yaw + delegation matchers can go RED without
    touching any file."""
    aim = open(AIM_GD, encoding="utf-8").read()
    code = hyg.blank_code(aim, "gd")
    assert ".new()" not in code, "the driver constructs NOTHING"
    for mutator in ("damage", "add_green", "place_defense", "add_child",
                    "remove_child", ".free(", "queue_free", "randf",
                    "randi", "assign_relic", "upgrade(", "sell(",
                    "repair(", "entities", "quit("):
        assert mutator not in code, \
            "driver touches a sim mutator: %s" % mutator
    writes = [ln.strip() for ln in code.splitlines()
              if re.match(r"^\s+[A-Za-z_][\w.]*\s*=[^=]", ln)
              and not ln.strip().startswith("var ")]
    assert len(writes) == 1 and writes[0].startswith(
        "turret.rotation.y ="), \
        "the ONE write must be the turret yaw, got: %r" % writes

    # ---- planted-red #1 (committed mutation gate, yaw) ----
    def yaw_faces_plus_z(text):
        m = re.search(r"turret\.rotation\.y\s*=\s*(.+)\n",
                      hyg.blank_code(text, "gd"))
        assert m, "tower_aim.gd exposes no turret.rotation.y write"
        return m.group(1).strip() == "atan2(to.x, to.z)"

    assert yaw_faces_plus_z(aim), "yaw expression drifted (RED)"
    inverted = aim.replace("atan2(to.x, to.z)", "-atan2(to.x, to.z)")
    assert inverted != aim, "planted-red anchor drifted"
    assert not yaw_faces_plus_z(inverted), \
        "yaw gate stayed green with the sign inverted"
    swapped = aim.replace("atan2(to.x, to.z)", "atan2(to.z, to.x)")
    assert swapped != aim and not yaw_faces_plus_z(swapped), \
        "yaw gate stayed green with the args swapped"

    # ---- delegation shape + planted-red #2 (the one line) ----
    obj = open(OBJ_GD, encoding="utf-8").read()
    body = _fn_body(obj, "func _make_visual():")
    assert body.strip() == "return TOWER_FORMS.build(self)", \
        "_make_visual is not the ONE delegation line: %r" % body
    assert not hyg.literal_violations(body), \
        "the delegation line carries literals (GOVERNED broken)"
    no_deleg = obj.replace("return TOWER_FORMS.build(self)",
                           "return obj.node")
    assert no_deleg != obj and _fn_body(no_deleg, "func _make_visual():") \
        .strip() != "return TOWER_FORMS.build(self)"

    # ---- retirement touches the WORLD path only ----
    mission = open(MISSION_GD, encoding="utf-8").read()
    fx = open(FX_GD, encoding="utf-8").read()
    for token in ("tower_aim", "TowerAim", "tower_forms", "TowerForm",
                  "Turret"):
        assert token not in mission, \
            "mission.gd carries a V-B line: %s" % token
        assert token not in fx, \
            "fx_director.gd carries a V-B line: %s" % token
    bank = open(BANK_GD, encoding="utf-8").read()
    assert '"icon_ballista"' in bank and '"icon_core"' in bank, \
        "the UI icon bank must survive the world-path retirement (P2b)"
    forms = open(FORMS_GD, encoding="utf-8").read()
    assert "Sprite3D" not in forms and "make_sprite" not in forms, \
        "the world FORM path must not ride the medallion bank"

    # ---- exactly-one mount in build_cores (the declared hook home) ----
    world = open(WORLD_GD, encoding="utf-8").read()
    assert 'const TOWER_AIM := preload("res://scripts/tower_aim.gd")' \
        in world, "driver preloaded on the const block (G1 idiom)"
    cores = _fn_body(world, "static func build_cores(")
    assert cores.count("TOWER_AIM.new()") == 1, cores
    assert cores.count('aim.name = "TowerAim"') == 1, cores
    assert cores.count("m.add_child(aim)") == 1, cores

    # gate metric rows (the wave-log LOC figures)
    for path in (AIM_GD, FORMS_GD, OBJ_GD, WORLD_GD):
        n = len(open(path, encoding="utf-8").read().split("\n"))
        assert n <= 400, (path, n)
