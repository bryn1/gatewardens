# W17g evidence — hub station panels scroll into the hero equip rows (MC card 11408 / workspace 11274)

PROBE: grep -c '222 passed' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W17g-suite-final.log => ^1$
PROBE: grep -c 'check_hygiene: 0 hit' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W17g-hygiene-final.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_hard.jsonl => ^5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628
PROBE: grep -c 'freed or unreferenced' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W17g3-red-click_stderr.log => ^1$
PROBE: grep -c 'rc=1' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W17g4-red-click_save.log => ^1$
PROBE: grep -c 'rc=1' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W17g4-red-persist_roundtrip.log => ^1$
PROBE: grep -c 'queue_free' /home/claudecode/Games/gatewardens/godot/scripts/gear_panel_ui.gd => ^2$
PROBE: grep -c 'equipped_json' /home/claudecode/Games/gatewardens/godot/scripts/game_state.gd => ^5$
PROBE: grep -c 'equipped_json' /home/claudecode/Games/gatewardens/godot/scripts/save_store.gd => ^5$
PROBE: grep -c 'ScrollContainer' /home/claudecode/Games/gatewardens/godot/scripts/hub.gd => ^4$
PROBE: grep -c 'W17g' /home/claudecode/Games/gatewardens/LEDGER.md => ^1$
PROBE: sha256sum /home/claudecode/Games/gw-persisted-deck2.png => ^93dac9ba24f54ca044d428127033b9f6b2ed89fe3e7d4f48337e836d55ba65c7
PROBE: grep -c 'VERIFY_EXIT=0' /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W17g-evidence.md => ^6$
DOCS: LEDGER.md W17g rows updated in commits e839fa1/47287d3/cbfe6ff; no other doc describes the fixed behavior (README product claims unchanged).

## The defect (A9 journey limitation (b), LEDGER row 0afe00c)
The hub mounted the six station panels in a plain VBox "PanelSlot" — no
ScrollContainer anywhere in godot/scripts (grep: zero hits). A single
normal WIN banks ~150 items (golden fixture pins loot_events:148), so the
gear panel's DECK hero-equip buttons rendered ~3600–5300px down, BELOW the
720px served viewport: the A9 REQUIRED "equip" served leg was unreachable
to a mouse player. Engine-level equip already worked headless.

## The fix (godot/scripts/hub.gd ONLY — one mechanism, replace-not-add-beside)
- PanelSlot WRAPS in exactly ONE `ScrollContainer` ("PanelScroll",
  `vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO` — engine enum
  constants only, `SIZE_EXPAND_FILL` on both axes). ALL station panels
  ride the same scroll; the six `slot.add_child(...)` mounts and every
  coordinate/pick/refresh/equip semantic stay verbatim.
- Engine fact E10 (VERIFIED 4.7.2 this card): a plain Control root reports
  min size (0,0) to Container ancestors — the ScrollContainer never sees
  the panel content height (first spike: scrollbar max = 0 with 150 rows).
  Bridge: the hub syncs each panel root's CUSTOM minimum from its content
  Container's combined min (`custom_minimum_size` — Control.minimum_size
  is READ-ONLY in 4.7, VERIFIED via the assignment SCRIPT ERROR); hidden
  panels sync to ZERO (the scroll range never sums hidden stations); the
  content box's `minimum_size_changed` re-fires the sync on every refill,
  and `_refresh_status` — the shipped `mutated`/`_open` relay — resyncs on
  station switches. Sizing only: containers still own every position.
- Engine fact E11 (VERIFIED): the headless `-s` window is a fixed 64x64
  and refuses `root.size` (prints (64,64) after the set) — the probe sizes
  the hub root Control, which is EXACTLY what the served 1280x720 browser
  canvas does for it (spike: hub.size=1280x720 -> PanelScroll (1280, 631)).
  The W13 hub-layout gate passes untouched (slot_parents "PanelSlot" x6,
  disjointness, F-2 relay all still green).

## Declared readings
- The DoD names `bash tools/check_hygiene.sh`; the repo's gate is
  `python3 tools/check_hygiene.py` (no .sh exists; every prior card from
  W15 on ran the .py — same gate, output below).
- "~150-item bank": the probe seeds 150 weapon rows through the SHIPPED
  C13 mutator only (`bank_add`, uid stamped by `next_uid`), mirroring the
  normal-WIN bank scale (golden loot_events:148 + starter rows).

## Test legs — tests/test_hub_scroll.py (4 legs, engine tier + source truth)
GREEN (engine tier): boots the real Main.tscn under real frames,
set_deck + 150x bank_add (shipped mutators), opens gear via the shipped
`handle_press("Digit2")` route, asserts: rows >= 150, scrollbar max > 0,
the hero button rect is OUTSIDE the ScrollContainer visible rect BEFORE
scrolling (anti-vacuous), then scrolls to the bottom and asserts the
button's GLOBAL rect INTERSECTS the ScrollContainer's visible rect
(pytest re-derives the rects numerically from the printed machine rows).

## GREEN — full suite on the final committed tree
```
217 passed in 100.87s (0:01:40)     # baseline 213 + the 4 W17g legs
FINAL_SUITE_RC=0
```
Full transcript: W17g-full-suite-green.log. Gate file alone: 4 passed
(W17g-green-hub_scroll.log).

## RED #1 — PRE-FIX SHAPE (permanent planted-red, arg "prefix")
The SAME reachability predicate run against the pre-fix container shape
(full-rect VBox + plain VBox PanelSlot, no ScrollContainer — the W17f
tree the A9 journey walked). Hero row global Y exceeds the viewport
height; the check goes RED (rc=1, no GWSCROLL-OK, EMPTY stderr). Raw
probe transcript (W17g-red-prefix_probe.log):
```
=== planted-red (PRE-FIX container shape), rc=1 ===
Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org

GWSCROLL-PREFIX btn_y=5277.0 view_h=720.0
GWSCROLL-FAIL prefix shape hero row below the viewport (y=5277.0 > h=720.0)
```
In-suite permanently as test_scroll_planted_red_prefix_shape_goes_red
(plus a source-tier planted-red: unwrapping PanelSlot off the scroll
trips the same gate).

## RED #2 — PRE-FIX CODE (red-before-green, real tree)
`git stash` of the hub.gd fix, then the SAME green engine leg — fails by
the missing container (W17g-red-prefix_code.log):
```
AssertionError: probe rc=1
  GWSCROLL-FAIL PanelScroll missing or not a ScrollContainer
ERR:ERROR: Node not found: "Layout/PanelScroll" (relative to "/root/Main/Hub").
1 failed in 50.85s
```
Fix restored (`git stash pop`), everything above re-run against the
restored tree.

## Hygiene — 0 hits (W17g-hygiene.log)
```
check_hygiene: 0 hit(s)
HYGIENE_RC=0
```
(hub.gd 260 lines — soft-250 note only, like defense_obj 275; ceiling 400
not approached; test file 320 lines < 600.)

## Golden + hard fixture shas — BYTE-UNCHANGED (W17g-fixture-shas.log)
```
eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912  tests/fixtures/mission_gatefall_normal.jsonl
5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628  tests/fixtures/mission_gatefall_hard.jsonl
```
Byte-identical to the card's pins eafe3932 / 5e37c4b0; the golden replay
legs (test_sim_golden) ran inside the 217-green suite above (zero sim/
data/ files touched by the change — hub UI layer only).

## Scope notes
- Mission layer, defense_panel, HUD, bridge, sim: untouched (git diff
  shows hub.gd + LEDGER.md + the new test file only).
- Click/pick/refresh/equip paths unchanged — ScrollContainer only adds
  the viewport clip + wheel scroll Godot implements natively
  (mouse_force_pass_scroll_events stays default).
- Known limits (declared): keyboard focus-follow (ScrollContainer
  follow_focus, default false) not enabled — wheel/scrollbar drive the
  served mouse leg this card gates; the hub stations' min-size sync sums
  direct CONTENT Containers (each of the six panels carries exactly one,
  VERIFIED per file).

VERIFY_EXIT=0

---

## W17g FIX ROUND (served wheel-floor, 2026-10-27)

Served verification FAILED round 1: wheel scrolled ~18-20 rows (~500px)
then a PERMANENT floor; byte-identical frames after +80/+400/+300/+300
events; a meta mutation did not unstick. Root cause: _sync_panel_min ran
SAME-FRAME in _open/_refresh_status; a content Container's min size is
only valid AFTER its layout frame completes. Headless proof (boot-timed
seed spike, pre-fix hub, fresh XDG save):

    F8 scroll=(1280.0, 631.0) sbmax=93.0 sv=0 panel_custom_min=(0.0, 0.0) hero_y=89.0
    panel custom_min=(0.0, 0.0) box_min=(312.0, 9248.0)

— panel min NEVER tracked the 9248px content; the min-change signal never
re-delivered a fresh value. (Fix-round VERIFIED -s harness fact: the
engine fires main._ready a SECOND time at frame 0 under -s — hub.setup
runs again — so boot-timed probes get wiped; seeds are frame-timed in
the gate.)

FIX (hub.gd, ONE mechanism): _sync_panel_mins runs EVERY frame from the
hub's OWN _process pump (the shipped per-frame drain) — DEFERRED by
construction; change-gated sets (no per-frame re-sort churn); converges
as layout frames land; hidden-to-zero kept. Spike post-fix:
custom_min=(0,9248) sbmax=9248; a real MOUSE_BUTTON_WHEEL_DOWN via
root.push_input moved scroll_vertical 0->78 in one event (F10).

TESTS TIGHTENED (tests/test_hub_scroll.py, "scroll_to hides a ceiling
bug" addressed): green leg opens gear via the shipped handle_press route,
reads after >=2 process frames (f8), asserts the scroll LIMIT numerically
(limit >= hero_btn_bottom - viewport_h, GWSCROLL-LIMIT row), delivers a
real InputEventMouseButton WHEEL_DOWN via push_input (f10) and asserts
scroll_vertical INCREASED (f12), then sets scroll_vertical to the limit
(clamp-safe) and asserts the hero weapon-slot rect INTERSECTS the
ScrollContainer visible rect (f16). Source gate now PINS the _process
pump call; planted pump-drop goes RED (test_hub_scroll_planted_red_-
unwrapped_slot_goes_red second assertion, in-suite).

HONEST LIMIT: the pre-fix same-frame code also PASSES the tightened
runtime leg under -s (1 passed, transcript below summary) — the frame-0
double-_ready masks the served stale ordering headless; deterministic
teeth for this round are the source-gate pump pin + the served browser
re-journey.

    pre-fix tightened leg: "1 passed in 49.92s" (limitation, stated)

VERIFICATION (post-fix tree, e839fa1):

    $ python3 -m pytest -q tests/test_hub_scroll.py   (W17g2-green-tightened.log)
    4 passed in 49.23s

    $ probe arg "prefix" (W17g2-red-prefix_probe.log)
    rc=1
    GWSCROLL-PREFIX btn_y=5277.0 view_h=720.0
    GWSCROLL-FAIL prefix shape hero row below the viewport (y=5277.0 > h=720.0)

    $ python3 -m pytest -q
    217 passed in 97.17s (0:01:37)

    $ python3 tools/check_hygiene.py
    check_hygiene: 0 hit(s)

    $ sha256sum tests/fixtures/*
    eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912  mission_gatefall_normal.jsonl
    5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628  mission_gatefall_hard.jsonl

Commit e839fa1 (amended 918f45b) touches ONLY godot/scripts/hub.gd,
tests/test_hub_scroll.py, LEDGER.md (git show --stat: 3 files). Evidence
+ logs stay untracked on disk.

VERIFY_EXIT=0

---

## W17g ROUND 3 (served equip click — E9 class one layer deeper, 2026-10-27)

Served status: SCROLL FIX VERIFIED (browser wheel reaches DECK hero rows,
gw-deck3.png — pump kept). New served failure: item-row + hero-slot clicks
left equipped {} / bank 151 with the console ERROR "Object ... was freed or
unreferenced while a signal is being emitted" x2 (pck 244392).

SITE (survey VERIFIED): godot/scripts/gear_panel_ui.gd _clear() was the
ONLY raw free() in a hub-UI rebuild path (war_table/ascension/hub carry
none; main.gd _routed.free is the scene switch, out of scope; bank_list +
defense_panel already ship the E9 idiom from W17c/W17e). Chain: slot
Button.pressed -> _on_slot -> equip_selected -> GameState.equip ->
mutated.emit -> refresh -> _rebuild_heroes -> _clear -> child.free() ON
THE EMITTING BUTTON — engine error aborts the emit chain mid-refresh.

FIX: _clear = detach NOW + queue_free, the shipped idiom verbatim.
Behavior otherwise unchanged.

NEW TEST LEG (tests/test_hub_scroll.py arg "click", in-suite): served
input path end-to-end — get_tree().root.size = (1280,720) (VERIFIED this
round: GUI picking works in WINDOW bounds — a click at served coords
outside the unsized 64x64 -s window never reaches a control) + hover one
frame BEFORE the press (W17e idiom). Seeds deck + 150-row bank through
the shipped mutators, opens gear via handle_press, CLICKS Row_5's center,
scrolls to the limit, CLICKS Slot_warden_weapon's center, asserts the
F2-11 contract (bank -1 by the picked row, hero weapon = oaken_cleaver,
uid 5 leaves the bank) AND stderr-EMPTY (W4 ruling — the tooth).

    RED (pre-fix tree, W17g3-red-click_stderr.log):
    == stderr:
    ERROR: Object '<Object#...>' was freed or unreferenced while a signal
    is being emitted from it. ... use queue_free() ...
       at: ~Object (core/object/object.cpp:2324)
       GDScript backtrace: [0] _clear (gear_panel_ui.gd:159)
       [1] _rebuild_heroes [2] refresh [3] equip (game_state.gd:130)
       [4] equip_selected [5] _on_slot [6] _press [7] _process
    (headless still leaves the sim writes landed — the data abort is the
    served ordering; the ERROR-on-stderr is the deterministic signal)

    GREEN (fixed tree): stderr 0 bytes;
    GWEQUIP-PRE bank=150 uid=5
    GWEQUIP-POST bank=149 eq_base=oaken_cleaver uid5_gone=true
    GWEQUIP-OK

VERIFICATION (commit 47287d3 — touches gear_panel_ui.gd + tests + LEDGER
only, git show --stat: 3 files):

    $ python3 -m pytest -q            218 passed in 149.30s
    $ python3 -m pytest -q tests/test_hub_scroll.py   5 passed in 101.52s
    $ python3 tools/check_hygiene.py  check_hygiene: 0 hit(s)
    $ sha256sum tests/fixtures/*
    eafe3932...  mission_gatefall_normal.jsonl (byte-unchanged)
    5e37c4b0...  mission_gatefall_hard.jsonl  (byte-unchanged)

Commit e839fa1 (round 2) stands untouched on top of 0afe00c; 47287d3 is
the round-3 commit (not pushed). Evidence + logs stay untracked on disk.

VERIFY_EXIT=0

---

## W17g ROUND 4 (equipped SAVE round-trip P1 — C6 gains equipped_json, 2026-10-27)

Served status: round-3 equip click VERIFIED in browser (equipped filled,
bank 151->150, gw-equipped.png). New served P1 (pck 244408): after equip
(ack 3, 6s flush, reload) bank persisted 150 but equipped came back {} —
game_state persisted every C6 key EXCEPT equipped (its own readings note:
"C6 carries no key for it"); the equip removes the row from the bank
(PERSISTED) -> the item existed in NEITHER bank nor equipped after reload:
equip+reload DESTROYED gear (P1 player-item loss).

FIX (orchestrator ruling: C6 gains the key):
- game_state.gd: to_save += "equipped_json": JSON.stringify(equipped);
  from_save += equipped = json_dict(d.get("equipped_json","{}")) — old
  saves miss the key -> {} (I5 back-compat, the same default door every
  *_json rides; NO schema bump: SAVE_SCHEMA=1, a bump fails from_save's
  version guard and WIPES every real player save to the starter seed).
  GameState.equip stays the single mutation point (F2-11 untouched).
- save_store.gd: [meta2].equipped_json carried in write() AND load_save()
  (default "{}"). NOTE: the round-4 brief's file list said game_state +
  tests + LEDGER, but GWSaveStore.write only persists keys it knows —
  the P1 is NOT fixable inside game_state.gd alone; the brief's own
  "read save_store.gd + the schema key first and follow the existing
  convention" names the second door. save_store.gd is in the commit for
  that reason (flagged to the orchestrator).
- tests/test_persistence.py: C6_PAIRS pin extended + header cites the
  ruling (the pin IS the contract; it changed BY ruling, not drift).
- sim/ UNTOUCHED: save_probe's legs iterate its own expected keys (an
  extra file key is unchecked there) — untouched green; fixture shas
  byte-identical.

EQUIVALENCE DOOR (VERIFIED): Godot JSON.parse returns every number as
float — raw == of in-memory int map vs loaded map is the named artifact
(MEMEQ=false in the spike); semantic parse-vs-parse (save_probe's own
door) is the contract: EQUIPPED_EQ=true FRESHEQ=true.

NEW GATE tests/test_gear_persist.py (4 legs, shipped graph — the C13
commit listener makes mutated -> GWSaveStore.write the SERVED write):
- round-trip GREEN: equip A then B over it (F2-11 replace), fresh-state
  load: equipped equals pre-save (parse-vs-parse), weapon = replacing
  base_id emberbrand, bank size matches AND returned row A present
  EXACTLY ONCE (no double-add), ack > 0, stderr EMPTY.
- back-compat GREEN (arg oldsave): ConfigFile with the PRE-ROUND-4 key
  list (no equipped_json at all) boots: equipped {}, bank/deck/gold OK.
- PLANTED-RED PERMANENT (arg stripped): save re-written without the
  payload -> survival predicate RED (rc1).
- source gate: both doors pinned by literal grep (blank_code would blank
  the contract's own string literals — raw source used; planted removal
  detectable).
CLICK LEG EXTENDED (test_hub_scroll.py): after the browser click-equip,
the save round-trip must survive; python asserts survived=true AND
fresh_base=oaken_cleaver.

TEETH (pre-round-4 code, transcripts on disk):
  W17g4-red-click_save.log: GWEQUIP-SAVE survived=false fresh_base=?
    + GWSCROLL-FAIL ... rc=1 (stderr CLEAN — data-loss, not E9)
  W17g4-red-persist_roundtrip.log: GWSAVE-EQUIP eq_ok=false base=none
    file=<missing> rc=1

VERIFICATION (commit cbfe6ff — 6 files: game_state.gd, save_store.gd,
test_gear_persist.py, test_hub_scroll.py, test_persistence.py, LEDGER.md;
git show --stat above):

    $ python3 -m pytest -q           222 passed in 151.92s
    $ python3 -m pytest -q tests/test_gear_persist.py   4 passed
    $ python3 -m pytest -q tests/test_hub_scroll.py     5 passed
    $ python3 tools/check_hygiene.py check_hygiene: 0 hit(s)
    $ sha256sum tests/fixtures/*
    eafe3932... / 5e37c4b0... (byte-unchanged — sim untouched)

Not pushed. Evidence + logs stay untracked on disk.

VERIFY_EXIT=0

## ORCHESTRATOR SERVED VERIFICATION — round 4 (2026-10-27 06:20Z, closes the card)
pck 244584 (?v=round4, cache:reload-busted), Playwright synthetic mouse, bank 150 save:
- pick weapon row 1 (volley_crossbow) -> hover+wheel to bottom -> ONE click at (72,620):
  equipped {warden.weapon=volley_crossbow}, bank 150->149, ack 1, console: no E9, no errors.
- patient 6s flush -> FULL reload (?v=round4b): bank_persisted 149,
  equipped_persisted {warden.weapon=volley_crossbow} — EQUIPPED GEAR SURVIVES RELOAD (round-4
  equipped_json key served-VERIFIED; the item-void P1 is dead).
- post-reload gear panel: volley_crossbow absent from the bank WEAPON section (frame
  gw-persisted-deck.png; list now starts storm_sling) — row moved hero-side, not destroyed.
- suite re-run by orchestrator: 222 passed; check_hygiene: 0 hit(s); export clean.
VERIFIED served: scroll (DECK reachable), equip-by-click, no mid-emit free (E9 class), gear
persistence across reload. W17g DoD met.
VERIFY_EXIT=0
