# sprite_bank — the ONE v1.1 sprite map (V1.1-a MC 11466, (id, tier)
# aware since V1.1-b MC 11520): unit id + tower tier -> the committed
# 3090 sheet under assets/v11/, plus the ONE billboard factory every
# sprite-backed unit shares. Replace-not-add: each draw site
# (hero_pawn, defense_obj, enemy_runner) asks HERE first and keeps its
# greybox when this returns null — no second render path.
# Tier skin rule (V1.1-b): TEXTURES carries the BASE sheet of every
# sprited id — the T1 skin of the 3 shooters, the tier-agnostic sheets
# (gate_blockade, barbed_snare since batch 2, heroes, enemies);
# TIER_TEXTURES adds the committed _T2/_T3 shooter skins only. An
# unknown tier falls back to the base sheet (bombard T3 has no
# committed skin -> reads T1), so a tiered id is never null once a T1
# exists. Ids with no committed sheet at all (warden_breaker...) return
# null by design: no fake art (brief rule). Sheet names differ from
# data ids (hailspire_tower -> tower_hailspire_T1.png), so the map is
# explicit, never a stem rule.
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
	# V1.1-b batch 2: these two exit the greybox; tier-agnostic sheets
	# (the upgrade ladder changes hp/dps, never the art).
	"gate_blockade": preload("res://assets/v11/tower_gate_blockade.png"),
	"barbed_snare": preload("res://assets/v11/tower_barbed_snare.png"),
}

# The committed batch-2 upgrade skins of the 3 shooters, keyed
# (id, DISPLAY tier). T1 rides TEXTURES; no other entry lives here —
# enemy_skitterling_run.png is a run pose for the later animation card
# and is deliberately NOT wired.
const TIER_TEXTURES := {
	"ballista": {2: preload("res://assets/v11/tower_ballista_T2.png"),
		3: preload("res://assets/v11/tower_ballista_T3.png")},
	"bombard": {2: preload("res://assets/v11/tower_bombard_T2.png")},
	"hailspire_tower": {2: preload("res://assets/v11/tower_hailspire_T2.png"),
		3: preload("res://assets/v11/tower_hailspire_T3.png")},
}

# World height each sheet is scaled to — the greybox footprint it
# replaces (VISUAL-TARGET "scaled to the existing box footprint"): the
# pawn and ground-enemy capsules are 2 world units tall, the tower
# capsule is authored scale.y 2 -> 4 units. Sprite3D maps 100 px to one
# world unit at scale 1, so the scale is height / (px / 100); no layout
# or coordinate ever changes (the node still sits on the record's pos).
const WORLD_H_UNIT := 2.0     # heroes + enemies: the 2u capsule
const WORLD_H_TOWER := 4.0    # tower capsule footprint: scale.y 2 -> 4u


# tier is the DISPLAY tier (T1 = 1); the 1-arg call shape keeps working
# for every un-tiered caller (heroes, enemies, the V1.1-a probe rows).
# An unknown tier falls back to the base (T1/tier-agnostic) sheet —
# never null while a base sheet exists; null only for un-sprited ids.
static func texture_for(id: String, tier: int = 1) -> Texture2D:
	var by_tier: Dictionary = TIER_TEXTURES.get(id, {})
	var tex: Texture2D = by_tier.get(tier, null)
	if tex == null:
		tex = TEXTURES.get(id, null)
	return tex


# The shared sprite visual: null = no committed sheet, the caller keeps
# its greybox. Camera-facing billboard is the DD2 anchor-frame read.
static func make_sprite(id: String, world_h: float, tier: int = 1) -> Sprite3D:
	var tex := texture_for(id, tier)
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
