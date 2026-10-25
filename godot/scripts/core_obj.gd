# core_obj — one core record (Modules row scripts/core_obj.gd,
# MC 11274.1.13 / card 11308): main + sub cores. The greybox box mesh is
# authored by mission.gd from C7 data; this record owns the health values
# and the destroyed transition (game-over / open-lane-on-death live in the
# mission's bookkeeping, which reads destroyed + opens_lanes — C7).
#
# take_damage(d) takes the MITIGATED amount: callers route damage through
# SimCombat.dmg_to_core (the pinned core row) and never inline HP math.
#
# Readings recorded on the card trail: RefCounted record in the scene layer
# (same mechanism as bridge/game_state — injectable under `-s`); the
# "health bar" of the pinned row is the hp/hp_max pair the C5 cores dict
# exposes every frame; a destroyed core takes no further damage (the death
# transition fires once).

var id := "main"
var kind := "main"            # "main" | "sub"
var hp := 0.0
var hp_max := 0.0
var pos := Vector3.ZERO
var opens_lanes: Array = []   # lane ids this sub-core's death opens (C7)
var destroyed := false
var node = null               # greybox MeshInstance3D (mission-authored)


func take_damage(d: float) -> void:
	if destroyed:
		return
	hp = maxf(hp - d, 0.0)
	if hp <= 0.0:
		destroyed = true
