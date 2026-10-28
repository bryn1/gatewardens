# DA verdict — Gatewardens v1.2 plan (MC 11607, gate c1)

`# JUDGED: n/a (no hash cmd in brief)` — per the gate brief.

Subject: `.audits/20261028-1500-v12-plan/V12-PLAN.md` (committed `a20ae69`, base tip `5304d87`).
DA run 2026-10-28, READ-ONLY on the repo; scratch `/tmp/v12da/` (python re-derivations, live kit
re-runs incl. a full scratch copy of `godot/` with the candidate rig swapped — the repo was not
touched). All numbers below are MY OWN command outputs this session, next to the plan's claims.

## 1. F6 math — independent re-derivation (the brief's mandated row)

Gate-A re-derived with the test's OWN functions (`_cam_from_tscn` regex, `_map_points` 28 points,
`_in_frustum` angular model, MARGIN 0.92, FOV 75 vertical, 1280×720), extracted from
`tests/test_hub_layout.py:331-384` and run standalone over the live `mission.tscn` row.
Kit rows are live runs of `/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64
--headless --path godot -s res://sim/v1_world_probe.gd` (shipped tree AND a scratch copy carrying
the candidate rig).

| # | plan claim | my measurement (this session) | match |
|---|---|---|---|
| 1 | shipped Gate-A worst **0.9096** at (34,0,30), 98.9% of budget | **0.9096** at (34.0, 0.0, 30.0) | MATCH |
| 2 | along-to-hero **70.451** | **70.451** | MATCH |
| 3 | baseline (0,58,46) worst **0.8741** ("95.0%") | **0.8741** (95.01% of 0.92) | MATCH |
| 4 | baseline→shipped zoom **1.0355×**; 1.0355×1.010=1.0458 | **1.0355×**; arithmetic ✓ | MATCH |
| 5 | pure zoom dolly-along-view max **+1.00%**, origin→**69.751** | bisection: dolly 0.70015 m → **+0.994%**, hero-along 69.751 | MATCH |
| 6 | pure zoom FOV-shrink max **+1.55%**, fov_min **74.15°** | fov_min **74.149**, worst(74.15)=0.9200 exactly at limit; px gain cot-ratio **+1.55%** | MATCH |
| 7 | D=64 re-aim pitch 48°: char **+10.2%**, Gate-A worst **0.718**, D 63.91, pitch 48.00° | **+10.24%**, **0.7179**, **63.909**, **48.00°** | MATCH |
| 8 | live kit shipped: `n=33 min_margin=113.6 worst=lane_g3:wp0 floor=60` → V1W-OK | reproduced **byte-equal**, rc=0 | MATCH |
| 9 | candidate D=64 Gate-B margin **121.9 px**, binding point unchanged lane_g3:wp0 | LIVE kit on scratch copy w/ candidate rig: **min_margin=121.8 worst=lane_g3:wp0** V1W-OK rc=0 | MATCH (0.1 px, plan rounds up; actual slightly WORSE and still ≥ shipped 113.6 and ≥ the plan's own ≥110 re-run leg) |
| 10 | shipped basis **non-orthonormal**, col1·col2 = **−0.112** | **−0.1116**; row norms 0.943 / 1.055 ≠ 1 | MATCH |
| 11 | engine-vs-model replication median **0.91 px**, max **21.3 px** on shipped rig | my own replication: median **1.02 px**, max **27.3 px** over the 33 live engine rows | PHENOMENON MATCH; exact px convention-dependent (see P4-b) |
| 12 | suite **222** | `pytest --collect-only -q` → **222 tests collected** | MATCH |

**Verdict on F6 numbers: the plan does not ship a wrong camera.** Every decision-relevant number
reproduces; both "noise" zoom bounds and the recommended rig pass my independent math AND a live
engine-kit re-run on the actual candidate transform.

## 2. Attack-surface rulings

**(a) Pin-#3 re-pin precedent — REAL, but read it exactly.** `git log -L 337,403:tests/test_hub_layout.py`:
the literal was CREATED once (865b668/W13) and moved exactly **ONCE** since (32b8f3a/V1 nudge), with
the LEDGER:82 row declaring the test edit ("DECLARED test edit: test_hub_layout planted-red fixture
string follows the new rig line"). FINDINGS §5 row 3's note is true. So the sanctioned path exists;
what the plan must NOT (and does not) do is presuppose it — W4 is owner-gated, correct. Extra fact
the plan understates in the safe direction: a stale planted literal **cannot false-green** —
`test_hub_layout.py:403` `assert planted != read_text(...)` goes RED LOUD if the replace no-ops
(plan's "stops firing / false-green class" phrasing is wrong in the plan's favour — the gate already
fails loudly; see P4-d).

**(b) The two-gates-disagree deferral — honest AND safe; named risk:** deferring the Gate-A model
fix would be UNSAFE if the shipped change relied on Gate-A's sloppiness for its margin (Gate-A
green at the engine's edge). It does not, and this is the reason to allow the deferral:
(1) the engine-truth gate (Gate B) gets **strictly better** (113.6→121.8 px, MY live kit run) —
the change cannot regress what the engine actually paints; (2) Gate-A worst falls to 0.7179 — the
angular model is nowhere near its limit post-change, so its inaccuracy is not load-bearing; (3)
decisively, the candidate transform is an **exact rotation** (rows orthonormal, col1·col2 = 0
exactly) — post-change transpose = inverse and **both gates read the same geometry**: the rig change
REMOVES the model ambiguity instead of exploiting it, and the plan declares that ("a
latent-sloppiness fix, declared"). The rejected aggressive variant D=56 is exactly where deferral
WOULD have been unsafe (Gate-A green 0.849 while engine margin ~63 px against a 60 px floor) — the
plan rejects it as the first move ✓. Fixing Gate-A's model (projection-based, or basis-inverted) is
a genuine follow-up P2-quality gate-quality item — surfacing it and shipping the conservative row
is the right ordering, not a dodge.

**(c) F1 flush-click edge — no double-save, no lost progress (code-verified).** `outcome` is set in
step_bookkeeping (`mission.gd:266-270`, win-then-lose ✓); the commit fires in `step_loot` slot (6)
the SAME tick, once-gated: `if outcome == null or committed: return` then `_end_mission()` which
sets `committed = true` first (`mission.gd:382`) and calls `commit_listener.commit()` once (:395-396).
Input lands between steps → the button can only exist post-commit → click cannot skip or repeat the
write. The deferred-route requirement matches the shipped F-2 relay precedent and its engine fact
(hub.gd:195-215 read: free-inside-pressed-emit console ERROR). Pin #7 (`test_bridge_contract.py:104-117`)
pins three token substrings + one exact code line + one absent call — all survive F1's ~25 added
LOC. Residual: P4-c.

**(d) F2 refusal strings + the :329 guard — the guard claim is WRONG about the mechanism (P2-1).**
The real `test_no_bank_writes_beside_the_mutators` (test_hub.py:329) is a **ban-regex**
(`bank.append(|bank_add(` + `mutated.emit(`) over the eight HUB_LAYER files — there is **no NAMED
mutator list to update**; game_state.gd is not in HUB_LAYER, and `state.sell_bank(` matches no
regex (the BN2 companion at :302 greps `spend_gold|consume_material` in gear_panel — sell's gold
lands via `add_gold` INSIDE the new game_state mutator, no match). So per the contract as written
**no guard edit is required** — yet the plan mandates one in-commit AND omits `tests/test_hub.py`
from W2's exclusive file list (internal contradiction, and a needless edit of a pin-adjacent test).
The rest of F2 checks out: `check_shape` is presence+kind over named keys only → a `sell_value`
extra key PASSES (body read); the exact-set traps are economy.json:172 and balance.feel:196
(untouched; rarity has no exact-set — only `chest_tiers ⊆ ladder` :350); sell-grep = defense rows
only ✓; zero egg rows (grep 0); equipped/materials boundaries true as stated.

**(e) F5 ungoverned constants — visual-only holds, no second mechanism, goldens safe.**
Broadened grep `bob|math.sin|sin\(` over ALL `godot/scripts/*.gd`: **0 hits** — no visual bob/scale
helper exists; ui_tween is Control enter/hover transitions (different concern, `create_tween`
mechanism untouched); fx_director is a pure observer (public field reads, zero writes — LEDGER V5
row + its code) so a node-y offset never propagates to fx. `ent["pos"]` is sim, node position is a
downstream visual (`enemy_runner.gd:136` writes node from `mv["pos"]`; golden fixtures record
step-observable sim, and the plan ASSERTS ent-pos equality against the no-anim run + the
v5_fx_probe tracer leg — I captured the V5FX-OK baseline for that comparison). I2: enemy_runner.gd
IS in `GOVERNED_LITERALS` (one call line, zero literals — compliant); the new `enemy_anim.gd` is
OUTSIDE the governed set and the **fx_director ungoverned-constants precedent is real** (fx_director
is not in the set). `balance.feel` is exact-set-pinned (:196) → constants-in-file is the correct
call, not a dodge.

**(f) WAVES — files exist, disjointness holds EXCEPT the P2-1 contradiction.** W1/W2/W3/W4 cited
files verified present (main.gd 193 L, game_state 365 L, gear_panel_ui 170 L, defense_panel 373 L,
rarity.json shape-map row :134); the four NEW files are genuinely new. Inside-wave disjointness
holds (F2∩F1 = ∅, etc.). LOCKED-pin sweep across all waves: F6 declares pin #3 (owner-gated) ✓;
pin #8's literal save strings are untouched by sell_bank; pin #7 survives F1; pins 1/2/4/5/6/9/11
untouched. **One undeclared collision path found: W3's fallback split violates pin #10 if taken
(P3-1).**

**(g) DoD-completeness** — every feature has a named verification leg (F1/F2 engine + journey
shot; F3 tests-only; F4/F5/F6 engine + browser + describe-image per MC 11509 D3; F6 kit re-run
≥110 px leg — measured 121.8 ✓). Two gaps: F3's planted-red row (P3-2); F6's W4 owner-gate is the
plan's strongest DoD row, no gap.

## 3. Findings (ranked)

**P2-1 — F2's guard-update instruction is wrong on the mechanism and contradicts W2's own file
list.** test_hub.py:329 has no NAMED list to extend; no guard edit is needed for the contract as
written; yet the plan says "must be updated IN THE SAME COMMIT, it greps call-sites" AND leaves
test_hub.py out of W2's "(exclusive)" set. The F2 card cannot follow both statements. FIX-LINE:
delete the guard-edit mandate (keep one verification leg: re-run test_hub.py unchanged to PROVE
sell_bank trips no ban-regex), OR if the team prefers a positive guard, add `tests/test_hub.py`
explicitly to the W2 file list with the exact edit named.

**P3-1 — W3 fallback can silently break LOCKED pin #10.** F4's LOC fallback ("W16-style split of
the action-button block into a sibling file") moves code OUT of the governed `defense_panel.gd`;
FINDINGS §5 row 10's rule is "a SPLIT of a governed file must update the GOVERNED_LITERALS set in
the same commit". The plan's fallback is silent → the new sibling would ship ungoverned (silent I2
governance loss). FIX-LINE: one sentence — fallback split adds the sibling to
`tools/check_hygiene.py` GOVERNED_LITERALS in the same commit.

**P3-2 — F3 violates the plan's own blanket acceptance row.** "Every card's acceptance: … its own
planted-red evidence beside the green run" is unsatisfiable for a TESTS-ONLY card (no implementation
change to plant). Declare F3's planted-red as N/A (the negative legs run over correct code —
the red case is a scratch-tree mutation proving the new asserts catch a broken sell/relic leg), or
add that scratch-plant leg explicitly.

**P4-a — LOC quotes off by one (gate metric = `text.split("\n")`):** defense_panel **373** not 372
(W3 +25 lands ~398/400 — set the fallback trigger at ~398); mission.gd **400** not 399 (conclusion
unchanged: it cannot grow); game_state **365**; main **193**. Harmless; correct the four numbers so
knut's hygiene leg and the card don't diverge.
**P4-b — "Gate A mis-measures the engine by ~2.5× at the margin"**: the ×-factor is not reproducible
in any reconstruction I could build (my independent replication: median 1.02 px / max 27.3 px, over
33 live rows — the plan's own cited numbers are 0.91/21.3, and no ratio between any pair of these
is 2.5). The phenomenon is real and load-bearing-free; state it in px (or per-gate margin ratio),
not as a ×-factor that no leg can re-check.
**P4-c — F1 CanvasLayer parent/teardown unspecified:** mount the banner-layer under `_routed` (freed
with the mission) or hide it in `open_hub()` — else a stale RETURN TO HUB button survives into the
hub. One sentence in the contract.
**P4-d — F6's "shipped planted-red stops firing if the literal goes stale" is false — the test
already RED-LOUDS at :403.** Harmless understatement; correct the sentence so the owner sees the
stale-pin failure mode is loud, not silent.
**P4-e — plan cites `sim/sim_harness.gd` staleness in ARCHITECTURE: honest and true** (shipped
runner is sim_headless; verified) — carry a doc-sweep row when the ARCHITECTURE row is next touched.

## 4. What this gate VERIFIED about the plan itself

Owner framing intact: zero monetization (nothing in F1-F6 touches prices/loot semantics),
replace-not-add (F4 delegates place→place_id, F5/F6 one mechanism each; second-mechanism greps ran
and came back empty), golden fixtures byte-safe by construction with an asserted proxy leg, LOCKED
pins declared where touched (F6) and provably untouched elsewhere, MC 11509 D3 respected (visual
legs are browser+describe-image, no sealed visual tests proposed). The F6 recommendation (D=64/48°,
one documented owner-authorized re-pin) is the SAME rig I would ship from my own numbers.

The three P2/P3 rows are plan-text corrections, not re-designs: each is one-to-three lines and none
reopens a contract, a wave, or an owner decision. They are, however, instructions a spawned card
cannot follow as written (P2-1) or would silently break a LOCKED rule with (P3-1) — that is exactly
what this gate exists to catch before W1 spawns.

# VERDICT: FIX
