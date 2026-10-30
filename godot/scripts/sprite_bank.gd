# sprite_bank — the ONE v1.1 sprite map (V1.1-a MC 11466, (id, tier)
# aware since V1.1-b MC 11520): unit id + tower tier -> the committed
# 3090 sheet under assets/v11/, plus the ONE billboard factory every
# sprite-backed unit shares. Replace-not-add: each draw site
# (hero_pawn, defense_obj, enemy_runner) asks HERE first and keeps its
# greybox when this returns null — no second render path.
# Tier skin rule (V1.1-b): TEXTURES carries the BASE sheet of every
# sprited id — the T1 skin of the 3 shooters, the tier-agnostic sheets
# (gate_blockade, barbed_snare since batch 2, heroes, enemies);
# TIER_TEXTURES adds the committed _T2/_T3 shooter skins only — all
# six are wired since clean-code W2 (MC 11575 CR-1: bombard T3 landed
# with batch 3 but shipped unwired, so a T3 bombard still read T1).
# An unknown tier falls back to the base sheet (no _T4/_T5 sheets
# exist -> those tiers read T1), so a tiered id is never null once a T1
# exists. Ids with no committed sheet at all (future ids) return null
# by design: no fake art (brief rule). Sheet names differ from
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
	# V1.1 DA fix loop (MC 11462): batch 5 — the boss exits the greybox.
	"warden_breaker": preload("res://assets/v11/enemy_warden_breaker.png"),
	# V1.1-b batch 2: these two exit the greybox; tier-agnostic sheets
	# (the upgrade ladder changes hp/dps, never the art).
	"gate_blockade": preload("res://assets/v11/tower_gate_blockade.png"),
	"barbed_snare": preload("res://assets/v11/tower_barbed_snare.png"),
	# V4 (MC 11549): the HUD/shop icon set rides the SAME id->file map —
	# texture_for(id) resolves icon_* ids exactly like unit ids (no
	# second preload path; VISUAL-TARGET V4 "icon-bearing presentation").
	"icon_ballista": preload("res://assets/v11/icon_ballista.png"),
	"icon_bombard": preload("res://assets/v11/icon_bombard.png"),
	"icon_hailspire": preload("res://assets/v11/icon_hailspire.png"),
	"icon_blockade": preload("res://assets/v11/icon_blockade.png"),
	"icon_snare": preload("res://assets/v11/icon_snare.png"),
	"icon_green": preload("res://assets/v11/icon_green.png"),
	"icon_wave": preload("res://assets/v11/icon_wave.png"),
	"icon_core": preload("res://assets/v11/icon_core.png"),
	# V5 (MC 11552): the combat-FX set rides the SAME id->file map —
	# fx_director.gd is its only consumer (billboards through make-
	# style scaling); no second preload path, no parallel fx system.
	"fx_spark_hit": preload("res://assets/v11/fx_spark_hit.png"),
	"fx_poof_death": preload("res://assets/v11/fx_poof_death.png"),
	"fx_proj_bolt": preload("res://assets/v11/fx_proj_bolt.png"),
	"fx_proj_ice": preload("res://assets/v11/fx_proj_ice.png"),
	# V1 world pass (MC 11559): the framed arena board rides the SAME
	# id->file map — mission_world.paint_arena is its only consumer (the
	# ground material albedo, 1:1 over the whole plane). ground_path.png
	# is deliberately NOT wired: NO lane mesh exists (lanes are waypoint
	# DATA, C7), so painting it would author a second visual mechanism,
	# not repaint a surface — the card's stated honest-cut row.
	"ground_arena": preload("res://assets/v11/ground_arena.png"),
	# G1 spawn-gate eyes (MC 11690, V121-PLAN G1): the gate-mouth marker
	# pair rides the SAME id->file map — mission_world.paint_spawn_gates
	# is its only consumer (billboards through make_sprite, no second
	# render path). icon_gate_eye_air is the WINGED variant marking the
	# gates that carry an air lane.
	"icon_gate_eye": preload("res://assets/v11/icon_gate_eye.png"),
	"icon_gate_eye_air": preload("res://assets/v11/icon_gate_eye_air.png"),
}

# V4 presentation sizes live HERE (the ui_tween.gd precedent): the I2-
# governed UI scripts (hud.gd, defense_panel.gd) carry ZERO number
# literals, so the ~28px icon size and the beside-label gap have their
# one home in this ungoverned presentation map.
const ICON_PX := 28          # the brief's ~28px chunky icon size
const ICON_GAP := 6          # HUD icon gap beside its label

# The committed upgrade skins of the 3 shooters (T2/T3 skins landed
# with batch 2, bombard T3 with batch 3), keyed (id, DISPLAY tier).
# T1 rides TEXTURES; no other entry lives here —
# enemy_skitterling_run.png is a run pose for the later animation card
# and is deliberately NOT wired.
const TIER_TEXTURES := {
	"ballista": {2: preload("res://assets/v11/tower_ballista_T2.png"),
		3: preload("res://assets/v11/tower_ballista_T3.png")},
	"bombard": {2: preload("res://assets/v11/tower_bombard_T2.png"),
		3: preload("res://assets/v11/tower_bombard_T3.png")},
	"hailspire_tower": {2: preload("res://assets/v11/tower_hailspire_T2.png"),
		3: preload("res://assets/v11/tower_hailspire_T3.png")},
}

# World height each sheet is scaled to — the greybox footprint it
# replaces (VISUAL-TARGET "scaled to the existing box footprint"): the
# ground-enemy capsule is 2 world units tall (hero pawns read bigger,
# WORLD_H_HERO below — G7), the tower capsule is authored scale.y 2 ->
# 4 units. Sprite3D maps 100 px to one world unit at scale 1, so the
# scale is height / (px / 100); no layout or coordinate ever changes
# (the node still sits on the record's pos).
const WORLD_H_UNIT := 2.0     # enemies: the 2u capsule
const WORLD_H_TOWER := 4.0    # tower capsule footprint: scale.y 2 -> 4u
# v1.2.1 G7 (MC 11695, V121-PLAN G7a): heroes-only presentation const —
# the hero must read bigger than the 2u mobs it fights at the shipped
# D=64 rig (camera LOCKED, pin #3 spent). Capsules, pos and every sim
# read stay untouched; enemies keep WORLD_H_UNIT (negative-leg pinned).
const WORLD_H_HERO := 3.0     # heroes: taller than the 2u mobs


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
