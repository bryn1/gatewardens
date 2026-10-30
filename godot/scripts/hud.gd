extends CanvasLayer

# hud — read-only mission overlay (Modules row scripts/hud.gd,
# MC 11274.1.18 / card 11325): wave/phase label, green count, defense
# count, core hp, the hero hot-swap bar for the deck (hp bar, blue bar,
# ACTIVE highlight, DOWN state, cooldown pips from mission.hero_state),
# the boss bar on the boss wave, and the outcome banner. It RENDERS
# injected state only, no logic (pinned row): zero mutator calls, zero
# state writes (I4 — test_hud.py gates both), zero balance literals
# (I2 structural set only — wave total via SimWave.total_waves, blue
# caps via the shipped C4 fields, every number a read).
#
# Readings (declared; evidence W10):
# - The hero bar renders ONE SLOT PER DECK MEMBER in deck array order
#   (the shipped C4 swap order); the F1..F3 hints sit on the first three
#   slots because those are the shipped SWAP_KEYS — a fourth key would
#   be a new input code (task: none).
# - Blue is ONE deck pool (C4), so the blue bar renders on the ACTIVE
#   slot only; its max is the shipped mission.blue_max, which the C4
#   swap clamp already keeps at the active hero's cap — the HUD never
#   recomputes it.
# - The build countdown reads PhaseController.build_timer (read-only
#   cross-node read): the phase machine owns the one timer; the HUD
#   mirrors it, it never duplicates the countdown state.
# - Boss bar visibility is exactly the shipped C5 truth: visible while
#   mission.boss_hp != null (non-null while the boss wave is live, F13).
# - Banner copy maps the shipped outcome field only: "win" -> "VICTORY",
#   "lose" -> "DEFEAT", null -> hidden (honest copy; no other value
#   exists in the shipped state machine).
# - The loot toast (W11, MC 11274.1.19 / card 11326): the event source the
#   W10 row declared open now EXISTS — the pinned C12 funnel's slot (6)
#   mirrors tray item drops into mission.loot_events (pinned C9 shape);
#   the toast renders the NEWEST row through toast_text(), a pure read
#   (zero writes, zero mutators — I4 intact). scripts/loot_pickup.gd (the
#   Modules row's world-drop pickup rule) stays its own later row; the
#   mission-local tray + event feed is what ships here.
# - Live game: _process refreshes every frame (one refresh call, no
#   math); under -s no frame dispatches (E5), so the smoke drives
#   refresh() directly — the panel.refresh() precedent. _ready stays a
#   router-safe no-op (mission.gd E5 idiom: add_child fires _ready
#   BEFORE setup injection).
# - Mouse (W17b, MC 11274.1.29 / card 11386): setup() ends with ONE
#   _ignore_mouse(self) pass — every Control under $Root IGNORE so the
#   read-only overlay can never swallow a click aimed at the defense
#   panel beneath it (P1: the code-built hero slots default PASS /
#   ProgressBars default STOP, VERIFIED headless; the hud.tscn rows were
#   IGNORE since W10, which is why the bug hid in the CODE-built nodes).
# - First-session coach (G8, MC 11692 / V121-PLAN §G8): _coach is a LOCAL
#   display var carrying the timed copy over the SAME banner (I4 — zero
#   mission writes; the copy strings are the plan's, I2-safe). The wave-0
#   build edge fires inside $PhaseController.setup (mission.gd:153) BEFORE
#   this node exists (mission.gd:168-171), so a connect can never see it —
#   setup BOOTSTRAPS _coach from the public reads (m.phase_kind, m.wave:
#   read + local assign only) and the EXISTING phase_changed signal carries
#   only the later edges (combat :82, build from _finish_wave :97→:74).
#   banner_text() priority = outcome > coach > "" — the outcome is NEVER
#   overridden; banner_shown() read-back unchanged.

const SIM_WAVE := preload("res://sim/sim_wave.gd")
const SPRITE_BANK := preload("res://scripts/sprite_bank.gd")

# G8 (MC 11692): the scripted first-mission copy, VERBATIM from
# V121-PLAN §G8 — copy strings only, zero balance numbers (I2).
const COACH_BUILD_W0 := "BUILD: tower buttons on the right panel — click arms, click again places"
const COACH_FIGHT_W0 := "FIGHT: both mouse buttons hit, F1-F3 swap heroes"
const COACH_TELEGRAPH_W1 := "NEXT WAVE: watch the gate billboards"

var m = null                        # mission root (duck-typed READ source)
var wave_label = null
var green_label = null
var def_label = null
var core_label = null
var icon_wave = null                # V4 (MC 11549): beside-label icons
var icon_green = null               # (TextureRect CHILDREN of the
var icon_core = null                # labels — the Label rect never moves)
var hero_bar = null
var boss_box = null
var boss_label = null
var boss_bar = null
var banner = null
var slots: Array = []               # deck order, one VBoxContainer per hero
var toast_label = null              # W11 loot toast (code-built Label)
var _coach := ""            # G8: timed first-mission copy — LOCAL display
# state only (I4: never a write onto m)

var _tint_active := Color("d8ecff")     # the highlight IS this tint:
var _tint_idle := Color("ffffff")       # highlight_index() reads it back
var _tint_down := Color("6f6f6f")


func _ready() -> void:
	# No-op by contract (E5, the mission.gd precedent): nothing here may
	# read injected deps — add_child fires _ready before setup().
	return


func _process(_delta: float) -> void:
	if m != null:
		refresh()


# The mission's DECLARED attach hook calls this right after mounting.
func setup(mission) -> void:
	m = mission
	wave_label = $Root/TopLeft/WaveLabel
	green_label = $Root/TopLeft/GreenLabel
	def_label = $Root/TopLeft/DefLabel
	core_label = $Root/TopLeft/CoreLabel
	hero_bar = $Root/HeroBar
	boss_box = $Root/BossBar
	boss_label = $Root/BossBar/BossLabel
	boss_bar = $Root/BossBar/BossHp
	banner = $Root/Banner
	# G8 (MC 11692): the banner box is the 480 px center column that keeps
	# the W17b disjointness budget (right edge 880, clear of the defense
	# panel at 904 — VERIFIED); the coach copy is longer than that box, so
	# it WRAPS instead of growing over the panel (grow_horizontal=BOTH grew
	# a 552 px line to x=916 -> the clicks gate went RED; VICTORY/DEFEAT
	# are single words — wrap never touches their shipped rendering).
	banner.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	for i: int in m.deck.size():
		var slot := _build_slot(i)
		hero_bar.add_child(slot)
		slots.append(slot)
	toast_label = Label.new()              # W11 loot toast (the shipped
	toast_label.name = "ToastLabel"        # hook pattern: code-built node)
	$Root/TopLeft.add_child(toast_label)
	# V4 (MC 11549 / VISUAL-TARGET row V4): icon_green beside the green
	# count, icon_wave beside the wave counter, icon_core beside core HP
	# — TextureRect CHILDREN of the Labels (a Label is not a Container,
	# so children never join the VBox layout and the pinned Label rects
	# stay byte-identical), riding to the RIGHT of the text in refresh():
	# TopLeft starts at x=16, so a left placement would clip off-canvas.
	# Label texts themselves are never edited (declared row: text stays);
	# mouse_filter lands via the shipped _ignore_mouse pass below.
	icon_wave = _build_icon("Icon_Wave", "icon_wave")
	wave_label.add_child(icon_wave)
	icon_green = _build_icon("Icon_Green", "icon_green")
	green_label.add_child(icon_green)
	icon_core = _build_icon("Icon_Core", "icon_core")
	core_label.add_child(icon_core)
	# W17b (MC 11274.1.29 / card 11386): the overlay is PURE DISPLAY, so
	# EVERY Control under $Root takes MOUSE_FILTER_IGNORE. Engine defaults
	# are NOT display-safe (VERIFIED headless this card): the code-built
	# hero slots default to PASS and their ProgressBars to STOP, and any
	# Control on this CanvasLayer that answers a click swallows the build
	# panel beneath it (the P1). mouse_filter is an input-presentation
	# property, not mission state (I4 untouched). The pinned read-only
	# row means no HUD button exists by contract; a future interactive
	# control must opt back IN by setting its own filter after setup().
	_ignore_mouse(self)
	# G8 first-session coach (MC 11692, Rev 2/DA A2 boot-order fix): the
	# wave-0 build edge was emitted in $PhaseController.setup BEFORE this
	# node existed, so the display var is BOOTSTRAPPED here from the
	# public reads (read + local assign — I4/WRITE_RE untouched), and the
	# EXISTING signal is connected for the LATER edges only.
	_coach = _coach_for(String(m.phase_kind), int(m.wave))
	$"../PhaseController".phase_changed.connect(_on_phase_changed)
	refresh()


func refresh() -> void:
	if m == null:
		return
	wave_label.text = wave_text()
	green_label.text = green_text()
	def_label.text = "Defenses %d / cap %d" % [
			int(m.defenses), int(m.defense_cap)]
	core_label.text = core_text()
	var active := active_index()
	for i: int in slots.size():
		var slot: VBoxContainer = slots[i]
		var hs: Dictionary = m.hero_state[String(m.deck[i])]
		var downed := bool(hs["downed"])
		slot.modulate = _tint_down if downed \
				else (_tint_active if i == active else _tint_idle)
		slot.get_node("NameLabel").text = \
				String(m.hero_defs[String(m.deck[i])]["name"])
		slot.get_node("StatusLabel").text = \
				"DOWN" if downed else ("ACTIVE" if i == active else "")
		var hp_bar: ProgressBar = slot.get_node("HpBar")
		hp_bar.max_value = float(hs["hp_max"])
		hp_bar.value = float(hs["hp"])
		var blue_bar: ProgressBar = slot.get_node("BlueBar")
		blue_bar.visible = i == active      # one deck pool -> active slot
		blue_bar.max_value = float(m.blue_max)
		blue_bar.value = float(m.blue)
		slot.get_node("CdLabel").text = _pips(hs)
	var show_boss := m.boss_hp != null
	boss_box.visible = show_boss
	if show_boss:
		boss_bar.max_value = float(m.boss["hp_max"])
		boss_bar.value = float(m.boss_hp)
		boss_label.text = boss_text()
	banner.visible = m.outcome != null or _coach != ""   # G8: coach rides
	banner.text = banner_text()                          # the SAME banner
	toast_label.text = toast_text()
	_place_icon(icon_wave, wave_label)     # V4: ride beside the CURRENT
	_place_icon(icon_green, green_label)   # text width as counts grow —
	_place_icon(icon_core, core_label)     # the Label rect itself never moves


# ---- V4 icon wiring (MC 11549) ----

func _build_icon(nm: String, id: String) -> TextureRect:
	var icon := TextureRect.new()
	icon.name = nm
	icon.texture = SPRITE_BANK.texture_for(id)   # THE one id->file map
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	icon.size = Vector2(SPRITE_BANK.ICON_PX, SPRITE_BANK.ICON_PX)
	return icon


func _place_icon(icon: TextureRect, label: Label) -> void:
	# Beside the text on the right, vertically centred (the 2.0 division
	# is the I2 structural set).
	icon.position = Vector2(label.size.x + float(SPRITE_BANK.ICON_GAP),
			(label.size.y - float(SPRITE_BANK.ICON_PX)) / 2.0)


# ---- accessors the smoke + pytest legs read back (pure reads) ----

func wave_text() -> String:
	if m == null:
		return ""
	if String(m.phase_kind) == "combat":
		return "Wave %d / %d" % [int(m.wave) + 1,
				SIM_WAVE.total_waves(m.waves_file)]
	var secs := 0
	var pc = m.get_node_or_null("PhaseController")
	if pc != null:
		secs = int(ceilf(float(pc.build_timer)))
	return "Build: wave %d in %d s" % [int(m.wave) + 1, secs]


func green_text() -> String:
	if m == null:
		return ""
	return "Green %d / cap %d" % [int(m.green),
			int(m.economy.get("green", {}).get("cap", 0))]


func core_text() -> String:
	var mainc: Dictionary = m.cores.get("main", {})
	var out := "Core %d / %d" % [int(float(mainc.get("hp", 0))),
			int(float(mainc.get("max", 0)))]
	for sub: Dictionary in m.cores.get("subs", []):
		out += " | %s %d / %d" % [String(sub.get("id", "")),
				int(float(sub.get("hp", 0))), int(float(sub.get("max", 0)))]
	return out


func toast_text() -> String:
	# W11 loot toast (card 11326): pure read of the C12 slot-(6) event
	# feed — the NEWEST mission.loot_events row (pinned C9 shape); "" until
	# the funnel has emitted one. No write, no mutator, no second source.
	if m == null or m.loot_events.is_empty():
		return ""
	var row: Dictionary = m.loot_events[m.loot_events.size() - 1]
	return "Picked up %s (%s)" % [String(row["base_id"]),
			String(row["rarity"])]


func boss_text() -> String:
	if m == null or m.boss_hp == null:
		return ""
	var def_row: Dictionary = m.boss.get("def", {})
	return "%s %d / %d" % [String(def_row.get("name", m.boss["id"])),
			int(float(m.boss_hp)), int(float(m.boss["hp_max"]))]


func banner_text() -> String:
	# G8 priority: outcome > coach > "" — an outcome NEVER loses to the
	# coach line (the plan row's binding order; the shipped copy map and
	# banner_shown() read-back are unchanged).
	if m == null:
		return ""
	if m.outcome != null:
		return "VICTORY" if String(m.outcome) == "win" else "DEFEAT"
	return _coach


func active_index() -> int:
	if m == null:
		return -1
	for i: int in m.deck.size():
		if String(m.deck[i]) == String(m.hero_id):
			return i
	return -1


func highlight_index() -> int:
	for i: int in slots.size():
		if slots[i].modulate == _tint_active:
			return i
	return -1


func boss_visible() -> bool:
	return boss_box != null and bool(boss_box.visible)


func banner_shown() -> bool:
	return banner != null and bool(banner.visible)


func slot_node(i: int) -> Control:
	return slots[i]


func hero_of_slot(i: int) -> String:
	if m == null or i < 0 or i >= m.deck.size():
		return ""
	return String(m.deck[i])


# ---- internals ----

# G8 (MC 11692): the ONE coach table — the bootstrap in setup() and the
# later-edge handler share it, so the copy can never differ between the
# two routes. Waves >= 2 answer "": the coach is a first-mission script.
func _coach_for(kind: String, wave: int) -> String:
	if kind == "build" and wave == 0:
		return COACH_BUILD_W0
	if kind == "combat" and wave == 0:
		return COACH_FIGHT_W0
	if kind == "build" and wave == 1:
		return COACH_TELEGRAPH_W1
	return ""


# The EXISTING PhaseController.phase_changed is the only new wiring; the
# wave row is read at emit time (_enter_build writes mission.wave before
# emitting; _enter_combat leaves it at the wave being fought).
func _on_phase_changed(kind) -> void:
	_coach = _coach_for(String(kind), int(m.wave))


func _build_slot(i: int) -> VBoxContainer:
	var slot := VBoxContainer.new()
	slot.name = "Hero_%d" % i
	var key := Label.new()
	key.name = "KeyLabel"
	if i < 3:                       # the shipped SWAP_KEYS are F1-F3 only
		key.text = "[F%d]" % (i + 1)
	var name_label := Label.new()
	name_label.name = "NameLabel"
	var status := Label.new()
	status.name = "StatusLabel"
	var hp_bar := ProgressBar.new()
	hp_bar.name = "HpBar"
	hp_bar.show_percentage = false
	var blue_bar := ProgressBar.new()
	blue_bar.name = "BlueBar"
	blue_bar.show_percentage = false
	var cd := Label.new()
	cd.name = "CdLabel"
	slot.add_child(key)
	slot.add_child(name_label)
	slot.add_child(status)
	slot.add_child(hp_bar)
	slot.add_child(blue_bar)
	slot.add_child(cd)
	return slot


func _pips(hs: Dictionary) -> String:
	# Four cooldown pips straight off hero_state (C4/F2-8): frozen
	# inactive arrays render with their remaining seconds unchanged.
	var pips: Array = []
	for cd: Variant in hs["cooldowns"]:
		pips.append("-" if float(cd) <= 0.0 else "%.1fs" % float(cd))
	return "cd " + " ".join(pips)


# W17b (MC 11274.1.29 / card 11386): one recursive pass setting the whole
# display overlay to IGNORE (see the setup() call site for the reason).
# Enums are referenced as Control.MOUSE_FILTER_* — never a literal (I2).
func _ignore_mouse(n: Node) -> void:
	if n is Control:
		(n as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	for c: Node in n.get_children():
		_ignore_mouse(c)
