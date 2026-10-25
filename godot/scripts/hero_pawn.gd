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

const MATS := {
	"warden": preload("res://assets/mat_hero_warden.tres"),
	"deadeye": preload("res://assets/mat_hero_deadeye.tres"),
	"embercaller": preload("res://assets/mat_hero_embercaller.tres"),
}

var hero_id := ""


# One-call parameterization (setup-by-injection doctrine, R3): id picks
# the tint; unknown ids fall back to the first deck hero's material —
# a greybox default, never a crash.
func setup_pawn(id: String) -> void:
	hero_id = id
	$Visual.material_override = MATS.get(id, MATS["warden"]).duplicate()
