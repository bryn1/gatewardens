# W15b evidence — MC 11274.1.27 / card 11379 — pierce/splash consumers + hard golden retry

Date: 2026-10-26. Seat: code (11379). Workdir: /home/claudecode/Games/gatewardens (git main).
BASE = da4d6aa (LEDGER: W14 done). RESULT commit = **e62859cf4efde1f53e9ab1a98ec890143ce0cd60**
(author `code (11379)`; 9 files; the ONE commit).

## Verdict: DELIVERED — mechanics live, normal golden DECLARED-REGEN, hard fixture WIN committed

## pytest (final, committed tree)

`python3 -m pytest tests/ -q` → **192 passed in 36.88s** (prior 190 + 2 new
test_pierce_splash legs; hard golden legs shipped because the run IS winnable).
`python3 tools/check_hygiene.py` → **0 hit(s)**.

## Machine rows per mechanic (engine probe, rc 0, EMPTY stderr, rows verbatim)

    EFFECT TOW-NONE e1=1 e2=0                     # ballista T1: primary only
    DROP TOW-NONE e1=14.4                        # = towers.json 12*1.2 exact
    EFFECT TOW-PIERCE e1=1 e2=1 e3=1 e4=0 e5=0   # T3: lane-chain hits e1,e2,e3
      # e3 sits at distance EXACTLY 18.0 (inclusive boundary); e4 cross-lane
      # inside radius refused; e5 same-lane beyond radius refused
    DROP TOW-PIERCE e1=33.6 e2=33.6 e3=33.6      # extras carry the SAME dps (I4)
    EFFECT TOW-PIERCE-END e1=1                   # degenerate lane-end: single hit
    EFFECT TOW-SPLASH e1=1 e2=1 e3=1 e4=1 e5=0   # bombard T3: e2 d=12.5, e3 d=
      # EXACTLY 13.0, e4 CROSS-LANE inside r, e5 beyond refused
    DROP TOW-SPLASH e1=49.2 e2=49.2 e3=49.2 e4=49.2   # 82*0.6 exact, one site
    EFFECT TOW-SPLASH-SOLO e1=1                  # degenerate: one enemy, single
    EFFECT TOW-NOEFFECT e1=1 e2=0                # tier row with "effect" key
                                                   # REMOVED = plain single hit
    EFFECT HERO-PIERCE-STATE ok=1                # blue - mana_cost, cd set (row)
    EFFECT HERO-PIERCE e1=1 e2=1 e3=0 e4=0       # deadeye piercer: same-lane
      # chain inside primary range; cross-lane-inside refused; beyond refused
    EFFECT HERO-AOE e1=1 e2=1 e3=0               # control: shipped AoE-around-
                                                   # hero mechanism UNCHANGED
    EFFECT STATIC ok=1                           # extra_targets direct: empty
      # pool / slow / none / r=0 / r<0 / dead-extras / primary-excluded /
      # pierce-vs-splash lane discrimination on identical geometry

All numbers re-derived from shipped JSON in tests/test_pierce_splash.py (zero
balance literals; I2 governed files clean).

## Planted reds (the gate can fail — VERIFIED this session)

1. LIVE, consumer removed: `sed s/String(row.get("effect", "none"))/"none"/`
   in defense_obj.gd → `test_effect_consumers_engine_leg` FAILED
   (`TOW-PIERCE` flags differ: e2/e3 1->0) AND the shipped matcher leg
   `test_fire_leg_wiring_with_planted_red` FAILED ("_fire_tower must route
   the row effect through extra_targets"). File restored (git diff clean).
2. LIVE, splash/pierce radius off-by-one: `s/distance_to(impact) <= r:/
   distance_to(impact) < r:/` in sim_combat.gd → engine leg FAILED,
   `{'e3': '0'} != {'e3': '1'}` (the EXACT-radius boundary legs bite).
   File restored.
3. SHIPPED (permanent, in-test, W11b idiom): matcher over an in-memory
   copy with the consumer pinned to "none" → matcher must report red.

## Normal golden — DECLARED REGENERATION (mechanics moved the out-rows)

Cause: uid1 (ballista lane_g1 wp3) reaches T3 ("pierce") at in-row tick
11600; from the first affected volley, kills land earlier → loot-tray drain
ticks shift, one extra drop exists, phase/boss/win ticks move. Regen ONLY
via the sanctioned route `sim_headless.gd -- --fixture <path> --regen`
(rc 0, EMPTY stderr). Row-by-row:
- header + all 23 in-rows: BYTE-IDENTICAL (harness echoes authored bytes).
- out-rows 212 → 213; 131 rows byte-unchanged; first divergence out-row
  idx 128: loot_pickup tick 12834 → 12806.
- changed rows by ev: loot_pickup 65, act 7, phase 6, ability 2, boss 1,
  outcome 1; +1 loot_pickup (extra kill's drop). Every changed row cause =
  kill-timing ripple from the pierce consumer; every row ok:true; win at
  tick 20353 → 19837 (faster clears); all other tests green against it
  (192 passed).
- file sha256 f0473c1ce447938aa6b5b8cb888c9be71c579a1e51142ec11f9b155d54380f23
  → eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912
- out-stream sha 8ea42737bc4a96249246fbf158a64beb79c90ff2aaf9c1722089065ad43528af
  → 1cbf3f44532f39b834745ae37e11d260eca73971d45268f9691ac0db8b809b35
  (recorded pre-change replay on the new build reproduced 1cbf3f44…, i.e.
  byte-identity was IMPOSSIBLE — hence this declared regen, never silent).

## Hard golden — WIN, committed (closes REVIEW P2-9)

`tests/fixtures/mission_gatefall_hard.jsonl` (file sha256
5e37c4b089209e64…): header seed 11379 difficulty hard; 23 in-rows ALL
applied ok:true (ZERO refused acts — every place in a build phase, every
upgrade affordable at its tick, traced green: 300 start → spends 50@2400,
100@3800, 50@4800, 150@6900, 100@10700, 150@14400, place 100@16800+50@16900,
200@18900, cap-tracked); outcome row ok:true: win, tick 21750, wave 10,
boss_neutralized, bank_is_tray_plus_chest, alive_cap_i7 (max 28), ack_mirror.
- A/B: two fresh replays byte-equal; out-stream sha d6d2adc30125af2d71a83b889d7ac05840c0e1ff22aaf23415db73d8b9f56c7d.
- Tampered leg: seed 11379→11378 diverges from the golden (gate RED-able).
- Doctrine (v7): 4-ballista pierce ladder (2 core-confluence, 1 g1-mid, 1
  air-end slot) + deadeye (storm hold) → embercaller at wave-8 build (nova
  hold + meteor press over the confluence) → deadeye for the boss wave.
  W15's wall (wave-4 double-flood) falls because ballista T3+ chains the
  lane (pierce) where W15 measured single-target ≈ 180–215 dps vs ≈ 250
  hp/s arrival: the same towers now multi-hit lane clumps.
- NAMED limit: bombard SPLASH is not fixture-reachable — defense_placer.
  row_for returns the FIRST towers.json row of the class, and the C12
  pinned act vocabulary {class,tier,lane,wp} names no id. Splash is proven
  at the mechanic-leg level (engine probe above); widening place-vocab is
  a harness/data decision out of this card — routed to the orchestrator.

## Readings (declared field readings)

- "pierce" (tower tier row / hero ability row): continue along the IMPACT
  ENTITY'S LANE — every other live same-lane entity within the row's DATA
  RADIUS of the impact point, inclusive boundary. The data declares no
  count and no direction, so count = lane ∩ radius (stated per brief).
  Radius sources: tower tier `range` (via bonus_row — relic-legal); hero
  ability = the primary-attack `range` already used to pick the target.
- "splash": every other live entity within that radius of the impact
  point, REGARDLESS of lane (lanes crossing near an impact splash).
- Any other effect string OR a missing key = plain single hit. "slow"/
  "block" stay honest inert (no magnitude exists in towers.json; inventing
  one breaks I2 — the pre-existing reading stands). Trap path unchanged.
- items.json shot_types ("pierce"/"splash"): NO consumer wired — no v1
  combat path consumes item rows' shot_type/proj_count at all (hero stats
  are heroes.json-static; the item→hero stat bridge is its own future
  card). Naming it is the deliverable there; wiring pierce to a dead
  bridge would be a second mechanism beside nothing.
- Entity identity in extra_targets uses GDScript Dictionary equality —
  probed 4.7.2: CONTENT equality; live records carry a distinct node,
  synthetic probe records keep distinct positions, so the primary is the
  only self-match (comment in sim_combat.gd).

## Files (in commit e62859c)

godot/sim/sim_combat.gd (+extra_targets, ONE selector) ·
godot/scripts/defense_obj.gd (effect leg + header truth) ·
godot/scripts/hero_combat.gd (single-target ability effect leg + header) ·
tests/test_pierce_splash.py (NEW engine probe + shipped matcher red) ·
tests/test_sim_golden.py (both-fixture legs: shape/replay/stable/tampered) ·
tests/fixtures/mission_gatefall_normal.jsonl (DECLARED REGEN) ·
tests/fixtures/mission_gatefall_hard.jsonl (NEW) · docs/ARCHITECTURE.md
(sim_combat/defense_obj rows carry the pinned signature) · LEDGER.md (W15
rows deduped to DONE). Line counts: sim_combat 71, defense_obj 280,
hero_combat 149, test_pierce_splash 458 (test ceiling 600), no new header
exemptions; hygiene gate 0 hits.

## Leftovers for the orchestrator (not fixed here, named)

- godot/scripts/ascension_ui.gd.uid UNTRACKED in the tree (W14 left it;
  every other .gd has its .uid tracked) — one-line hygiene commit.
- Bombard/splash fixture reachability (above).
- W15's .tmp scratch (hard_draft.jsonl, r*.txt, drive.py, mk_draft.py) is
  NOT mine — left in place; all w15b_* scratch deleted at close.

VERIFY_EXIT=0
