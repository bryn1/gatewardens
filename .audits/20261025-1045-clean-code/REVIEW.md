# Pre-GA CLEAN-CODE AUDIT — findings (devils-advocate, MC 11274.1.23 / card 11339)

Repo: /home/claudecode/Games/gatewardens @ 817f8d2 (W13 done). Findings-only,
refactor-consumable. Contract read against docs/ARCHITECTURE.md (pinned), LEDGER.md
A1–A10 + c3 rulings, deferral list honored (stables/pets/auras/nodes/extra maps/
leaderboards/pixel-art = INTENTIONAL — none filed).

Evidence run this session (VERIFIED): full suite COLLECTS 190 (claim matches);
fast non-engine tier re-run green (test_economy_numbers+test_scaffold+
test_bridge_contract = 25 passed); `tools/check_hygiene.py` re-run = 0 hits with
6 soft-ceiling notes; every claim below carries a file:line probed this session.
NOT re-run here: the engine-heavy legs (golden replay, served tests) — the suite
claim is accepted from the collect + fast tier + W11/W12/W13 evidence, not
independently re-executed.

Fairness notes (things that HOLD, checked adversarially and clean):
sim purity I6 (no Node/Engine/bare-randf in sim/), I4 single-site green math
(place site mission.gd:317, upgrade/repair/sell sites defense_obj.gd:178/192/200,
wave-award/refill/revival only in phase_controller.gd:73/81/90), I3 pool split,
C13 single write path (gw_compose.gd:44-51 WeakRef listener, anchored via
game_state.gd:61; mission-end commit mission.gd:392-393; no direct meta-field
writes outside game_state), E1–E6 engine facts all obeyed (OS.has_feature guard
main.gd:89, `_js_relay` anchor main.gd:61/173, no `var velocity`, probe
early-return discipline), I8 rename grep 0, monetization tripwire + schema guard
green, no autoload section, C5 field-complete, HUD read-only verified by read +
test gates. Golden gate has a real mutation leg (test_sim_golden.py:108-123).

## P1 — behavior gaps; NOT refactor-safe; must sequence BEFORE GA-tagging

### P1-1 Defense placement/upgrade/sell is UNREACHABLE in the served game
- Sites: mission.gd:119-166 (setup mounts HeroRig+HUD only), defense_panel.gd:44
  (`setup` never called by any product code — `DEF_PANEL.new()` appears only in
  the harness mission_smoke.gd:256), mission.tscn (no panel node),
  mission.gd:226-228 (step-(5) drain consumes only SWAP_KEYS; KeyM/KeyE/KeyN
  from defense_panel.gd:28 are relayed by bridge.gd:21-23 and reach nothing).
- Why it matters: A3's core verb (place/upgrade/repair/sell defenses) cannot be
  performed by a player. The suite proves the API works headlessly, and the A9
  LEDGER row names the journey as “wave 10 + boss kill, place/upgrade tower, …”
  — but the served-journey evidence itself shows a DEFENSE-LESS LOSE run
  (.audits/20261025-1033-dd2-decomposition/A9-journey.md:11) and no place leg.
  This is failure-taxonomy pattern 10: the acceptance row was never tested
  end-to-end, and the tower-defense half of the hybrid ships dark.
- Smallest fix: in mission.gd setup() mount defense_panel (the HUD idiom,
  E5-safe) and route non-swap press codes through `panel.poll(...)` in step (5);
  re-run A9 served with an asserted place→upgrade→sell leg.

### P1-2 Relic equip (C11 + owner ruling R2) does not exist
- Sites: no `assign_relic`/`unassign_relic` anywhere (contract pins them:
  docs/ARCHITECTURE.md C11); mission.gd:68 `relics_assigned` is written NEVER
  (C5 field dead at 0 forever, F2-7's ±1 journey leg untestable);
  SimInventory.relic_bonuses (sim_inventory.gd:133) is uncalled by product code
  (its only non-sim mention is the COMMENT defense_obj.gd:48-49); the relic
  picker is declared “NOT built here yet” and its stated reason is now FALSE —
  defense_panel.gd:14-17 claims item_row.gd/.tscn “do not exist”; they shipped
  in W9 (scripts/item_row.gd, scenes/item_row.tscn).
- Why it matters: R2 explicitly rejected descoping relics-for-towers (“stays in
  v1”). Today a relic in the bank does literally nothing anywhere. The stale
  “do not exist” comment hides the gap behind an outdated excuse.
- Smallest fix: `mission.assign_relic/unassign_relic` over relic_pool (build
  phase, one-per-defense, C11 rules), defense_obj applies `relic_bonuses` on the
  tier row, defense_panel picker = item_row instances over the pool, C5
  `relics_assigned` maintained, ±1 journey leg; or an owner ruling moving
  relics to the deferral list — never the current implied-ship state.

### P1-3 Ascension is a write-only ledger: points are earned and persisted, but
spending exists only in harnesses and the modifiers apply to NOTHING
- Sites: `asc_modifier` (sim_progression.gd:49) — zero product callers (only
  test_heroes.py:143 regex on its body); `spend_asc` (game_state.gd:87) callers:
  save_probe.gd:69 + hub_probe.gd only — no hub station (hub.gd:36-40 stations =
  WarTable/Gear/Blacksmith/Tinkerer/Dummies); mission.gd:434-445 hero stats come
  from heroes.json `base` untouched by `asc_spent`.
- Why it matters: A2 promises Offense/Defense/Utility ascension. Today a player
  earns points, sees them in C5 (`asc_points`), and can never spend or feel them.
  Contract-pinned statics kept alive only by text-matching tests.
- Smallest fix: apply `asc_modifier(trees, asc_spent)` at `_build_heroes` (and
  dummy/hub math) over the base stats + an ascension spend station (or panel);
  wire xp_need at the C5/panel XP-threshold read or drop it with a design-review
  row. Alternatively an owner ruling defers ascension application — recorded.

### P1-4 Ability keys Digit1..Digit3 ALSO hot-swap heroes (collision)
- Sites: bridge.gd:52-56 (`on_key` feeds BOTH `held` and `presses`);
  hero_combat.gd:38,55-62 (held Digit1..4 = abilities 1..4); mission.gd:48-49
  SWAP_KEYS maps Digit1/2/3 to hot-swap; step (2) casts, step (5) swaps — the
  SAME press does both, every time.
- Why it matters: pressing the ability-1 key in a live mission teleports the
  player to hero 1 mid-fight. The blind spot is structural: the golden fixture
  scripts `hotswap` acts directly (fixture codes pressed are only KeyW/KeyA/
  MouseLeft/MouseRight) and the smoke drives `panel.handle_press` — no leg ever
  presses Digit1 while both consumers are live.
- Smallest fix: drop Digit1..3 from mission.gd SWAP_KEYS (F1-F3 already ship and
  are the HUD hints, hud.gd:232-233); Digit4 stays ability-only. Then add one
  fixture/smoke leg that presses F1 mid-combat (byte-anchor: a F1 press is a
  scripted `in`-row — the golden can cover the fixed mapping).

## P2 — important; refactor-safe unless marked (behavior)

### P2-5 Hygiene ceiling exemption is unconditional — the 400 HARD ceiling is decorative
- Sites: tools/check_hygiene.py:166 (`exempt = lines[0].startswith("# hygiene:")`
  with no size bound); mission_smoke.gd 636 lines (>400, and > the 600 CEILING
  its own header claims as a “test asset”), hub_probe.gd 464, mission.gd 463.
- Why it matters: the pinned rule (ARCHITECTURE §Modules “≤ 250 soft / 400 hard
  (header comment may exceed)”) means the HEADER may push a file over — not
  “write a magic first line, get unlimited length.” The exemption is being used
  exactly the way an exemption gets used.
- Smallest fix: bound the exemption (counted length ≤ ceiling + header lines, or
  absolute 500), then split the three exempt files (pure moves, refactor-safe;
  probes/golden guard them). Note test_data_schemas.py sits at 599/600 — one
  line from its own ceiling; give it headroom in the same run.

### P2-6 `GWTables.validate` / `validate_probe` do not exist — yet the pinned doc
and three product-file comments name them (phantom-module chain)
- Sites: docs/ARCHITECTURE.md:122 (validate static), :132 (validate_probe module
  row incl. “calls build_graph”), :171 (test line “+ validate_probe -s leg”);
  on disk: no sim/validate_probe.gd, sim_tables.gd has NO validate() —
  sim_tables.gd:9-10 defers it “with validate_probe (W5)” (which never shipped);
  dangling refs remain in sim_parse_probe.gd:3, main.gd:33-36 + :70-71.
  test_data_schemas.py has no engine/probe leg at all — deep data validation
  NEVER runs anywhere; boot is only a per-file parseability fail-fast
  (main.gd:72-78).
- Why it matters: F16's chain (validator + probe + test leg) is paper. A corrupt
 -but-parsable data file (missing key, wrong type) boots the game fine.
- Smallest fix: land `GWTables.validate` + boot_probe leg + test leg; OR amend
  the three doc rows to the shipped fail-fast reading and delete every dangling
  comment reference. (Decision needed, then mechanical.)

### P2-7 docs/ARCHITECTURE.md (the living pinned contract) has drifted from code
  - economy.json row (:104) lacks the `starter` key the data + game_state.gd:314
    now ship (W13 commit itself left this “doc-sync row” undone).
  - `scripts/loot_pickup.gd` row (:160) — module never shipped; its behavior
    shipped as mission.gd tray/event-feed; `balance.pickup_radius` consumed by
    nothing.
  - Scenes list (:162-164) names enemy/defense/core/ghost/pawn_<archetype>×3/
    dummy.tscn — on disk: hero_pawn.tscn (one), hub, hud, item_row, mission,
    mission_stub (unlisted, and dead — see P3-12).
  - test_waves.py named in :171 and in I4 (:207 “wording identical in
    test_waves”) — file does not exist (rows ride test_data_schemas).
  - game_state mutator list (:138) lacks add_gold/spend_gold/set_deck/
    complete_mission (all ship, all emit mutated — behavior correct, row stale).
- Why it matters: the doc is the refactor run's map; stale rows send it at
  phantom modules and hide real ones.
- Smallest fix: one doc-sync sweep (this is exactly the MC 11277 release row;
  do it as a committed row of the refactor run, grep-to-zero per retired names).

### P2-8 The I2 number-literal gate never landed in its pinned home; it exists as
FOUR copy-pasted STRUCT_VALS sets in test files instead
- Sites: check_hygiene.py:24-25 promises the whitelist “lands in this file
  then” — absent; copies: test_hub.py:61, test_mission_smoke.py:286,
  test_hud.py:39, test_loot_structure.py:286, each scanning its own file-list.
- Why it matters: one concern, four mechanisms (drift + silent-GREEN when a
  governed script is dropped from one list). The I2 invariant itself held under
  spot-reading (governed files math-via-data), so this is enforcement debt, not
  a live violation.
- Smallest fix: implement the whitelist over the governed .gd set inside
  check_hygiene (its pinned home + planted-red), collapse the four test copies
  to one call.

### P2-9 Golden coverage is normal-difficulty ONLY — the byte-anchor is half the game
- Sites: tests/fixtures/ has exactly mission_gatefall_normal.jsonl; the hard leg
  of mission.gd:271 (chest tier `else 1`), hard hp rows, hard drop_weights, and
  hard map routing are NEVER replayed. sim_headless already honors the fixture
  header difficulty (sim_headless.gd:90) — adding the hard golden is cheap.
- Why it matters: the refactor run's byte-anchor = golden + data JSONs; a
  refactor that breaks ONLY hard mode stays green through GA.
- Smallest fix: `sim_headless --regen` a mission_gatefall_hard.jsonl + second
  replay/stability legs (refactor-safe: it ADDS an anchor, changes no product
  byte).

### P2-10 `SimInventory.equip` returns ok:true for a row NOT in the bank (behavior — needs judgment, not refactor-safe)
- Sites: sim_inventory.gd:42-59 — uid not found → `index == -1` → nothing
  removed, still `{"ok": true}`; GWGameState.equip then marks it worn. Equipping
  a bank-row the bank no longer holds (stale panel reference) duplicates the
  item (worn + still in bank). No negative leg covers the absent-uid case
  (test_hub legs cover swap-return + relic-refusal).
- Smallest fix: `ok = index >= 0` when uid > 0 (one line) + negative leg.

## P3 — reliability/economy hygiene

### P3-11 Training Dummies = uncapped XP faucet
- Sites: dummy_range.gd:74-77 (`strike()` awards `xp.enemy_xp_base.normal` per
  button press through `add_hero_xp`, no daily/session cap); A6 (LEDGER:26-27)
  names Dummies “DPS test” only; declared as “practice XP” in-file but never on
  the deferral/acceptance list.
- Why it matters: hub-side, risk-free, infinite hero XP = the balance layer
  (and the XP the golden fixture records) becomes a click-count function.
- Smallest fix (decision): cap per build-phase or zero the XP (keep the DPS
  readout, which is what A6 promises); adjust hub_probe leg either way.

### P3-12 Dead mission-stub fallback + orphan scene
- Sites: main.gd:47,107-108 (`ResourceLoader.exists(MISSION_SCENE)` is always
  true since W6) + scenes/mission_stub.tscn (zero references outside main.gd);
  header comment still claims “until the mission milestone lands it” (main.gd:17).
- Smallest fix: delete the branch + scene + stale sentence (refactor-safe).

### P3-13 Duplication that should be ONE mechanism (all refactor-safe)
- Raw array-data door copied 5×: mission.gd:455-459, defense_placer.gd:184-189,
  blacksmith_ui.gd:180-187, game_state.gd:318-327 (roster), main.gd:72-78
  (inline variant). The W3a dict-door ruling manufactured this; add
  `GWTables.rows(stem)` as the single array door (doc-review row) and call it.
- Nearest/AoE entity search 3×: hero_combat.gd:116-124 (_nearest),
  defense_obj.gd:149-157 (_nearest), hero_combat.gd:128-133 (_in_range) — same
  loop over `$EnemyRunner.entities`; move to enemy_runner methods
  (`nearest(pos,r)`, `in_range(pos,r)`) — single home, one behavior.
- Item-list build 3×: blacksmith_ui refresh (120-133) + tinkerer_ui +
  gear_panel_ui each loop bank→item_row→connect(picked) — F2-12 shared the ROW,
  not the LIST-BUILD; one bank_list helper kills all three.

## P4 — polish

### P4-14 Banned-vocabulary WORDS in product comments (tripwire survives them only because comments are blanked)
- “price” in comments: mission_smoke.gd:48,167,254; defense_obj.gd:162.
  check_hygiene blanks comments (BN1), but test_hud.py:218-224 and
  test_hub.py:371-376 scan RAW source for the same tokens — two guards, two
  rules, same concern; and a naive MC 11277 release-sweep grep hits these.
- Fix: rename to “cost” in comments; align the two raw-scans with the blanking
  rule (one vocabulary, one mechanism).

### P4-15 Brief-trail residue in product headers
- defense_placer.gd:8-11 “REFERENCE NOTE: … the W8 brief's
  ‘defense_placement.gd’ is the paraphrase” (the exact brief-paraphrase
  residue class the task named); wave-trail prose (“readings on the trail”,
  hud.gd:13 “R-list”) is provenance that belongs on the LEDGER/evidence side.
- Fix: one-line contract statements in headers; trail references → LEDGER.

### P4-16 Golden comparator filter is substring-brittle
- test_sim_golden.py:41-47 drops any stdout line containing `"schema"` or the
  literal `"kind":"in"`; a future out-row field named `schema*` would silently
  leave the comparison. Fix: filter on parsed `kind == "out"`.

### P4-17 Dead data fields (contract-pinned but unconsumed)
- balance.pickup_radius (no consumer — loot_pickup never shipped),
  feel.cam_yaw_rate, feel.death_fade, heroes.defense_id (0 reads).
- Fix: consume or drop with a doc row (they're the byte-anchor — dropping is a
  DECLARED change, not drive-by cleanup).

### P4-18 save_probe bad_mode path: `quit(1)` without `return` (save_probe.gd:47-49)
- Last statement of `_init`, so inert today — but it is the one site violating
  the file's own E3 discipline text (:57-59). Add the `return`.

## Refactor-run readiness verdict (the task's question)

A zero-behavior refactor run (byte-anchor = golden fixture + data JSONs) can
safely close **P2-5, P2-6 (either branch), P2-7, P2-8, P2-9, P3-12, P3-13,
P4-14..P4-18** — structural moves under the suite plus the golden anchor.
It CANNOT close P1-1..P1-4, P2-10, P3-11 without behavior changes — and P1-1 is
not “clean code,” it is a core acceptance verb that the served build does not
offer while the A9 LEDGER row names it in the journey definition. Those need
their own fix legs with new served-journey evidence (place/upgrade/sell leg,
F1 hot-swap leg, relic ±1 leg, ascension-visible or owner-deferred), BEFORE the
GA tag per the release-gate order (LEDGER §Release gate).

Sequencing recommended: (1) P1 legs + P2-10 + P3-11 decisions, each with
planted-red + re-journey; (2) the refactor run over the refactor-safe list with
golden+data bytes unchanged and the hard-mode golden ADDED first; (3) release
notes + README + doc-sync sweep (P2-7 lands here); (4) tag.

VERDICT FILE: DA-verdict.md (same dir).

VERIFY_EXIT=0
