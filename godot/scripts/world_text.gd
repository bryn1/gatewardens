# world_text — the ONE world-text mechanism (v1.2.1 G6, MC 11691).
# Label3D appeared ZERO times in godot/ before this file (V121-PLAN §0
# grep row, §G6); its first use here is DECLARED, and every world text
# from here on rides this factory — no second one. Presentation-only,
# the sprite_bank doctrine: this ungoverned file owns the presentation
# numbers (I2/C-4 — the governed UI scripts carry none), make_text owns
# nothing else: no id map, no lifetime, no cap, no sim reads or writes.
# Callers (fx_director's damage numbers first; G3's telegraph counts and
# G7's hero crests next) decide WHEN and WHERE a text appears.

const TEXT_PX := 48          # nominal glyph block height in px; with
                             # pixel_size below, one line ≈ world_h
const OUTLINE_PX := 6        # default-black outline keeps the white
                             # text readable over the arena board


# The shared world text: camera-facing, one line scaled so its glyph
# block is world_h world units tall (the make_sprite scaling idiom,
# px-space instead of sheet-space). Position is set HERE, so callers
# hand in the final paint point and never touch the node again.
static func make_text(text: String, pos: Vector3,
		world_h: float) -> Label3D:
	var l := Label3D.new()
	l.text = text
	l.font_size = TEXT_PX
	l.pixel_size = world_h / float(TEXT_PX)
	l.outline_size = OUTLINE_PX
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	l.position = pos
	return l
