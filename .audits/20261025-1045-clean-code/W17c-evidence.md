# W17c evidence — tower SELECT has no player path (card 11387, MC 11274.1.30)

Commit: `13516cb044892c0fa40d26772230126459a6c8e9` (author `frontend (11387)`, base = W17b `908c219`)
All transcripts executed this session on the committed tree.

## 1. Mechanism quote — the harness had powers the player did not

The finding, as grepped on the base tree:

```
$ grep -rn select_defense godot/
godot/scripts/defense_panel.gd:96:   func select_defense(uid: int) -> void:   # definition
godot/sim/mission_smoke.gd:128:      panel.select_defense(int(m.defense_list[0]["uid"]))
godot/sim/mission_smoke_w8.gd:137:   panel.select_defense(int(tres["uid"]))
```

`selected_uid` (defense_panel.gd:38, 0 = none) gates Upgrade/Repair/Sell —
nothing in the game ever set it. In a real session the three action buttons
were permanently disabled: placement worked (W17b) but a placed tower could
never be upgraded/repaired/sold. Same false-green class as W17b: the smoke
harness called the panel method directly, so every prior leg passed while the
player path did not exist.

## 2. Fix (greybox-consistent, no camera picking)

`defense_panel.gd`:
- setup() adds `Head_defenses` ("DEFENSES") + `Rows_defenses` VBox between the
  Sell button and the relic section; `refresh()` ends with
  `_rebuild_defense_rows()` — the shipped clear+rebuild fill shape, over the
  EXISTING defense-list API (`m.defense_list`, the same list `_selected_obj`
  and the placer already read; no new mechanism).
- Each placed defense renders one Button row:
  `"uid %d %s T%d hp %d/%d"` (data-only text, I2 clean) named `Row_<uid>`;
  the selected row is visibly marked with the `»` text prefix and is rebuilt
  on every refresh (place/upgrade/sell/row-click all pass through refresh()).
- A row press calls the SHIPPED `select_defense(uid)` — the harness entry
  point becomes the player's. Upgrade/Repair/Sell untouched (they act on
  `selected_uid`, gates intact).
- Reuse reading declared: rows are plain greybox Buttons, NOT `item_row` —
  that widget is the pinned ITEM-pool renderer (F2-12; show_item paints
  base_id/rarity/mods — a placed defense is not an inventory item).

## 3. Geometry + refresh notes (engine read-back, served 1280x720)

Rows sit in the W17b right column and stay disjoint/on-screen:
`W17CGEOM row1=904.0,276.0,221.0,31.0` (x 904..1125 < 1280; y 276 between Sell
(ends 245) and the relic head; every HUD rect ends x≤900 or starts y≥540). The
W17b FILTER/GEOMETRY/PICK legs run unchanged in the same probe and stay green.

Refresh contract (declared greybox reading): rows rebuild on every panel
ACTION (place/upgrade/sell/select) — matching the shipped Green-label behavior
(also refresh-on-action, no per-frame polling; bridge input stays relay-only,
the panel still never polls Input). Wave-time hp drift repaints at the next
panel action; W17b's row-hiding is prevented because rebuild is inside the
single refresh() path every action takes.

## 4. Engine legs (push_input = the Viewport's own browser-input pipeline)

Machine rows, normal run (rc=0, EMPTY stderr):

```
GWMICE-PICK clicked=8 class_clicks=3 placed=3
GWMICE-SEL rows=3 list=3 want_uid=1        <- class click -> ROW appeared
GWMICE-UPL cost=50 green=70 tier=0         <- ROW click: selected_uid=1,
                                             "»" mark + URS gates flipped enabled
GWMICE-UPL2 tier=1 green_drop=50           <- Upgrade button: tier+1, EXACT cost
GWMICE-SEL2 selected=0 rows=2 list=2       <- Sell: selection cleared + row gone
GWMICE-OK
```

The exact-drop check mirrors the shipped C3 formula FROM DATA in the test
(`base_cost 100 x upgrade_ratios[0] 0.5 = 50`, economy.json read at test time
— no test-side cost copy). Before this card the gates only ever flipped for
the harness; these legs prove the PLAYER drives them.

## 5. Engine finding E9 + the shared-loop fix (VERIFIED red->green)

The first rebuild used the shipped `child.free()` idiom and hit, on a row
click (refresh runs inside the row's own `pressed` emit):

```
ERROR: Object is locked and can't be freed.   at: callp (core/object/object.cpp:787)
SCRIPT ERROR: Attempted to free a locked object (calling or emitting).
```

Fix: detach NOW (`remove_child`, no flicker) + `queue_free` (unwinds after the
emit) — stderr EMPTY after (scratch transcript: same flow, 0 stderr bytes).
The SAME latent bug lived in the SHARED `bank_list.fill` (bank_list.gd:17 —
gear panel, blacksmith, tinkerer, relic picker): reproduced live (mid-emit
refill through a real `picked.emit` printed the lock ERROR on the shared
line), fixed ONCE in the shared loop per the fix-every-caller doctrine — the
keyboard-path harnesses that drove picks by direct call never emitted
mid-emit, which is why 200 green tests sat on it. In-suite now: shared-fill
ENGINE leg (mid-emit refill, EMPTY stderr, `WFILL rows=1 filled=1`) +
emit-safe source gate + planted-red in tests/test_hub.py.

## 6. Planted-red transcripts

Engine tier, mission probe (`no_row_refresh` — rows surface detached, the
W17c regression shape):

```
GWMICE-PICK clicked=8 class_clicks=3 placed=3
GWMICE-FAIL defense rows surface missing (no player select path)     rc=1
```

(declared: the planted red's stderr holds only exit-time leak warnings from
the detached plant subtree itself — an artifact of the plant; the NORMAL run
is asserted EMPTY-stderr by the gate.)

Also shipped red and asserted in-suite: `queue_free()` -> `free()` planted in
bank_list.gd trips the emit-safe gate; the W17b `stop_root` engine red still
holds (`GWMICE-FAIL filter ... mf=0` + `pick ... receiver=0`).
Live red-before/green-after for E9: §5 transcripts (pre-fix ERROR, post-fix
clean) — a gate that never failed is not a gate; this one failed for real.

## 7. Verification (committed tree, this session)

- `python3 -m pytest tests/ -q` -> **204 passed** (200 prior + 4 new legs),
  exit 0
- `python3 tools/check_hygiene.py` -> **0 hits** (defense_panel.gd 289 ≤ 400,
  test_hub.py 507 ≤ 600, test_mission_clicks.py 600 ≤ 600)
- one commit `13516cb044892c0fa40d26772230126459a6c8e9`, author
  `frontend (11387) <frontend@agent-town.local>`; LEDGER W17c row +
  journey-row correction + engine fact E9 in the same commit
- no data/balance touched; PINNED TABLE WINS x16 untouched (golden suite green)
- known limitation declared: row hp repaints on panel actions (greybox, §3);
  served re-journey owed by the orchestrator (LEDGER journey row updated).

VERIFY_EXIT=0
