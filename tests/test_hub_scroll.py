"""W17g hub-scroll gate (MC card 11408 / workspace 11274, fix round) — the
A9-served greybox overflow closed: the hub station panels ride ONE
ScrollContainer (hub.gd "PanelScroll"), so a full victory bank (~150 rows)
reaches the DECK hero-equip rows by MOUSE WHEEL.

Fix round (served browser verification FAILED the first shape): the min
sync ran SAME-FRAME in _open/_refresh_status, but a content Container's
min size is only valid AFTER its layout frame completes — served, the
wheel burst scrolled ~500px and hit a permanent floor (byte-identical
frames after +80/+400/+300/+300 events; a meta mutation did not unstick
it). hub.gd now syncs the panel min from its OWN _process pump: the
DEFERRED-by-construction read of the next frame(s), change-gated (no
re-sort churn), converging as layout lands.

Tiers (test_hub_layout precedent):
- ENGINE TIER (green): a SceneTree probe boots the REAL Main.tscn under
  REAL frames, sizes the hub root to the served 1280x720, seeds through
  the shipped C13 mutators ONLY (set_deck + 150x bank_add — the ~150-item
  bank a normal WIN banks, golden pins loot_events:148), opens the gear
  station through the shipped route (handle_press Digit2), then — after
  at least TWO process frames — asserts the scroll LIMIT (not a forced
  scroll_to, which hides a ceiling bug): limit >= hero_btn_bottom -
  viewport_height; delivers a real InputEventMouseButton MOUSE_BUTTON_
  WHEEL_DOWN through root.push_input (the served input path, W17b
  idiom) and asserts scroll_vertical INCREASED; then sets scroll_vertical
  to the limit (clamp-safe) and asserts the hero weapon-slot button's
  GLOBAL rect INTERSECTS the ScrollContainer's visible rect — the
  wheel-reachable end state. EMPTY stderr (W4 ruling).
- PLANTED-RED (permanent): arg "prefix" runs the SAME reachability
  predicate against the PRE-FIX container shape (plain VBox PanelSlot, no
  ScrollContainer — the W17f tree the A9 journey walked): RED there, the
  hero row's global Y exceeds the viewport height; rc1 + GWSCROLL-FAIL.
- SOURCE TRUTH (stdlib): exactly ONE ScrollContainer wraps the shared
  PanelSlot (replace-not-add-beside); the vertical mode is the engine
  enum constant; the min sync is pumped from the hub _process (DEFERRED
  by construction — same-frame syncs are the bug this round fixed);
  hidden-sync-to-zero kept. Planted-red: unwrapping the slot AND dropping
  the pump call both go RED.
"""

import re
import sys
from pathlib import Path

import conftest

sys.path.insert(0, conftest.repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code for code greps)

GODOT = Path(conftest.repo_path("godot"))
HUB_GD = GODOT / "scripts" / "hub.gd"


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


PROBE_SRC = '''\\

extends SceneTree
# gw hub-scroll probe (W17g, fix round). Machine rows: GWSCROLL-VIEW /
# -RANGE / -LIMIT / -SCROLL / -WHEEL / -REACH / -PREFIX / -OK; any failed
# check prints GWSCROLL-FAIL <detail> + rc1. Arg "prefix": the SAME
# reachability predicate runs against the PRE-FIX container shape (plain
# VBox PanelSlot, no ScrollContainer) and MUST fail there (planted-red).
const MAIN_SCENE := "res://Main.tscn"
const BANK_FILL := 150              # ~one normal WIN banks this many rows
const DECK := ["warden", "deadeye", "embercaller"]
const SLOT := "Slot_warden_weapon"  # gear_panel_ui _rebuild_heroes name
const SERVED := Vector2(1280, 720)   # the served canvas (project viewport)


class Monitor:
	extends Node
	var main_ref
	var prefix := false
	var frames := 0
	var hero = null
	var scroll = null
	var sv_before := 0

	func _process(_d: float) -> void:
		frames += 1
		if frames > 240:               # 4s ceiling: a hang is FAIL not spin
			print("GWSCROLL-FAIL no settle after %d frames" % frames)
			get_tree().quit(1)
			return
		if prefix:
			if frames == 4:
				_build_prefix()
			elif frames == 10:
				_check_prefix()
			return
		if frames == 2:
			# The served canvas mirror: the headless `-s` window is a fixed
			# 64x64 and refuses resize (VERIFIED) — sizing the hub root is
			# EXACTLY what the 1280x720 browser viewport does for it.
			main_ref._routed.size = SERVED
		elif frames == 4:
			var hub = main_ref._routed
			hub.state.set_deck(DECK.duplicate())
			for i in BANK_FILL:
				hub.state.bank_add({"base_id": "oaken_cleaver",
					"rarity": "worn", "ilvl": 5, "slot": "weapon"})
			hub.handle_press("Digit2")   # the shipped gear-station route
		elif frames == 8:                # >= TWO process frames after open
			_precheck()
		elif frames == 10:
			_wheel()
		elif frames == 12:
			_moved()
		elif frames == 13:
			_bottom()
		elif frames == 16:
			_check_reach()

	# The ONE reachability predicate both legs share: does the button's
	# global rect intersect the VISIBLE rect of the box it must be seen
	# in (post-fix the ScrollContainer's rect, pre-fix the viewport)?
	func _reaches(view: Rect2, br: Rect2) -> bool:
		return view.intersects(br)

	func _fail(why: String) -> void:
		print("GWSCROLL-FAIL " + why)
		get_tree().quit(1)

	func _node() -> void:
		var hub = main_ref._routed
		if scroll == null:
			scroll = hub.get_node("Layout/PanelScroll")
		if scroll == null or not scroll.is_class("ScrollContainer"):
			_fail("PanelScroll missing or not a ScrollContainer")
		if hero == null:
			hero = hub.gear.find_child(SLOT, true, false)
		if hero == null:
			_fail("hero equip slot button " + SLOT + " not rendered")

	func _precheck() -> void:
		_node()
		var hub = main_ref._routed
		var rows: int = hub.gear.shown_rows()
		var br: Rect2 = hero.get_global_rect()
		var view: Rect2 = scroll.get_global_rect()
		var sb = scroll.get_v_scroll_bar()
		print("GWSCROLL-VIEW hub_h=" + str(hub.size.y) + " scroll_h=" \\
				+ str(view.size.y))
		print("GWSCROLL-RANGE max=" + str(sb.max_value) + " rows=" + str(rows))
		if rows < 150:
			_fail("bank did not fill the gear list: rows=" + str(rows))
			return
		if sb.max_value <= 0.0:
			_fail("scroll limit 0 with " + str(rows) \\
					+ " rows — content does not overflow, the leg " \\
					+ "would pass vacuously")
			return
		if _reaches(view, br):
			_fail("hero slot visible WITHOUT scrolling — the panel does " \\
					+ "not overflow, the leg would pass vacuously")
			return
		# THE CEILING ASSERT (fix round, MC 11408): the scroll LIMIT —
		# not a forced scroll_to — must cover the hero row: a same-frame
		# min sync floors this and the served wheel ~500px below.
		var required: float = br.end.y - view.size.y
		print("GWSCROLL-LIMIT limit=" + str(sb.max_value) + " hero_b=" \\
				+ str(br.end.y) + " view_h=" + str(view.size.y))
		if sb.max_value < required:
			_fail("scroll limit " + str(sb.max_value) + " cannot reach " \\
					+ "the hero row (needs >= " + str(required) \\
					+ ") — the min sync never tracked the content")
			return
		sv_before = int(scroll.scroll_vertical)


	func _wheel() -> void:
		# The SERVED input path: a real mouse-wheel event through the
		# Viewport pipeline (the W17b push_input idiom) — not a forced
		# scroll_to (which hides a scroll-limit ceiling bug).
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_WHEEL_DOWN
		ev.pressed = true
		ev.position = Vector2(640.0, 400.0)   # inside the scroll view
		ev.global_position = ev.position
		get_tree().root.push_input(ev)
		print("GWSCROLL-WHEEL sent button=WHEEL_DOWN at " + str(ev.position))

	func _moved() -> void:
		var sv_now := int(scroll.scroll_vertical)
		print("GWSCROLL-WHEEL before=" + str(sv_before) + " after=" \\
				+ str(sv_now))
		if sv_now <= sv_before:
			_fail("wheel event moved nothing (" + str(sv_before) + " -> " \\
					+ str(sv_now) + ") — the served path stays dead")
			return
		var sb = scroll.get_v_scroll_bar()
		scroll.scroll_vertical = int(sb.max_value)   # the limit, clamp-safe
		print("GWSCROLL-SCROLL set=" + str(int(sb.max_value)) + " clamped=" \\
				+ str(int(scroll.scroll_vertical)))

	func _bottom() -> void:
		pass

	func _check_reach() -> void:
		var br: Rect2 = hero.get_global_rect()
		var view: Rect2 = scroll.get_global_rect()
		print("GWSCROLL-REACH btn_y=" + str(br.position.y) + " btn_b=" \\
				+ str(br.end.y) + " view_y=" + str(view.position.y) \\
				+ " view_b=" + str(view.end.y))
		if not _reaches(view, br):
			_fail("hero slot unreachable at the wheel-reachable end " \\
					+ "state btn=" + str(br) + " view=" + str(view))
			return
		if int(scroll.scroll_vertical) <= 0:
			_fail("scroll_vertical stayed 0 at the bottom leg")
			return
		print("GWSCROLL-OK")
		get_tree().quit(0)

	# The pre-fix shape VERBATIM (W17f hub.gd): full-rect root VBox,
	# plain VBox PanelSlot, station panel = plain Control holding one
	# tall VBox. NO ScrollContainer; NO min-size sync.
	func _build_prefix() -> void:
		var host := Control.new()
		host.name = "PreFixHost"
		host.size = SERVED          # the served canvas (green leg's mirror)
		get_tree().root.add_child(host)
		var outer := VBoxContainer.new()
		host.add_child(outer)
		var head := Label.new()
		head.text = "GATEWARDENS — HUB"
		outer.add_child(head)
		var slot := VBoxContainer.new()
		slot.name = "PanelSlot"
		outer.add_child(slot)
		var panel := Control.new()
		slot.add_child(panel)
		var inner := VBoxContainer.new()
		panel.add_child(inner)
		for i in BANK_FILL:
			var r := Button.new()
			r.text = "oaken_cleaver [worn]"
			inner.add_child(r)
		hero = Button.new()
		hero.name = SLOT
		hero.text = "weapon: -"
		inner.add_child(hero)

	func _check_prefix() -> void:
		# Pre-fix there is NO scroll container: the ONLY visible rect is
		# the served viewport the host Control stands in for.
		var view: Rect2 = get_tree().root.get_node("PreFixHost").get_global_rect()
		var br: Rect2 = hero.get_global_rect()
		print("GWSCROLL-PREFIX btn_y=" + str(br.position.y) + " view_h=" \\
				+ str(view.size.y))
		if _reaches(view, br):
			print("GWSCROLL-PREFIXOK — planted shape unexpectedly " \\
					+ "reaches, the red has gone green")
			get_tree().quit(0)
			return
		_fail("prefix shape hero row below the viewport (y=" \\
				+ str(br.position.y) + " > h=" + str(view.size.y) + ")")


func _init() -> void:
	var packed = ResourceLoader.load(MAIN_SCENE)
	if packed == null:
		print("GWSCROLL-FAIL Main.tscn not loadable")
		quit(1)
		return
	var main = packed.instantiate()
	root.add_child(main)
	# E5 (VERIFIED W13): under `-s` add_child never dispatches _ready —
	# the harness drives the real boot entry point; frames then run.
	# (Fix-round VERIFIED: the engine fires the real _ready at frame 0
	# too — hub.setup runs AGAIN — so seeding waits for frame 4, after
	# the boot rebuild settled, mirroring a player acting on a settled
	# served hub.)
	main._ready()
	var mon := Monitor.new()
	mon.main_ref = main
	mon.prefix = "prefix" in OS.get_cmdline_user_args()
	root.add_child(mon)
'''


def _run_scroll_probe(extra_args, tmp_path):
    probe = Path(tmp_path) / "gw_scroll_probe.gd"
    probe.write_text(PROBE_SRC, encoding="utf-8")
    return conftest.run_probe_script(str(probe), extra_args,
                                     tmp_path / "user_home")


def _kv(out, tag, nth=1):
    hits = [ln for ln in out.splitlines() if ln.startswith(tag + " ")]
    assert len(hits) >= nth, "%s row count=%d\n%s" % (tag, len(hits), out)
    return dict(kv.split("=", 1) for kv in
                hits[nth - 1].split(" ")[1:] if kv)


def test_scroll_reaches_hero_slots_engine_leg(tmp_path, class_cache):
    proc = _run_scroll_probe([], tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (true parse signal):\n%s" % proc.stderr
    out = proc.stdout
    assert "GWSCROLL-FAIL" not in out, out
    assert out.rstrip().endswith("GWSCROLL-OK"), out

    # ~150-item bank overflows the served viewport (the A9 journey wall).
    rng = _kv(out, "GWSCROLL-RANGE")
    assert int(rng["rows"]) >= 150, rng
    assert float(rng["max"]) > 0.0, rng

    # THE CEILING LINE: the scroll limit must cover the hero row —
    # re-derived numerically from the printed machine rows.
    lim = _kv(out, "GWSCROLL-LIMIT")
    assert float(lim["limit"]) >= float(lim["hero_b"]) - float(lim["view_h"]), \
        "scroll limit cannot reach the hero row: %s" % lim

    # The SERVED path: a real wheel event moved the scroll.
    wheel_hits = [ln for ln in out.splitlines()
                  if ln.startswith("GWSCROLL-WHEEL ")]
    assert len(wheel_hits) == 2, out
    moved = _kv(out, "GWSCROLL-WHEEL", nth=2)
    assert int(moved["after"]) > int(moved["before"]), moved
    assert int(moved["before"]) == 0, moved

    # The wheel-reachable end state: at the limit the hero equip-slot
    # button's global rect INTERSECTS the ScrollContainer's visible rect.
    reach = _kv(out, "GWSCROLL-REACH")
    btn_y, btn_b = float(reach["btn_y"]), float(reach["btn_b"])
    view_y, view_b = float(reach["view_y"]), float(reach["view_b"])
    assert btn_y < view_b and btn_b > view_y, reach
    scrolled = _kv(out, "GWSCROLL-SCROLL")
    # The engine clamps the request to the TRUE bottom; the ScrollBar
    # control's own max can lag one sort behind (VERIFIED this card),
    # so the bottom is pinned by the rects above — here only that the
    # scroll genuinely moved.
    assert int(scrolled["clamped"]) > 0, scrolled


def test_scroll_planted_red_prefix_shape_goes_red(tmp_path, class_cache):
    # The PRE-FIX container shape run through the SAME reachability
    # predicate: it MUST go RED (an unbroken reach check is no check).
    proc = _run_scroll_probe(["prefix"], tmp_path)
    assert proc.returncode == 1, \
        "planted-red: the pre-fix VBox shape slipped the reach check\n%s" \
        % proc.stdout
    out = proc.stdout
    assert "GWSCROLL-FAIL" in out and "GWSCROLL-OK" not in out, out
    pre = _kv(out, "GWSCROLL-PREFIX")
    assert float(pre["btn_y"]) > float(pre["view_h"]), \
        "planted-red: hero row must sit BELOW the viewport height: %s" % pre


# ---------- source truth: ONE scroll + the DEFERRED pump ------------

def _hub_code():
    return hyg.blank_code(read_text(HUB_GD), "gd")


def _scroll_violations(code):
    bad = []
    if len(re.findall(r"ScrollContainer\.new\(\)", code)) != 1:
        bad.append("the station scroll must be EXACTLY ONE container "
                   "(replace-not-add-beside: no per-panel scroll)")
    if not re.search(r"scroll\.add_child\(slot\)", code):
        bad.append("the shared PanelSlot must mount INSIDE the ScrollContainer")
    if not re.search(r"vertical_scroll_mode\s*=\s*ScrollContainer\."
                     r"SCROLL_MODE_AUTO", code):
        bad.append("vertical scroll must be enabled via the engine enum "
                   "constant (no magic ints)")
    # DEFERRED by construction: the sync is pumped from _process (the
    # shipped per-frame drain), never only same-frame — the served floor
    # (wheel stuck ~500px below the DECK rows) was the same-frame shape.
    if not re.search(r"_process\(_delta[\s\S]{0,700}?_sync_panel_mins\(\)",
                     code):
        bad.append("the min sync must run from the hub _process pump "
                   "(deferred: a content min is only valid after its "
                   "layout frame — same-frame syncs floor the scroll)")
    if "custom_minimum_size" not in code:
        bad.append("panel roots must sync their min from their content "
                   "boxes (a plain Control reports min (0,0) — the "
                   "ScrollContainer would never see the content height)")
    return bad


def test_hub_wraps_the_shared_panel_slot_in_one_scroll():
    bad = _scroll_violations(_hub_code())
    assert not bad, "hub station scroll regressed: %r" % bad


def test_hub_scroll_planted_red_unwrapped_slot_goes_red():
    # Fixture trick (nothing written): re-parent PanelSlot straight onto
    # the layout root (the pre-W17g shape) — the same gate MUST catch it.
    planted = _hub_code().replace("scroll.add_child(slot)",
                                  "root_box.add_child(slot)", 1)
    bad = _scroll_violations(planted)
    assert bad, "planted-red: an unwrapped PanelSlot slipped the scroll gate"
    # And the same-frame shape (this round's served bug): drop the pump
    # call — the gate must catch a same-frame-only sync too.
    unplamped = _hub_code().replace("_sync_panel_mins()", "", 1)
    bad2 = _scroll_violations(unplamped)
    assert any("pump" in b for b in bad2), \
        "planted-red: a dropped min-sync pump slipped the gate: %r" % bad2
