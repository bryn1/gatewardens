# A9 FULL browser journey — FINAL (2026-10-27, served W17f build, orchestrator Playwright)

Server: server/server.py :8124 serving static/ pck W17f export (243640 B). All input = synthetic
MouseEvents/KeyboardEvents on the canvas (browser_run_code_unsafe forbidden); state via GW_STATE().

## Run j3 (existing save, bank 152) — VICTORY
- Atomic start+loop evaluate (golden-emulated inputs): hub War Table start click -> mission;
  F2 deadeye hot-swap; HELD MouseLeft+MouseRight (primary+secondary, the golden line-12 lever);
  Digit2 held (skill); KeyA/KeyW nudges; economy loop: class-button place (exact 100 spend),
  row-select + Upgrade (exact step costs), to 6 towers, T3 rotation.
- Waves 4-5 cleared FULL core (the W17f lane round-robin + both-buttons fix), wave 10/11 boss
  (Warden Breaker), outcome=win, core 500/1000, t=336-343s. Screenshot gw-victory.png
  ("Wave 11/11 ... VICTORY", boss bar 2050/3500 = boss_neutralized pin, loot toast, 6 rows).
- Run j4 REPLAY on a WIPED save (indexedDB /userfs deleted): identical recipe, outcome=win again
  (t=336, core 500) — reproducible, not a fluke.

## Hub legs (clicks, this build)
- Reload -> hub: bank 152 + materials (ember_core/iron_bar/torn_hide x1) PERSIST from victory commit.
- Ascension station: +1 click power_strike -> asc 27->26 live; RELOAD -> 26 + bank 152 persist
  (save-mutation-by-click -> reload-persist VERIFIED).
- All station tabs render: War Table/Gear/Blacksmith/Tinkerer/Dummies/Ascension.
- Gear panel: bank rows visible + selectable; item-row click = pick (selected path).
- Console: ZERO errors whole journey (uid warnings were the pre-reexport pck; fresh pck strings:
  0 hits of the stale uid pair).

## Journey-surfaced limitations (NOT fixed; release-notes rows)
1. NO in-game return to hub after a mission (open_hub is boot-only; page reload is the only
   route). Mission-end save still commits at _end_mission — nothing is lost.
2. Gear panel overflow: ONE normal win banks ~150 items (golden loot_events:148); no scroll
   container existed => hero equip-slot buttons render ~3600px below the 720px viewport and are
   UNCLICKABLE after any win. "equip" is a named A9 leg => W17g (card 11408) fans the scroll fix.
3. Reload within ~1s of the win banner CAN lose the mission-end write (IndexedDB flush races
   navigation; j4 immediate-reload read bank 0, j3 patient reload persisted 152). Risk row.
4. Relic assign: RELIC-slot items DO drop into the bank (medallion_of_the_gate rows seen
   served post-win, gear panel RELIC section); SimInventory refuses slot=relic gear-panel
   equip (data-declared contract), and the mission-side Assign/Unassign positive path was
   NOT click-verified in v1 — honest "not fully verified" release-notes line.
5. Full-HP Sell refunds 0 (wiki-pinned formula, BY DESIGN) — note for player expectation.
6. Greybox cosmetics unchanged: row label overlap in tall lists, hub center label, meta row.

## POST-REPORT UPDATE (same day, W17g rounds)
- (2) SCROLL FIXED + SERVED-VERIFIED: W17g _process pump (e839fa1); hover+wheel reaches DECK
  hero rows at bank 151 (gw-hover-wheel.png / gw-deck3.png). Harness lesson: Godot-web routes
  a synthetic wheel at the LAST mousemove position — dispatch mousemove before wheel.
- NEW P1 located (round-3 fanned): the E9 "Object freed while signal emitted" console print
  the journey logged earlier (unlocated at the time) = hub gear panel _clear()/rebuild
  free()ing Buttons during their own pressed-signal frame => equip click aborts served
  (equipped {}, bank 151, ack 0->1 partial write, console ERROR x2). Fix = the shipped W17e
  E9 pattern (detach + queue_free) across hub UI rebuild paths + a push_input
  click->equip engine leg with stderr-empty assert.
- ROUND-3 VERIFIED SERVED (pck 244408): pick weapon row -> scroll -> hero-slot click =>
  equipped {warden.weapon=oaken_cleaver}, bank 151->150, NO E9 error (screenshot
  gw-equipped.png). A9 equip leg completes IN-PAGE by pure mouse. Harness lesson: synthetic
  clicks on a scrolled ScrollContainer need per-scroll-state calibration (screenshot the
  state, then click; blind y carried between states misses).
- ROUND-4 P1 (fanned): SERVED reload after equip: bank persists (150) but equipped returns {}
  — game_state.gd documents "equipped NOT persisted — C6 carries no key". Consequence: equip
  removes the row from the PERSISTED bank while equipped never saves => item exists nowhere
  after reload = ITEM VOID (P1 data-loss). Fix: C6 equipped key + save/load + back-compat
  (missing -> {}), round-trip test + planted-red. Orchestrator note: "C6 carries no key" is a
  W-era contract decision, never surfaced to the owner as a product limitation; A7 ("gear
  bank ... survives reload") intent + zero item-loss make the fix in-scope for v1.
