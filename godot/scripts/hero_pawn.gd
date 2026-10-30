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
const CREST_Y := 2.4          # crest anchor height above the pawn origin
const CREST_SHEET_H := 1.2    # mini hero sheet world height
const CREST_NAME_DY := 0.85   # name line above the crest anchor
const CREST_NAME_H := 0.55    # name line world height

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
	var sprite := SPRITE_BANK.make_sprite(id, SPRITE_BANK.WORLD_H_HERO)
	if sprite != null:
		sprite.name = "Sprite"
		$Visual.visible = false
		add_child(sprite)
	else:
		$Visual.material_override = MATS.get(id, MATS["warden"]).duplicate()
	add_child(_make_crest(id))


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
			Vector3(0.0, CREST_NAME_DY, 0.0), CREST_NAME_H)
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
