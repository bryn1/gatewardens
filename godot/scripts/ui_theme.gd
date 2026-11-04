# ui_theme — the ONE themed-HUD palette builder (v1.6 V-E, MC 12084).
# P5b: the grey/white default-text HUD the V16 BEFORE frame reads (plan §0)
# becomes the warm golden-hour set. Pixel-judge law (L2 / plan row 8): this
# file is UNGOVERNED (not in check_hygiene GOVERNED_LITERALS) so ALL palette
# numbers live HERE; hud.gd / defense_panel.gd each carry exactly TWO lines
# (preload + apply). Button RECTS must never move: every StyleBoxFlat is a
# DUPLICATE of the engine's own default stylebox with ONLY the colors
# rewritten — content/expand margins, corners and border widths stay byte
# the engine's, so get_combined_minimum_size() is identical by construction
# (test_ui_theme.py pins it engine-side: theme ON == theme OFF rects).
# The 3D warm mood is mission.tscn property VALUES (same card), not here.
# Colors are string-hexes (the defense_rows_ui:50 Color("808080") idiom —
# readable, and BN1-neutral wherever a consumer file is governed).
extends RefCounted

# Warm golden-hour HUD set (the 3D-side twins live in mission.tscn):
const BTN_NORMAL := Color("5c4326")    # amber-brown button body
const BTN_HOVER := Color("7a5c33")     # lit by the hour
const BTN_PRESSED := Color("3d2b16")   # pressed into the wood
const BTN_DISABLED := Color("463c2f66")  # desaturated, the default alpha
const BTN_FONT := Color("f5e8cf")      # cream label on brown (>= 4.5:1)
const BTN_FONT_HOVER := Color("fff6e2")
const BTN_FONT_PRESSED := Color("ffffff")
const BTN_FONT_DISABLED := Color("a89a83")
const LABEL_TONE := Color("f2e8d5")    # the header/label tone: parchment
const BAR_BG := Color("241a10cc")      # the bar troughs (panel bg family)
const FOCUS_TONE := Color("ffd89ac0")  # warm focus outline (a11y kept)


# The apply half of the two-line call (hud.gd $Root, defense_panel.gd self).
static func apply(host: Control) -> void:
	host.theme = build()


# The themed HUD palette as ONE Theme resource. Keys set are exactly the
# consumers that EXIST in the mounted mission UI (Button, Label, ProgressBar
# — checked this card: no PanelContainer/Panel node is mounted, so no dead
# stylebox key is shipped); an unset key keeps the engine default (e.g. the
# ProgressBar "fg" semantics: white hp fill / blue mana stay TRUE colors).
static func build() -> Theme:
	var t := Theme.new()
	for key: String in ["normal", "hover", "pressed", "disabled"]:
		t.set_stylebox(key, "Button", _recolor(key, "Button", {
			"normal": BTN_NORMAL, "hover": BTN_HOVER,
			"pressed": BTN_PRESSED, "disabled": BTN_DISABLED}[key]))
	t.set_stylebox("focus", "Button", _recolor("focus", "Button", FOCUS_TONE))
	t.set_color("font_color", "Button", BTN_FONT)
	t.set_color("font_hover_color", "Button", BTN_FONT_HOVER)
	t.set_color("font_pressed_color", "Button", BTN_FONT_PRESSED)
	t.set_color("font_disabled_color", "Button", BTN_FONT_DISABLED)
	t.set_color("default_font_color", "Label", LABEL_TONE)
	t.set_stylebox("background", "ProgressBar", _recolor(
			"background", "ProgressBar", BAR_BG))
	return t


# Duplicate the engine default stylebox and rewrite ONLY its colors — the
# geometry (content/expand margins, corner radii, border widths) is the
# engine's own, byte for byte: the button-rect law cannot break by edit.
static func _recolor(key: String, class_: String, col: Color) -> StyleBoxFlat:
	var src: StyleBoxFlat = ThemeDB.get_default_theme().get_stylebox(
			key, class_) as StyleBoxFlat
	assert(src != null)                      # an engine key we misname
	var sb := src.duplicate() as StyleBoxFlat
	sb.bg_color = col
	sb.border_color = col
	return sb
