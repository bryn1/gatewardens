# W17f — lane round-robin placement order (MC 11274.1.33 / card 11403)

Commit: `18273410b35a0109d594c39fefca2bc00c9ac297` (author `frontend (11403) <frontend@agent-town.local>`, base 2685bed, NOT pushed per brief).
Files: `godot/scripts/defense_placer.gd` (fix), `tests/test_lane_order.py` (new), `LEDGER.md` (W17f row, same commit).

## Root cause

`_build_slots()` in defense_placer.gd built the placeable slot list in LANE-FILE BLOCK order: every lane_g1 waypoint (deduped, cores excluded), then lane_g2's, then lane_g3's (11 slots on gatefall: g1a–g1d, g2a–g2d, g3a–g3c). The panel class-button place route (defense_panel.place_selected → `placer.place(class, 1)` with no slot) falls to `first_free()`, which returns the FIRST free index of that list. Consequence: every consecutive UI-style place piled into lane_g1 until all 4 of its slots filled, then lane_g2, etc. The browser journey wave-4/5 wall: the player's towers all stood in one ground lane while the other lanes walked free (leaks the placed towers could never cover). Explicit-slot callers (fixture place-rows, mission_smoke_w8, panel row lifecycle) resolve positions by `slot_at(pos)` — order-independent — which is why only the first-free win-path was hit and why the goldens cannot move.

## Fix (single concern)

`_build_slots()` now collects per-ground-lane slot lists with the SAME content rules (ground-only, dedup-by-position, core exclusion), then emits them INTERLEAVED round-robin: g1a, g2a, g3a, g1b, g2b, g3b, g1c, g2c, g3c, g1d, g2d. Panel, keyboard map, place/upgrade/sell/repair, occupied/class/phase gating untouched. No new literals (literals used: 0/1 — structural per I2; hygiene proves it).

## TDD RED — test against the PRE-FIX tree

(tests/test_lane_order.py written first; ran `python3 -m pytest tests/test_lane_order.py -q` at base 2685bed; full transcript also in W17f-red-lane_order.log)

```
F.                                                                       [100%]
_______________________ test_first_free_round_robin_leg ________________________
E       AssertionError: probe rc=1
E         OUT:Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org
E
E         GWRR-PLACE n=1 lane=lane_g1 pos=(-40.0, 0.0, 0.0)
E         GWRR-PLACE n=2 lane=lane_g1 pos=(-28.0, 0.0, 4.0)
E         GWRR-PLACE n=3 lane=lane_g1 pos=(-14.0, 0.0, 6.0)
E         GWRR-PLACE n=4 lane=lane_g1 pos=(-6.0, 0.0, 3.0)
E         GWRR-FAIL first three places share a lane: ["lane_g1", "lane_g1", "lane_g1", "lane_g1"]
E
E         ERR:
1 failed, 1 passed in 1.38s
```

(The RED run shows the defect exactly: all four first-free places land g1a,g1b,g1c,g1d. The `1 passed` line is the planted-red leg, which asserts rc==1 and passed for the pre-fix code too — the pre-fix tree IS the planted shape. GREEN transcript below proves the leg discriminates.)

## GREEN — same test after the fix

```
..                                                                       [100%]
2 passed in 1.34s
```

Probe stdout (fixed order, GWRR-OK): `lanes=lane_g1|lane_g2|lane_g3|lane_g1` — first three first-free places land on THREE DIFFERENT ground lanes; the 4th lands in rotation on the empty g1 rank-1 slot; the probe itself refuses any repeat position (never an occupied slot) and any refused place (W17f-green-lane_order.log).

## Gates

### 1. Full suite (`python3 -m pytest tests/ -q`) — 213 passed (211 prior + 2 new)

```
213 passed in 47.64s
```
(W17f-full-suite-green.log — includes tests/test_sim_golden.py: both fixture replays rc 0, EMPTY stderr, replayed out-row streams BYTE-EQUAL to the committed rows, plus stability + tampered-red legs.)

### 2. Fixture replay BIT-IDENTICAL — shas before and after UNCHANGED

| fixture | before (base 2685bed) | after (this commit) |
|---|---|---|
| mission_gatefall_normal.jsonl | `eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912` | `eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912` |
| mission_gatefall_hard.jsonl | `5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628` | `5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628` |

(`git show 2685bed --stat` touches no fixture; the post-fix `sha256sum` runs are in W17f-fixture-shas.log; both fixture files are NOT in this commit — `git show --stat` above lists only the three files.)

### 3. Hygiene (`python3 tools/check_hygiene.py`) — 0 hits

```
check_hygiene: 0 hit(s)
```
(notes only — all pre-existing; defense_placer.gd now 198 lines < 250, test file 190 < 600; W17f-hygiene.log)

### 4. Permanent planted-red in the suite

`test_planted_red_blocked_order_goes_red` rebuilds the pre-fix lane-blocked order live onto the placer (arg `blocked_order`) and asserts the SAME leg goes RED (`GWRR-FAIL ... share a lane`) — the gate can never silently re-green.

## Limits / notes

- Not pushed (orchestrator pushes). Web export/static/ untouched; running server untouched.
- The panel's ghost path (`set_ghost`/`slot_at`) is position-keyed and unaffected; the browser re-journey of the served build is the orchestrator's owed leg (as with W17e).

VERIFY_EXIT=0
