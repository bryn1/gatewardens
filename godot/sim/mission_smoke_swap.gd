# mission_smoke_swap — the swap/HUD/boss/lose legs of the mission smoke
# (W16 split of mission_smoke.gd, MC 11274.1.28 / card 11384; legs
# authored W6-W10 + W14, MC 11274.1.13/.18/.25). Pure move — code and
# rows byte-identical. Hot-swap F3 + F2-10 down-swap, the W7d swap/clamp
# + ACTIVE-highlight reads (the C4 blue clamp bites exactly at the new
# hero's cap), the W14 P1-4 digit-collision leg, the W10 boss bar on the
# boss wave, and the F2-9 all-down LOSE-wins-same-tick + single C13
# mission-end commit.
# Machine rows: SWAP HUD-HL x2 F1SWAP W14SWAP HUD-BOSS DOWN HUD-BANNER
# LOSE OK. Boss-row detail (HUD-BOSS): the boss bar appears exactly while
# C5 boss_hp is non-null on the boss wave; the harness drives the wave
# index + the real start_wave entry (the boot_probe license; the funnel
# fills boss + boss_hp unchanged). DOWN: all-down F2-9 with pawns live.
# LOSE: F2-9 same-tick LOSE wins + the single C13 mission-end commit.
extends RefCounted


static func run(smoke, leg: Dictionary) -> bool:
	var m = leg["m"]
	var hud = leg["hud"]
	var state = leg["state"]
	var save = leg["save"]
	var waves_total: int = int(leg["waves_total"])
	var deck: Array = leg["deck"]
	# --- 6) hot-swap F3 (manual) + down-swap to next healthy (F2-10)
	m.bridge.on_key("F3", true)
	m.step(1.0 / 60.0)
	m.bridge.on_key("F3", false)           # G5b: release — edge-trigger
	if String(m.hero_id) != "embercaller":
		smoke._fail("F3 manual swap: hero_id=%s" % m.hero_id)
		return false
	m.hero_state["embercaller"]["hp"] = 0.0
	m.step(1.0 / 60.0)
	if String(m.hero_id) != "warden" or not bool(m.hero_state["embercaller"]["downed"]):
		smoke._fail("F2-10 down-swap: hero_id=%s" % m.hero_id)
		return false
	print("MISSION-SMOKE-SWAP hero=%s" % m.hero_id)
	hud.refresh()
	if int(hud.highlight_index()) != 0 or String(hud.banner_text()) != "":
		smoke._fail("HUD highlight after F2-10 down-swap: hl=%s banner=%s" % [
				hud.highlight_index(), hud.banner_text()])
		return false
	print("MISSION-SMOKE-HUD-HL slot=%d hero=%s" % [
			hud.highlight_index(), m.hero_id])
	# --- 6b) (W7d) hot-swap changes the ACTIVE pawn visual and the C4 blue
	#        clamp bites EXACTLY at the new hero's cap: a harness blue write
	#        above every deck cap, then F2 (warden->deadeye, lower cap) —
	#        the swap clamp is min(100 -> 90) at the C4 _select site. F1
	#        swaps back and the pawn visuals toggle with the active hero.
	var rig = m.get_node("HeroRig")
	m.blue = 130.0                            # harness: above every cap
	m.bridge.on_key("F2", true)
	m.step(1.0 / 60.0)                        # clamp: 130->100 tick, 100->90 swap
	m.step(1.0 / 60.0)                        # pawn sync follows the swap
	m.bridge.on_key("F2", false)             # G5b: release — edge-trigger
	var swap_blue := float(m.blue)
	if String(m.hero_id) != "deadeye" \
			or swap_blue != float(m.hero_defs["deadeye"]["base"]["blue_max"]) \
			or not bool(rig.pawns["deadeye"].visible) \
			or bool(rig.pawns["warden"].visible):
		smoke._fail("F2 swap/clamp: hero=%s blue=%s deadeye_vis=%s" % [
				m.hero_id, m.blue, str(rig.pawns["deadeye"].visible)])
		return false
	hud.refresh()
	if int(hud.highlight_index()) != 1 or String(hud.hero_of_slot(1)) \
			!= "deadeye":
		smoke._fail("HUD highlight after F2: hl=%s slot1=%s" % [
				hud.highlight_index(), hud.hero_of_slot(1)])
		return false
	print("MISSION-SMOKE-HUD-HL slot=%d hero=%s" % [
			hud.highlight_index(), m.hero_id])
	m.bridge.on_key("F1", true)
	m.step(1.0 / 60.0)
	m.step(1.0 / 60.0)
	m.bridge.on_key("F1", false)             # G5b: release — edge-trigger
	if String(m.hero_id) != "warden" \
			or float(m.blue) > float(m.hero_defs["warden"]["base"]["blue_max"]) \
			or not bool(rig.pawns["warden"].visible) \
			or bool(rig.pawns["deadeye"].visible):
		smoke._fail("F1 swap/clamp: hero=%s blue=%s warden_vis=%s" % [
				m.hero_id, m.blue, str(rig.pawns["warden"].visible)])
		return false
	hud.refresh()
	if int(hud.highlight_index()) != 0 or String(hud.hero_of_slot(0)) \
			!= "warden":
		smoke._fail("HUD highlight after F1: hl=%s slot0=%s" % [
				hud.highlight_index(), hud.hero_of_slot(0)])
		return false
	print("MISSION-SMOKE-HUD-HL slot=%d hero=%s" % [
			hud.highlight_index(), m.hero_id])
	print("MISSION-SMOKE-F1SWAP hero=%s swap_blue=%s deadeye_max=%s" % [
			m.hero_id, str(swap_blue),
			str(m.hero_defs["deadeye"]["base"]["blue_max"])])
	# --- 6b2) W14 P1-4 (MC 11274.1.25 / card 11341): the digit-as-swap
	#        collision is GONE. A held Digit2 press CASTS ability 2 (blue
	#        drops EXACTLY heroes.json mana_cost, the shipped hero_combat
	#        crossing) and changes the ACTIVE HERO NOT AT ALL — the same
	#        press pre-W14 teleported the hero warden->deadeye (the audit
	#        P1-4 RED). The F-keys stay the swap path: the follow-up F2
	#        press DOES swap (C4 pinned keys).
	var w14_hero := String(m.hero_id)
	var w14_blue := float(m.blue)
	m.bridge.on_key("Digit2", true)
	m.step(1.0 / 60.0)
	m.bridge.on_key("Digit2", false)
	var w14_cost := w14_blue - float(m.blue)
	if String(m.hero_id) != w14_hero or w14_cost <= 0.0:
		smoke._fail("digit-collision: hero=%s (was %s) blue-drop=%s" % [
				m.hero_id, w14_hero, str(w14_cost)])
		return false
	m.bridge.on_key("F2", true)
	m.step(1.0 / 60.0)
	m.bridge.on_key("F2", false)
	if String(m.hero_id) == w14_hero:
		smoke._fail("F2 stopped swapping after the digit-alias removal")
		return false
	print("MISSION-SMOKE-W14SWAP hero=%s digit2_cast=1 blue_drop=%s f2_hero=%s" % [
			w14_hero, str(w14_cost), m.hero_id])
	# --- 6c) (W10) boss bar on the boss wave: the harness writes the wave
	#        index and calls the REAL start_wave entry (boot_probe drive-
	#        real-entry-points license — nothing in v1 clears waves 0..9 to
	#        reach index 10 inside a smoke); the boss spawn + the boss_hp
	#        mirror are filled by the shipped funnel step-(4)/(5) paths, and
	#        the HUD bar renders C5's non-null truth (F13) with no literals.
	var pc = m.get_node("PhaseController")
	pc.wave = waves_total - 1
	m.wave = waves_total - 1
	m.start_wave(waves_total - 1)
	var guard := 0
	while guard < 600 and m.boss == null:
		m.step(1.0 / 60.0)
		guard += 1
	if m.boss == null:
		smoke._fail("boss never spawned on the boss wave")
		return false
	hud.refresh()
	if not bool(hud.boss_visible()) or String(hud.wave_text()) \
			!= "Wave %d / %d" % [waves_total, waves_total]:
		smoke._fail("HUD boss bar: visible=%s text=%s" % [
				hud.boss_visible(), hud.wave_text()])
		return false
	print("MISSION-SMOKE-HUD-BOSS visible=1 wave=%d hp=%s max=%s text=%s" % [
			m.wave, m.boss_hp, m.boss["hp_max"], hud.boss_text()])
	# --- 7) F2-9: all-down SAME TICK as a recorded win -> LOSE wins; the
	#        mission-end commit fired once through the C13 wiring.
	m.win_pending = true
	for hid: String in deck:
		m.hero_state[hid]["hp"] = 0.0
	m.step(1.0 / 60.0)
	if String(m.outcome) != "lose":
		smoke._fail("F2-9 same-tick: outcome=%s (lose must overwrite win)" % m.outcome)
		return false
	if not bool(m.committed) or int(save.write_seq) < 1 \
			or int(state.saved_ack) != int(save.write_seq):
		smoke._fail("mission-end commit/ack: committed=%s seq=%d ack=%d" % [
				m.committed, save.write_seq, state.saved_ack])
		return false
	if int(state.heroes["warden"]["xp"]) != int(m.xp_earned):
		smoke._fail("end xp award: %s != %s" % [state.heroes["warden"]["xp"], m.xp_earned])
		return false
	# (W7c) the pawns are LIVE through this path: the rig holds one pawn
	# per deck hero and the all-down hero stand shows NONE of them (the
	# hp>0 sync rule — same-tick hp writes land before the sync).
	var shown := 0
	for pid: String in rig.pawns:
		if bool(rig.pawns[pid].visible):
			shown += 1
	if int(rig.pawns.size()) != deck.size() or shown != 0:
		smoke._fail("pawns in all-down path: total=%d shown=%d" % [
				rig.pawns.size(), shown])
		return false
	print("MISSION-SMOKE-DOWN pawns=%d visible=%d" % [rig.pawns.size(), shown])
	hud.refresh()
	if String(hud.banner_text()) != "DEFEAT" or not bool(hud.banner_shown()):
		smoke._fail("HUD banner: text=%s shown=%s outcome=%s" % [
				hud.banner_text(), hud.banner_shown(), m.outcome])
		return false
	print("MISSION-SMOKE-HUD-BANNER outcome=%s text=%s" % [
			m.outcome, hud.banner_text()])
	print("MISSION-SMOKE-LOSE outcome=%s ack=%d seq=%d" % [
			m.outcome, state.saved_ack, save.write_seq])
	print("MISSION-SMOKE-OK")
	smoke.quit(0)   # E3: quit is the driver's (SceneTree) — fires exactly once
	return true
