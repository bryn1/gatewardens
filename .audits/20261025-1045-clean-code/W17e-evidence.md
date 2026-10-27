# W17e — panel action-button state STALE vs SIM (MC 11274.1.32 / card 11397)

Commit: `2685bed` — author `frontend (11397) <frontend@agent-town.local>`, files:
`godot/scripts/defense_panel.gd`, `tests/test_mission_stale.py` (new), `LEDGER.md`.
Sim, data, mission.gd, fixtures: ZERO hunks (byte-anchors hold — no `godot/sim/`,
`godot/data/`, `tests/fixtures/` path in the commit: `git show --stat 2685bed`).

## 1. ROOT CAUSE — quote, file:line (served HEAD 940ecc6)

`godot/scripts/defense_panel.gd@940ecc6:211-217` — the ONLY writer of the enabled
state lived inside `refresh()`:

> ```
> func refresh() -> void:
> 	info_label.text = "green %d / cap %d / defenses %d" % [...]
> 	for row: Dictionary in class_rows:
> 		var btn = class_buttons[String(row["class"])]
> 		btn.disabled = not SIM_ECONOMY.can_afford(int(m.green),
> 				int(row["cost"]))
> ```

`godot/scripts/defense_panel.gd@940ecc6:177-179` — the poll path NEVER re-gated:

> ```
> func poll(presses: Array) -> void:
> 	for code: Variant in presses:
> 		handle_press(String(code))
> ```

`godot/scripts/mission.gd@940ecc6:249` is the per-frame caller — `$DefensePanel.poll(presses)`.
`grep refresh` in mission.gd hits ONLY `MISSION_WORLD.refresh_cores` (:161,:265) — the
mission drives NO panel refresh per poll (the W17b per-frame refresher is the HUD's own
`hud.gd:77`, a different widget). VERDICT: `refresh()` ran ONLY on action-driven events
(select/place/upgrade/sell/relic), so BETWEEN actions the enabled flags froze at the last
refresh's verdict while `m.green` rose via kill awards (`mission.gd:360-362`,
per_kill_default 3) and wave awards (`phase_controller.gd:90-92`, per_wave 40). A disabled
Button silently swallows the browser's click — REPRO-B ("~100 Ballista clicks, green 148 ≥
cost 100, NOTHING placed, green never spent") is exactly this: headless replay showed
`class_disabled=true` frozen while affordable, the click doing nothing.

REPRO-A has the same staleness plus a second native loss mode, VERIFIED headless
(`W17e-native-churn-prefix.log`, panel@940ecc6): `refresh()` ended with an UNCONDITIONAL
`_rebuild_defense_rows()` (`:233`), so a row SELECT re-created every row Button — and a
freshly added Control is UNSIZED until the frame-end container sort:

> S6 Row_2 y=311.0 h=31.0
> S6 clicked row0 center y=291.5 -> selected=1
> S6N Row_1 y=276.0 h=31.0        <- rebuilt
> S6N Row_2 y=276.0 h=31.0        <- stacked, NOT laid out (pre-sort)
> S6 stale-coord 2nd-row click -> selected=1   <- the player's click hit nothing

Measured served layout (same probe): Sell y214-245 (the repro's y225 lands inside Sell ✓),
rows 276-307 / 311-342 / 346-377 — the repro's y344 was the 4px VBox SEPARATION gap
between Row_2 and Row_3, so their round-1 row click selected NOTHING, `sell_btn` stayed
at its last-refresh `disabled = obj == null` verdict = true, and the Sell click was
swallowed silently. "First sell after a selection does nothing; later ones work" =
stale-disabled sell + the lost row click; "refund never landed for the swallowed clicks"
matches (when the click lands, the refund DOES — sell row below).

## 2. Per-click green/defenses BEFORE / AFTER (headless, push_input, same build)

| step | click | BEFORE fix: green | defenses (list) | AFTER fix: green | defenses |
|---|---|---|---|---|---|
| f4 | Class_tower | 300→200 | 0→1 | 300→200 | 0→1 |
| f5 | Class_tower | 200→100 | 1→2 | 200→100 | 1→2 |
| f6 | Class_tower | 100→0 | 2→3 (button self-disables) | 100→0 | 2→3 |
| f6 | (green regains, NO action) | green:=150, btn STALE disabled | 3 | green:=150 (synced next poll) | 3 |
| f7 | Class_tower (affordable) | **150, 3→3 SWALLOWED** (`GWMICE-FAIL place starved while affordable`) | — | **150→50, 3→4 PLACED+SPENT** ✓ | 4 |
| f8 | Row_1 then Row_2 @ measured coords, same frame | selected **stays 1** (churn lost click 2) | 4 | **selected=2** ✓ | 4 |
| f9 | Sell, immediately next poll | one attempt sells the WRONG full-HP row, refund **0** | — | **refund=38 → green 50→88, list 4→3 (uids 1,3,4), selected=0, ONE attempt** ✓ | 3 |

Full transcripts: `W17e-prefix-red.log` (pre-fix RED), probe lines below (fixed).

## 3. Mechanism of the fix (defense_panel.gd ONLY — the smallest truthful mirror)

- `poll(presses)` now runs `sync()` BEFORE draining presses: enabled/disabled of ALL
  gated buttons (class rows, Upgrade/Repair/Sell, Assign pair) recomputed from the
  CURRENT sim state via the shipped `SIM_ECONOMY.can_afford` static (no cost math, I2)
  + the selected-marks (class `" *"`, defense-row `"» "` prefix) — cheap by contract,
  text touched only where a mark changed; rows are never freed on this path.
- poll then rebuilds rows only if `_rows_dirty()` (count/uids changed — a defense DIED
  since the last refresh still re-enters the rows through the same check).
- `refresh()` = info label + `sync()` + relic fill + the rebuild behind the SAME dirty
  check: a select/upgrade refresh no longer churns the row buttons into unsized controls
  (the REPRO-A loss mode is gone; the repro's missed gap click now still lands next try
  for the same reason the next-poll state is live).
- E9 rule kept: the rebuild that remains (real list changes) keeps detach-NOW +
  queue_free — never free a control mid-emit.
- Kept unchanged: click=place bindings, select_defense rows, bridge keys, relic picker,
  mission.gd, sim, data (mission.gd is 399 lines — untouched per the brief).

## 4. Tests (tests/test_mission_stale.py, engine tier, EMPTY stderr)

GREEN run rows: `GWSYNC-ARM green=150 class_disabled=true` → `GWSYNC-REGAIN placed=4
green=50` → `GWSYNC-SEL want=2 selected=2` → `GWSYNC-SELL2 refund=38 n=4->3 left=1,3,4,
selected=0` → `GWMICE-OK`, stderr empty.

### Planted-red 1 — sync removed (REPRO-B reintroduced): RED (rc=1)
`W17e-red-stale_buttons.log` (class button re-frozen every frame after the mission poll):
> GWSYNC-REGAIN placed=2 green=150 class_disabled=true
> GWMICE-FAIL place starved while affordable (placed=2 green=150)

### Planted-red 2 — dirty check removed (REPRO-A churn reintroduced): RED (rc=1)
`W17e-red-rows_churn.log` (rebuild right after a select):
> GWSYNC-REGAIN placed=4 green=50 class_disabled=true
> GWSYNC-SEL want=2 selected=1
> GWMICE-FAIL browser-style row click lost (selected=1)

### Source gate planted-red (dropped `sync()` from poll body): `_sync_violations` RED
(poll-body mutation `sync()`→`pass` → "poll() never calls sync()" + "rebuild is not
dirty-guarded"). Pre-fix, the engine legs are RED BY CONSTRUCTION (native transcripts
above + `GWMICE-FAIL place starved…` in `W17e-prefix-red.log`).

## 5. Gates

- `python3 -m pytest tests/ -q` → `211 passed in 46.68s`, FULL_RC=0
  (`W17e-full-suite-green.log`) = 206 prior (W17d-era) + 5 new (2 engine legs, one being
  the REGAIN+SELLS pair the brief names, 2 planted-red, 2 source-truth incl. its plant).
- `python3 tools/check_hygiene.py` → `check_hygiene: 0 hit(s)`, HYGIENE_RC=0
  (`W17e-hygiene.log`; defense_panel.gd 349 ≤ 400 hard).
- Byte anchors: no sim/ data/ fixtures/ file in the commit; the sim-golden + smoke
  suites run green inside the 211.
- Files: mission.gd untouched (399); defense_panel.gd 349 (hard 400 ✓, soft-250 note
  class like before); test_mission_stale.py 317 < 600 test ceiling (test_mission_clicks.py
  sits AT 599 — the new legs went to a companion file, the W16 split idiom; the push_input
  gate as a whole is extended, same probe boot + click pipeline).
- Repro coords sanity: served layout measured (Sell 214-245, Rows_defenses 276-377 at
  panel position 904,12), matching the orchestrator's synthetic-canvas coordinates.

git sha: 2685beddf21c92686379d038b74e596b8c902b00

VERIFY_EXIT=0
