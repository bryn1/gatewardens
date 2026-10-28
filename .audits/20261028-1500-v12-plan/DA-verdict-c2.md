# DA verdict c2 — Gatewardens v1.2 plan (MC 11607, gate c2)

`# JUDGED: n/a (no hash cmd in brief)` — per the gate brief.

Subject: `.audits/20261028-1500-v12-plan/V12-PLAN.md` at `dfb7ddc` (DA-fix c1 revision).
Scope view: `git diff a20ae69..dfb7ddc` — touches ONLY V12-PLAN.md (+94/−20) and the trail copy
of my c1 verdict (+169). **F6 camera numbers, the measurement table, the recommended rig and the
W1–W4 wave structure are UNCHANGED in the diff — every F6 number was judged at c1 (all MATCHED my
independent re-derivation incl. the live kit re-runs) and is not re-derived here.** Repo
READ-ONLY this run; every re-check below is a fresh read of the shipped sources this session.

## c1 finding → fix landing → re-check

| c1 finding | where the fix landed (dfb7ddc) | my re-check (fresh measurement) | result |
|---|---|---|---|
| **P2-1** F2 guard mandate wrong on mechanism + W2 file-list contradiction | F2 "Today" + "Files" + Tests row; WAVES W2 note — mandate DELETED, ban-regex truth stated, `tests/test_hub.py` DELIBERATELY ABSENT with reason, run-only leg ("re-run the UNEDITED test_hub.py green") + a NEW-test source-truth grep | `tests/test_hub.py:60-61` — HUB_LAYER is EXACTLY the 8 scene-script files, game_state.gd NOT a member ✓; `:329-336` regex is `bank\.append\(|bank_add\(` + `mutated\.emit\(` over those 8 — no named list exists ✓; `state.sell_bank(` matches no pattern ✓. W2 note now even names the honest residual (bare `bank = []` trips nothing → the NEW test asserts the sanctioned clear) — STRONGER than my fix-line required | **FIXED — verified** |
| **P3-1** W3 fallback could silently break LOCKED pin #10 | F4 LOC-watch row + WAVES W3 note: split "adds the sibling to GOVERNED_LITERALS in-commit (pin #10)" + acceptance carries a grep green-leg (sibling present in the set) | `tools/check_hygiene.py:78-83` — defense_panel.gd IS a member (tuple closes at :83) ✓; mission.gd and its siblings (mission_world/mission_relics/mission_heroes) are NOT — grep "mission" over check_hygiene.py: comment hits only, no set entry ✓ (the W16-contrast claim is TRUE); application site: `if rel(path) in GOVERNED_LITERALS` at **:227** exactly as the plan cites, so an unregistered sibling genuinely drops I2 governance ✓ | **FIXED — verified, with a green-test leg** |
| **P3-2** F3 tests-only card had no planted-red path | New F3 "Planted-red leg" paragraph: two scratch-copy mutations in /tmp (repo never touched), each named to the leg it must RED | (a) `mission_relics.gd:24-25` — the taken-guard `if int(obj.relic_uid) != 0 or relic_owner(m, relic_uid) != 0: return {"why":"taken"}` exists exactly; dropping it in a scratch copy makes `assign` ok on a taken relic → the refused_taken leg must RED ✓. (b) sell-safety IS the removal: `defense_placer.gd:145-154` — on `obj.sell().ok` the record is freed and `m.defense_list.remove_at(i)`; `relic_owner` (and `live_count`) iterate `m.defense_list`, so a scratch mutation that leaves the sold row in the list keeps the relic reading owned → the new stale-uid/sell-return legs must RED ✓. Both legs mechanically sound over the real code | **FIXED — verified both legs bite** |
| **P4-a** off-by-one LOC quotes | mission.gd row "400/400" + gate-metric definition stated; main 193→~218; game_state 365→~386; gear_panel_ui 170→~186; defense_panel 373 with the wc-vs-gate-metric explanation; W3 row 373→~398, fallback trigger ">400" | my c1 gate-metric measurements were 400/193/365/170/373 — every corrected number matches | **FIXED** |
| **P4-b** "~2.5×" unreproducible | DA-gate note: shorthand RETIRED, restated with the measured px reproduction (median ~1 px, max 21–27 convention-dependent, both sides' numbers quoted) + the correct conclusion (neither gate says anything numerical about the other) | matches my c1 replication (median 1.02 / max 27.3) and my phenomenon-vs-factor ruling | **FIXED** |
| **P4-c** F1 CanvasLayer teardown unspecified | F1 boundary row (4): banner CanvasLayer mounts UNDER the routed mission subtree (not in mission.tscn → no pin #1 hit), `_mount`'s free tears it down, open_hub hides as belt | consistent with `main.gd:118-130` _mount (c1 read): freeing `_routed` frees descendants; stale-into-hub impossible under the belt — mechanically sound | **FIXED** |
| **P4-d** stale-literal "false-green" phrasing | F6 owner-decision row rewritten: RED-LOUD at `:403`, failure mode loud not silent | verified at c1 (`assert planted != read_text(...)` no-op-RED) | **FIXED** |
| **P4-e** stale ARCHITECTURE sim_harness row | doc-sweep carry-row added to the fixtures constraint row | matches c1 verification (shipped runner = sim_headless) | **FIXED** |

## New-claim spot-verification (producer's c2 additions)

All three new source claims measured TRUE this session: (1) ban-regex + 8-file HUB_LAYER set,
game_state outside it; (2) defense_panel.gd governed at `check_hygiene.py:83`, mission.gd siblings
never governed, gate application at `:227` set-membership-only; (3) F3 scratch legs land on real
mechanisms (`:24` taken-guard; `defense_list.remove_at` as the sell-safety, relic_owner/live_count
as the observers). No new defect introduced by the revision — the diff adds no fresh numeric claim
I cannot re-check, and re-checks the ones it does.

**Self-correction (mine, not the plan's):** an interim pass of mine mis-cited `relic_owner` as
":63-67" and I nearly filed a P4 citation-drift row; fresh grep settles it — `relic_owner` def is
at **:61** (span :61-65) and `live_count` at **:71** (span :71-76): every F3-paragraph line cite in
the plan (`:24`, `:61-65`, `:71-76`) is EXACT as measured. No P4-f; the paragraph's cites stand.

## Disposition

Every c1 gate row is closed with my own measurement behind it; the two cards the c1 verdict blocked
(F2's guard leg, F4's fallback leg) are now implementable as written, and F3 has a sanctioned,
mechanically-sound planted-red path. Wave structure, file-disjointness (with the test_hub.py
absence now REASONED rather than contradictory), owner-decision framing (F6 re-pin ONCE, gated),
and the measured camera recommendation stand exactly as audited at c1. The plan can spawn W1.

# VERDICT: SHIP
