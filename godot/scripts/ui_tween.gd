# ui_tween — the ONE shared menu-motion mechanism (V6, MC card 11530 /
# milestone 11462). GATE FACT (VERIFIED 2026-10-27): no UI script
# animated anything before this card — grep create_tween/Tween over
# godot/**/*.gd lands zero animation sites — so this file IS that path,
# not a second mechanism beside an old one. Hub stations call enter()
# on the NEWLY OPENED panel's content box (tab switch); attach() is the
# one-line hover/press scale on the hub tab bar + defense-panel buttons.
# ENGINE FACTS (VERIFIED 4.7.2 this card, sim/v6_tween_probe.gd rows):
# Control has NO "position_offset" property (the brief name does not
# exist in the engine); the visual-only family is
# offset_transform_enabled / offset_transform_position /
# offset_transform_visual_only, with pivot_offset_ratio centring any
# scale pivot at every size. With _visual_only = true the engine keeps
# layout, input and every get_global_rect() PINNED through the
# animation (the probe prints the same rect mid-tween and at rest).
# .from() carries the start values INSIDE the tween — nothing at rest
# is written synchronously (probe row V6-ATREST-START pins the rest
# values on the switch frame, before any pump), so a headless -s leg
# that never pumps frames still measures pixel-rest geometry.
# At rest everything here is identity — offset ZERO, modulate
# Color(1,1,1,1), scale ONE — and the tween ENDS on those values plus
# _at_rest re-pins them on finished, so a settled panel is pixel-
# identical to a never-animated one.
# THE HONEST CUT (declared, the brief's fallback clause): the OUTGOING
# panel keeps the shipped synchronous hide instead of a leave-fade —
# hub_probe_stations.gd asserts the previous station's visible == false
# in the SAME synchronous call (:93), so deferring the flip into a fade
# is exactly the logic change this card forbids, and an invisible
# "fade" on a hidden root would be theater, not motion. Every panel
# still animates: the station you navigate TO slides + fades.
extends RefCounted

const SLIDE_PX := 24.0            # ~24px in from the navigation side
const ENTER_SECS := 0.15          # the brief's 0.12-0.18 band
const HOVER_SCALE := 1.03         # the brief's 1.0->1.03->1.0 cycle
const REST_SCALE := 1.0
const PRESS_SECS := 0.08
const MOTION_META := &"gw_motion"   # the node's current motion tween


# The tab-switch ENTER: the opened panel's CONTENT box slides SLIDE_PX
# from the side the navigation came from (dir: +1 from the right,
# -1 from the left) and fades in, both over ENTER_SECS.
static func enter(content: Control, dir: float) -> void:
	content.offset_transform_enabled = true
	content.offset_transform_visual_only = true
	_kill_prev(content)
	var t := content.create_tween()
	content.set_meta(MOTION_META, t)
	t.set_parallel(true)
	t.tween_property(content, "offset_transform_position", Vector2.ZERO,
			ENTER_SECS).from(Vector2(SLIDE_PX * dir, 0.0))
	t.tween_property(content, "modulate", Color(1, 1, 1, 1),
			ENTER_SECS).from(Color(1, 1, 1, 0))
	t.finished.connect(_at_rest.bind(content))


# The one-line BUTTON feedback: hover/press scale 1.0->1.03->1.0 with a
# centred pivot (pivot_offset_ratio — centred at EVERY size, no manual
# pivot math). Same signals the mouse drives; zero logic added.
static func attach(button: Button) -> Button:
	button.pivot_offset_ratio = Vector2(0.5, 0.5)
	button.mouse_entered.connect(_scale_to.bind(button, HOVER_SCALE))
	button.mouse_exited.connect(_scale_to.bind(button, REST_SCALE))
	button.button_down.connect(_scale_to.bind(button, HOVER_SCALE))
	button.button_up.connect(_release.bind(button))
	return button


static func _release(button: Button) -> void:
	# the press cycle lands back on the hover state it actually sits in
	var still_under := button.get_global_rect().has_point(
			button.get_global_mouse_position())
	_scale_to(button, HOVER_SCALE if still_under else REST_SCALE)


static func _scale_to(button: Button, target: float) -> void:
	_kill_prev(button)
	var t := button.create_tween()
	button.set_meta(MOTION_META, t)
	t.tween_property(button, "scale", Vector2(target, target), PRESS_SECS)


static func _kill_prev(node: Control) -> void:
	if not node.has_meta(MOTION_META):
		return
	var prev: Tween = node.get_meta(MOTION_META)
	if prev != null and prev.is_valid():
		prev.kill()
	node.remove_meta(MOTION_META)


static func _at_rest(content: Control) -> void:
	# belt-and-pins: the tween already ENDS on these identity values;
	# re-writing them on finished makes the rest state a fact of this
	# file, not of interpolation arithmetic.
	content.offset_transform_position = Vector2.ZERO
	content.modulate = Color(1, 1, 1, 1)
	content.remove_meta(MOTION_META)
