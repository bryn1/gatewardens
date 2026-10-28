# v4_icon_probe — the V4 HUD/shop icon-wiring headless proof (MC card
# 11549 / milestone 11462; idiom: v6_tween_probe.gd for the frame pump +
# mission_clicks.gd for the boot — mission.tscn instantiated, _ready and
# setup driven directly (E5: the router-added mission never dispatches
# _ready under -s), root.size = served canvas, pump = MainLoop._process).
# Pins are CONCRETE committed RESOURCE PATHS + byte texts declared HERE,
# never read back through sprite_bank/sync (fleet lesson, v11_sprite_probe
# TIER leg: the mechanism as oracle makes a broken map self-consistent).
# Rows (print order): V4-ICONS-BOOT TEX SHOP TEXT HUD COEXIST OK; any
# failure prints V4-ICON-FAIL <why> and quits 1 (quit fires exactly once, E3).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")
const UITWEEN := preload("res://scripts/ui_tween.gd")

const MISSION_SCENE := "res://scenes/mission.tscn"
const HERO_IDS := ["warden", "deadeye", "embercaller"]  # deck seed (v11)

# The 8 committed icon sheets, id -> the file it MUST resolve to.
const ICON_PATHS := {
	"icon_ballista": "res://assets/v11/icon_ballista.png",
	"icon_bombard": "res://assets/v11/icon_bombard.png",
	"icon_hailspire": "res://assets/v11/icon_hailspire.png",
	"icon_blockade": "res://assets/v11/icon_blockade.png",
	"icon_snare": "res://assets/v11/icon_snare.png",
	"icon_green": "res://assets/v11/icon_green.png",
	"icon_wave": "res://assets/v11/icon_wave.png",
	"icon_core": "res://assets/v11/icon_core.png",
}
# The shipped build bar = one Button per distinct towers.json class
# (defense_placer.classes(), first row wins): pinned class button ->
# [icon path, byte-exact label text incl. the " *" selected mark]. The
# text leg is the brief's byte-stability row: green-cost text EXACT.
const CLASS_ROWS := {
	"tower": ["res://assets/v11/icon_ballista.png", "Ballista (100) *"],
	"blockade": ["res://assets/v11/icon_blockade.png", "Gate Blockade (50)"],
	"trap": ["res://assets/v11/icon_snare.png", "Barbed Snare (80)"],
}
# HUD icons: label var -> [icon var, pinned sheet]. Beside = the icon's
# x EQUALS the laid-out label's width + the declared gap (right side;
# TopLeft starts at x=16 so a left spot would clip off-canvas —
# declared reading in hud.gd).
const HUD_ICONS := {
	"wave_label": ["icon_wave", "res://assets/v11/icon_wave.png"],
	"green_label": ["icon_green", "res://assets/v11/icon_green.png"],
	"core_label": ["icon_core", "res://assets/v11/icon_core.png"],
}

var m = null
var panel = null
var hud = null
var frames := 0
var hover_btn: Button = null
var hover_t: Tween = null
var hover_out := false
var scan_max_scale := 1.0
var fail_msg := ""


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	graph["state"].set_deck(HERO_IDS.duplicate())   # starter deck (C13)
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	m = packed.instantiate()
	root.add_child(m)
	m._ready()                                  # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274                            # pinned seed, smoke idiom
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	if String(m.phase_kind) != "build":
		_fail("mission setup did not land the build phase")
		return
	panel = m.get_node("DefensePanel")
	hud = m.get_node("HUD")
	if panel.class_buttons.is_empty():
		_fail("no class buttons on the mounted panel")
		return
	print("V4-ICONS-BOOT buttons=%d phase=build" % panel.class_buttons.size())


func _process(_delta: float) -> bool:
	if fail_msg != "":
		return true                       # quit(1) already fired
	frames += 1
	if frames == 2:
		root.size = Vector2i(1280, 720)   # the served canvas mirror
		return false
	if frames == 6:
		_check_wiring()
		if fail_msg == "":
			hover_btn = panel.class_buttons["tower"] as Button
			hover_btn.mouse_entered.emit()   # the mouse's own signal
			hover_t = _meta_tween(hover_btn)
		return false
	if frames > 6 and hover_btn != null:
		if hover_t != null and not hover_t.is_valid() \
				and not hover_t.is_running():
			if not hover_out:            # the hover leg settled at 1.03:
				hover_out = true         # the mouse's exit completes the
				hover_btn.mouse_exited.emit()   # 1.0->1.03->1.0 cycle
				hover_t = _meta_tween(hover_btn)
				scan_max_scale = 1.0
				return false
			_check_tween_settled()
			if fail_msg == "":
				print("V4-ICONS-COEXIST moved=1 rest=1 icon=ok scale=%s" \
						% str(hover_btn.scale))
				print("V4-ICONS-OK")
				quit(0)
			return false
		if hover_t != null and hover_t.is_valid() and hover_t.is_running():
			scan_max_scale = maxf(scan_max_scale, float(hover_btn.scale.x))
		if frames > 2406:
			_fail("hover cycle never settled (cap 2400)")
	return false


# ---- wiring legs (frame 6: canvas sized + pumped, layout done) --------

func _check_wiring() -> void:
	# 1) all 8 icon ids resolve on THE bank to the committed sheets.
	for id: String in ICON_PATHS.keys():
		var tex := SPRITE_BANK.texture_for(id)
		if tex == null \
				or String(tex.resource_path) != String(ICON_PATHS[id]) \
				or tex.get_width() != 512:
			_fail("icon id not on its committed sheet: %s" % id)
			return
	print("V4-ICONS-TEX n=%d px=512" % ICON_PATHS.size())

	# 2) every class button carries its icon: non-null, pinned PATH,
	#    left-aligned, 28px theme clamp (concrete values pinned HERE).
	for cls: String in CLASS_ROWS.keys():
		var b := panel.class_buttons.get(cls, null) as Button
		var want: Array = CLASS_ROWS[cls]
		if b == null or b.icon == null:
			_fail("class button missing or icon-less: %s" % cls)
			return
		if String(b.icon.resource_path) != String(want[0]) \
				or b.icon_alignment != HORIZONTAL_ALIGNMENT_LEFT \
				or int(b.get_theme_constant("icon_max_width")) != 28:
			_fail("class button icon drift: %s" % cls)
			return
	print("V4-ICONS-SHOP n=%d paths=left=28" % CLASS_ROWS.size())

	# 3) byte-stability: the green-cost label text is the pinned bytes
	#    even WITH the icon mounted (decoration over, never inside, text).
	for cls: String in CLASS_ROWS.keys():
		var b := panel.class_buttons[cls] as Button
		if String(b.text) != String((CLASS_ROWS[cls] as Array)[1]):
			_fail("label text changed with the icon: %s -> %s" \
					% [cls, String(b.text)])
			return
	print("V4-ICONS-TEXT n=%d byte-exact" % CLASS_ROWS.size())

	# 4) HUD: TextureRect children of the three count labels, beside the
	#    laid-out text, carrying the pinned sheets. refresh() first (the
	#    panel.refresh smoke precedent) so placement has run post-layout.
	hud.refresh()
	for lbl: String in HUD_ICONS.keys():
		var label: Label = hud.get(lbl)
		var icon: TextureRect = hud.get(String((HUD_ICONS[lbl] as Array)[0]))
		var want_path := String((HUD_ICONS[lbl] as Array)[1])
		if icon == null or icon.texture == null \
				or String(icon.texture.resource_path) != want_path:
			_fail("hud icon sheet: %s" % lbl)
			return
		if label.size.x <= 0.0 \
				or absf(icon.position.x - (label.size.x + 6.0)) > 0.01:
			_fail("hud icon not beside laid-out label: %s lx=%s ix=%s" \
					% [lbl, str(label.size.x), str(icon.position.x)])
			return
		if icon.size != Vector2(28.0, 28.0):
			_fail("hud icon size: %s" % str(icon.size))
			return
	print("V4-ICONS-HUD n=%d beside=1" % HUD_ICONS.size())


# ---- tween-coexistence leg (icons ride the V6 hover scale) ------------

func _check_tween_settled() -> void:
	if scan_max_scale <= 1.0:
		_fail("hover never scaled (icons claimed to coexist): max=%s" \
				% str(scan_max_scale))
		return
	if hover_btn.scale != Vector2.ONE or hover_btn.icon == null \
			or String(hover_btn.icon.resource_path) \
			!= String((CLASS_ROWS["tower"] as Array)[0]):
		_fail("after hover: scale=%s icon=%s" % [str(hover_btn.scale),
				str(hover_btn.icon)])


func _meta_tween(node: Control) -> Tween:
	if not node.has_meta(UITWEEN.MOTION_META):
		return null
	return node.get_meta(UITWEEN.MOTION_META) as Tween


func _fail(why: String) -> void:
	if fail_msg == "":
		fail_msg = why
		print("V4-ICON-FAIL " + why)
		quit(1)
