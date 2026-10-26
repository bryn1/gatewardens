"""W9 hub gate (MC 11274.1.16 / card 11323) — hub, gear panel, item_row,
war table, blacksmith, tinkerer, dummy range + the hub_probe harness.

Two tiers, one idiom per repo (test_mission_smoke precedent):
- ENGINE: run godot/sim/hub_probe.gd through conftest.run_probe_script
  (headless `-s`, XDG_DATA_HOME isolated — BN4) and re-derive EVERY
  machine-row number from the shipped data files (blacksmith.json /
  rarity.json / xp.json / items.json), never from a test-side copy of a
  cost. EMPTY stderr is asserted (W4 ruling: stderr noise = parse noise).
  Byte-stable reruns are asserted (pinned seed 11274).
- SOURCE TRUTH: the I4/I2 gates pytest can settle without the engine —
  the cost-literal ban over the new hub layer, single application sites
  (one equip crossing, one payment site per service panel, one xp site),
  and the item_row widget reuse (exactly ONE row renderer, shared).

Readings recorded (R-list, card trail):
- The brief paraphrases "rarity.json colors" and SimInventory
  salvage_yield/unequip — neither exists in the shipped data/statics;
  rarity.json carries NO colors key (item_row shows the rarity NAME
  tinted via a data-side optional `colors` map when one ever lands) and
  salvage/unequip are NOT implemented (no second write mechanism beside
  the shipped C13 mutators). The shipped equip refusal (slot mismatch ->
  ok:false, bank untouched) is the relic behavior, asserted in the probe.
- hub_probe.gd carries `# hygiene:` like mission_smoke: machine-row
  headers hold digit-bearing doc text, so the file is exempt from the
  cost-literal gate (test assets encode the expected numbers; the gate
  scopes the SHIPPED hub layer: hub.gd + the 7 station scripts).
- game_state.gd next_uid() now also anchors rows worn mid-session (the
  mission-end chest leg bank_adds while gear is equipped; a bank-only
  max could stamp a uid a worn row still carries and the pinned
  picked(uid) crossing would key the wrong row). Declared; save schema
  untouched.
"""

import json
import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code greps)

GODOT = Path(conftest.repo_path("godot"))
PROBE = "res://sim/hub_probe.gd"
SCRIPTS = GODOT / "scripts"

HUB_GD = SCRIPTS / "hub.gd"
GEAR_GD = SCRIPTS / "gear_panel_ui.gd"
ROW_GD = SCRIPTS / "item_row.gd"
WAR_GD = SCRIPTS / "war_table.gd"
SMITH_GD = SCRIPTS / "blacksmith_ui.gd"
TINK_GD = SCRIPTS / "tinkerer_ui.gd"
DUMMY_GD = SCRIPTS / "dummy_range.gd"
ASC_GD = SCRIPTS / "ascension_ui.gd"
GS_GD = SCRIPTS / "game_state.gd"
# The shipped hub layer W9 authors (+ ascension_ui, W14 leg 3): the
# cost-literal gate's scope.
HUB_LAYER = [HUB_GD, GEAR_GD, ROW_GD, WAR_GD, SMITH_GD, TINK_GD, DUMMY_GD,
             ASC_GD]
STATIONS = [GEAR_GD, SMITH_GD, TINK_GD, DUMMY_GD, ASC_GD]

# The I2 structural set + number regex — the ONE home is
# tools/check_hygiene.py (W16, MC 11274.1.28): the gate's i2-literal rule
# and this layer's guard read the SAME set, so they can never drift.


def read_json(name):
    with open(GODOT / "data" / ("%s.json" % name), encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


BLACKSMITH = read_json("blacksmith")
RARITY = read_json("rarity")
XP = read_json("xp")
ITEMS = read_json("items")


# ---------- engine tier: run the probe, parse rows, re-derive numbers ---

def _rows(out, tag):
    hits = [line for line in out.splitlines() if line.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), out)
    return dict(kv.split("=", 1) for kv in hits[0].split(" ")[1:])


def _mats(text):
    """'torn_hide:2,iron_bar:1,' -> {id: n} (probe mats-row format)."""
    out = {}
    for pair in text.rstrip(",").split(","):
        if pair:
            key, val = pair.split(":")
            out[key] = int(val)
    return out


def _service_gold():
    return (int(BLACKSMITH["upgrade"]["gold_by_rarity"]["worn"])
            + int(BLACKSMITH["evolve"]["gold"])
            + int(BLACKSMITH["reroll"]["gold"])
            + int(BLACKSMITH["tinkering"]["gold"]))


def _want_mats():
    want = {}
    for key in ("upgrade", "evolve", "tinkering"):
        for mid, n in BLACKSMITH[key]["materials"].items():
            want[mid] = want.get(mid, 0) + int(n)
    return want


def test_hub_probe_engine_leg(tmp_path, class_cache):
    proc = conftest.run_probe_script(PROBE, (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    assert "HUB-PROBE FAIL" not in proc.stdout, proc.stdout
    out = proc.stdout

    boot = _rows(out, "HUB-PROBE-BOOT")
    assert int(boot["gold"]) == _service_gold() + 1, boot
    assert _mats(boot["mats"]) == _want_mats(), boot
    assert int(boot["bank"]) == 2, boot

    eq = _rows(out, "HUB-PROBE-EQUIP")
    # F2-11: each equip shrinks the bank to the one row left; the swap's
    # replaced row rides back INTO the bank (returned=uid of item A).
    assert eq["bank_after_first"] == "1" and eq["bank_after_swap"] == "1", eq
    assert int(eq["returned"]) > 0, eq
    twin = next(r for r in ITEMS if r["id"] == "twin_fang")
    assert eq["equipped"] == twin["id"], eq
    assert eq["relic_refused"] == "1", eq
    assert int(eq["bank_after_relic"]) == 2, eq  # A back + the relic row
    # W14 P2-10: a uid the bank does not hold is refused in the pinned
    # {ok,bank} shape — ok only when a row actually left the bank.
    assert eq["unknown_refused"] == "1", eq

    up = _rows(out, "HUB-PROBE-UPGRADE")
    cost = int(BLACKSMITH["upgrade"]["gold_by_rarity"]["worn"])
    assert int(up["cost"]) == cost, up
    assert _mats(up["mats_dropped"]) == BLACKSMITH["upgrade"]["materials"], up
    assert up["upgraded"] == "1" and up["rarity"] == "worn", up
    assert int(up["gold_left"]) == int(boot["gold"]) - cost, up

    ev = _rows(out, "HUB-PROBE-EVOLVE")
    ladder = RARITY["ladder"]
    assert ev["from"] == "worn" and ev["to"] == ladder[1], ev
    evo_cost = int(BLACKSMITH["evolve"]["gold"])
    assert int(ev["cost"]) == evo_cost and ev["refused"] == "1", ev
    assert int(ev["gold_left"]) == int(up["gold_left"]) - evo_cost, ev

    rr = _rows(out, "HUB-PROBE-REROLL")
    reroll_cost = int(BLACKSMITH["reroll"]["gold"])
    assert int(rr["cost"]) == reroll_cost and rr["stats_changed"] == "1", rr
    assert rr["mods_kept"] == "1" and rr["rarity"] == "powerful", rr
    assert int(rr["gold_left"]) == int(ev["gold_left"]) - reroll_cost, rr

    cap = _rows(out, "HUB-PROBE-TINKERCAP")
    assert cap["refused"] == "1" and cap["gold_unchanged"] == "1", cap
    assert cap["mods_unchanged"] == "1", cap

    tk = _rows(out, "HUB-PROBE-TINKER")
    tink_cost = int(BLACKSMITH["tinkering"]["gold"])
    assert int(tk["cost"]) == tink_cost and tk["moved"] == "1", tk
    assert _mats(tk["mats_dropped"]) == BLACKSMITH["tinkering"]["materials"], tk
    assert tk["source_mods"] == "0" and tk["target_mods"] == "1", tk
    # Whole-chain exactness: every service charged its data price once.
    assert int(tk["gold_left"]) == int(boot["gold"]) - _service_gold(), tk

    dm = _rows(out, "HUB-PROBE-DUMMY")
    # W14 P3-11 (declared reading, R-list): the practice-XP faucet is
    # CLOSED — the dummy is the DPS test A6 names; strike pays zero XP
    # and never emits mutated (meta untouched; the row carries the proof
    # the probe asserted over the whole heroes table + gold).
    assert dm["xp_paid"] == "0" and dm["meta_untouched"] == "1", dm
    assert dm["invulnerable"] == "1", dm
    assert abs(float(dm["dps"]) - float(dm["absorbed"])) < 1e-6, dm
    assert float(dm["dps"]) > 0.0, dm

    war = _rows(out, "HUB-PROBE-WAR")
    assert "normal" in war["maps"] and "hard" in war["maps"], war
    assert war["start"] == "gatefall" and war["difficulty"] == "hard", war

    panels = _rows(out, "HUB-PROBE-PANELS")
    assert panels["open"] == "blacksmith", panels

    asc = _rows(out, "HUB-PROBE-ASC")
    # W14 P1-3: one hero level-up earns points_per_level points (xp.json
    # x ascension.json), both refusals are spend_asc's own answers, the
    # station's button spent exactly one and left zero available.
    ascension = read_json("ascension")
    assert int(asc["earned"]) == int(ascension["points_per_level"]), asc
    assert asc["refused_unknown"] == "1" and asc["refused_over"] == "1", asc
    assert asc["spent"] == "1" and int(asc["available"]) == 0, asc
    assert asc["station"] == "visible", asc

    rl = _rows(out, "HUB-PROBE-RELIC")
    # W14 P1-2 (C11 pool) machine rows: the probe asserted the pinned
    # mission crossing + both slot-cap refusals + uid/relic/phase/none
    # refusals + unequip-return; hp_delta re-derives from items.json
    # (orb_of_the_deep primary = hp) and the scripted ilvl the probe
    # seeds (fixture input, not a balance literal). effect_blue proves
    # the asc_modifier consumer site: heroes.json base + reservoir val.
    assert all(rl[k] == "1" for k in ("assigned", "refused_taken",
               "refused_uid", "refused_relic", "refused_phase",
               "refused_none", "unequip", "asc_kept")), rl
    assert rl["pool_intact"] == "2" and rl["save_roundtrip"] == "2", rl
    orb = next(r for r in ITEMS if r["id"] == "orb_of_the_deep")
    assert orb["primary"] == "hp", orb           # the hp leg is the data
    assert abs(float(rl["hp_delta"]) - 3.0) < 1e-6, rl   # scripted ilvl 3
    heroes = {h["id"]: h for h in read_json("heroes")}
    res_row = next(row for row in ascension["tree"]["defense"]
                   if row["id"] == "reservoir")
    want_blue = float(heroes["warden"]["base"]["blue_max"]) \
        + float(res_row["per_point"]["val"])
    assert abs(float(rl["effect_blue"]) - want_blue) < 1e-6, (rl, want_blue)

    chest = _rows(out, "HUB-PROBE-CHEST")
    assert int(chest["bank_after"]) == int(chest["bank_before"]) + 1, chest
    assert chest["rarity"] == RARITY["chest_tiers"][0], chest
    assert chest["gold_untouched"] == "1", chest
    assert int(chest["shown"]) == int(chest["bank_after"]), chest

    ok_hits = [ln for ln in out.splitlines() if ln.strip() == "HUB-PROBE-OK"]
    assert len(ok_hits) == 1 and out.rstrip().endswith("HUB-PROBE-OK"), out


def test_hub_probe_is_deterministic(tmp_path, class_cache):
    first = conftest.run_probe_script(PROBE, (), tmp_path / "a")
    second = conftest.run_probe_script(PROBE, (), tmp_path / "b")
    assert first.returncode == 0 and second.returncode == 0
    assert first.stdout == second.stdout, \
        "probe output must be byte-stable under the pinned seed"


# ---------- source truth: I2 cost-literal ban over the hub layer -------

def _literal_violations(text):
    return hyg.literal_violations(text)


def test_hub_layer_carries_no_cost_literals():
    for path in HUB_LAYER:
        bad = _literal_violations(read_text(path))
        assert not bad, "%s carries non-structural number literals %r " \
            "(I2/I4: costs ride the data via the shipped statics)" % (path, bad)


def test_hub_planted_red_cost_literal_goes_red():
    # Fixture trick (nothing written): the evolve price as a code literal
    # must trip the SAME gate — an unbroken number gate is no gate.
    planted = read_text(GEAR_GD).replace(
        "func refresh() -> void:",
        "func _planted() -> int:\n\treturn 600\n\nfunc refresh() -> void:", 1)
    assert _literal_violations(planted) == [600.0], \
        "planted-red: 600 slipped through the hub literal gate"


# ---------- source truth: single application sites (C13/I4) ------------

def _blank(path):
    return hyg.blank_code(read_text(path), "gd")


def test_equip_crossing_is_the_single_one():
    gear = _blank(GEAR_GD)
    assert len(re.findall(r"state\.equip\(", gear)) == 1, \
        "gear_panel_ui crosses into meta ONLY through GameState.equip"
    for path in STATIONS:
        if path == GEAR_GD:
            continue
        assert not re.search(r"\.equip\(", _blank(path)), \
            "%s must not open a second equip door (F2-11/C13)" % path.name
    # equip is never called under another name in the hub layer.
    for path in HUB_LAYER:
        assert not re.search(r"SIM_INVENTORY\.equip\(", _blank(path)), \
            "%s bypasses GameState.equip into the raw static" % path.name


def test_service_statics_have_their_single_station():
    calls = {"svc_upgrade": (SMITH_GD, "upgrade"), "svc_evolve": (SMITH_GD,
           "evolve"), "svc_reroll": (SMITH_GD, "reroll"),
           "tinkering": (TINK_GD, "tinkering")}
    for static, (home, name) in calls.items():
        total = sum(len(re.findall(r"SIM_INVENTORY\.%s\(" % static,
                                   _blank(path))) for path in HUB_LAYER)
        assert total == 1, "%s must apply at exactly one hub site (I4)" % static
        assert re.search(r"SIM_INVENTORY\.%s\(" % static, _blank(home)), \
            "%s must be applied by %s (pinned %s leg)" % (static,
                                                          home.name, name)


def test_payment_and_xp_sites_are_named_and_scoped():
    # BN2: every service payment rides the named gold mutator; each
    # charging panel owns ONE call site; the free legs never touch gold.
    assert len(re.findall(r"state\.spend_gold\(", _blank(SMITH_GD))) == 1, \
        "blacksmith pays through exactly one spend_gold site"
    assert len(re.findall(r"state\.spend_gold\(", _blank(TINK_GD))) == 1, \
        "tinkerer pays through exactly one spend_gold site"
    for path in (GEAR_GD, WAR_GD, DUMMY_GD, ASC_GD):
        assert not re.search(r"spend_gold|consume_material", _blank(path)), \
            "%s is a free leg: no meta spend allowed" % path.name
    # W14 P3-11 (declared reading): the dummy practice-XP faucet is
    # CLOSED — ZERO add_hero_xp sites in the hub layer. The bound the
    # brief paraphrased names no data source, and a literal cap would
    # break I2; A6 declares the dummies as the DPS test only.
    total = sum(len(re.findall(r"add_hero_xp\(", _blank(p))) for p in HUB_LAYER)
    assert total == 0, "the hub layer must not open an XP faucet (P3-11)"
    assert not re.search(r"add_hero_xp\(", _blank(DUMMY_GD)), \
        "dummy_range is a DPS instrument only (the faucet stays closed)"
    # W14 P1-3: ascension points leave the account through exactly ONE
    # crossing — the station's shipped spend_asc mutator call.
    assert len(re.findall(r"state\.spend_asc\(", _blank(ASC_GD))) == 1, \
        "the ascension station pays through exactly one spend_asc site"
    for path in HUB_LAYER:
        if path != ASC_GD:
            assert not re.search(r"spend_asc\(", _blank(path)), \
                "%s opens a second ascension spend door" % path.name


def test_no_bank_writes_beside_the_mutators():
    for path in HUB_LAYER:
        code = _blank(path)
        assert not re.search(r"bank\.append\(|bank_add\(", code), \
            "%s writes the bank beside the C13 bank_add mutator" % path.name
        assert not re.search(r"mutated\.emit\(", code), \
            "%s must not emit the save signal itself — meta changes flow " \
            "through the shipped mutators (C13); listening is fine" % path.name


def test_no_progression_or_loot_math_in_hub_layer():
    for path in HUB_LAYER:
        code = _blank(path)
        assert not re.search(r"level_from_xp|SIM_PROGRESSION|hero_curve", code), \
            "%s re-implements level/xp math (SimProgression owns it)" \
            % path.name
        assert not re.search(r"roll_item|roll_victory_chest|victory_chest\(",
                             code), \
            "%s duplicates loot rolling — the victory chest rides the " \
            "shipped mission step (6) commit only" % path.name


def test_dummy_is_unkillable_by_shape():
    # Raw text: the keys are string literals (blank_code blanks those).
    code = read_text(DUMMY_GD)
    assert re.search(r'"absorbed"', code) and not re.search(r'"hp"', code), \
        "the dummy record carries absorbed/elapsed and NO hp key — " \
        "invulnerability is the row shape, not a guard (declared reading)"


# ---------- source truth: the shared item_row widget -------------------

def test_item_row_widget_is_shared_not_duplicated():
    # W14 (F2-12): the relic pickers render through the SAME widget —
    # the defense_panel (mission layer) joins the hub's three users.
    # W16 (MC 11274.1.28): the four users carried the SAME six-line fill
    # loop; it lives ONCE in bank_list.gd, which preloads the shared
    # scene — every user now routes through that ONE loop.
    assert re.search(r'preload\("res://scenes/item_row\.tscn"\)',
                     read_text(SCRIPTS / "bank_list.gd")), \
        "bank_list renders rows with the shared item_row scene"
    for path in (GEAR_GD, SMITH_GD, TINK_GD, SCRIPTS / "defense_panel.gd"):
        assert re.search(r'preload\("res://scripts/bank_list\.gd"\)',
                         read_text(path)), \
            "%s must render rows through the single bank_list fill loop" \
            % path.name
    defs = 0
    for gd in SCRIPTS.glob("*.gd"):
        defs += len(re.findall(r"^func show_item\(", read_text(gd), re.M))
    assert defs == 1, \
        "exactly ONE show_item exists repo-wide (gear, blacksmith, tinkerer " \
        "and the relic picker all render through the single item_row widget)"
    assert not re.search(r"show_item|item_row|bank_list", _blank(HUB_GD)), \
        "hub.gd composes panels only — no row rendering beside the widget"


# ---------- W17c (MC 11274.1.30): the shared fill loop is EMIT-SAFE ------
# Engine fact E9 (VERIFIED this card): free() on a Button while it emits
# `picked` is an engine ERROR ("Object is locked", object.cpp:787) — the
# MOUSE press path reaches every panel's pick handler mid-emit, so the
# shared clear must detach NOW + queue_free. The keyboard-path harnesses
# never emitted mid-emit: the false-green class again, at the shared-
# mechanism layer. Red-before/green-after transcripts: evidence W17c.

FILL_PROBE_SRC = """
extends SceneTree
# gw fill-chain probe: row.picked refills the shared loop mid-emit (the
# mouse press path). rc0 + EMPTY stderr + one live row after the refill.
const BANK_LIST := preload("res://scripts/bank_list.gd")


class Box:
	extends Node
	var frames := 0
	var filled := 0

	func _process(_d: float) -> void:
		frames += 1
		var item := {"uid": 1, "base_id": "x", "rarity": "", "slot": "relic"}
		if frames == 1:
			BANK_LIST.fill(self, null, [item], 0, _picked)
		elif frames == 2:
			(get_child(0) as Button).picked.emit(1)   # press == emit
		elif frames == 3:
			print("WFILL rows=%d filled=%d" % [get_child_count(), filled])
			get_tree().quit(0)

	func _picked(_uid: int) -> void:
		var item := {"uid": 2, "base_id": "y", "rarity": "", "slot": "relic"}
		BANK_LIST.fill(self, null, [item], 2, _picked)
		filled += 1


func _init() -> void:
	root.add_child(Box.new())
"""


def test_shared_fill_loop_engine_leg(tmp_path, class_cache):
    probe = Path(tmp_path) / "gw_fill_probe.gd"
    probe.write_text(FILL_PROBE_SRC, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), [], tmp_path / "user_home")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (W4 ruling):\n%s" % proc.stderr
    assert "WFILL rows=1 filled=1" in proc.stdout, proc.stdout


def _emit_safe_violations(code):
    bad = []
    if "queue_free()" not in code:
        bad.append("shared fill loop never queue_frees (E9 mid-emit lock)")
    if re.search(r"\.free\(\)", code):
        bad.append("shared fill loop frees a row directly")
    return bad


def test_shared_fill_loop_is_emit_safe():
    code = _blank(SCRIPTS / "bank_list.gd")
    bad = _emit_safe_violations(code)
    assert not bad, "bank_list.gd lost the emit-safe clear: %r" % bad


def test_shared_fill_loop_planted_red_direct_free_goes_red():
    code = _blank(SCRIPTS / "bank_list.gd").replace(
        "child.queue_free()", "child.free()")
    bad = _emit_safe_violations(code)
    assert bad, "planted-red: a direct free() slipped the emit-safe gate"


def test_item_row_planted_red_duplicate_renderer_goes_red():
    # Fixture trick: a second row renderer in the gear panel must trip the
    # single-widget gate.
    planted = read_text(GEAR_GD) + "\nfunc show_item(item, selected) -> void:\n\tpass\n"
    defs = 0
    for gd in SCRIPTS.glob("*.gd"):
        text = planted if gd == GEAR_GD else read_text(gd)
        defs += len(re.findall(r"^func show_item\(", text, re.M))
    assert defs == 2, "planted-red: duplicate show_item slipped through"


# ---------- source truth: pinned crossings ------------------------------

def test_war_table_hands_start_mission_to_the_router():
    war = _blank(WAR_GD)
    assert re.search(r"router\.start_mission\(", war), \
        "war_table.start crosses main's pinned start_mission (C13 hub->mission)"
    assert re.search(r'func setup\(router_in, tables', read_text(WAR_GD)), \
        "war_table.setup takes the router the hub injects (its parent)"


def test_hub_routes_stations_off_the_bridge_input_model():
    hub = _blank(HUB_GD)
    assert re.search(r"bridge\.drain_presses\(\)", hub), \
        "hub consumes discrete presses through the shipped bridge model " \
        "(no second input path)"
    for code in ['"Digit1"', '"Digit2"', '"Digit3"', '"Digit4"', '"KeyE"',
                 '"Escape"']:
        assert code in read_text(HUB_GD), "station map misses %s" % code
    assert re.search(r"\nfunc _open\(", read_text(HUB_GD)), \
        "one station-open crossing drives visibility"


def test_next_uid_anchors_worn_rows():
    # W9 declared finding, pinned as source truth: bank_add stamps uid
    # from max(bank, worn) — the pinned picked(uid) keys stay unique while
    # heroes wear gear and the mission-end chest bank_adds.
    gs = _blank(GS_GD)
    body = gs[gs.index("func next_uid"):]
    assert "for slots: Dictionary in equipped.values()" in body, \
        "next_uid must anchor on equipped rows too (R-list)"


def test_hub_layer_avoids_monetization_vocabulary():
    for path in HUB_LAYER:
        text = read_text(path).lower()
        for token in ("shop", "price", "cash", "gem", "wallet", "iap"):
            assert token not in text, \
                "%s carries monetization vocabulary %r (I1)" % (path.name, token)
