# sprite_bank — the ONE v1.1 batch-1 sprite map (V1.1-a, MC 11466):
# unit id -> the committed 3090 sheet under assets/v11/, plus the ONE
# billboard factory every sprite-backed unit shares. Replace-not-add:
# each draw site (hero_pawn, defense_obj, enemy_runner) asks HERE first
# and keeps its greybox when this returns null — no second render path.
# Ids with no committed sheet (gate_blockade, barbed_snare,
# warden_brute... every un-sprited unit) return null by design: no fake
# art (brief rule). Sheet names differ from data ids (hailspire_tower
# -> tower_hailspire_T1.png), so the map is explicit, never a stem rule.
# Facings (VISUAL-TARGET V2/V3): heroes/towers sheets face RIGHT, enemy
# sheets face LEFT as generated; the mission camera maps world +x to
# screen right (mission.tscn CameraRig basis), so face() is the ONE
# mirror mechanism — only a left-facing sheet stepping toward +x flips.

const TEXTURES := {
	"warden": preload("res://assets/v11/hero_warden.png"),
	"deadeye": preload("res://assets/v11/hero_deadeye.png"),
	"embercaller": preload("res://assets/v11/hero_embercaller.png"),
	"ballista": preload("res://assets/v11/tower_ballista_T1.png"),
	"bombard": preload("res://assets/v11/tower_bombard_T1.png"),
	"hailspire_tower": preload("res://assets/v11/tower_hailspire_T1.png"),
	"skitterling": preload("res://assets/v11/enemy_skitterling.png"),
	"husk_brute": preload("res://assets/v11/enemy_husk_brute.png"),
	"ash_bandit": preload("res://assets/v11/enemy_ash_bandit.png"),
	"bone_lobber": preload("res://assets/v11/enemy_bone_lobber.png"),
	"cinder_wisp": preload("res://assets/v11/enemy_cinder_wisp.png"),
	"gale_harpy": preload("res://assets/v11/enemy_gale_harpy.png"),
}

# World height each sheet is scaled to — the greybox footprint it
# replaces (VISUAL-TARGET "scaled to the existing box footprint"): the
# pawn and ground-enemy capsules are 2 world units tall, the tower
# capsule is authored scale.y 2 -> 4 units. Sprite3D maps 100 px to one
# world unit at scale 1, so the scale is height / (px / 100); no layout
# or coordinate ever changes (the node still sits on the record's pos).
const WORLD_H_UNIT := 2.0     # heroes + enemies: the 2u capsule
const WORLD_H_TOWER := 4.0    # tower capsule footprint: scale.y 2 -> 4u


static func texture_for(id: String) -> Texture2D:
	var tex: Texture2D = TEXTURES.get(id, null)
	return tex


# The shared sprite visual: null = no committed sheet, the caller keeps
# its greybox. Camera-facing billboard is the DD2 anchor-frame read.
static func make_sprite(id: String, world_h: float) -> Sprite3D:
	var tex := texture_for(id)
	if tex == null:
		return null
	var s := Sprite3D.new()
	s.texture = tex
	s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	s.scale = Vector3.ONE * (world_h / (float(tex.get_height()) / 100.0))
	return s


# ONE facing mechanism: enemy sheets face left, so a step toward screen
# right (+x) mirrors them; right-facing sheets (heroes, towers) never
# call this. No-op on greybox nodes, so callers stay branch-free.
static func face(node: Node, dx: float) -> void:
	if node is Sprite3D:
		(node as Sprite3D).flip_h = dx > 0.0
