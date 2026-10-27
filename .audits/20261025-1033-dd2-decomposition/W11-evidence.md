# W11 golden-simulation evidence — MC 11274.1.19 / card 11326

Deliverables (all landed, one commit): `godot/sim/sim_headless.gd`
(+`.uid`), `tests/fixtures/mission_gatefall_normal.jsonl`,
`tests/test_sim_golden.py`, plus the loot-event source files
(`godot/scripts/mission.gd`, `godot/scripts/hud.gd`,
`godot/sim/mission_smoke.gd`, `tests/test_mission_smoke.py`).

## Verdict: THE GOLDEN WINS — full 11-wave Gatefall normal, deterministic

`sim_headless.gd` (SceneTree `-s`) loads tables + GWCompose graph, seeds
ONE `RandomNumberGenerator(fixture.seed=11326)` handed through
`mission.setup`, instantiates mission.tscn, drives `_ready` directly
(E5: `-s` add_child does not dispatch `_ready`), applies fixture in-rows
at their ticks, steps the FULL mission at the pinned `1.0/60.0`, and
emits canonical C12 out-rows. Outcome row: **win, wave index 10** (the
boss wave), rc 0, EMPTY stderr (E3).

Sanity eyeball of the committed run (all pass):
- win at wave idx 10 of 11 (`win_at_last_wave`); `boss_neutralized` —
  see breach note below; start row waves=11, deck fallback
  [warden,deadeye,embercaller], green 300.
- green build-start curve 48→98→109→179→157→183→288→288→307→283 — dips
  land only on upgrade-spend builds ✓; bank 148 = 147 loot events + 1
  victory chest (`bank_is_tray_plus_chest` ✓ C12 step-6 chest BEFORE
  the C13 mission-end commit — `saved_ack 157 == write_seq 157` ✓);
- blue 83.69 ≤ 90 cap (`blue_capped`); max_alive 21 ≤ 100 (I7);
- 147 loot events span the full rarity ladder (worn→mythical);
  materials ember_core 2 + iron_bar 2 (tray-only material rows);
- all 23 in-rows replayed `applied:true`; every ability row shows
  cost_from_data + blue_le_cap; 0 refill-vacuity rows — every one of
  the 11 combat-transition rows shows blue==blue_max (no cast fired on
  a transition tick in this script, so the `cast_now` clause never
  carried a row alone).
- **Design fact (VERIFIED, engine semantics):** the boss ends the run
  by BREACHING the core at hp 1450.955 and being CONSUMED (C7: a breach
  is NOT a kill — C12 step 4 death-only: no rewards, no crystal drop).
  Wave 10 then clears (alive 0) → boss row → win with the core at 500
  (3 breaches across the run ≤ budget 3). The golden therefore ships
  the honest checks `outcome_win + win_at_last_wave +
  boss_neutralized (boss seen, lanes empty)` — NOT `boss_dead`, which
  would encode a lossy fiction; no aether_crystal row is required
  (a no-kill boss CANNOT drop per C12 — asserted-absence documented
  here instead of a fake check).

## sha256 trio (out-row stream: lines starting `{"`, banner excluded —
the `-s` engine banner prints to STDOUT, so the compared bytes are the
JSON row stream only)

- fresh replay A:   `8ea42737bc4a96249246fbf158a64beb79c90ff2aaf9c1722089065ad43528af`
- fresh replay B:   `8ea42737bc4a96249246fbf158a64beb79c90ff2aaf9c1722089065ad43528af`
- committed expected rows in the fixture: SAME `8ea42737…`
  (fixture also re-verified byte-identical after `.uid` generation)

File hashes: sim_headless.gd `27793f0a…`, fixture `f0473c1c…`,
test_sim_golden.py `ced98be0…`.

## Gates (tests/test_sim_golden.py, 4 legs)

1. fixture shape (header dict, act vocabulary, every row ok:true, last
   row ev=outcome);
2. fresh replay: rc 0 + EMPTY stderr + all rows ok + sha256(replayed)
   == sha256(committed);
3. two fresh runs byte-stable (sha equal);
4. MUTATION leg: one tampered byte in a fixture copy
   (`"seed":11326`→`"seed":11325`) must NOT reproduce the golden —
   asserted RED inside the test.

## A9 planted-bad RUN (gate proves it can fail on real sim truth)

Flipped a shipped DATA literal — ballista T1 `"damage": 12`→`11`
(unique-string sed, on-disk verified BEFORE the run):
- replay: rc 0, EMPTY stderr, but the out-row stream DIVERGED:
  `ddf99bca7706a6d309fa76f6ef6e9d20655147d1c420789384d18babd5719bd3`
  ≠ golden `8ea42737…` (boss hp 1481.515, bank_count 149 — the crit/
  drop RNG interleaving shifted every downstream row).
- pytest: `FAILED tests/test_sim_golden.py::test_golden_replay_matches_committed — 1 failed, 3 passed`
- restored via `git checkout -- godot/data/towers.json`;
  `git diff --quiet` → RESTORED-DIFF-CLEAN; post-restore replay hash
  back to `8ea42737…` (re-verified after .uid generation too).

## Suite + hygiene

`python3 -m pytest tests/ -q` → **172 passed in 18.85s** exit 0
(167 pre-W11 + mission_smoke loot leg + 4 golden legs).
`python3 tools/check_hygiene.py` → **0 hits** (notes only:
sim_headless 317 > soft 250, < 400 hard). test_purity (11 legs) covers
sim_headless.gd: no `extends Node`/`Engine`/`get_node`/bare rand
tokens; the only draws flow through the injected rng (F2-1).

## Findings

- **P2 (shipped bug, NOT fixed here — out of commit scope):**
  `defense_placer.gd` `upgrade()`/`repair()` (~line 128) resolve
  unknown uids through `return rec if rec.is_empty() else
  (rec["obj"] as RefCounted)…` — the not-found sentinel
  `{"ok":false,"why":"uid"}` is NON-empty → SCRIPT ERROR
  `Invalid access to property or key 'obj'` under `-s`. Reproduced by
  an upgrade to a never-placed uid (the first plan iteration hit it
  when a refused `place` was followed by an `upgrade`). Winning
  fixtures never send acts for uids that may not exist; the crash
  stands as a P2 for the ledger (sell() returns its uid-miss dict
  safely — upgrade/repair need the same).
- **Byte-shift declaration:** `mission_smoke.gd` gained one print row
  (`MISSION-SMOKE-LOOT events=… base=… rarity=… toast=on`) AFTER the
  MISSION-SMOKE-WAVE row, so every later smoke row shifts one line
  down in smoke stdout. No byte-anchor exists over smoke stdout
  (test_mission_smoke parses by row KEY), and the new row is
  deterministic under the fixed smoke seed; structural asserts only.
- HUD loot toast consumes the C9 event rows (I4 green):
  `hud.toast_text()` reads the LAST `mission.loot_events` row
  (`Picked up <base_id> (<rarity>)`); `loot_pickup.gd`'s world-drop
  rule remains a separate row (DECLARED-OPEN bullet in hud.gd updated).
- sim_headless.gd.uid (`uid://c88si0h67iovs`) generated by Godot's own
  headless editor scan (`--headless --editor --quit`; the scan's
  exit-time singleton abort is benign — file landed, suite re-verified
  green afterwards).

## R-list / rulings

- **C12 encoding, verbatim (docs/ARCHITECTURE.md):**
  `tests/fixtures/mission_<map>_<difficulty>.jsonl` — LINE 1 (header):
  `{"schema":int,"seed":int,"map":String,"difficulty":String}`; the
  remaining lines are, in file order, SCRIPTED-INPUT rows
  `{"kind":"in","tick":int,"act":"input|place|upgrade|repair|sell|assign|unassign|hotswap","args":{…}}`
  (applied before step for tick; "args" carries bridge key events or
  mission call args) and EXPECTED-OUTPUT rows
  `{"kind":"out","tick":int,"ev":String,…,"checks":{…},"ok":true}`;
  every line is one of the three kinds; sim_headless applies in-rows at
  their ticks, drives `step(1.0/60.0)`, emits out-rows, and
  test_sim_golden asserts byte-equality of emitted vs committed
  expected rows plus every `ok:true`; goldens regen only via `--regen`
  (never run by the number pytest). RNG: "the harness seeds ONE
  `RandomNumberGenerator(fixture.seed)` and hands IT to
  `GWCompose.build_graph` consumers".
- **Filename ruling:** brief's `golden_*` is a paraphrase; the PINNED
  table name wins → `mission_gatefall_normal.jsonl` (defense_placer
  precedent, brief vs ARCHITECTURE.md → pinned table wins).
- **Canonical serialization:** rows are printed with `JSON.stringify`
  which SORTS keys — the byte-stability law is "sorted stringify", not
  insertion order; tests hash the JSON row stream, never raw stdout
  (engine banner is stdout, E3 verdict = rc + empty stderr).
- **Godot JSON floats everything:** regen echoes the authored
  header/in-rows RAW (fixture keeps authored ints, e.g. `"seed":11326`,
  `"tier":1`); parsed floats never round-trip into the file.
- **assign/unassign are DECLARED, not exercised:** no mission call site
  exists in this build (C11 relic pool exists, the act vocabulary row
  returns `act_unpinned` → ok:false) — the winning fixture never
  sends them; the vocabulary row documents the gap honestly.
- **Cooldown/refill truth:** cds tick continuously in all phases
  (step_hero ungated except `downed`); the storm therefore runs on a
  960-tick grid while Digit2 is held — the script releases Digit2
  (tick 15370) to suppress a whiffed build-phase cast whose cd reset
  would land after the wave-9 leak front, and presses at 16894 and
  19440 to time the two decisive casts; `_enter_combat` refills blue
  and spawns the first group inside phase step (1), hence the named
  `refill_full` clause (vacuity rows: 0, above).
- Hero walk rows (KeyA/KeyS/KeyW holds) are plain bridge `input` acts;
  deterministic landing verified mid-iteration (hero ends at the
  a1/a2 corridor anchor and stays; no second walk in the winning
  script).

python3 -m pytest tests/ -q → 172 passed, exit 0.
check_hygiene → 0 hits. Golden: deterministic WIN, byte-stable.

VERIFY_EXIT=0
