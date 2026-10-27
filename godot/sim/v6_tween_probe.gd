# v6_tween_probe — the V6 menu-motion headless proof (MC card 11530 /
# milestone 11462; idiom: v11_sprite_probe.gd — scripted SceneTree under
# -s, real scenes, shipped entry points, machine rows + quit codes; E5:
# _ready driven here; the frame pump is the scripted MainLoop._process,
# VERIFIED 4.7.2 this card). Boots the REAL hub.tscn under a RouterSpy
# (the hub_probe_stations mount), sizes the served canvas (the
# test_hub_scroll mirror), then drives tab switches THROUGH handle_press
# (the shipped greybox station route) and hover/press THROUGH the
# Button's own mouse signals (the exact signals a mouse emits — the
# same connections attach() made). Pinned concrete values, never the
# tested mechanism as oracle: the asserts are the property VALUES
# (offset Vector2(0,0), modulate Color(1,1,1,1), the printed scale +
# rects) and the per-frame OBSERVED min-alpha / max-offset / max-scale
# (a never-moving tween cannot pass); the tween's own is_running()
# serves only as the required "a tween runs on the content node" row
# and the scan stop-condition. Rows (print order):
#   V6-PROBE-BOOT | V6-TWEEN-START | V6-ATREST-START | V6-TWEEN-MID |
#   V6-REST-RECT | V6-REST | V6-HOVER | V6-PRESS | V6-OK
# Any failure prints V6-FAIL <why> and quits 1; quit fires exactly once
# (the E3 rule).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const UITWEEN := preload("res://scripts/ui_tween.gd")

const HUB_SCENE := "res://scenes/hub.tscn"
const PHASES := ["WARSETTLE", "MID", "GEAR", "BACK", "BACKSETTLE",
		"REOPEN", "HOVERIN", "HOVEROUT", "PRESSDOWN", "PRESSUP", "DONE"]
const PHASE_CAP := 1200           # frames before a phase declares FAIL

class RouterSpy:
	extends Node

	var calls: Array = []

	func start_mission(map_id: String, difficulty: String) -> void:
		calls.append({"map": map_id, "difficulty": difficulty})

var hub = null
var bar_btn: Button = null
var black_content: Control = null
var gear_content: Control = null
var phase := 0
var phase_frames := 0
var frames := 0
var running_t: Tween = null
var scan_min_alpha := 1.0
var scan_max_offx := 0.0
var scan_max_scale := 1.0
var btn_rect_pre := Rect2()
var black_rect_1 := Rect2()
var fail_msg := ""


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                                  # pinned (hub_probe)
	var spy := RouterSpy.new()
	spy.name = "RouterSpy"
	root.add_child(spy)
	var packed = ResourceLoader.load(HUB_SCENE)
	if packed == null:
		_fail("hub.tscn not loadable")
		return
	hub = packed.instantiate()
	spy.add_child(hub)
	hub._ready()                                      # E5
	hub.setup(tables, graph["state"], graph["save"], graph["bridge"], rng)
	if hub._panels.size() != 6:
		_fail("panels=%d" % hub._panels.size())
		return
	print("V6-PROBE-BOOT panels=%d open=war" % hub._panels.size())


func _process(delta: float) -> bool:
	if fail_msg != "":
		return true                       # quit(1) already fired
	frames += 1
	if frames == 2:
		root.size = Vector2i(1280, 720)   # the served canvas mirror
		hub.size = Vector2(1280.0, 720.0)
	elif frames == 6:
		_tab_switch()                     # WARSETTLE -> MID
	elif phase < PHASES.size() - 1:
		phase_frames += 1
		if phase_frames > PHASE_CAP:
			_fail("%s never settled (cap %d, dt=%s)" % [
					PHASES[phase], PHASE_CAP, str(delta)])
		else:
			_step_phase()
	return false


# ---- the tab-switch legs ----------------------------------------------

func _tab_switch() -> void:
	bar_btn = hub.get_node("Layout/Stations/Bar/Open_blacksmith") as Button
	btn_rect_pre = bar_btn.get_global_rect()
	hub.handle_press("Digit3")        # the shipped station route
	var vis_ok: bool = bool(hub.blacksmith.visible) \
			and not bool(hub.war.visible)
	black_content = hub.blacksmith.get_child(0)
	running_t = _meta_tween(black_content)
	if not vis_ok or running_t == null or not running_t.is_valid() \
			or not running_t.is_running():
		_fail("tab-switch tween: vis=%s meta_running=%s" % [str(vis_ok),
				str(running_t != null and running_t.is_running())])
		return
	# ENGINE FACT (4.7.2, this run): Node.is_tween_running and
	# SceneTree.is_tween_valid do NOT exist here — is_running() on the
	# tween fetched FROM THE CONTENT NODE'S META is the start flag, and
	# the observed mid-frame motion (V6-TWEEN-MID) is what proves it
	# actually pumps through the tree.
	print("V6-TWEEN-START running=1 visible war=0 black=1")
	# rest values on the SWITCH frame, before any pump: the helper's
	# .from() must write NOTHING synchronously — a leg that never pumps
	# frames still measures pixel-rest geometry.
	if black_content.offset_transform_position != Vector2.ZERO \
			or black_content.modulate != Color(1, 1, 1, 1):
		_fail("start-frame wrote rest values: off=%s mod=%s" % [
				str(black_content.offset_transform_position),
				str(black_content.modulate)])
		return
	print("V6-ATREST-START off=0,0 mod=1,1,1,1")
	_next_phase()


func _step_phase() -> void:
	match String(PHASES[phase]):
		"MID":
			_scan_content(black_content)
			if _t_done():
				print("V6-TWEEN-MID frames=%d min_alpha=%s max_offx=%s" % [
						phase_frames, str(scan_min_alpha),
						str(scan_max_offx)])
				_check_rest(black_content, "MID")
				if fail_msg == "":
					black_rect_1 = black_content.get_global_rect()
					var btn_post := bar_btn.get_global_rect()
					print("V6-REST-RECT black=%s same_as_pre=%s" % [
							str(black_rect_1),
							str(btn_post == btn_rect_pre)])
					if btn_post != btn_rect_pre:
						_fail("bar button rect moved by a tab switch")
						return
					gear_content = hub.gear.get_child(0)
					hub.handle_press("Digit2")
					running_t = _meta_tween(gear_content)
					_next_phase()
		"GEAR":
			_scan_content(gear_content)
			if _t_done():
				_check_rest(gear_content, "GEAR")
				if fail_msg == "":
					hub.handle_press("Digit3")
					running_t = _meta_tween(black_content)
					_next_phase()
		"BACK":
			_scan_content(black_content)
			if _t_done():
				_check_rest(black_content, "BACK")
				if fail_msg == "":
					_next_phase()
		"BACKSETTLE":
			var rt := black_content.get_global_rect()
			if rt != black_rect_1:
				_fail("blacksmith rect after round trip: %s != %s" % [
						str(rt), str(black_rect_1)])
				return
			if not bool(hub.blacksmith.visible) or bool(hub.gear.visible) \
					or bool(hub.war.visible):
				_fail("visibility after round trip: black=%s gear=%s" % [
						str(hub.blacksmith.visible),
						str(hub.gear.visible)])
				return
			print("V6-REST roundtrip_rect=same visibility=1")
			hub.handle_press("Escape")            # shipped close route
			hub.handle_press("Digit3")            # reopen from closed
			running_t = _meta_tween(black_content)
			_next_phase()
		"REOPEN":
			_scan_content(black_content)
			if _t_done():
				_check_rest(black_content, "REOPEN")
				if fail_msg == "":
					bar_btn.mouse_entered.emit()  # the mouse's own signal
					running_t = _meta_tween(bar_btn)
					_next_phase()
		"HOVERIN":
			_scan_scale(bar_btn)
			if _t_done():
				_check_scale(bar_btn, UITWEEN.HOVER_SCALE, "HOVERIN")
				if fail_msg == "":
					bar_btn.mouse_exited.emit()
					running_t = _meta_tween(bar_btn)
					_next_phase()
		"HOVEROUT":
			_scan_scale(bar_btn)
			if _t_done():
				_check_scale(bar_btn, UITWEEN.REST_SCALE, "HOVEROUT")
				if fail_msg == "":
					print("V6-HOVER in=%s out=%s moved=1 rect=%s" % [
							str(Vector2(UITWEEN.HOVER_SCALE,
									UITWEEN.HOVER_SCALE)),
							str(Vector2.ONE),
							str(bar_btn.get_global_rect())])
					bar_btn.button_down.emit()
					running_t = _meta_tween(bar_btn)
					_next_phase()
		"PRESSDOWN":
			_scan_scale(bar_btn)
			if _t_done():
				_check_scale(bar_btn, UITWEEN.HOVER_SCALE, "PRESSDOWN")
				if fail_msg == "":
					bar_btn.button_up.emit()
					running_t = _meta_tween(bar_btn)
					_next_phase()
		"PRESSUP":
			_scan_scale(bar_btn)
			if _t_done():
				var still_under := bar_btn.get_global_rect().has_point(
						bar_btn.get_global_mouse_position())
				var want := UITWEEN.HOVER_SCALE if still_under \
						else UITWEEN.REST_SCALE
				_check_scale(bar_btn, want, "PRESSUP")
				if fail_msg == "":
					print("V6-PRESS down=%s up=%s under=%s rect=%s" % [
							str(Vector2(UITWEEN.HOVER_SCALE,
									UITWEEN.HOVER_SCALE)),
							str(Vector2(want, want)), str(still_under),
							str(bar_btn.get_global_rect())])
					print("V6-OK")
					quit(0)
					phase = PHASES.size() - 1     # DONE: idle
		_:
			pass


# ---- scans + asserts ---------------------------------------------------

func _scan_content(content: Control) -> void:
	if _t_scanning():
		scan_min_alpha = minf(scan_min_alpha, float(content.modulate.a))
		# ABS: a dir=-1 (left) slide travels NEGATIVE x toward 0 —
		# a plain max would never see it (this exact bug turned the
		# GEAR leg red on its first run).
		scan_max_offx = maxf(scan_max_offx,
				absf(float(content.offset_transform_position.x)))


func _scan_scale(btn: Button) -> void:
	if _t_scanning():
		scan_max_scale = maxf(scan_max_scale, float(btn.scale.x))


func _t_scanning() -> bool:
	return running_t != null and running_t.is_valid() \
			and running_t.is_running()


func _t_done() -> bool:
	return not _t_scanning()


# Settle check: EXACT identity values + the observed motion (a tween
# that never started would leave _t_done true immediately — the
# observed min/max is what proves it actually animated).
func _check_rest(content: Control, why: String) -> void:
	if content.offset_transform_position != Vector2.ZERO \
			or content.modulate != Color(1, 1, 1, 1):
		_fail("%s did not settle to rest: off=%s mod=%s" % [why,
				str(content.offset_transform_position),
				str(content.modulate)])
		return
	if scan_min_alpha >= 1.0 or scan_max_offx <= 0.0:
		_fail("%s never moved: min_alpha=%s max_offx=%s" % [why,
				str(scan_min_alpha), str(scan_max_offx)])


func _check_scale(btn: Button, want: float, why: String) -> void:
	if btn.scale != Vector2(want, want):
		_fail("%s scale=%s want=%s" % [why, str(btn.scale),
				str(Vector2(want, want))])
		return
	if want > UITWEEN.REST_SCALE and scan_max_scale <= 1.0:
		_fail("%s never moved: max_scale=%s" % [why, str(scan_max_scale)])


# ---- phase plumbing -----------------------------------------------------

func _meta_tween(node: Control) -> Tween:
	if not node.has_meta(UITWEEN.MOTION_META):
		return null
	return node.get_meta(UITWEEN.MOTION_META) as Tween


func _next_phase() -> void:
	phase += 1
	phase_frames = 0
	scan_min_alpha = 1.0
	scan_max_offx = 0.0
	scan_max_scale = 1.0


func _fail(why: String) -> void:
	if fail_msg == "":
		fail_msg = why
		print("V6-FAIL " + why)
		quit(1)
