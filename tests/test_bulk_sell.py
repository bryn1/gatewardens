"""F2 — bulk sell: SELL ALL behind one total-gold confirm (MC 11622 /
V12-PLAN §F2, wave W2). Owner ruling 2026-10-28 (verbatim): "rec on all 3"
ratifying "SELL ALL sellable items with ONE confirm dialog showing the
total gold BEFORE it is applied".

Mechanism (replace-not-add, plan §F2):
- SimInventory.bulk_sell is the ONE bulk-total sum (pure static, no RNG);
  the confirm quote (GWGameState.sell_bank_quote, read-only, no emit) and
  the applied delta (GWGameState.sell_bank) BOTH route through it, so the
  number the dialog shows IS the number paid — no second math.
- Pricing is DATA: rarity.json "sell_value" (one int per ladder name,
  plan's suggested ladder values, monotone) — zero cost literals in code
  (I2; the gear panel is also gate-governed by check_hygiene i2-literal).
- sell_bank on ok clears the bank and pays the total through the
  sanctioned add_gold emit: ONE C13 write for the whole bulk sell.
  Refusal (empty bank) is bulk_sell's {ok:false, why:"empty"} with no
  bank write, no gold write and NO emit (plan: bank/gold/save unchanged,
  assert all three). Nothing-sellable IS the empty case structurally:
  every ladder rarity carries a declared value and no special
  non-sellable row classes exist (plan VERIFIED grep) — equipped gear
  never sits in the bank (C6/C9 split), so bank-only sell cannot touch
  it. Materials are not items (plan: out of scope, stated).

Contract legs (engine tier = the conftest.run_probe_script idiom, probe
generated into tmp_path per the test_family_picker/test_defense_boundaries
precedent; numbers re-derived from rarity.json, never literals):
- VALID (BS-PRESS/BS-APPLY/BS-SAVE): the confirm state carries the summed
  total BEFORE apply (gold + ack still untouched at BS-PRESS — the number
  exists in the CONFIRM state, not just the result); confirming pays
  EXACTLY Σ sell_values, empties the bank, commits with ack delta 1, and
  a fresh from_save reload persists gold + empty bank.
- INVALID (BS-EMPTY/BS-DOUBLE): empty bank refused {ok:false,why:"empty"}
  — bank/gold/save byte-unchanged (no file written at all), the second
  press idempotent, gold unchanged (duplicates+repeats leg).
- BOUNDARY (BS-CANCEL/BS-DOUBLE shown): CANCEL closes the dialog with
  nothing applied; a press over an empty bank opens NO dialog (shown=0,
  button disabled) and applies nothing.
- Purity: bulk_sell mutates no row (pure-static leg below) and the probe
  keeps the seeded rows' uids after the quote.

Source-truth legs (plan DA P2-1): game_state.gd has exactly one
bank.append site and every inline bank write lives in a sanctioned func
(bank_add/sell_bank-clear/equip/from_save); sell_bank itself never emits
(the single-write leg); gear_panel_ui stays the pure mutator door (no
gold/bank writes, one sell_bank site — the test_hub.py :329 ban-regex is
UNEDITED and re-run green separately: game_state is not a HUB_LAYER file
and `state.sell_bank(` matches no pattern there).

PLANTED-RED (wave log transcript): scratch mutation makes bulk_sell's
gold the row COUNT (gold = bank.size()) -> BS-QUOTE/BS-PRESS/BS-APPLY/
BS-SAVE go RED rc1; git checkout -- restores; green re-run beside the red.
"""

import json
import re

import conftest

RARITY = json.load(open(conftest.repo_path("godot", "data", "rarity.json"),
                        encoding="utf-8"))
SELL = RARITY["sell_value"]
LADDER = RARITY["ladder"]
SEEDED = ["worn", "sturdy", "powerful"]   # the probe's three bank rows
TOTAL = sum(SELL[r] for r in SEEDED)      # re-derived, never a literal

SIM_INV = conftest.repo_path("godot", "sim", "sim_inventory.gd")
GAME_STATE = conftest.repo_path("godot", "scripts", "game_state.gd")
GEAR_PANEL = conftest.repo_path("godot", "scripts", "gear_panel_ui.gd")

# The bulk-sell probe (test_family_picker R5 idiom: generated into
# tmp_path — the probe home outside the shipped tree). Machine rows:
#   BS-EMPTY ok=0 why=empty gold=0 bank=0 seq=<n> save_exists=<0|1>
#   BS-QUOTE ok=1 total=<g> sold=3 uid_intact=<0|1>
#   BS-PRESS shown=<0|1> in_text=<0|1> total=<g> gold=<g> bank=3 ack_delta=<n>
#   BS-CANCEL shown=<0|1> gold=<g> bank=3
#   BS-APPLY gold=<g> bank=<n> ack_delta=<n> shown=<0|1>
#   BS-SAVE gold=<g> bank=<n>
#   BS-DOUBLE ok=0 why=<w> gold=<g> bank=<n> shown=<0|1> ack_delta=<n>
#   BS-OK
# Every contract leg is ALSO checked in-probe (BS-FAIL + quit 1), so a
# failure names its leg before the stderr leg even matters.
PROBE_SRC = '''\
# bulk_sell probe — F2 (MC 11622). Test asset under -s (E5: setup driven
# directly, Button pressed.emit is the shipped chain; E3: failure paths
# print BS-FAIL and quit(1)).
extends SceneTree

const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const GW_GAME_STATE := preload("res://scripts/game_state.gd")
const GEAR_PANEL := preload("res://scripts/gear_panel_ui.gd")
const SIM_INVENTORY := preload("res://sim/sim_inventory.gd")

const SEEDED := [["oaken_cleaver", "worn"], ["iron_hauberk", "sturdy"],
	["twin_fang", "powerful"]]


func _init() -> void:
	var tables = GW_TABLES.new("res://data")
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)   # F2-5 wiring
	var state = graph["state"]
	var save = graph["save"]
	var panel: Control = GEAR_PANEL.new()
	panel.name = "GearPanel"
	root.add_child(panel)                    # tree-owned: no leak at exit
	panel.setup(tables, state)

	# INVALID leg FIRST (empty from the start): refused, no writes at all.
	var res0: Dictionary = state.sell_bank()
	var seq0 := int(save.write_seq)
	print("BS-EMPTY ok=%d why=%s gold=%d bank=%d seq=%d save_exists=%d" % [
			1 if bool(res0.get("ok", false)) else 0,
			String(res0.get("why", "")), int(state.gold),
			state.bank.size(), seq0,
			1 if FileAccess.file_exists("user://gatewardens.cfg") else 0])
	if bool(res0.get("ok", false)) or String(res0.get("why", "")) != "empty" \\
			or int(state.gold) != 0 or not state.bank.is_empty() \\
			or int(state.saved_ack) != seq0 \\
			or FileAccess.file_exists("user://gatewardens.cfg"):
		_fail("empty refusal changed state or wrote a save: %s" % str(res0))
		return

	# Seed the bank through the shipped C13 mutator ONLY (uids stamped).
	var items: Array = tables.rows("items")
	for spec: Array in SEEDED:
		state.bank_add(_scripted_row(items, String(spec[0]),
				String(spec[1])))
	var ack_seed := int(state.saved_ack)
	var sell_values: Dictionary = tables.table("rarity").get("sell_value", {})
	var total := 0
	for spec: Array in SEEDED:
		total += int(sell_values.get(String(spec[1]), 0))

	# Quote (pure): the pre-apply sum + purity read-back (rows untouched).
	var q: Dictionary = state.sell_bank_quote()
	var uid_ok := true
	for row: Dictionary in state.bank:
		if int(row.get("uid", 0)) <= 0:
			uid_ok = false
	print("BS-QUOTE ok=%d total=%d sold=%d uid_intact=%d" % [
			1 if bool(q.get("ok", false)) else 0, int(q.get("gold", -1)),
			int(q.get("sold", -1)), 1 if uid_ok else 0])
	if not bool(q.get("ok", false)) or int(q.get("gold", -1)) != total \\
			or int(q.get("sold", -1)) != SEEDED.size() or not uid_ok:
		_fail("quote wrong: %s total=%d" % [str(q), total])
		return

	# VALID half 1 — the CONFIRM STATE carries the total BEFORE apply:
	# press the shipped SELL BANK button, then read back gold, bank and
	# the C13 ack: NOTHING was applied yet, the number lives in the dialog.
	var sell_btn := panel.get_node_or_null("Gear/SellBank") as Button
	if sell_btn == null:
		_fail("shipped sell entry not mounted by panel.setup")
		return
	sell_btn.pressed.emit()
	var cs: Dictionary = panel.sell_confirm_shown()
	var shown := bool(cs["shown"])
	var in_text := 1 if String(cs["text"]).contains(str(total)) else 0
	print("BS-PRESS shown=%d in_text=%d total=%d gold=%d bank=%d ack_delta=%d" % [
			1 if shown else 0, in_text, total, int(state.gold),
			state.bank.size(), int(state.saved_ack) - ack_seed])
	if not shown or in_text != 1 or int(state.gold) != 0 \\
			or state.bank.size() != SEEDED.size() \\
			or int(state.saved_ack) - ack_seed != 0:
		_fail("confirm state broken: %s gold=%d" % [str(cs), int(state.gold)])
		return

	# BOUNDARY: CANCEL closes with nothing applied.
	var cancel := panel.get_node_or_null("Gear/SellRow/SellCancel") as Button
	if cancel == null:
		_fail("confirm cancel button missing")
		return
	cancel.pressed.emit()
	var cs2: Dictionary = panel.sell_confirm_shown()
	print("BS-CANCEL shown=%d gold=%d bank=%d" % [
			1 if bool(cs2["shown"]) else 0, int(state.gold),
			state.bank.size()])
	if shown and (bool(cs2["shown"]) or int(state.gold) != 0 \\
			or state.bank.size() != SEEDED.size()):
		_fail("cancel applied state: %s" % str(cs2))
		return

	# VALID half 2 — CONFIRM pays exactly the shown total, ONE C13 write.
	sell_btn.pressed.emit()
	var confirm := panel.get_node_or_null("Gear/SellRow/SellConfirm") as Button
	if confirm == null:
		_fail("confirm button missing")
		return
	confirm.pressed.emit()
	var cs3: Dictionary = panel.sell_confirm_shown()
	print("BS-APPLY gold=%d bank=%d ack_delta=%d shown=%d" % [
			int(state.gold), state.bank.size(),
			int(state.saved_ack) - ack_seed,
			1 if bool(cs3["shown"]) else 0])
	if int(state.gold) != total or not state.bank.is_empty() \\
			or int(state.saved_ack) - ack_seed != 1 \\
			or bool(cs3["shown"]):
		_fail("apply broken: gold=%d bank=%d ack=%d" % [
				int(state.gold), state.bank.size(),
				int(state.saved_ack) - ack_seed])
		return

	# Save round-trip: a fresh state over the SAME save file carries the
	# sold gold and the emptied bank (C13 single write persisted both).
	var st2: RefCounted = GW_GAME_STATE.new(tables)
	st2.from_save(save.load_save())
	print("BS-SAVE gold=%d bank=%d" % [int(st2.gold), st2.bank.size()])
	if int(st2.gold) != total or not st2.bank.is_empty():
		_fail("save round-trip lost the bulk sell: gold=%d bank=%d" % [
				int(st2.gold), st2.bank.size()])
		return

	# INVALID/BOUNDARY repeat (duplicates+repeats): the sold-out bank
	# presses open NO dialog and the mutator refuses idempotently.
	sell_btn.pressed.emit()
	var res2: Dictionary = state.sell_bank()
	var cs4: Dictionary = panel.sell_confirm_shown()
	print("BS-DOUBLE ok=%d why=%s gold=%d bank=%d shown=%d ack_delta=%d" % [
			1 if bool(res2.get("ok", false)) else 0,
			String(res2.get("why", "")), int(state.gold),
			state.bank.size(), 1 if bool(cs4["shown"]) else 0,
			int(state.saved_ack) - ack_seed - 1])
	if bool(res2.get("ok", false)) \\
			or String(res2.get("why", "")) != "empty" \\
			or int(state.gold) != total or not state.bank.is_empty() \\
			or bool(cs4["shown"]) or int(state.saved_ack) - ack_seed != 1:
		_fail("sold-out repeat applied: %s" % str(res2))
		return

	print("BS-OK")
	quit(0)


# Full C9 row through the hub_probe _scripted_item door (the bank rows the
# shipped item_row renderer draws; no mods leg needed here).
func _scripted_row(items: Array, base_id: String, rarity: String) -> Dictionary:
	var base: Dictionary = {}
	for row: Dictionary in items:
		if String(row.get("id", "")) == base_id:
			base = row
	if base.is_empty():
		_fail("no items.json base %s" % base_id)
		return {}
	return {
		"uid": 0,
		"base_id": String(base["id"]),
		"slot": String(base["slot"]),
		"rarity": rarity,
		"ilvl": 5,
		"primary": {"stat": String(base["primary"]), "value": 5.0},
		"secondary": null,
		"atk_speed": float(base["roll_ranges"]["atk_speed"][0]),
		"shot_type": (String(base["shot_types"][0])
				if int(base["shot_types"].size()) > 0 else null),
		"proj_count": int(base["roll_ranges"]["proj_count"][0]),
		"mods": [],
		"upgraded": 0,
	}


func _fail(why: String) -> void:
	print("BS-FAIL " + why)
	quit(1)
'''


def _rows(out, tag):
    hits = [line for line in out.splitlines() if line.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), out)
    return dict(kv.split("=", 1) for kv in hits[0].split(" ")[1:])


def check_rows(out):
    """All machine-row asserts over probe stdout — shared so the
    planted-red mutated run must fail the SAME checks."""
    emp = _rows(out, "BS-EMPTY")
    assert emp["ok"] == "0" and emp["why"] == "empty", \
        "empty bank must refuse with the pinned string: %s" % emp
    assert emp["gold"] == "0" and emp["bank"] == "0", emp
    assert emp["save_exists"] == "0", \
        "the refusal wrote a save file: %s" % emp

    q = _rows(out, "BS-QUOTE")
    assert q["ok"] == "1" and int(q["total"]) == TOTAL, \
        "quote must equal Σ sell_values (rarity.json re-derived): %s" % q
    assert q["sold"] == "3" and q["uid_intact"] == "1", \
        "quote must be pure (rows untouched): %s" % q

    press = _rows(out, "BS-PRESS")
    assert press["shown"] == "1", \
        "press on a sellable bank must open the confirm dialog: %s" % press
    assert press["in_text"] == "1", \
        "the CONFIRM STATE must carry the total gold before apply: %s" % press
    assert press["gold"] == "0" and press["bank"] == "3" \
            and press["ack_delta"] == "0", \
        "BS-PRESS must apply NOTHING (no gold, no bank clear, no save): %s" \
        % press

    cancel = _rows(out, "BS-CANCEL")
    assert cancel["shown"] == "0" and cancel["gold"] == "0" \
            and cancel["bank"] == "3", \
        "cancel must close the dialog with nothing applied: %s" % cancel

    apply = _rows(out, "BS-APPLY")
    assert int(apply["gold"]) == TOTAL, \
        "sell-all moves EXACTLY the summed shipped sell values: %s" % apply
    assert apply["bank"] == "0" and apply["shown"] == "0", apply
    assert apply["ack_delta"] == "1", \
        "one save commit — the bulk sell rides exactly ONE C13 write: %s" \
        % apply

    sv = _rows(out, "BS-SAVE")
    assert int(sv["gold"]) == TOTAL and sv["bank"] == "0", \
        "save round-trip must persist gold + empty bank: %s" % sv

    dbl = _rows(out, "BS-DOUBLE")
    assert dbl["ok"] == "0" and dbl["why"] == "empty", \
        "sold-out re-click is the same empty case refused: %s" % dbl
    assert int(dbl["gold"]) == TOTAL and dbl["bank"] == "0", dbl
    assert dbl["shown"] == "0", \
        "nothing-sellable must open NO dialog: %s" % dbl
    assert dbl["ack_delta"] == "0", \
        "the refusal wrote no second save: %s" % dbl

    assert "BS-OK" in out.splitlines(), out


def test_bulk_sell_engine_leg(tmp_path, class_cache):
    probe = tmp_path / "bulk_sell_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse/crash signal):\n%s" \
        % proc.stderr
    assert "BS-FAIL" not in proc.stdout, proc.stdout
    check_rows(proc.stdout)


def _read(path):
    import sys
    sys.path.insert(0, conftest.repo_path("tools"))
    import check_hygiene as hyg  # noqa: E402  (reuse: ONE blanking home)
    with open(path, encoding="utf-8") as fh:
        return hyg.blank_code(fh.read(), "gd")


def _body(text, header):
    start = text.index(header)
    rest = text[start + len(header):]
    end = re.search(r"\n(?:static )?func ", rest)
    return rest[:end.start()] if end else rest


# ---------- data leg: the shipped sell ladder IS the price (I2) ----------

def test_sell_value_is_one_int_per_ladder_name_and_monotone():
    assert set(SELL) == set(LADDER), \
        "sell_value must carry exactly one price per ladder name"
    values = [SELL[name] for name in LADDER]
    assert all(isinstance(v, int) and v > 0 for v in values), values
    assert all(b > a for a, b in zip(values, values[1:])), \
        "plan §F2: monotone with the ladder (worn 2 -> legendary 40)"


# ---------- source-truth legs (no engine) ----------

def test_bulk_sell_is_pure_and_the_one_bulk_math():
    inv = _read(SIM_INV)
    body = _body(inv, "static func bulk_sell(")
    for banned in ("rand", ".append(", ".remove_at", "mutated", "queue_free"):
        assert banned not in body, \
            "bulk_sell must stay pure (no mutation/RNG): %r found" % banned
    # ONE bulk math: the sell ladder is summed ONLY inside bulk_sell and
    # reached ONLY through it — game_state reads the map, sums nowhere.
    gs = _read(GAME_STATE)
    assert "sell_value" not in gs.replace("_sell_values", ""), \
        "only the _sell_values door may name the data key"
    assert gs.count("SIM_INVENTORY.bulk_sell(") == 2, \
        "quote + mutator are the two, and ONLY two, bulk_sell call sites"
    panel = _read(GEAR_PANEL)
    assert "sell_value" not in panel and "bulk_sell" not in panel, \
        "the panel does no math of its own (pure-UI reading)"


def test_game_state_bank_writes_stay_sanctioned():
    # Plan DA P2-1 leg over game_state.gd itself: exactly one bank.append
    # site (bank_add) and every inline `bank =` write inside a sanctioned
    # func — the new sell_bank clear included.
    raw = open(GAME_STATE, encoding="utf-8").read()
    assert raw.count("bank.append(") == 1, \
        "the bank must be appended ONLY in the bank_add mutator"
    code = _read(GAME_STATE)
    sanctioned = {"bank_add", "equip", "from_save", "sell_bank"}
    writers = set()
    for m in re.finditer(r"func (\w+)\(.*?(?=\nfunc |\Z)", code, re.S):
        if re.search(r"\bbank\s*=|bank\.append\(", m.group(0)):
            writers.add(m.group(1))
    assert writers == sanctioned, \
        "inline bank writers drifted from the sanctioned set: %r" % writers
    assert "bank = []" in _body(code, "func sell_bank("), \
        "sell_bank must route the clear through the bank field, once"


def test_sell_bank_is_the_single_write_and_the_panel_is_the_mutator_door():
    code = _read(GAME_STATE)
    body = _body(code, "func sell_bank(")
    assert "add_gold(" in body and "mutated.emit" not in body, \
        "the total must ride the sanctioned add_gold emit — sell_bank " \
        "itself never fires a second C13 trigger (one save commit)"
    quote = _body(code, "func sell_bank_quote(")
    assert "mutated.emit" not in quote and "add_gold" not in quote \
            and "bank =" not in quote, \
        "the quote is read-only: no write, no trigger"
    panel = _read(GEAR_PANEL)
    for banned in ("bank.append(", "bank_add(", "mutated.emit", "add_gold",
                   "spend_gold", "gold", ".sell_bank_quote()."):
        # the LAST banned entry is the refresh-call suffix used for the
        # count leg below — the ban itself checks inline writes/copy
        if banned != ".sell_bank_quote().":
            assert banned not in panel, \
                "the panel writes/applies beside the mutators: %r" % banned
    assert panel.count("state.sell_bank_quote()") == 2, \
        "quote reached at the press + the refresh, not a third math site"
    assert panel.count("state.sell_bank()") == 1, \
        "exactly ONE application crossing (the confirm handler)"
