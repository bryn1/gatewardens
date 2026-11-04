extends Node3D

# hero_pawn — the ONE greybox pawn scene (MC 11274.1.14 / card 11321),
# parameterized by hero id: primitive mesh from assets/ + a per-hero
# material tint. heroes.json carries no color field (the data-checked
# reading: I2 keeps numbers in data, a palette is asset data), so the
# tint ships as the fixed greybox palette mat_hero_<id>.tres (brief-
# sanctioned "from data if present, else fixed palette — declare").
# The pinned Scenes row names pawn_<archetype>.tscn ×3: that is the ART
# wave's shape — W6 shipped zero per-entity .tscn files (enemy/core
# visuals are code + .tres, the same idiom here), so one parameterized
# scene serves W7 and the archetype split rides the 3090 pipeline wave
# (reading recorded in W7-evidence.md, pinned-table precedent MC
# 11274.1.9-.13 applied to the visual-only row).
# v1.6 P4a (MC 12083, V16-PLAN V-D): the F-BUILD frame read the hero as
# an ~8-px speck at the frozen D=64 rig — the pawn was ONE billboard.
# The pawn becomes a PRIMITIVE-COMPOSED BODY per archetype (shipped
# BoxMesh/CylinderMesh law, kb 2d5274003 — zero runtime ArrayMesh), the
# per-hero MATS tints REUSED, silhouette inside the WORLD_H_HERO 3u
# door. DECLARED: the committed hero sheet does NOT survive as visible
# body decor — it hides through the SAME shipped visibility-swap idiom
# as $Visual below (its G7 eff_h=3.0 scale contract stays byte-pinned
# on the live node), and the sheet survives visibly in its 1.2u crest
# miniature, which rides the pawn origin as the figure's medallion
# backdrop (the core-box truth moved the figure in front of the rim —
# see BODY_PARTS §COMPOSITION; served-proven VD-wave.log). The crest
# block stays byte-untouched (P8 shipped); camera_zoom.gd /
# mission.tscn / hero_controller.gd ZERO lines (L4 — OD1 DEFER, fixed
# framing).

const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")
const WORLD_TEXT := preload("res://scripts/world_text.gd")
const GW_TABLES := preload("res://sim/sim_tables.gd")

const MATS := {
	"warden": preload("res://assets/mat_hero_warden.tres"),
	"deadeye": preload("res://assets/mat_hero_deadeye.tres"),
	"embercaller": preload("res://assets/mat_hero_embercaller.tres"),
}

# Crest presentation numbers (ungoverned file, the sprite_bank/world_text
# doctrine — the governed UI scripts carry none). A crest = the hero's
# own sheet miniature + its heroes.json name line, riding the shipped
# factories above the pawn's head (V121-PLAN G7b).
# v1.4 P8 (MC 11835): the P4 served measure read the 0.55 name line as
# ~4-6px glyph smudges at default D=64 — ILLEGIBLE. The name rides the
# SAME crest mechanism at x2 height; the DY lift keeps the taller block
# entirely above the mini sheet (block bottom = DY - H = 1.45 > the
# sheet's +SHEET_H/2 = 0.6 top even in the top-anchored worst case),
# and a stronger outline carries the white glyphs over the bright tan
# floor (the world_text outline_px override, one mechanism). RESHOOT
# round (P8-wave.log §RESHOOT): the served re-shoot spelled the name
# but the pawn's own shield crown painted over its middle — the name
# band lifts clear of the pawn art (DY 1.9 -> 2.55); CREST_Y, H, the
# outline and the pawn are untouched.
const CREST_Y := 2.4           # crest anchor height above the pawn origin
const CREST_SHEET_H := 1.2     # mini hero sheet world height
const CREST_NAME_DY := 2.55    # name line above the crest anchor (P8 re-shoot)
const CREST_NAME_H := 1.1      # name line world height — x2 the P4 pin
const CREST_NAME_OUTLINE := 10 # px outline over OUTLINE_PX for the floor

# Body presentation numbers (v1.6 P4a, same ungoverned-home doctrine as
# the crest consts): one composed figure per ARCHETYPE (heroes.json
# "archetype" through the array door — never a per-id branch), parts =
# BoxMesh {"box": size} / CylinderMesh {"cyl": (r_top, r_bot, h)} at
# {"at": pos}, world units. Feet sit on the pawn origin (y=0); every
# top stays inside the 3u door (the crest miniature 1.8..3.0 rides the
# pawn origin BEHIND the figure as its medallion backdrop).
# SERVED TRUTH (VD-wave.log §COMPOSITION): the main core's greybox box
# (mesh_core 3x4x3, rim y~2) stands ON the hero stand (hero_controller
# position = core_main.pos), so a pawn at the origin renders INSIDE the
# box — the shipped sheet top (1.5u) was already under the rim, which
# is WHY F-BUILD reads only crest + rim. The figure therefore stands
# BODY_OFFSET toward the camera, on the board in front of the near box
# face: hero-forward framing at the frozen D=64 rig, feet on the ground
# plane, a visual-only offset (the pawn node and every sim position are
# untouched — zero-sim-writes law).
const BODY_OFFSET := Vector3(0.0, 0.0, 2.6)  # toward the camera (+z at rig)
const BODY_PARTS := {
	"melee": [
		{"box": Vector3(0.45, 0.82, 0.45), "at": Vector3(-0.34, 0.41, 0.0)},
		{"box": Vector3(0.45, 0.82, 0.45), "at": Vector3(0.34, 0.41, 0.0)},
		{"box": Vector3(1.2, 1.12, 0.65), "at": Vector3(0.0, 1.38, 0.0)},
		{"box": Vector3(1.75, 0.38, 0.73), "at": Vector3(0.0, 2.14, 0.0)},
		{"box": Vector3(0.67, 0.62, 0.6), "at": Vector3(0.0, 2.47, 0.0)},
		{"box": Vector3(0.2, 1.25, 0.94), "at": Vector3(-1.02, 1.32, 0.0)},
	],
	"ranger": [
		{"box": Vector3(0.34, 0.9, 0.36), "at": Vector3(-0.26, 0.45, 0.0)},
		{"box": Vector3(0.34, 0.9, 0.36), "at": Vector3(0.26, 0.45, 0.0)},
		{"box": Vector3(0.83, 1.06, 0.52), "at": Vector3(0.0, 1.45, 0.0)},
		{"box": Vector3(1.04, 0.15, 1.04), "at": Vector3(0.0, 2.07, 0.0)},
		{"box": Vector3(0.57, 0.65, 0.55), "at": Vector3(0.0, 2.44, 0.0)},
		{"box": Vector3(1.93, 0.15, 0.15), "at": Vector3(0.58, 1.53, 0.0)},
	],
	"mage": [
		{"cyl": Vector3(0.33, 0.83, 1.7), "at": Vector3(0.0, 0.85, 0.0)},
		{"box": Vector3(0.75, 0.63, 0.58), "at": Vector3(0.0, 1.89, 0.0)},
		{"box": Vector3(0.65, 0.63, 0.63), "at": Vector3(0.0, 2.39, 0.0)},
		{"cyl": Vector3(0.09, 0.09, 2.88), "at": Vector3(0.83, 1.44, 0.0)},
	],
}

var hero_id := ""

# One-call parameterization (setup-by-injection doctrine, R3): id picks
# the visual. V1.1-a (MC 11466): a committed batch-1 sheet replaces the
# tinted capsule — the greybox $Visual is hidden, never freed (the W6
# destroyed-core visibility idiom), and the right-facing sheet ships
# unflipped (V2 facing). Unknown ids fall back to the greybox tint —
# a greybox default, never a crash.
# v1.2.1 G7 (MC 11695): the hero sheet rides WORLD_H_HERO (> WORLD_H_UNIT)
# so the hero reads bigger than the 2u mobs, and a name CREST — the hero's
# own sheet miniature + its heroes.json name through world_text.make_text —
# is parented ABOVE the pawn. The crest is a pawn CHILD, so the shipped
# visibility swap (hero_controller._sync_pawns) moves it with the active
# hero for free: the crest over the visible pawn is the active hero's name.
func setup_pawn(id: String) -> void:
	hero_id = id
	# v1.6 P4a: the composed body mounts FIRST (the hero), the crest
	# last as shipped. The null-guard is the declared planted-red home
	# (V16-PLAN V-D): a builder that stops composing reddens HB-BODY.
	var body := _make_body(id)
	if body != null:
		add_child(body)
	var sprite := SPRITE_BANK.make_sprite(id, SPRITE_BANK.WORLD_H_HERO)
	if sprite != null:
		sprite.name = "Sprite"
		sprite.visible = false   # P4a: the body is the hero (see header)
		$Visual.visible = false
		add_child(sprite)
	else:
		$Visual.material_override = MATS.get(id, MATS["warden"]).duplicate()
	add_child(_make_crest(id))


# The primitive-composed figure (v1.6 P4a): one Body node of BoxMesh/
# CylinderMesh parts from the BODY_PARTS table of the hero's archetype
# (heroes.json through the array door — I2-safe, a greybox "melee"
# default for an absent/unknown archetype, never a crash), tinted with
# the hero's shipped MATS entry REUSED (one duplicate per pawn shared
# by its parts). Zero sim reads/writes beyond the heroes.json door.
func _make_body(id: String) -> Node3D:
	var body := Node3D.new()
	body.name = "Body"
	body.position = BODY_OFFSET   # in front of the core box (see above)
	var mat: StandardMaterial3D = MATS.get(id, MATS["warden"]).duplicate()
	var parts: Array = BODY_PARTS.get(hero_archetype(id), BODY_PARTS["melee"])
	for spec: Dictionary in parts:
		var mi := MeshInstance3D.new()
		if spec.has("box"):
			var bm := BoxMesh.new()
			bm.size = spec["box"]
			mi.mesh = bm
		else:
			var cm := CylinderMesh.new()
			var dims: Vector3 = spec["cyl"]
			cm.top_radius = dims.x      # MEASURED 4.7.2 property names
			cm.bottom_radius = dims.y
			cm.height = dims.z
			mi.mesh = cm
		mi.position = spec["at"]
		mi.material_override = mat
		body.add_child(mi)
	return body


# The name crest (V121-PLAN G7b): a small sheet miniature + the hero's
# heroes.json name as camera-facing world text (Label3D default), both
# under a child positioned above the pawn's head. This file owns the
# presentation offsets (crest consts); the NAME is data read from
# heroes.json (I2-safe — a string read through the GWTables array door,
# never a literal). Unknown id -> empty name (greybox default, no crash).
func _make_crest(id: String) -> Node3D:
	var crest := Node3D.new()
	crest.name = "Crest"
	crest.position = Vector3(0.0, CREST_Y, 0.0)
	var sheet := SPRITE_BANK.make_sprite(id, CREST_SHEET_H)
	if sheet != null:
		sheet.name = "CrestSheet"
		crest.add_child(sheet)
	var label := WORLD_TEXT.make_text(hero_name(id),
			Vector3(0.0, CREST_NAME_DY, 0.0), CREST_NAME_H,
			CREST_NAME_OUTLINE)
	label.name = "CrestName"
	crest.add_child(label)
	return crest


# hero_name reads the hero's display name through the ONE array door
# (GWTables.rows, "heroes"), so crest text == heroes.json name (a data
# leg, never a literal — I2). Empty for an id absent from the table.
static func hero_name(id: String) -> String:
	for row: Dictionary in GW_TABLES.new().rows("heroes"):
		if String(row["id"]) == id:
			return String(row["name"])
	return ""


# hero_archetype (v1.6 P4a) reads the hero's archetype through the SAME
# array door as hero_name — the body SHAPE is data (heroes.json), the
# tint stays the MATS palette (asset data, the W6 header reading).
# Empty for an id absent from the table (greybox melee default).
static func hero_archetype(id: String) -> String:
	for row: Dictionary in GW_TABLES.new().rows("heroes"):
		if String(row["id"]) == id:
			return String(row.get("archetype", ""))
	return ""
