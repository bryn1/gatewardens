# v11_sprite_probe — the V1.1-a/b headless render proof (MC 11466,
# (id, tier) rows since V1.1-b MC 11520). Boots the REAL Main.tscn
# composition root under -s, enters a mission through the shipped
# router (main.start_mission — never around it), and asserts on the
# LIVE scene tree that (1) the 12 committed batch-1 sheets load at
# 512px, (2) the sprite-backed entity nodes carry their bank texture
# — hero pawns (incl. the F2 hot-swap visibility) and spawned
# enemies — while placed defenses carry the LIVE V-B world shape: the
# TOWER_FORMS container defense_obj delegates to (MC 12082; the
# sprite-era obj.node-as-Sprite3D pin REDDENED on the live tree and
# was re-pinned by the MC 12116 de-stale, the VB-wave routed finding),
# (3) V1.1-b tier ladder: a ballista upgraded ONCE and
# a hailspire upgraded TWICE through the shipped defense_obj.upgrade()
# entry point swap-rebuild their live form, and the bank's committed
# (id, tier) answer stays pinned against the literal sheet path it
# must return; gate_blockade/barbed_snare ride the SAME container
# shape (their batch-2 Sprite3D pin re-pinned like the tower legs).
# (3b) Since the MC 11462 DA fix loop the warden_breaker boss carries
# its batch-5 sheet too, asserted path-pinned (the tier-leg pattern).
# (3c) Since clean-code W2 (MC 11575 CR-1) the bombard batch-3 T3 skin
# (committed unwired) rides the same leg shape: load + form swap-
# rebuild + the bank answer pinned against the literal path it must
# return.
# (4) the ONE facing mechanism flips the left-facing enemy sheets only
# on a screen-right step, at spawn and live through runner.step.
# Harness license (the mission_smoke precedent, declared): the main
# core is made 5x sturdier so the legs cannot end the mission, and
# `green` is written to fund the place and upgrade legs. Everything
# else drives real entry points. E5: -s never dispatches _ready —
# main._ready() is driven here.
# Machine rows, print order: SPRITEBANK-TEX HEROES SWAP TOWERS TIER
# TIER3 GATEART ENEMIES FLIP OK; any failure prints SPRITEBANK-FAIL
# <why> and quits 1.
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")

const MAIN_SCENE := "res://Main.tscn"
const HERO_IDS := ["warden", "deadeye", "embercaller"]
const TOWER_IDS := ["ballista", "bombard", "hailspire_tower"]
const ENEMY_IDS := ["skitterling", "husk_brute", "ash_bandit", "bone_lobber",
	"cinder_wisp", "gale_harpy"]
const FORM_PREFIX := "TowerForm"   # tower_forms FORM_NAME literal-PINNED
	# (never preloaded: a builder the probe asks is an oracle — the
	# bank-as-oracle lesson riding the tower legs since V1.1-b)


func _init() -> void:
	# Deck seed through the REAL C13 wiring before boot (mission_smoke
	# idiom), so the boot-time from_save carries the 3-hero deck.
	var seed_graph: Dictionary = GW_COMPOSE.build_graph(GW_TABLES.new("res://data"))
	seed_graph["state"].set_deck(HERO_IDS.duplicate())
	var packed = ResourceLoader.load(MAIN_SCENE)
	if packed == null:
		_fail("Main.tscn not loadable")
		return
	var main = packed.instantiate()
	root.add_child(main)
	main._ready()                                  # E5 (no loop dispatch)
	main.start_mission("gatefall", "normal")       # the shipped router
	var m = main.mission
	if m == null or String(m.phase_kind) != "build":
		_fail("router start_mission did not land a mission")
		return
	m.core_main.hp_max *= 5.0                      # license (header)
	m.core_main.hp = m.core_main.hp_max

	# --- 1) the 12 committed sheets load at their authored size ---
	var n := 0
	for id: String in HERO_IDS + TOWER_IDS + ENEMY_IDS:
		var tex := SPRITE_BANK.texture_for(id)
		if tex == null or tex.get_width() != 512 or tex.get_height() != 512:
			_fail("sheet missing or not 512px: %s" % id)
			return
		n += 1
	print("SPRITEBANK-TEX n=%d px=512" % n)

	# --- 2) hero pawns carry their sheet, greybox capsule hidden ---
	var rig = m.get_node("HeroRig")
	for hid: String in HERO_IDS:
		var pawn = rig.pawns[hid]
		var spr: Sprite3D = pawn.get_node_or_null("Sprite")
		if spr == null or spr.texture != SPRITE_BANK.texture_for(hid) \
				or pawn.get_node("Visual").visible:
			_fail("hero pawn sheet missing or greybox visible: %s" % hid)
			return
	print("SPRITEBANK-HEROES n=3")

	# Enter combat the way the game does (the build timer, not a write),
	# then the hot-swap leg: F2 through the bridge, one real step.
	var guard := 0
	while guard < 1700 and String(m.phase_kind) == "build":
		m.step(1.0 / 60.0)
		guard += 1
	if String(m.phase_kind) != "combat":
		_fail("combat never started")
		return
	m.bridge.on_key("F2", true)
	m.bridge.on_key("F2", false)
	m.step(1.0 / 60.0)      # step (5) records the swap ...
	m.step(1.0 / 60.0)      # ... the next slot-(2) tick paints it
	if int(m.active) != 1 or not bool(rig.pawns["deadeye"].visible) \
			or bool(rig.pawns["warden"].visible):
		_fail("F2 hot-swap visibility: active=%d" % int(m.active))
		return
	print("SPRITEBANK-SWAP active=1 visible=deadeye")

	# --- 3) placed defenses carry the LIVE world shape: the TowerForm
	#         container defense_obj._make_visual delegates to since V-B
	#         (MC 12082). The sprite-era sheet-on-node pin retired with
	#         that delegation (MC 12116 de-stale); the form's mesh/
	#         turret/aim CONTRACT is test_tower_forms.py's home — this
	#         leg pins only the shape the bank era pinned: the visual
	#         that stands on the placed slot. ---
	m.green = 100000                               # license (header)
	var trows := {}
	for row: Dictionary in m.tables.rows("towers"):
		trows[String(row["id"])] = row
	var ti := 0
	var tobjs := {}
	for tid: String in TOWER_IDS:
		var pl: Dictionary = m.place_defense(trows[tid], 1, Vector3(ti, 0.0, 0.0))
		if not bool(pl["ok"]):
			_fail("place_defense refused %s: %s" % [tid, str(pl)])
			return
		var obj = (m.defense_list[-1] as Dictionary)["obj"]
		if not _is_form(obj.node):
			_fail("tower form: %s" % tid)
			return
		tobjs[tid] = obj
		ti += 1
	print("SPRITEBANK-TOWERS n=3")

	# --- 3b) V1.1-b tier ladder through the SHIPPED upgrade entry point:
	#         ballista upgraded once and hailspire twice SWAP-REBUILD the
	#         live TowerForm (the V-B shape, MC 12116 re-pin) and the
	#         tier index rides the ladder. The committed tier sheet is
	#         pinned through the bank answer against its committed
	#         RESOURCE PATH literal — asking the bank whether its own
	#         answer holds was the proven false-green shape (a dropped
	#         T3 key reads green through the T1 fallback); here the
	#         compare TARGET is the literal, so a dropped entry reddens
	#         the map itself. ---
	for legs: Array in [
			["ballista", 1, "res://assets/v11/tower_ballista_T2.png"],
			["hailspire_tower", 2, "res://assets/v11/tower_hailspire_T3.png"]]:
		var tid2: String = String(legs[0])
		var tobj = tobjs[tid2]
		var form0 := int(tobj.node.get_instance_id())
		for _i in range(int(legs[1])):
			var up: Dictionary = tobj.upgrade()
			if not bool(up["ok"]):
				_fail("upgrade refused %s: %s" % [tid2, str(up)])
				return
		var uobj = tobj
		var want_tier: int = int(legs[1]) + 1
		if not _is_form(uobj.node) \
				or int(uobj.node.get_instance_id()) == form0 \
				or int(uobj.tier) != want_tier - 1:
			_fail("tier form swap: %s T%d" % [tid2, want_tier])
			return
		var tier_tex: Texture2D = SPRITE_BANK.texture_for(tid2, want_tier)
		if tier_tex == null \
				or String(tier_tex.resource_path) != String(legs[2]):
			_fail("tier sheet map: %s T%d" % [tid2, want_tier])
			return
	print("SPRITEBANK-TIER ballista=T2 hailspire=T3")

	# --- 3c) W2 (MC 11575 CR-1): bombard T3 — the batch-3 skin that
	#        shipped COMMITTED BUT UNWIRED (dead weight in the pck, the
	#        T3 tower still painted T1). Same tier-leg idiom (V-B
	#        re-pin, MC 12116), three assertions: the committed sheet
	#        LOADS as a Texture2D, the live slot upgraded twice through
	#        the shipped upgrade() entry point SWAP-REBUILDS its
	#        TowerForm, and the bank's own answer for ("bombard", 3) is
	#        pinned against the literal path it must return — a dropped
	#        entry goes RED on the map. ---
	var bomb_t3 := "res://assets/v11/tower_bombard_T3.png"
	var t3res := ResourceLoader.load(bomb_t3)
	if t3res == null or not (t3res is Texture2D):
		_fail("bombard T3 sheet does not load as Texture2D")
		return
	var bobj = tobjs["bombard"]
	var bform0 := int(bobj.node.get_instance_id())
	for _i in range(2):
		var bup: Dictionary = bobj.upgrade()
		if not bool(bup["ok"]):
			_fail("upgrade refused bombard: %s" % str(bup))
			return
	if not _is_form(bobj.node) \
			or int(bobj.node.get_instance_id()) == bform0 \
			or int(bobj.tier) != 2:
		_fail("tier form swap: bombard T3")
		return
	var bank_t3: Texture2D = SPRITE_BANK.texture_for("bombard", 3)
	if bank_t3 == null or not String(bank_t3.resource_path) \
			.contains("tower_bombard_T3"):
		_fail("bank answer for bombard T3 is not the T3 sheet")
		return
	print("SPRITEBANK-TIER3 bombard=T3")

	# --- 4) V1.1-b gate art exits the greybox; since V-B (MC 12082)
	#        gate_blockade / barbed_snare ride the SAME TowerForm
	#        container shape as the shooters — the batch-2 Sprite3D
	#        sheet pin re-pinned with the tower legs (MC 12116) ---
	for gid: String in ["gate_blockade", "barbed_snare"]:
		var pl2: Dictionary = m.place_defense(trows[gid], 1,
				Vector3(20 + ti, 0.0, 0.0))
		if not bool(pl2["ok"]):
			_fail("place_defense refused %s: %s" % [gid, str(pl2)])
			return
		if not _is_form(((m.defense_list[-1] as Dictionary)["obj"]).node):
			_fail("%s not a tower form" % gid)
			return
		ti += 1
	print("SPRITEBANK-GATEART blockade=form trap=form")

	# --- 5) spawned enemies carry their sheet (lane_g1 walks +x: the
	#        left-facing sheets must already read flip at spawn) ---
	var runner = m.get_node("EnemyRunner")
	var lane_g1: Dictionary = m.lanes["lane_g1"]
	for eid: String in ENEMY_IDS:
		runner.spawn({"enemy_id": eid, "count": 1}, lane_g1, m.enemy_defs, m.rng)
		var ent: Dictionary = runner.entities[-1]
		var espr: Sprite3D = ent["node"] as Sprite3D
		if espr == null or espr.texture != SPRITE_BANK.texture_for(eid) \
				or not espr.flip_h:
			_fail("enemy sheet/flip on a +x lane: %s" % eid)
			return
	# --- 5b) the boss (MC 11462 DA fix loop): warden_breaker now
	#        carries its batch-5 sheet. Pinned by its committed RESOURCE
	#        PATH, never through the bank — asking the bank was the
	#        proven false-green shape (the tier-leg comment above). ---
	runner.spawn({"enemy_id": "warden_breaker", "count": 1}, lane_g1,
			m.enemy_defs, m.rng)
	var bspr: Sprite3D = runner.entities[-1]["node"] as Sprite3D
	var boss_want := "res://assets/v11/enemy_warden_breaker.png"
	if bspr == null or String(bspr.texture.resource_path) != boss_want:
		_fail("boss sheet path-pinned: warden_breaker")
		return
	print("SPRITEBANK-ENEMIES n=6 boss_sheet=1")

	# --- 6) the ONE facing mechanism, live through runner.step ---
	# Synthetic lanes (the shipped map has no pure ±x lane); wps typed
	# Array[Vector3] exactly like mission_world.build_lanes authors them.
	var wps_r: Array[Vector3] = [Vector3(-40.0, 0.0, 0.0),
			Vector3(-20.0, 0.0, 0.0)]
	var wps_l: Array[Vector3] = [Vector3(-20.0, 0.0, 0.0),
			Vector3(-40.0, 0.0, 0.0)]
	var lane_r := {"id": "probe_r", "kind": "ground", "target": "main",
		"wps": wps_r}
	var lane_l := {"id": "probe_l", "kind": "ground", "target": "main",
		"wps": wps_l}
	runner.spawn({"enemy_id": "skitterling", "count": 1}, lane_r, m.enemy_defs, m.rng)
	var ent_r: Dictionary = runner.entities[-1]
	runner.spawn({"enemy_id": "skitterling", "count": 1}, lane_l, m.enemy_defs, m.rng)
	var ent_l: Dictionary = runner.entities[-1]
	runner.step(1.0)
	if not bool((ent_r["node"] as Sprite3D).flip_h) \
			or bool((ent_l["node"] as Sprite3D).flip_h):
		_fail("facing after live step: r=%s l=%s" % [
				str((ent_r["node"] as Sprite3D).flip_h),
				str((ent_l["node"] as Sprite3D).flip_h)])
		return
	print("SPRITEBANK-FLIP right=flipped left=plain")
	print("SPRITEBANK-OK")
	quit(0)


# The V-B live world shape (MC 12116 re-pin): defense_obj hands back the
# tower_forms container — "TowerForm_<uid>", geometry under it, parented
# by place_defense. SHAPE-only pin (name prefix + kids + parented): the
# form's mesh/turret/aim CONTRACT stays test_tower_forms.py's one home —
# no second copy here (the probe never preloads tower_forms: a builder
# the probe asks about its own name is an oracle).
func _is_form(nd) -> bool:
	return nd != null and is_instance_valid(nd) \
			and nd.get_parent() != null \
			and String(nd.name).begins_with(FORM_PREFIX) \
			and nd.get_child_count() > 0


func _fail(why: String) -> void:
	print("SPRITEBANK-FAIL " + why)
	quit(1)
