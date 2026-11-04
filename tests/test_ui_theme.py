"""v1.6 V-E lighting + materials + themed HUD (MC 12084 / V16-PLAN-c2 §3 V-E).

Two legs, one per plan row-8 requirement:

(1) ENGINE LEG (the conftest.run_probe_script idiom, tmp-probe shape of
test_hero_crest / test_camera_zoom): boots the REAL mission.tscn over the
composed tables/graph (GWMICE boot, pinned seed 11274), sizes the root
1280x720 (the served size), and on live frames checks — a) VETH-SCENE: the
V-E mission.tscn PROPERTY VALUES resolve on the running scene (background
and ambient read WARM R,G>B, the sun color reads golden R>G>B, ambient > 0,
shadow_enabled stays TRUE — the existing Sun only, no new light); b)
VETH-APPLY/VETH-PALETTE: the themed palette resolves THROUGH the shipped
mounts (HUD $Root and DefensePanel each carry a Theme applied by their two
UI_THEME lines; the Button body/font, Label tone and bar trough colors
equal the ui_theme.gd constants — the probe compares against the SAME
constants the file ships, and the Python side re-parses the file hexes so
a probe edit cannot agree green); c) VETH-RECT: THE PIXEL-JUDGE LAW
pre-checked engine-side — every panel button rect and three HUD control
rects are captured theme-ON, the two themes are then nulled in place, the
same rects are recaptured theme-OFF, and every pair must be byte-equal
(button rects must NEVER move; test_mission_clicks' geom leg stays the
served-contract owner of these routes, untouched). VETH-OK prints LAST;
in-probe VETH-FAIL guards + rc1, stderr must stay EMPTY.

(2) SOURCE-TRUTH LEG (pytest cannot exec the scene file — the text IS the
contract): mission.tscn moved by PROPERTY VALUES ONLY — the load_steps
header, the 7 ext_resource rows (pin-7's set, byte-pinned verbatim), the
env_greybox sub_resource id + its WorldEnvironment use-row, the CameraRig
row (pin #3 SPENT) and shadow_enabled are all byte-unchanged; the new Sun
transform + light_color rows are byte-pinned AS SHIPPED, the warmth parses
from the file, and the sun elevation derives from the transform (Z column)
at 12..32 degrees — LOW golden hour, moved > 10 degrees off v1.5's 45. The
two-line apply budget is measured (exactly two UI_THEME occurrences per
file, gate metric hud.gd <= 396, defense_panel.gd <= 368 — both AT the
plan's bar), and the palette keeps the P8 legibility door: WCAG ratio of
the cream button font over the amber body >= 4.5 (and hover pair), the
Label parchment tone over 0.70 relative luminance.
"""

import math
import re

import conftest
from conftest import repo_path

MISSION_TSCN = repo_path("godot", "scenes", "mission.tscn")
MAT_GROUND = repo_path("godot", "assets", "mat_ground.tres")
UI_THEME_GD = repo_path("godot", "scripts", "ui_theme.gd")
HUD_GD = repo_path("godot", "scripts", "hud.gd")
PANEL_GD = repo_path("godot", "scripts", "defense_panel.gd")

FIELD_RE = re.compile(r"(\w+)=((?:\([^)]*\)|\S)+)")
COLOR_RE = re.compile(r"\(([^)]*)\)")

# The 7 ext_resource rows as shipped since the v1.4 SelectionRing mount —
# V-E touches NONE of them (pin-7 set, byte-verbatim here too).
EXT_ROWS = (
    '[ext_resource type="Script" uid="uid://duidisb02w2tl" '
    'path="res://scripts/mission.gd" id="1_mission"]',
    '[ext_resource type="Script" uid="uid://d4iftsrpsjard" '
    'path="res://scripts/phase_controller.gd" id="2_phase"]',
    '[ext_resource type="Script" uid="uid://xpjka6ao86h0" '
    'path="res://scripts/enemy_runner.gd" id="3_runner"]',
    '[ext_resource type="Script" uid="uid://cccegrgctci7" '
    'path="res://scripts/fx_director.gd" id="3b_fx"]',
    '[ext_resource type="Mesh" path="res://assets/mesh_plane.tres" '
    'id="4_ground"]',
    '[ext_resource type="Material" path="res://assets/mat_ground.tres" '
    'id="5_matg"]',
    '[ext_resource type="Script" uid="uid://7cf4beti21gb" '
    'path="res://scripts/wave_telegraph.gd" id="3c_tele"]',
    '[ext_resource type="Script" uid="uid://b4yoi8pquwrwm" '
    'path="res://scripts/camera_zoom.gd" id="6_zoom"]',
    '[ext_resource type="Script" uid="uid://cdar478iaf3cq" '
    'path="res://scripts/selection_ring.gd" id="7_selring"]',
)

CAMERA_ROW = ('transform = Transform3D(1, 0, 0, 0, 0.669, 0.743, 0, '
              '-0.743, 0.669, 0, 47.47, 42.79)')
SUN_ROW = ('transform = Transform3D(0.573576, -0.280168, 0.769753, 0, '
           '0.939693, 0.34202, -0.819152, -0.196175, 0.538986, 20, 30, 10)')
SUN_COLOR_ROW = "light_color = Color(1, 0.72, 0.45, 1)"


PROBE_SRC = '''
extends SceneTree
# V-E tmp probe: palette resolves on the booted mission + button rects
# theme-ON == theme-OFF (pixel-judge law pre-check) + scene values warm.
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const MISSION_SCENE := "res://scenes/mission.tscn"
const UI_THEME := preload("res://scripts/ui_theme.gd")
const DECK := ["warden", "deadeye", "embercaller"]


class Monitor:
	extends Node
	var m
	var frames := 0
	var rects_on := {}
	var failed := false

	func _fail(why: String) -> void:
		failed = true
		print("VETH-FAIL " + why)
		get_tree().quit(1)

	func _process(_d: float) -> void:
		frames += 1
		if frames == 2:
			get_tree().root.size = Vector2i(1280, 720)
		if frames == 6:
			_scene_leg()
			if not failed:
				_apply_leg()
			if not failed:
				_capture(true)
		if frames == 8 and not failed:
			(m.get_node("HUD/Root") as Control).theme = null
			(m.get_node("DefensePanel") as Control).theme = null
		if frames == 10 and not failed:
			_capture(false)
			if not failed:
				print("VETH-OK")
				get_tree().quit(0)

	func _scene_leg() -> void:
		var env: Environment = m.get_node("WorldEnv").environment
		var bg := env.background_color
		var amb := env.ambient_light_color
		var sun := m.get_node("Sun") as DirectionalLight3D
		var lc := sun.light_color
		print("VETH-SCENE bg=%s amb=%s amb_e=%.2f sun=%s shadow=%s" % [
				str(bg), str(amb), env.ambient_light_energy, str(lc),
				str(sun.shadow_enabled)])
		if not (bg.r > bg.b and bg.g > bg.b):
			_fail("background not warm (R,G must beat B): %s" % str(bg))
			return
		if not (amb.r > amb.b and amb.g > amb.b):
			_fail("ambient not warm: %s" % str(amb))
			return
		if not (lc.r > lc.g and lc.g > lc.b):
			_fail("sun color not golden: %s" % str(lc))
			return
		if env.ambient_light_energy <= 0.0 or not sun.shadow_enabled:
			_fail("lit/shadow door broken: amb_e=%f shadow=%s" % [
					env.ambient_light_energy, str(sun.shadow_enabled)])
			return

	func _panel_buttons() -> Array:
		var out: Array = []
		_collect(m.get_node("DefensePanel"), out)
		return out

	func _collect(n: Node, out: Array) -> void:
		if n is Button:
			out.append(n)
		for c: Node in n.get_children():
			_collect(c, out)

	func _apply_leg() -> void:
		var hud_root := m.get_node("HUD/Root") as Control
		var panel := m.get_node("DefensePanel") as Control
		if hud_root.theme == null:
			_fail("HUD $Root carries no theme (apply line dead?)")
			return
		if panel.theme == null:
			_fail("DefensePanel carries no theme (apply line dead?)")
			return
		var btns := _panel_buttons()
		if btns.size() < 6:
			_fail("expected >= 6 panel buttons, got %d" % btns.size())
			return
		var btn: Button = btns[0]
		var sb := btn.get_theme_stylebox("normal") as StyleBoxFlat
		var df := ThemeDB.get_default_theme().get_stylebox("normal",
				"Button") as StyleBoxFlat
		if sb == null:
			_fail("Button normal stylebox did not resolve")
			return
		print("VETH-APPLY normal_bg=%s want=%s margin_equal=%s" % [str(sb.bg_color),
				str(UI_THEME.BTN_NORMAL), str(sb.content_margin_left == df.content_margin_left \\
					and sb.content_margin_right == df.content_margin_right \\
					and sb.content_margin_top == df.content_margin_top \\
					and sb.content_margin_bottom == df.content_margin_bottom \\
					and sb.corner_radius_top_left == df.corner_radius_top_left)])
		if sb.bg_color != UI_THEME.BTN_NORMAL:
			_fail("Button body color is not the palette: %s != %s" % [
					str(sb.bg_color), str(UI_THEME.BTN_NORMAL)])
			return
		if sb.content_margin_left != df.content_margin_left \\
				or sb.content_margin_top != df.content_margin_top \\
				or sb.corner_radius_top_left != df.corner_radius_top_left:
			_fail("stylebox geometry drifted from the engine default")
			return
		if btn.get_theme_color("font_color") != UI_THEME.BTN_FONT:
			_fail("Button font color is not the palette: %s" % str(
					btn.get_theme_color("font_color")))
			return
		var lbl := m.get_node("HUD/Root/TopLeft/WaveLabel") as Label
		if lbl.get_theme_color("default_font_color") != UI_THEME.LABEL_TONE:
			_fail("Label tone is not the palette: %s" % str(
					lbl.get_theme_color("default_font_color")))
			return
		var bar := m.get_node("HUD/Root/BossBar/BossHp") as ProgressBar
		var bsb := bar.get_theme_stylebox("background") as StyleBoxFlat
		if bsb == null or bsb.bg_color != UI_THEME.BAR_BG:
			_fail("bar trough color wrong")
			return
		print("VETH-PALETTE font=%s label=%s trough=%s" % [
				str(btn.get_theme_color("font_color")),
				str(lbl.get_theme_color("default_font_color")),
				str(bsb.bg_color)])

	func _capture(on: bool) -> void:
		var tag := "on" if on else "off"
		var rects := {}
		for b: Variant in _panel_buttons():
			var btn := b as Button
			rects["B:" + String(btn.get_path())] = btn.get_global_rect()
		var hud_root: Node = m.get_node("HUD/Root")
		var bar := hud_root.get_node("HeroBar").get_child(0).get_node("HpBar") as ProgressBar
		rects["H:HpBar"] = (bar as Control).get_global_rect()
		var lbl := hud_root.get_node("TopLeft/WaveLabel") as Label
		rects["H:WaveLabel"] = lbl.get_global_rect()
		var bsb := hud_root.get_node("BossBar/BossHp") as ProgressBar
		rects["H:BossHp"] = bsb.get_global_rect()
		if on:
			rects_on = rects
			for k: String in rects.keys():
				print("VETH-RECT-%s %s %s" % [tag, k, str(rects[k])])
			return
		for k: String in rects.keys():
			var r_on: Rect2 = rects_on[k]
			var r_off: Rect2 = rects[k]
			print("VETH-RECT-%s %s %s" % [tag, k, str(r_off)])
			if r_on != r_off:
				_fail("rect moved for %s: on=%s off=%s" % [k, str(r_on), str(r_off)])
				return
		print("VETH-RECT-EQUAL count=%d" % rects.size())


func _initialize() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var state = graph["state"]
	state.set_deck(DECK.duplicate())
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		print("VETH-FAIL mission.tscn not loadable")
		quit(1)
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()
	var rng := RandomNumberGenerator.new()
	rng.seed = 11274
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	var mon := Monitor.new()
	mon.m = m
	root.add_child(mon)
'''


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _rows(out, tag):
    return [dict(FIELD_RE.findall(ln.split(tag, 1)[1]))
            for ln in out.splitlines() if ln.startswith(tag + " ")]


def _const_hex(name):
    """The ui_theme.gd constant as (r,g,b) floats, parsed from the SHIPPED
    string-hex (BN1 idiom) — the file's own text is the palette contract."""
    m = re.search(r'^const %s := Color\("([0-9a-fA-F]{6,8})"\)' % name,
                  _read(UI_THEME_GD), re.M)
    assert m, "const %s missing (or not a string-hex) in ui_theme.gd" % name
    h = m.group(1)[:6]
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _color_tuple(text):
    m = COLOR_RE.search(text)
    assert m, "no Color(...) in %r" % text
    return tuple(float(x) for x in m.group(1).split(","))[:3]


def _same_color(printed, file_hex):
    """Engine str(Color) rounds to ~4 decimals — compare WITHIN print
    precision (1e-3), never byte-equal, never sloppier (a plant that
    shifts a channel by 0.01 must still redden)."""
    got, want = _color_tuple(printed), file_hex
    return all(abs(a - b) < 1e-3 for a, b in zip(got, want))


def _luminance(rgb):
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _wcag(fg, bg):
    hi, lo = max(_luminance(fg), _luminance(bg)), min(_luminance(fg),
                                                      _luminance(bg))
    return (hi + 0.05) / (lo + 0.05)


def _tscn_color(text, prop):
    m = re.search(r"^%s = Color\(([^)]*)\)" % prop, text, re.M)
    assert m, "%s row missing from mission.tscn" % prop
    return tuple(float(x) for x in m.group(1).split(",")[:3])


# ---- leg 1: engine tier ------------------------------------------------

def test_ve_theme_palette_resolves_and_rects_never_move(tmp_path,
                                                        class_cache):
    probe = tmp_path / "v16_ve_ui_theme_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), (), tmp_path / "user_home")
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s" % (proc.returncode, proc.stdout)
    out = proc.stdout
    assert "VETH-FAIL" not in out, out
    assert out.rstrip().splitlines()[-1].strip() == "VETH-OK", out

    # Scene VALUES resolve on the RUNNING scene (mission.tscn, not the log).
    scene = _rows(out, "VETH-SCENE")
    assert len(scene) == 1, out
    sc = scene[0]
    bg, amb, sun = (_color_tuple(sc[k]) for k in ("bg", "amb", "sun"))
    assert bg[0] > bg[2] and bg[1] > bg[2], "void not warm: %s" % sc["bg"]
    assert amb[0] > amb[2] and amb[1] > amb[2], "ambient not warm: %s" % sc["amb"]
    assert sun[0] > sun[1] > sun[2], "sun not golden: %s" % sc["sun"]
    assert float(sc["amb_e"]) > 0.0 and sc["shadow"] == "true", sc

    # Palette resolves through the shipped mounts AND equals the FILE hexes
    # (probe-vs-file cross-check: an edit to one without the other reddens).
    ap = _rows(out, "VETH-APPLY")
    assert len(ap) == 1 and ap[0]["margin_equal"] == "true", out
    assert _same_color(ap[0]["normal_bg"], _const_hex("BTN_NORMAL")), \
        "Button body painted is not the shipped file hex"
    pal = _rows(out, "VETH-PALETTE")
    assert len(pal) == 1, out
    assert _same_color(pal[0]["font"], _const_hex("BTN_FONT"))
    assert _same_color(pal[0]["label"], _const_hex("LABEL_TONE"))
    assert _same_color(pal[0]["trough"], _const_hex("BAR_BG"))

    # Pixel-judge law, engine-side: every captured rect is theme-ON equal.
    assert len(_rows(out, "VETH-RECT-EQUAL")) == 1, out
    on = {}
    for ln in out.splitlines():
        if ln.startswith("VETH-RECT-on "):
            key, rect = ln[len("VETH-RECT-on "):].split(" ", 1)
            on[key] = rect
    assert len(on) >= 13, "expected >=13 pinned rects, got %d" % len(on)
    assert all(k.startswith("B:") for k in list(on)[:10])
    off = {}
    for ln in out.splitlines():
        if ln.startswith("VETH-RECT-off "):
            key, rect = ln[len("VETH-RECT-off "):].split(" ", 1)
            off[key] = rect
    assert set(off) == set(on) and on == off, \
        "a rect moved with the theme: %s" % {k: (on[k], off[k])
                                             for k in on if on[k] != off[k]}


# ---- leg 2: source truth — VALUES ONLY + two-line budget + legibility ---

def test_ve_mission_tscn_values_only_and_two_line_budget():
    text = _read(MISSION_TSCN)
    # VALUES ONLY: the structural rows are byte-verbatim (pin-7 set rides).
    assert text.startswith("[gd_scene load_steps=11 format=3]"), \
        "load_steps moved — V-E adds NO resource"
    ext = [ln for ln in text.splitlines() if ln.startswith("[ext_resource")]
    assert ext == list(EXT_ROWS), "an ext_resource row moved (pin-7 law)"
    assert len(text.split("[sub_resource")) == 2, "exactly ONE sub_resource"
    assert '[sub_resource type="Environment" id="env_greybox"]' in text
    assert 'environment = SubResource("env_greybox")' in text
    assert CAMERA_ROW in text, "the CameraRig row moved (pin #3 SPENT)"
    assert "shadow_enabled = true" in text

    # The V-E values, byte-pinned AS SHIPPED (versioned truth of this card).
    assert SUN_ROW in text, "the V-E sun transform drifted"
    assert SUN_COLOR_ROW in text, "the V-E sun light_color drifted"
    bg = _tscn_color(text, "background_color")
    amb = _tscn_color(text, "ambient_light_color")
    assert bg[0] > bg[2] and bg[1] > bg[2] and amb[0] > amb[2] > 0, \
        "the golden-hour values drifted back to cool"
    ground = _tscn_color(_read(MAT_GROUND), "albedo_color")
    assert sum(abs(a - b) for a, b in zip(bg, ground)) > 0.15, \
        "background and ground read identical — the world dissolves (F-3)"

    # Golden hour: the sun rides a LOW angle (the census moves the shadows).
    m = re.search(r"Transform3D\(([^)]*)\)", text.split(SUN_ROW)[0] + SUN_ROW)
    vals = [float(x) for x in m.group(1).split(",")]
    z_col = (vals[2], vals[5], vals[8])          # .tscn rows-major layout
    elev = math.degrees(math.asin(max(-1.0, min(1.0, -z_col[1]))))  # dir=-Z
    assert 12.0 <= -elev <= 32.0, "sun elevation %s off the golden-hour band" % elev
    assert abs(-elev - 45.0) >= 10.0, "the sun angle never moved off v1.5"

    # Two-line apply budget in the GOVERNED files (L1 WATCH respected).
    for gd, ceiling in ((HUD_GD, 396), (PANEL_GD, 368)):
        body = _read(gd)
        assert body.count("UI_THEME") == 2, \
            "%s carries %d UI_THEME lines (budget is 2: preload + apply)" \
            % (gd, body.count("UI_THEME"))
        assert len(body.split("\n")) <= ceiling, \
            "%s at %d lines tips the plan's ceiling %d" % (
                gd, len(body.split("\n")), ceiling)

    # P8 legibility door, computed from the FILE hexes (not the probe).
    assert _wcag(_const_hex("BTN_FONT"), _const_hex("BTN_NORMAL")) >= 4.5
    assert _wcag(_const_hex("BTN_FONT_HOVER"),
                 _const_hex("BTN_HOVER")) >= 4.5
    assert _luminance(_const_hex("LABEL_TONE")) >= 0.70, \
        "parchment label tone lost its brightness (P8 lesson)"
