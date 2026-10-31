# camera_zoom — the v1.3 mouse-wheel zoom owner (Z2, MC 11813; the one
# home: .audits/20261031-1100-v13-zoom-plan/ZOOM_SPEC.md §1–§2, the
# DA-verdict-c2 SHIP gate). A runtime, wheel-driven translation of the
# shipped CameraRig ORIGIN along its own frozen line of sight: wheel-UP
# steps D toward the map, wheel-DOWN steps it away, D clamped to
# [D_MIN, D_MAX] around the CAPTURED default. The rig owner is the scene:
# its default row (godot/scenes/mission.tscn:34,
# `transform = Transform3D(1, 0, 0, 0, 0.669, 0.743, 0, -0.743, 0.669,
# 0, 47.47, 42.79)`, |origin| ≈ 63.909 — the "D=64" shorthand) is NEVER
# EDITED and no `64` literal lives here: _capture reads the default FROM
# the parent rig at _ready. Zero wheel events = zero writes, so a fresh
# mission renders the byte-identical default frame (spec §2 proof-row).
#
# D3 PIN: the ONLY property this node touches is the rig position, and
# only ALONG the captured unit LOS — the basis (pitch) is never touched
# (position-only writes leave it byte-equal) and the camera FOV is never
# touched at all. Wheel is the ONLY shipped affordance (spec §1: +/− keys
# would be a second mechanism beside it and mission.gd is at the 400-LOC
# ceiling); the wheel never enters GWBridge — it rides the hub
# ScrollContainer precedent (hub.gd panel scroll), not the key relay.
#
# PRESENTATION constants (the declared-UNGOVERNED doctrine, the
# range_ring/world_text/sprite_bank/hero_pawn-crest precedent family):
# the envelope endpoints and the tick size live on THIS file; I2 guards
# gameplay ECONOMY literals and a camera distance cannot smuggle a cost
# or ratio, so this file stays OUT of GOVERNED_LITERALS (the set is 17).
#
# INPUT CONTRACT (spec §1, DA P1-2 — mechanism stated before build):
# node-local _unhandled_input; InputEventMouseButton with button_index
# in {MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN} (the field the
# shipped wheel model carries — tests/test_hub_scroll.py:249-251);
# PRESS-ONLY (releases ignored); and ONE step per event FRAME per
# button_index — the per-tick EDGE GUARD. The frame source is declared
# (DA note N-A): Engine.get_process_frames(), VERIFIED to advance one
# per _process frame under this pinned 4.7.2 -s harness. This collapses
# the web double-feed (one physical event arriving twice through two
# paths, bridge.gd G5b header / served 19715d4) to ONE step while two
# distinct ticks — always distinct frames — stay two steps. The bridge's
# rising-edge dedup is structurally unavailable (the wheel never enters
# GWBridge), so a node-local guard is the only home; it is wheel-path-
# only and never stands beside on_key as a second key mechanism.

extends Node

const D_MIN := 56.0      # closest allowed rig distance (u) — the derived
const D_MAX := 128.0     #   frustum floor + readable-far cap (spec §2)
const ZOOM_STEP := 8.0   # u per wheel tick, applied around the default

var _rig: Node3D = null
var _los := Vector3.ZERO   # frozen unit line of sight, captured at ready
var _dist := 0.0           # current distance; starts at the captured D
var _captured := false
var _last_frame := {}      # button_index -> frame of its last step


func _ready() -> void:
	_capture()


# The scene row is the ONE home of the default: read the parent rig's
# origin once, keep its direction and length. Idempotent (a second call
# never re-reads a moved rig — nor a moved default).
func _capture() -> void:
	if _captured:
		return
	_rig = get_parent() as Node3D
	if _rig == null:
		return
	_los = _rig.position.normalized()
	_dist = _rig.position.length()
	_captured = true


func _unhandled_input(event: InputEvent) -> void:
	var button := event as InputEventMouseButton
	if button == null or not button.pressed:
		return                     # press-only: releases never step
	var idx := int(button.button_index)
	var zooming := idx == MOUSE_BUTTON_WHEEL_UP \
			or idx == MOUSE_BUTTON_WHEEL_DOWN
	if not zooming:
		return
	_capture()                     # -s harnesses may skip _ready (E5)
	if not _captured:
		return
	var frame := Engine.get_process_frames()
	if int(_last_frame.get(idx, -1)) == frame:
		return                     # edge guard: one step per frame
	_last_frame[idx] = frame
	var step := -ZOOM_STEP if idx == MOUSE_BUTTON_WHEEL_UP \
			else ZOOM_STEP
	_dist = clampf(_dist + step, D_MIN, D_MAX)
	_rig.position = _los * _dist   # position-only: basis + FOV untouched
