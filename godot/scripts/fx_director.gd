# fx_director — V5 combat FX via a VISUAL-ONLY OBSERVER (MC card 11552
# / milestone 11462, VISUAL-TARGET row V5). The binding ruling for this
# card: THE SIM IS NOT TOUCHED — no state, signal or step-order edit in
# mission/enemy_runner/defense_obj/mission_world, and the sim's fires
# are instant with no event stream (inventing one would be the
# forbidden second mechanism). So every FX here is DERIVED FROM OUTSIDE:
# one fx_step(delta) pass compares the director's own last-frame
# snapshot against the sim's published fields (defense records, the
# runner's entities array) and paints the delta — it NEVER writes to a
# sim object (reads only: pos/tier fields via the public accessors,
# runner.entities/nearest, no mutators, no signal wiring).
#
# Mount: mission.tscn ships it as the root's LAST scene child (the
# smallest hook that cannot reorder sim steps — the root's _process
# runs step() first, then this node's _process observes the finished
# frame; the probe drives fx_step() by hand under -s exactly like
# mission.step is driven by hand, E5 idiom).
#
# Detection readings (declared on the card):
# - FIRE -> TRACER: the sim ships NO per-shot cooldown field (defense
#   fire is sustained dps x delta against the nearest entity), so the
#   observable "shot this frame" = the defense's OWN current nearest
#   target lost hp this frame by >= dps*delta (the sim's exact applied
#   amount through its public dps()/bonus_row() accessors, halved for
#   float margin). A blockade (dps 0) never qualifies. Tracer art per
#   tower data id: ballista = fx_proj_bolt, hailspire_tower =
#   fx_proj_ice, bombard = fx_proj_bolt — the bomb T3 sheet is a LATER
#   VISUAL-TARGET row; the bolt standing in for both is the brief's
#   declared reading, not an oversight.
# - DAMAGE -> SPARK: any tracked entity whose hp DROPPED between frames
#   gets one spark (hero hits qualify too — the row is damage-driven).
# - DESPAWN -> POOF: the brief's "vanished with hp<=0" is realized as
#   the observationally equivalent half of the despawn split: the
#   runner drains dead AND arrived entities inside the same mission
#   step, so an outside observer never catches hp<=0 inside the live
#   entities array — the death case is therefore the despawn whose
#   last-known pos is NOT at the lane's final waypoint (a breacher is
#   consumed AT the waypoint, hp>0; and a future hp<=0 despawn still
#   poofs via the primary hp check).
#
# Cost discipline: at most MAX_FX live fx nodes; past the cap NEW fx
# are DROPPED (never freed early — the cap protects the frame, the
# look stays honest). Every fx node is a child of THIS node: mission
# cleanup frees the director and every fx with it (no leaks, probe row).

extends Node3D

const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")

# Tower data id -> projectile fx id (declared reading in the header;
# unlisted firing ids ride the bolt default).
const PROJ_FOR := {
	"ballista": "fx_proj_bolt",
	"hailspire_tower": "fx_proj_ice",
	"bombard": "fx_proj_bolt",
}
const PROJ_DEFAULT := "fx_proj_bolt"

const MAX_FX := 64            # live fx node cap (header: drop NEW past it)
const TRACER_LIFE := 0.2      # seconds, brief's 0.15-0.25 window
const SPARK_LIFE := 0.2
const POOF_LIFE := 0.3
const FX_H_SPARK := 1.2       # world-unit heights (512px sheets:
const FX_H_POOF := 2.2        # Sprite3D maps 100px to 1u at scale 1)
const FX_H_PROJ := 1.0
const FX_LIFT := Vector3(0.0, 1.0, 0.0)   # paint above the ground line
const HP_EPS := 1e-6          # float margin on "hp changed at all"
const FIRE_FRAC := 0.5        # observed drop / sim-applied dps*delta
const REACH_EPS := 0.5        # "at the lane's final waypoint" radius

# Probe counters (READ-ONLY for probing, brief row 5: plain vars the
# probe reads — nothing in the sim reads them).
var spawned_tracers := 0
var spawned_sparks := 0
var spawned_poofs := 0
var live_max := 0             # high-water mark of live fx nodes

var _tracked := {}            # entity node instance-id -> snapshot dict
var _fx := []                 # live fx bookkeeping, parallel to children


func _process(delta: float) -> void:
	fx_step(delta)


# One observation pass over the finished frame. Public so the headless
# probe can drive it in lockstep with mission.step (E5: -s dispatches
# no _process).
func fx_step(delta: float) -> void:
	var m = get_parent()
	if m == null or not ("defense_list" in m):
		return                 # not set up (E5: scene child, pre-setup)
	var runner = m.get_node_or_null("EnemyRunner")
	if runner == null:
		return
	var drops := _observe_enemies(runner)   # iid -> hp lost this frame
	_observe_fires(m, runner, drops, delta)
	_advance_fx(delta)
	live_max = maxi(live_max, _fx.size())


# Entity tracking: hp drops spark, despawns poof. Snapshots carry only
# plain values (hp float, pos Vector3, lane-end Vector3) — no sim
# object is ever held past the frame it was read in.
func _observe_enemies(runner) -> Dictionary:
	var drops := {}
	var seen := {}
	for ent: Dictionary in runner.entities:
		var iid: int = (ent["node"] as Node).get_instance_id()
		var hp := float(ent["hp"])
		var pos: Vector3 = ent["pos"]
		var prev: Variant = _tracked.get(iid)
		if prev != null and hp < float(prev["hp"]) - HP_EPS:
			drops[iid] = float(prev["hp"]) - hp
			_spawn_spark(pos)
		if prev == null:
			var wps: Array = (ent["lane"] as Dictionary).get("wps", [])
			_tracked[iid] = {"hp": hp, "pos": pos,
					"end": wps[wps.size() - 1] if not wps.is_empty()
							else pos}
		else:
			prev["hp"] = hp
			prev["pos"] = pos
		seen[iid] = true
	for iid: int in _tracked.keys():
		if seen.has(iid):
			continue
		var snap: Dictionary = _tracked[iid]
		var end: Vector3 = snap["end"]
		if float(snap["hp"]) <= 0.0 \
				or (snap["pos"] as Vector3).distance_to(end) > REACH_EPS:
			_spawn_poof(snap["pos"])
		_tracked.erase(iid)
	return drops


# Fire detection: the defense's own nearest target lost the sim's exact
# frame damage (public reads only: obj.pos/hp/dps()/bonus_row(), the
# runner's nearest — the same selection the sim itself just made).
func _observe_fires(m, runner, drops: Dictionary, delta: float) -> void:
	if drops.is_empty():
		return
	for rec: Dictionary in m.defense_list:
		var obj = rec["obj"]
		if float(obj.hp) <= 0.0:
			continue
		var applied := float(obj.dps()) * delta
		if applied <= 0.0:
			continue            # blockade (and dead-fire classes) never
		var row: Dictionary = obj.bonus_row()
		var target: Dictionary = runner.nearest(obj.pos, float(row["range"]))
		if target.is_empty():
			continue
		var iid: int = (target["node"] as Node).get_instance_id()
		if float(drops.get(iid, 0.0)) < applied * FIRE_FRAC:
			continue
		_spawn_tracer(obj.pos, target["pos"], String(
				PROJ_FOR.get(String(obj.trow["id"]), PROJ_DEFAULT)))


# ---- fx spawn + lifetime (all children of THIS node, header) ----

func _spawn_tracer(from: Vector3, to: Vector3, fx_id: String) -> void:
	var e := _spawn_fx(fx_id, from + FX_LIFT, TRACER_LIFE, FX_H_PROJ)
	if e.is_empty():
		return
	e["from"] = from + FX_LIFT
	e["to"] = to + FX_LIFT      # a target freed this frame still reads
	spawned_tracers += 1        # its last observed pos via the drop leg


func _spawn_spark(at: Vector3) -> void:
	if not _spawn_fx("fx_spark_hit", at + FX_LIFT, SPARK_LIFE,
			FX_H_SPARK).is_empty():
		spawned_sparks += 1


func _spawn_poof(at: Vector3) -> void:
	if not _spawn_fx("fx_poof_death", at + FX_LIFT, POOF_LIFE,
			FX_H_POOF).is_empty():
		spawned_poofs += 1


# The ONE billboard factory here: bank texture (the same id->file map —
# V5 card row 3), camera-facing, footprint-scaled like make_sprite.
# {} = nothing spawned (bank null OR the MAX_FX cap dropped it).
func _spawn_fx(fx_id: String, at: Vector3, life: float,
		h: float) -> Dictionary:
	if _fx.size() >= MAX_FX:
		return {}               # cost cap: drop NEW (header discipline)
	var tex := SPRITE_BANK.texture_for(fx_id)
	if tex == null:
		return {}
	var s := Sprite3D.new()
	s.texture = tex
	s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	s.scale = Vector3.ONE * (h / (float(tex.get_height()) / 100.0))
	s.position = at
	add_child(s)
	var e := {"node": s, "life": life}
	_fx.append(e)
	return e


# Age out; tracers travel their chord over their short life. Reverse
# walk so free() during iteration is safe.
func _advance_fx(delta: float) -> void:
	for i: int in range(_fx.size() - 1, -1, -1):
		var e: Dictionary = _fx[i]
		e["life"] = float(e["life"]) - delta
		var node: Sprite3D = e["node"]
		if float(e["life"]) <= 0.0:
			_fx.remove_at(i)
			remove_child(node)
			node.free()
		elif e.has("from"):
			var k := 1.0 - float(e["life"]) / TRACER_LIFE
			node.position = (e["from"] as Vector3).lerp(e["to"], k)
