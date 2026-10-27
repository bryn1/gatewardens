"""W17g round-4 gate (MC card 11408) — the equip SAVE ROUND-TRIP P1.

Served facts (pck 244408, orchestrator browser verification): after a
VERIFIED equip (bank 150, warden.weapon = oaken_cleaver, ack 3, flush,
reload) the bank persisted but equipped came back {} — game_state
persisted every C6 key EXCEPT equipped ("C6 carries no key for it"),
while the equip itself removes the row from the bank (persisted). The
item existed NEITHER in bank NOR equipped after reload: equipping +
reload DESTROYED gear (P1 player-item loss; equipped gear IS the meta,
DD2 lineage). C6 gains [meta2].equipped_json (game_state to_save/
from_save + the save_store file key): rows ride the same JSON-string door
as items_json; OLD saves miss the key -> {} (I5 back-compat, NO schema
bump — a bump fails the version guard and wipes every real save).

Legs (engine tier, the SHIPPED graph: GWCompose.build_graph wires the C13
commit listener, so mutated -> GWSaveStore.write is the served write;
from_save into a fresh GWGameState is the served load):
- GREEN round-trip: equip A, equip B over it (F2-11 replace returns A to
  the bank), read the file through save.load_save(), load into a FRESH
  state: equipped equals the pre-save map (semantic parse-vs-parse —
  save_probe's VERIFIED door: JSON numbers arrive as float), hero weapon
  = the replacing row's base_id, bank size matches AND the returned row
  is in the bank EXACTLY ONCE (no double-add). stderr EMPTY (W4).
- BACK-COMPAT (arg "oldsave"): a file written with the PRE-ROUND-4 key
  list (ConfigFile, no equipped_json AT ALL) boots: equipped EMPTY, bank/
  deck/gold intact.
- PLANTED-RED (permanent, arg "stripped"): the save re-written WITHOUT
  the equipped payload (the pre-fix writer's world) — the survival
  predicate MUST go RED on it (rc1 + GWSAVE-FAIL).
"""

import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402 (blank_code for source greps)

GODOT = Path(conftest.repo_path("godot"))
STATE_GD = GODOT / "scripts" / "game_state.gd"
STORE_GD = GODOT / "scripts" / "save_store.gd"


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


PROBE_SRC = '''
extends SceneTree
# gw gear-persist probe (W17g round 4, MC card 11408). Machine rows:
# GWSAVE-ACK / -EQUIP / -OLD / -OK; failures print GWSAVE-FAIL + rc1.
# THE P1 (served pck 244408): equip persisted bank-1 while the equipped
# map had no save key — equip + reload DESTROYED the item (neither bank
# nor equipped after boot). The graph is the SHIPPED one
# (GWCompose.build_graph: state + save + C13 commit listener), so the
# writes this probe rides ARE the served writes (mutated -> commit ->
# GWSaveStore.write, synchronous; saved_ack mirrors write_seq).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const GW_GAME_STATE := preload("res://scripts/game_state.gd")


func _fail(why: String) -> void:
	print("GWSAVE-FAIL " + why)
	quit(1)


func _build() -> Dictionary:
	var tables := GW_TABLES.new()
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var state = graph["state"]
	state.set_deck(["warden", "deadeye", "embercaller"])
	state.bank_add({"base_id": "oaken_cleaver", "rarity": "worn",
		"ilvl": 5, "slot": "weapon"})
	state.bank_add({"base_id": "emberbrand", "rarity": "worn",
		"ilvl": 5, "slot": "weapon"})
	return graph


func _init() -> void:
	var args: Array = OS.get_cmdline_user_args()
	var graph: Dictionary = _build()
	var state = graph["state"]
	var save = graph["save"]
	var item_a: Dictionary = state.bank[state.bank.size() - 2] as Dictionary
	var item_b: Dictionary = state.bank[state.bank.size() - 1] as Dictionary
	if not state.equip("warden", "weapon", item_a) \\
			or not state.equip("warden", "weapon", item_b):
		_fail("shipped equip path refused the setup equips")
		return
	# EQ2 REPLACED A: row A returned to the bank, B is worn. The persisted
	# bank must carry A EXACTLY ONCE (no double-add on the replace).
	print("GWSAVE-ACK ack=" + str(state.saved_ack) + " bank_pre=" \\
			+ str(state.bank.size()))
	var d: Dictionary = save.load_save()
	if "stripped" in args:
		# PLANTED-RED: a save WITHOUT the equipped payload (the pre-fix
		# writer's world: to_save carried no key). Re-writing through the
		# shipped write() lands the same "{}" nothing an old file carries
		# — the survival predicate MUST fail on it.
		d.erase("equipped_json")
		if not save.write(d):
			_fail("stripped re-write failed")
			return
		d = save.load_save()
	if "oldsave" in args:
		# TRUE OLD FILE: ConfigFile with the PRE-ROUND-4 key list — no
		# equipped_json AT ALL (not even "{}").
		var cfg := ConfigFile.new()
		cfg.set_value("meta", "schema_version", int(d["schema_version"]))
		cfg.set_value("meta", "asc_earned", int(d["asc_earned"]))
		cfg.set_value("meta", "asc_spent_json", String(d["asc_spent_json"]))
		var heroes_in: Dictionary = d.get("heroes", {})
		for hero_id: String in heroes_in:
			cfg.set_value("hero:" + hero_id, "level",
					int(heroes_in[hero_id]["level"]))
			cfg.set_value("hero:" + hero_id, "xp",
					int(heroes_in[hero_id]["xp"]))
		cfg.set_value("bank", "items_json", String(d["items_json"]))
		cfg.set_value("meta2", "gold", int(d["gold"]))
		cfg.set_value("meta2", "deck_json", String(d["deck_json"]))
		cfg.set_value("meta2", "completed_json", String(d["completed_json"]))
		cfg.set_value("meta2", "materials_json", String(d["materials_json"]))
		if cfg.save(save.path) != OK:
			_fail("old-format file write failed")
			return
		d = save.load_save()
	# The shipped LOAD path into a FRESH state (a boot reads like this).
	var fresh = GW_GAME_STATE.new(state.tables)
	fresh.from_save(d)
	if "oldsave" in args:
		# Back-compat contract: the old file boots — equipped starts EMPTY
		# (no ghost rows) and everything the old file DID carry lands.
		var ok_old: bool = fresh.equipped.is_empty() \\
				and fresh.bank.size() == state.bank.size() \\
				and fresh.deck == state.deck and fresh.gold == state.gold
		print("GWSAVE-OLD eq_empty=" + str(fresh.equipped.is_empty()) \\
				+ " bank_ok=" + str(fresh.bank.size() == state.bank.size()))
		if not ok_old:
			_fail("old save did not boot intact")
			return
		print("GWSAVE-OK")
		quit(0)
		return
	var eq_saved: Variant = JSON.parse_string(JSON.stringify(state.equipped))
	var eq_file: Variant = JSON.parse_string(
			String(d.get("equipped_json", "{}")))
	# Semantic equality (save_probe's VERIFIED door): Godot JSON.parse
	# returns every number as float, so raw == against the in-memory
	# int map is the named artifact — parse-vs-parse is the contract.
	var eq_ok: bool = eq_saved == eq_file \\
			and JSON.parse_string(JSON.stringify(fresh.equipped)) == eq_file
	var base := "none"
	var wmap: Dictionary = fresh.equipped.get("warden", {})
	if wmap.get("weapon") != null:
		base = String((wmap["weapon"] as Dictionary).get("base_id", ""))
	var a_count := 0
	for row: Dictionary in fresh.bank:
		if int(row.get("uid", 0)) == int(item_a["uid"]):
			a_count += 1
	print("GWSAVE-EQUIP eq_ok=" + str(eq_ok) + " base=" + base \\
			+ " bank_post=" + str(fresh.bank.size()) + " a_count=" \\
			+ str(a_count))
	if not eq_ok:
		_fail("equipped did not survive save->load: file=" \\
				+ String(d.get("equipped_json", "<missing>")))
		return
	if base != "emberbrand":
		_fail("hero weapon after reload is " + base + " — expected " \\
				+ "emberbrand (the REPLACING row; A returned to bank)")
		return
	if fresh.bank.size() != state.bank.size() or a_count != 1:
		_fail("bank after reload wrong: post=" + str(fresh.bank.size()) \\
				+ " pre=" + str(state.bank.size()) + " a_count=" \\
				+ str(a_count) + " — the replace-return row must be in " \\
				+ "the bank EXACTLY once (F2-11, no double-add)")
		return
	print("GWSAVE-OK")
	quit(0)
'''


def _run_probe(extra_args, tmp_path):
    probe = Path(tmp_path) / "gw_persist_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), extra_args,
                                     tmp_path / "user_home")


def _rows(out, tag):
    return [dict(kv.split("=", 1) for kv in
                 ln.split(" ")[1:] if "=" in kv)
            for ln in out.splitlines() if ln.startswith(tag + " ")]


def test_equipped_survives_save_load_engine_leg(tmp_path, class_cache):
    proc = _run_probe([], tmp_path)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (W4):\n%s" % proc.stderr
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    out = proc.stdout
    assert "GWSAVE-FAIL" not in out, out
    assert out.rstrip().endswith("GWSAVE-OK"), out
    eq = _rows(out, "GWSAVE-EQUIP")
    ack = _rows(out, "GWSAVE-ACK")
    assert len(eq) == 1 and len(ack) == 1, out
    eq, ack = eq[0], ack[0]
    # Re-derive the contract numerically from the machine rows.
    assert eq["eq_ok"] == "true", eq
    assert eq["base"] == "emberbrand", eq
    assert eq["a_count"] == "1", eq
    assert int(ack["bank_pre"]) == int(eq["bank_post"]), (ack, eq)
    assert int(ack["ack"]) > 0, ack   # the C13 write really landed


def test_old_save_without_the_key_boots_clean(tmp_path, class_cache):
    proc = _run_probe(["oldsave"], tmp_path)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (W4):\n%s" % proc.stderr
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    out = proc.stdout
    assert out.rstrip().endswith("GWSAVE-OK"), out
    old = _rows(out, "GWSAVE-OLD")
    assert len(old) == 1, out
    assert old[0]["eq_empty"] == "true", old
    assert old[0]["bank_ok"] == "true", old


def test_persist_planted_red_stripped_save_goes_red(tmp_path, class_cache):
    # A save WITHOUT the equipped payload (the pre-fix writer's world):
    # the SAME survival predicate leg MUST fail — permanent in-suite.
    proc = _run_probe(["stripped"], tmp_path)
    assert proc.returncode == 1, \
        "planted-red: a stripped save slipped the round-trip\n%s" \
        % proc.stdout
    out = proc.stdout
    assert "GWSAVE-FAIL" in out and "GWSAVE-OK" not in out, out


def test_equipped_key_is_pinned_in_both_doors():
    # Source truth: to_save WRITES the map, from_save READS it with the
    # {} back-compat default, and the store carries the key BOTH ways
    # (write + load). A planted removal is detectable by the same greps.
    # RAW source: the contract lives in the string literals themselves,
    # which blank_code would blank out.
    state = read_text(STATE_GD)
    assert '"equipped_json": JSON.stringify(equipped)' in state, \
        "to_save must write the equipped map"
    assert 'equipped = json_dict(d.get("equipped_json", "{}"))' in state, \
        "from_save must restore equipped with the {} back-compat default"
    store = read_text(STORE_GD)
    assert store.count('"equipped_json"') >= 2, \
        "save_store must carry the key in write() AND load_save()"
    planted = state.replace(
        '"equipped_json": JSON.stringify(equipped),', "")
    assert '"equipped_json": JSON' not in planted  # planted shape is red
