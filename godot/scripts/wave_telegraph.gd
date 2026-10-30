# wave_telegraph — build-phase wave telegraph billboards (v1.2.1 G3,
# MC 11696 / V121-PLAN §G3). During the BUILD phase the NEXT wave's
# carriers are previewed per spawner: the enemy's OWN sheet icon (ids
# already in sprite_bank.TEXTURES — the G3 row's "ids already in the
# bank") + one world_text count, grouped by lane -> spawner through the
# ONE shared raw lane read, MISSION_WORLD.raw_lane_rows (build_lanes
# drops the per-lane "spawner" key, §0; map_def is the public read the
# plan names and the helper is its single home, D-2 fold MC 11723).
# Cleared at wave start, re-shown next build phase with UPDATED
# counts (the plan's HUD split: panel = when, billboards =
# what/where).
#
# OBSERVER doctrine (the fx_director header extends here, plan §G3):
# ZERO writes to sim state — reads only, no mutators. Detection rides
# its OWN _process diffing the public mission fields (m.phase_kind,
# m.wave — the plan row's named field set): the phase_changed signal
# fires "combat" EXACTLY once per wave start (§0 anchor,
# phase_controller.gd:82), so the observer reacts to that edge's
# observable EFFECT — phase_kind build->combat — which is the same
# event, without signal wiring (the fx doctrine's "no signal wiring"
# line; G8 owns the wave's one signal connect). The diff also makes it
# boot-order-proof (the G8/DA-A2 class): whatever state the first
# observation lands in IS the state it paints or clears, so no edge
# can be missed the way a late listener misses the wave-0 build emit.
#
# Mount: mission.tscn scene child (the FxDirector precedent, :43) —
# mission.gd sits at the 400-line ceiling and adds ZERO lines. Probe
# drives telegraph_step() by hand under -s exactly like fx_step (E5:
# -s dispatches no _process); every entry node is a child of THIS
# node, so mission cleanup frees the telegraph and its billboards.
#
# Ground/air distinction (declared, plan row "winged marks air" kin):
# an entry rides its group's lane SPAWN HEIGHT — the first waypoint's
# y read straight off the raw map lane row (gatefall: ground 0.0, air
# 2.5) — so air carriers preview ABOVE the ground stack at the same
# gate, mirroring the altitude their lane spawns them at. Multiple
# entries per gate stack per kind by ROW_GAP (presentation numbers
# live here, the ungoverned-file doctrine — the sprite_bank ICON_PX
# precedent).

extends Node3D

const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")
const WORLD_TEXT := preload("res://scripts/world_text.gd")
const SIM_WAVE := preload("res://sim/sim_wave.gd")
# D-2 fold (MC 11723): the raw lane->spawner read has ONE home,
# mission_world.raw_lane_rows — the door this observer now calls
# (mission_world preloads nothing back: no cycle).
const MISSION_WORLD := preload("res://scripts/mission_world.gd")

const ICON_H := 1.6       # small: the preview must not out-shout the gate
const COUNT_H := 1.0      # world_text line height (make_text scales to it)
const BASE_Y := 6.5       # above the 5u G1 gate-eye (its top ~5.5)
const ROW_GAP := 2.6      # per-kind stack step at one gate
const COUNT_LIFT := 1.2   # count rides beside the icon, not on it

# Probe reads (READ-ONLY for probing, the fx counter idiom — plain
# vars, nothing in the sim reads them): spawner id -> entries, and the
# live entry count. Empties on the combat edge together with the nodes.
var shown: Dictionary = {}
var shown_total := 0

var _last_phase := ""     # observer's own last-frame snapshot
var _last_wave := -1


func _process(_delta: float) -> void:
	telegraph_step()


# One observation pass over the finished frame (public: the -s probe
# drives it in lockstep AFTER mission.step, the exact live tree order).
func telegraph_step() -> void:
	var m = get_parent()
	if m == null or not ("waves_file" in m) or m.waves_file.is_empty():
		return                 # not set up (E5: scene child, pre-setup)
	var phase := String(m.phase_kind)
	var w := int(m.wave)
	if phase == _last_phase and w == _last_wave:
		return                 # no phase/wave edge since the last frame
	_last_phase = phase
	_last_wave = w
	if phase != "build":
		_clear()               # the combat edge (header): markers GONE
		return
	_paint(m, w)


# Group the upcoming wave's spawn rows into per-gate entries. THE READ
# SITES, all read-only: SIM_WAVE.wave_comp(waves_file, i) — the sim's
# OWN wave-row read, the same one mission.start_wave drives; and the
# raw lane rows through MISSION_WORLD.raw_lane_rows (the §0 public read
# that still carries per-lane "spawner"/"kind"/waypoint-y — ONE home
# shared with the gate-eye wing read, D-2 fold MC 11723). Counts are
# summed per (spawner, enemy_id, kind), so multi-lane groups add up.
func _paint(m, w: int) -> void:
	_clear()
	var waves: Array = m.waves_file.get("waves", [])
	if w < 0 or w >= waves.size():
		return                 # defensive: no such wave row to preview
	var lane_rows: Dictionary = MISSION_WORLD.raw_lane_rows(m)
	var counts := {}
	var origin_y := {}
	for row: Dictionary in SIM_WAVE.wave_comp(m.waves_file, w):
		var lane: Dictionary = lane_rows.get(String(row.get("lane", "")), {})
		if lane.is_empty():
			continue           # unknown lane id: preview nothing, stay honest
		var sid := String(lane.get("spawner", ""))
		if not m.map_def.get("spawners", {}).has(sid):
			continue
		var kind := String(lane.get("kind", ""))
		var key := sid + "|" + String(row.get("enemy_id", "")) + "|" + kind
		counts[key] = int(counts.get(key, 0)) + int(row.get("count", 0))
		if not origin_y.has(key):
			var wps: Array = lane.get("waypoints", [])
			var wp: Array = wps[0] if not wps.is_empty() else [0.0, 0.0, 0.0]
			origin_y[key] = float(wp[1])
	# Deterministic stacking (sorted keys — the scene mirrors `shown`).
	var keys: Array = counts.keys()
	keys.sort()
	var stacks := {}
	for key: String in keys:
		var parts: PackedStringArray = key.split("|")
		var sid: String = parts[0]
		var stack := int(stacks.get(sid + "|" + parts[2], 0))
		stacks[sid + "|" + parts[2]] = stack + 1
		var icon := SPRITE_BANK.make_sprite(parts[1], ICON_H)
		if icon == null:
			continue           # un-sprited id mounts nothing (bank guard)
		var sp: Array = m.map_def["spawners"][sid]
		var at := Vector3(float(sp[0]), BASE_Y + float(origin_y[key]) \
				+ float(stack) * ROW_GAP, float(sp[2]))
		icon.position = at
		add_child(icon)
		add_child(WORLD_TEXT.make_text(str(int(counts[key])),
				at + Vector3(0.0, COUNT_LIFT, 0.0), COUNT_H))
		if not shown.has(sid):
			shown[sid] = []
		shown[sid].append({"id": parts[1], "kind": parts[2],
				"count": int(counts[key]), "y": at.y})
		shown_total += 1


func _clear() -> void:
	for c: Node in get_children():
		remove_child(c)
		c.free()
	shown = {}
	shown_total = 0
