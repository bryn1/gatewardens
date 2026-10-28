# enemy_anim — the procedural enemy walk pose (v1.2 F5, MC card 11610 /
# milestone 11462, V12-PLAN §F5 decision (i) PROCEDURAL). WHAT: pure
# helpers the enemy runner calls once per walk tick — phase accumulates
# with the DISTANCE walked (plan line: phase += |velocity|*delta, in the
# distance lane_path already integrated), the pose is |sin(phase)|*amp on
# y plus a small sin sway on the billboard's roll (face()'s flip_h is
# orthogonal, untouched). WHY PROCEDURAL: the plan REJECTED (ii) 6
# generated 2-frame sheets (real 3090 budget; 2-frame pop at variable
# walk speeds reads as strobe, not gait; per-id pose state would be a
# SECOND visual path beside sprite_bank.make_sprite) and (iii) the
# hybrid (one enemy with a different motion language, both code paths).
# The committed enemy_skitterling_run.png stays declared-UNWIRED (its
# natural home if the owner ever wants it is an optional pose-map INSIDE
# this helper — one mechanism, not two).
#
# VISUAL LAYER ONLY (binding): the pose NEVER writes ent["pos"] — the
# runner hands it the pos it already published and the step distance it
# already computed; only node.position/rotation.z ride the offset, so
# every sim row, every golden fixture and every hitbox stays byte-
# identical (the test file's ent-pos single-write pin is the golden
# proxy). The constants live HERE, ungoverned (the declared precedent is
# fx_director owning MAX_FX/scale outside I2; enemy_runner.gd IS I2-
# governed and gains exactly ONE call line, zero literals). balance.
# feel is exact-set-pinned (test_data_schemas), so nothing lands in data.
# Determinism: a pure function of accumulated path length — no RNG, no
# timers, no extra Nodes; the phase accumulator rides the VISUAL node as
# meta and dies with it (plan: reuse the _process visual update).
extends RefCounted

# UNGOVERNED VISUAL CONSTANTS (plan F5: values declared with rationale).
const PHASE_PER_UNIT := 9.0   # rad of phase per world unit WALKED: one
                              # full bob cycle every TAU/9.0 = 0.70 u, so
                              # the shipped speeds 1.8-5.0 u/s (enemies.
                              # json) cycle ~1.1-3.2 times/s (~2.2-4.6
                              # |sin| steps/s) — an alive shuffle, never
                              # the F5-vetoed strobe
const BOB_AMP := 0.23        # world-unit vertical bob amplitude: the
                              # enemy billboard is WORLD_H_UNIT 2.0 u
                              # tall and renders ~13 px at the shipped
                              # camera (1 px ~= 0.154 u), so 0.23 u ~=
                              # 1.5 px sits mid of the plan's honest
                              # limitation band "the bob is +-1-2 px"
const SWAY_AMP := 0.06        # billboard roll sway, radians (~3.4 deg):
                              # reads as lean at 13 px, stays under the
                              # jitter-percept threshold at this scale
const PHASE_META := &"gw_walk_phase"   # accumulator key on the VISUAL
                              # node only — freed with the node, so the
                              # runner record carries zero visual state


# Phase after walking `distance` further (the plan's phase += |vel|*dt,
# distance-integrated form). absf on the input so a caller can never
# walk the phase backwards; fmod wrap keeps the accumulator bounded in
# [0, TAU) for float stability over a whole mission.
static func phase_advance(prev: float, distance: float) -> float:
	return fmod(prev + absf(distance) * PHASE_PER_UNIT, TAU)


# The vertical bob (the plan's |sin(phase)|*amp): never dips BELOW the
# lane's authored y — F16 owns y (ground 0, air at the flight height),
# this rides ON TOP of the sim y, it never replaces it.
static func bob_offset(phase: float) -> float:
	return absf(sin(phase)) * BOB_AMP


# The roll sway: a lean about the world Z axis, which is the screen
# plane for the shipped rig (camera at +Z looking -Z, V1.1-a row).
static func sway_offset(phase: float) -> float:
	return sin(phase) * SWAY_AMP


# THE MOUNT (enemy_runner.step, visual branch): one call per tick with
# the sim-published pos (mission-local space, root identity) and the
# step distance the walk already has. A zero-distance step at a fresh
# node lands the pose byte-identical on `base` (sin(0) = 0 exactly), so
# a standing enemy paints exactly what the pre-F5 tree painted.
static func walk_step(node: Node, base: Vector3, distance: float) -> void:
	var phase := phase_advance(float(node.get_meta(PHASE_META, 0.0)),
			distance)
	node.set_meta(PHASE_META, phase)
	node.position = base + Vector3(0.0, bob_offset(phase), 0.0)
	node.rotation.z = sway_offset(phase)
