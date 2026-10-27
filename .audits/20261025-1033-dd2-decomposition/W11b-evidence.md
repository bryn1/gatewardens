# W11b evidence — defense_placer P2 boundary fix (MC 11274.1.20 / card 11330)

**Commit:** `3a8c8b360e9d1ed354e8adb539c77c83c23233a8` (author `code (11330) <code@agent-town.local>`, repo gatewardens main; touches ONLY godot/scripts/defense_placer.gd + tests/test_defense_boundaries.py)

**Outcome:** upgrade()/repair() on an unknown uid now return the shipped sell() not-found refusal `{"ok": false, "why": "uid"}` with NO crash and NO state change; known-good upgrade path verified still working.

## The fix (one mechanism, per the finding)

`_rec(uid)` ALREADY returns the refusal `{"ok": false, "why": "uid"}` (the sell() not-found shape); the bug was the guard: `rec.is_empty()` can never fire on a NON-empty sentinel, so the code fell through and `rec["obj"]` was a SCRIPT ERROR under `-s` (LEDGER "Findings open (pre-GA)": "sell() pattern is the correct shape"). Fix = guard the sentinel structurally (`if not rec.has("obj"): return rec`) in BOTH upgrade() and repair() — no new sentinel mechanism, sell() untouched.

## Pinned-shape quotes (R-list)

- **R1 PINNED Modules row** (docs/ARCHITECTURE.md:156): `| scripts/defense_placer.gd | build-phase placement: ghost, validity (range/overlap), confirm/cancel, cost via SimEconomy | validity from injected tables; calls mission.place_defense |` — the row pins the INTERFACE, not a per-method refusal value, so the governing refusal value is the shipped sell() one (R2).
- **R2 shipped sell() not-found return** (defense_placer.gd, sold-verified this session): `return {"ok": false, "why": "uid"}` — THE pinned refusal shape upgrade/repair now return.
- **R3 sold-then-used leg IS allowed by the record shape:** sell() REMOVES the record from m.defense_list (shipped: `m.defense_list.remove_at(i)`), so the sold uid rides the same not-found path. Declared reading; asserted in the probe (BOUND-UPG-SOLD / BOUND-REP-SOLD refused, green unchanged).
- **R4 found records are `{uid, obj, tick}`** (mission.gd:322 `defense_list.append({"uid": ..., "obj": ..., "tick": ...})`) — no `"ok"` key; the refusal has one. `rec.has("obj")` guards the routing without inventing a second sentinel.
- **R5 probe placement reading:** W11b's file constraint is defense_placer.gd + tests/ + evidence, so the godot/sim/ probe home cannot take a new file; the boundary probe is generated into pytest tmp_path from tests/test_defense_boundaries.py and run via `run_probe_script` with an absolute `-s` path (preload resolves res:// inside `--path godot/` — verified). test_probe_home_stays_outside_shipped_tree books this.
- **R6 E3/E5 honored:** failure paths early-return (E3: quit() does not abort the running frame); `_ready()`/`setup(...)` driven directly (E5). The `-s` verdict is EMPTY stderr (W4 ruling / E3-E5 facts) — that assert is the crash detector.

## RED-before-FIX (ran the new legs against the UNFIXED placer first)

Standalone probe vs unfixed placer (rc=1, non-empty stderr):

```
BOUND-PLACE ok=1 uid=1 green=200
BOUND-UPG-UNKNOWN ok=1 why= green=200 tier=0
BOUND FAIL UPG-UNKNOWN {  } green=200 tier=0 count=1
--- stderr ---
SCRIPT ERROR: Invalid access to property or key 'obj' on a base object of type 'Dictionary'.
          at: upgrade (res://scripts/defense_placer.gd:128)
          GDScript backtrace (most recent call first):
              [0] upgrade (res://scripts/defense_placer.gd:128)
              [1] _init (.../w11b_probe.gd:55)
```

Same legs through the real pytest machinery (fix reverted via git, ran, re-applied):

```
>       assert proc.returncode == 0, ...
E       AssertionError: probe rc=1
E         OUT: ... BOUND FAIL UPG-UNKNOWN {  } green=200 tier=0 count=1
E         ERR:SCRIPT ERROR: Invalid access to property or key 'obj' on a base object of type 'Dictionary'.
E                   at: upgrade (res://scripts/defense_placer.gd:128)
FAILED tests/test_defense_boundaries.py::test_placer_boundaries_engine_leg - ...
FAILED tests/test_defense_boundaries.py::test_sentinel_guard_source_truth_with_planted_red
2 failed, 1 passed in 0.78s
```

(the source-truth gate also went RED against the unfixed file — and the shipped planted-red leg proves it can reject the restored OLD `rec.is_empty()` guard on the fixed file.)

## GREEN-after-FIX

Probe rows (rc=0, EMPTY stderr = 0 bytes):

```
BOUND-PLACE ok=1 uid=1 green=200
BOUND-UPG-UNKNOWN ok=0 why=uid green=200 tier=0
BOUND-REP-UNKNOWN ok=0 why=uid green=200 tier=0
BOUND-UPG-OK ok=1 cost=50 green=150 tier=1
BOUND-SELL ok=1 refund=0 green=150
BOUND-UPG-SOLD ok=0 why=uid green=150
BOUND-REP-SOLD ok=0 why=uid green=150
BOUND-OK
```

Numbers re-derived from shipped data (not literals): start_green 300 (gatefall.json) − base_cost 100 (towers.json) = 200; upgrade T1→T2 = 100×ratios[0]=0.5 → cost 50 (economy.json, C3 ladder), green 150; full-hp sell refund = total_spent×0.75×missing(0) = 0 (R1). Unknown-uid refusals left green, the live tower's tier, and defense_list size byte-identical.

## Gates run (this session, repo root)

- `python3 -m pytest tests/ -q` → **175 passed** (172 prior + 3 new), `PYTEST_RC=0`
- `python3 tools/check_hygiene.py` → **`check_hygiene: 0 hit(s)`**, `HYGIENE_RC=0` (notes only: pre-existing soft-ceiling/sanctioned-draw informational lines)
- File hygiene: defense_placer.gd 189 L (≤250), test_defense_boundaries.py 291 L (tests ≤600)

VERIFY_EXIT=0
