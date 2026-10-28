# v1_world_probe — the V1 stylized-world headless proof (MC card 11559 /
# milestone 11462). Boot idiom = v4_icon_probe (itself mission_clicks +
# v6_tween): mission.tscn instantiated, _ready and setup driven directly
# (E5: the router-added mission never dispatches _ready under -s), the
# pinned smoke seed, root.size = the served canvas. The mission enters
# the SceneTree root, so the SHIPPED Camera3D is inside the tree and its
# own unproject_position answers — no re-derived projection anywhere.
# Rows (machine lines, any failure prints V1W-FAIL <why> and quits 1):
#  FLOOR  the live Ground material's albedo texture is pinned by its
#         COMMITTED RESOURCE PATH (ground_arena — never through the
#         bank, the v11_sprite_probe bank-as-oracle lesson), repeat is
#         OFF, and the modulate is the pinned ARENA_MODULATE value.
#  AABB   the ground node's mesh AABB (component-wise numeric pin) and
#         its node-local transform origin are byte-pinned, with the
#         mission root's own transform origin pinned at zero (pre==post:
#         the V1 pass paints the plane, never moves it; global xforms
#         are not read — the pinned root origin makes local == global).
#  CORE   each core node (main + every sub) carries the icon_core
#         Sprite3D billboard child on the pinned committed path, at the
#         pinned local y and the pinned bank-scaled size.
#  FRAME  every lane waypoint, spawner, lane end, both cores and the
#         hero battle space project THROUGH THE SHIPPED Camera3D
#         (unproject_position — the engine's own projection, not a
#         re-derivation) inside the 1280x720 viewport with min/max
#         screen coords printed and every 4-edge margin pinned >= 60 px.
# Planted-red (run with user arg "planted"): the FLOOR expectation
# switches to the OTHER committed terrain sheet (ground_path) — the
# mechanism is unchanged, only the pinned expected path is wrong, so a
# working paint MUST trip it. An unbroken gate is no gate.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")
const MISSION_WORLD := preload("res://scripts/mission_world.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const HERO_IDS := ["warden", "deadeye", "embercaller"]  # deck seed (v4)
const VIEW := Vector2i(1280, 720)          # the A9 screenshot viewport
const MIN_MARGIN := 60.0                   # the brief's pinned frame margin
const ARENA_PATH := "res://assets/v11/ground_arena.png"
const PATH_TRAP := "res://assets/v11/ground_path.png"   # planted-red only
const CORE_PATH := "res://assets/v11/icon_core.png"
const REPEAT_OFF := false         # 4.7.2 texture_repeat is a BOOL (VERIFIED
                                  # via ClassDB dump); literal pin: the
                                  # mechanism never supplies its expectation
const BILLBOARD_ENABLED := 1      # BaseMaterial3D.BillboardMode literal pin
# ground-plane invariants (mesh_plane.tres: PlaneMesh 160x160 at the
# identity node), pinned COMPONENT-WISE — the byte-pin the V1 pass must
# not move (numeric compare, never a formatted-string compare):
const AABB_POS := Vector3(-80, 0, -80)
const AABB_SIZE := Vector3(160, 0, 160)
const EMBLEM_SCALE := 6.0 / (512.0 / 100.0)  # make_sprite math, pinned

var _planted := false
var _failed := false
var _frames := 0
var _m = null


func _init() -> void:
	_planted = OS.get_cmdline_user_args().has("planted")
	root.size = VIEW
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(HERO_IDS.duplicate())   # starter deck (C13)
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                                  # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                            # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	_m = m


# v4_icon_probe pump: the MainLoop._process override iterates frames under
# `-s`; the FRAME leg needs the Camera3D CURRENT, and current turns on
# viewport handling, not add_child (engine fact, this card).
func _process(_delta: float) -> bool:
	if _failed:
		return true                       # quit(1) already fired
	_frames += 1
	if _frames == 2:
		root.size = VIEW                            # v4: applied AT the pump
		return false
	if _frames == 4:
		_floor(_m)
		_aabb(_m)
		_core(_m)
		_frame(_m)
		if not _failed:
			print("V1W-OK")
			quit(0)
	return false


func _floor(m) -> void:
	var want_arena := PATH_TRAP if _planted else ARENA_PATH
	var ground := m.get_node_or_null("Ground") as MeshInstance3D
	if ground == null:
		_fail("mission.tscn does not ship a Ground node")
		return
	var mat := ground.material_override as StandardMaterial3D
	if mat == null or mat.albedo_texture == null \
			or String(mat.albedo_texture.resource_path) != want_arena:
		_fail("ground albedo is not the pinned arena board: %s (want %s)" % [
				str(mat.albedo_texture.resource_path) if mat != null \
						and mat.albedo_texture != null else "null",
				want_arena])
		return
	if mat.texture_repeat != REPEAT_OFF:
		_fail("arena board repeats (framed board must be 1:1): %s" \
				% str(mat.texture_repeat))
		return
	if mat.albedo_color != MISSION_WORLD.ARENA_MODULATE:
		_fail("arena modulate drifted: %s != %s" % [str(mat.albedo_color),
				str(MISSION_WORLD.ARENA_MODULATE)])
		return
	if not _planted and SPRITE_BANK.texture_for("ground_arena") == null:
		_fail("ground_arena missing from the ONE sprite_bank map")
		return
	print("V1W-FLOOR tex=%s repeat=off modulate=%s" % [want_arena,
			str(mat.albedo_color)])


func _aabb(m) -> void:
	var ground := m.get_node("Ground") as MeshInstance3D
	var aabb: AABB = ground.mesh.get_aabb()
	if aabb.position != AABB_POS or aabb.size != AABB_SIZE \
			or ground.transform.origin != Vector3.ZERO \
			or m.transform.origin != Vector3.ZERO:
		_fail("ground AABB/origin moved: %s - %s @ %s (root @ %s)" % [
				str(aabb.position), str(aabb.size),
				str(ground.transform.origin), str(m.transform.origin)])
		return
	print("V1W-AABB pos=%s size=%s origin=0,0,0 unchanged=1" % [
			str(aabb.position), str(aabb.size)])


func _core(m) -> void:
	var cores: Array = [m.core_main]
	for rec: Variant in m.core_subs.values():
		cores.append(rec)
	for rec: Variant in cores:
		var node: Node = rec.node
		var spr: Sprite3D = null
		for c: Node in node.get_children():
			if c is Sprite3D:
				spr = c as Sprite3D
		if spr == null or spr.texture == null \
				or String(spr.texture.resource_path) != CORE_PATH:
			_fail("core %s has no icon_core billboard child" % rec.id)
			return
		if int(spr.billboard) != BILLBOARD_ENABLED:
			_fail("core %s emblem is not a billboard: %d" % [rec.id,
					int(spr.billboard)])
			return
		if spr.position != Vector3(0, MISSION_WORLD.CORE_EMBLEM_Y, 0) \
				or not is_equal_approx(spr.scale.x, EMBLEM_SCALE):
			_fail("core %s emblem placement drifted: pos=%s scale=%s" % [
					rec.id, str(spr.position), str(spr.scale)])
			return
	print("V1W-CORE n=%d emblem=%s parented=1" % [cores.size(), CORE_PATH])


func _frame(m) -> void:
	var cam := m.get_node("CameraRig/Camera3D") as Camera3D
	if cam == null or not cam.current:
		_fail("shipped Camera3D missing or not current")
		return
	var pts: Array = []
	for lane: Variant in m.map_def["lanes"]:
		var wps: Array = lane["waypoints"]
		for i: int in range(wps.size()):
			var wp: Variant = wps[i]
			pts.append(["%s:wp%d" % [lane["id"], i],
					Vector3(float(wp[0]), float(wp[1]), float(wp[2]))])
		var last: Variant = wps[wps.size() - 1]
		pts.append(["%s:end" % lane["id"],
				Vector3(float(last[0]), float(last[1]), float(last[2]))])
	for sid: String in m.map_def["spawners"]:
		var p: Variant = m.map_def["spawners"][sid]
		pts.append([String(sid), Vector3(float(p[0]), float(p[1]), float(p[2]))])
	pts.append(["core_main", m.core_main.pos])
	for sid: String in m.core_subs:
		pts.append([String(sid), m.core_subs[sid].pos])
	pts.append(["hero_space", Vector3.ZERO])
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	var worst := INF
	var worst_name := ""
	for e: Variant in pts:
		var sp: Vector2 = cam.unproject_position(e[1] as Vector3)
		lo = Vector2(minf(lo.x, sp.x), minf(lo.y, sp.y))
		hi = Vector2(maxf(hi.x, sp.x), maxf(hi.y, sp.y))
		var margin: float = minf(minf(sp.x, sp.y),
				minf(float(VIEW.x) - sp.x, float(VIEW.y) - sp.y))
		print("V1W-FRAME-PT %s px=%.1f,%.1f margin=%.1f" % [e[0], sp.x, sp.y,
				margin])
		if margin < worst:
			worst = margin
			worst_name = String(e[0])
	print("V1W-FRAME n=%d px_min=%.1f,%.1f px_max=%.1f,%.1f min_margin=%.1f worst=%s floor=%.1f" \
			 % [pts.size(), lo.x, lo.y, hi.x, hi.y, worst, worst_name,
			 MIN_MARGIN])
	if worst < MIN_MARGIN:
		_fail("frame margin %s=%.1f < %.1f" % [worst_name, worst, MIN_MARGIN])
		return


func _fail(why: String) -> void:
	_failed = true
	print("V1W-FAIL " + why)
	quit(1)
