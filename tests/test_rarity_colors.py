"""v1.5 W-Q rarity colors (MC 11877 / V15-PLAN §3 W-Q, §2 row 8c) —
light the data-waiting tint + tint the loot toast.

THE MECHANISM THIS LIGHTS: item_row.bind(tables) -> rarity["colors"]
shipped in v1.2 waiting for the data key (its W9 header declared exactly
this); hud's loot toast grew the SAME door in this card (toast_modulate,
zero literals — every color arrives from rarity.json). rarity.json is
the authored side: `colors` carries ONE Color string per ladder name,
authored PER NAME IN THE LADDER'S OWN ORDER (DA N3 — none invented).

Legs (RC-* rows; in-probe RC-FAIL guards + RC-OK-LAST so a silent skip
cannot go green; ONE probe run serves both engine legs — conftest
tmp-probe idiom R5, E5: refresh() hand-driven, the panel.refresh()
precedent):
  RC-DATA      (pytest, data): colors present; keys == ladder set; the
               key ORDER is pinned to the ladder order; every value one
               lowercase #rrggbb string (parseable by the shipped door);
               all six pairwise distinct; worn neutral (r==g==b).
  RC-TINT x6   (engine): shipped scenes/item_row.tscn fresh per name,
               bind(real GWTables) + show_item(C9 row) -> $Tint.color
               == the authored color, every ladder name.
  RC-FALLBACK  (engine): an off-ladder name keeps the shipped neutral
               grey — the door's fallback. Pre-flight (plan §3 W-Q):
               NO pre-existing in-suite leg pinned any tint or the grey
               fallback (grep clean, WQ-wave.log §0), so lighting the
               key could not silently move a pinned pixel.
  RC-TOAST x7  (engine): real mission.tscn, HUD via the SHIPPED mount
               (mission.gd setup hook); seeded loot_events rows (the
               plan's named route) -> toast_label.modulate == the
               authored color per name; the no-row baseline is the grey
               fallback. RC-TEXT pins the toast copy shape unchanged.
  RC-SIMBLIND  (pytest, source truth): no godot/sim file and no
               game_state.gd names "colors" — the key can never be sim
               input, so the golden fixtures stay byte-pinned (the suite
               runs its own golden legs; `git diff tests/fixtures/`
               EMPTY is a gate row in WQ-wave.log).

PLANTED-RED x2 (WQ-wave.log): colors swapped in rarity.json -> RC-TINT
engine leg RED; colors key removed -> RC-DATA leg RED. Reverts
byte-verified. SERVED legs (hub bank rows + mission toast: shipped
clicks, state marker before pixel census, describe-image literal read)
are the card's served acceptance — transcripts and crops in the same
run dir. TWO layers, one contract: the probe proves the SHIPPED
renderer == the shipped data (a renderer bug reddens in-probe), every
pytest leg compares against the AUTHORED CONTRACT pinned below (a data
edit cannot silently move what the player sees).
"""

import json
import re
from pathlib import Path

import pytest

import conftest

GODOT = Path(conftest.repo_path("godot"))
_RARITY = json.loads((GODOT / "data" / "rarity.json").read_text(
    encoding="utf-8"))
LADDER = _RARITY["ladder"]
# THE AUTHORED CONTRACT (DA N3: colors authored PER NAME in the ladder's
# own order — this dict is that ruling made machine-checked). This card
# AUTHORS the palette, so pinning it HERE is the immutability mechanism,
# not a copy-to-agree: RC-DATA proves rarity.json == CONTRACT (values +
# order), the engine rows prove the shipped renderer == CONTRACT. A
# palette edit is therefore a deliberate re-pin, never a drive-by; a
# swapped color cannot go green (planted-red 1).
CONTRACT = {
    "worn": "#9d9d9d",
    "sturdy": "#6abe30",
    "powerful": "#4b7bd4",
    "epic": "#a04fd0",
    "mythical": "#e8912d",
    "legendary": "#d64550",
}
HEX_RE = re.compile(r"^#[0-9a-f]{6}$")
# Godot's NAMED table (measured at the engine this card): Color("gray")
# = 0.745098 per channel -> 190 (it is NOT the CSS #808080=128); the
# RC-FALLBACK/none-toast rows pin exactly what the shipped fallback
# paints — same fact the served-census crops multiply with.
GRAY_RGB = (190, 190, 190)
# Color("darkgray") (the shipped unselected-row self_modulate) measured
# at the engine: 0.662745 -> 169. This is the W-Q served-census factor:
# an unselected bank row PAINTS data-rgb x 169/255 (pinned below).
ROW_MOD_RGB = (169, 169, 169)

PROBE_SRC = '''
extends SceneTree
# gw rarity-colors probe (v1.5 W-Q, MC 11877). Machine rows: RC-BOOT /
# RC-TINT x6 / RC-FALLBACK / RC-TOAST x7 / RC-TEXT / RC-OK (LAST). Any
# failed check prints RC-FAIL <detail> + quit(1); a skipped leg can
# never reach RC-OK. The toast section rides the SHIPPED mission mount
# (the mission.gd setup hook instantiates HUD) and hand-drives
# refresh() (E5). Loot rows are SEEDED — the plan's named route; the
# C9 shape is the pinned one (kit-probe F3 shape: rarity is the leg
# input, every other field a fixture constant, zero balance numbers).
const GW_TABLES := preload("res://sim/sim_tables.gd")
const GW_COMPOSE := preload("res://sim/gw_compose.gd")
const ITEM_ROW := preload("res://scenes/item_row.tscn")
const MISSION_SCENE := "res://scenes/mission.tscn"
const DECK := ["warden", "deadeye", "embercaller"]
const PROBE_BASE := "wq_probe_edge"

var tables = null


func _fail(why: String) -> void:
	print("RC-FAIL " + why)
	quit(1)


func _c9(rarity_name: String) -> Dictionary:
	return {
		"uid": 0, "base_id": PROBE_BASE, "slot": "weapon",
		"rarity": rarity_name, "ilvl": 1,
		"primary": {"stat": "damage", "value": 1.0}, "secondary": null,
		"atk_speed": null, "shot_type": null, "proj_count": null,
		"mods": [], "upgraded": 0,
	}


func _p255(c: Color) -> String:
	return "%d,%d,%d" % [roundf(c.r * 255.0), roundf(c.g * 255.0),
			roundf(c.b * 255.0)]


func _init() -> void:
	tables = GW_TABLES.new("res://data")
	var rar: Dictionary = tables.table("rarity")
	if not rar.has("colors"):
		_fail("rarity.json has no colors key")
		return
	var ladder: Array = rar["ladder"]
	var colors: Dictionary = rar["colors"]
	print("RC-BOOT ladder=%d colors=%d" % [ladder.size(), colors.size()])
	if ladder.size() != 6 or colors.size() != 6:
		_fail("ladder/colors count wrong")
		return

	# --- RC-TINT: the shipped renderer, one fresh instance per name. ---
	for nm_v: Variant in ladder:
		var nm := String(nm_v)
		if not colors.has(nm):
			_fail("no authored color for ladder name " + nm)
			return
		var want := Color.from_string(String(colors[nm]), Color("black"))
		var item = ITEM_ROW.instantiate()
		root.add_child(item)
		item.bind(tables)
		item.show_item(_c9(nm), false)
		var tint: Color = item.get_node("Tint").color
		if tint != want:
			_fail("Tint for %s is %s not %s" % [nm, str(tint), str(want)])
			return
		print("RC-TINT name=%s rgb=%s row_mod=%s" % [nm, _p255(tint),
				_p255(item.self_modulate)])

	# --- RC-FALLBACK: off-ladder name keeps the shipped neutral grey. ---
	var fb = ITEM_ROW.instantiate()
	root.add_child(fb)
	fb.bind(tables)
	fb.show_item(_c9("gilded"), false)
	if fb.get_node("Tint").color != Color("gray"):
		_fail("fallback tint drifted from the shipped grey")
		return
	print("RC-FALLBACK rgb=%s" % _p255(fb.get_node("Tint").color))

	# --- RC-TOAST: real mission, HUD through the shipped mount. ---
	var graph: Dictionary = GW_COMPOSE.build_graph(tables)
	var state = graph["state"]
	state.set_deck(DECK.duplicate())     # shipped C13 mutator only (F3)
	var packed = ResourceLoader.load(MISSION_SCENE)
	if packed == null:
		_fail("mission.tscn not loadable")
		return
	var m = packed.instantiate()
	root.add_child(m)
	m._ready()                           # E5: drive _ready directly
	var rng := RandomNumberGenerator.new()
	rng.seed = 11877
	m.setup(tables, graph["state"], graph["save"], graph["bridge"],
			"gatefall", "normal", rng)
	var hud = m.get_node("HUD")
	if hud.toast_label == null:
		_fail("HUD did not mount the toast label")
		return
	print("RC-TOAST name=none rgb=%s text_empty=%d" % [
			_p255(hud.toast_label.modulate),
			1 if String(hud.toast_text()) == "" else 0])
	for nm_v: Variant in ladder:
		var nm := String(nm_v)
		m.loot_events.append(_c9(nm))
		hud.refresh()                    # E5: hand-drive, shipped read
		var want2 := Color.from_string(String(colors[nm]), Color("black"))
		if hud.toast_label.modulate != want2:
			_fail("toast modulate for %s is %s not %s" % [
					nm, str(hud.toast_label.modulate), str(want2)])
			return
		print("RC-TOAST name=%s rgb=%s" % [nm, _p255(
				hud.toast_label.modulate)])
	print("RC-TEXT text=%s" % String(hud.toast_text()))
	print("RC-OK")
	quit(0)
'''


@pytest.fixture(scope="module")
def probe_out(tmp_path_factory, class_cache):
    """ONE headless run (the mission mount is the expensive half)."""
    probe = tmp_path_factory.mktemp("rcprobe") / "gw_rarity_colors_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    proc = conftest.run_probe_script(str(probe), (),
                                     probe.parent / "user_home")
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" \
        % proc.stderr
    assert "RC-FAIL" not in proc.stdout, proc.stdout
    assert proc.stdout.rstrip().endswith("RC-OK"), \
        "RC-OK must be the LAST row (a skipped leg cannot reach it)"
    return proc.stdout


def _rows(out, tag):
    hits = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert hits, "no %s row in probe output:\n%s" % (tag, out)
    return [dict(x.split("=", 1) for x in ln.split(" ")[1:])
            for ln in hits]


def _expect_rgb(hexstr):
    return tuple(int(hexstr[i:i + 2], 16) for i in (1, 3, 5))


def _close(a, b):
    return all(abs(x - y) <= 1 for x, y in zip(a, b))


def _rgb(row):
    return tuple(int(x) for x in row["rgb"].split(","))


def test_rarity_colors_data():
    """RC-DATA: rarity.json == the authored contract, values + order."""
    colors = _RARITY["colors"]
    assert list(colors) == LADDER, "colors key order must equal the ladder"
    assert set(colors) == set(LADDER)
    rgbs = []
    for name in LADDER:
        val = colors[name]
        assert HEX_RE.match(val), "%s: %r is not one lowercase #rrggbb" \
            % (name, val)
        assert val == CONTRACT[name], \
            "%s: %r moved off the authored contract %r — a palette edit " \
            "is a deliberate re-pin, not a drive-by" % (name, val,
                                                        CONTRACT[name])
        rgbs.append(_expect_rgb(val))
    assert len(set(rgbs)) == 6, "the six colors must be pairwise distinct"
    assert rgbs[0][0] == rgbs[0][1] == rgbs[0][2], \
        "worn (the ladder floor) stays neutral: r==g==b"


def test_colors_are_not_sim_input():
    """RC-SIMBLIND: no sim/state file names "colors" — the presentation
    key can never enter the golden replay path (fixtures byte-pinned)."""
    universe = sorted((GODOT / "sim").glob("*.gd")) + \
        [GODOT / "scripts" / "game_state.gd"]
    named = [p.name for p in universe
             if '"colors"' in p.read_text(encoding="utf-8")]
    assert named == [], \
        "sim/state layer reads the presentation key: %s" % named


def test_item_row_tints_are_the_data(probe_out):
    """RC-TINT (all six) + RC-FALLBACK on the shipped row scene."""
    tints = {r["name"]: _rgb(r) for r in _rows(probe_out, "RC-TINT")}
    assert set(tints) == set(LADDER), "one row per ladder name"
    for r in _rows(probe_out, "RC-TINT"):
        assert _close(_rgb({"rgb": r["row_mod"]}), ROW_MOD_RGB), \
            "unselected row modulate drifted off the shipped darkgray " \
            "(the served census multiplies by it): %s" % r
    for name in LADDER:
        assert _close(tints[name], _expect_rgb(CONTRACT[name])), \
            "item_row Tint for %s is not the contract color: %s != %s" % (
                name, tints[name], _expect_rgb(CONTRACT[name]))
    fb = _rows(probe_out, "RC-FALLBACK")[0]
    assert _close(_rgb(fb), GRAY_RGB), \
        "the off-ladder fallback is not the shipped neutral grey: %s" % fb


def test_loot_toast_tints_are_the_data(probe_out):
    """RC-TOAST (no-row baseline + all six) + RC-TEXT copy unchanged."""
    toasts = {r["name"]: _rgb(r) for r in _rows(probe_out, "RC-TOAST")}
    assert set(toasts) == {"none"} | set(LADDER)
    assert _close(toasts["none"], GRAY_RGB), \
        "the no-row toast is not the neutral fallback"
    assert _rows(probe_out, "RC-TOAST")[0]["text_empty"] == "1"
    for name in LADDER:
        assert _close(toasts[name], _expect_rgb(CONTRACT[name])), \
            "toast modulate for %s is not the contract color: %s != %s" \
            % (name, toasts[name], _expect_rgb(CONTRACT[name]))
    text_hits = [ln for ln in probe_out.splitlines()
                 if ln.startswith("RC-TEXT ")]
    assert len(text_hits) == 1, "RC-TEXT row count %d" % len(text_hits)
    text = text_hits[0].split("text=", 1)[1]   # rest of line = copy
    assert text == "Picked up wq_probe_edge (legendary)", \
        "toast copy drifted from the shipped shape: %s" % text
