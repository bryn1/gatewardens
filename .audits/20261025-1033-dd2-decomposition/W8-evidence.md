# W8 evidence — defenses: defense_placer + defense_obj + defense_panel (MC 11274.1.15 / card 11322)

## Commits
- W8 build: `26575a1bfc237dd13cff1fa64c1f8590718f83fd` (author `code (11322)`), 12 files, 979 insertions(+), 4 deletions(-):
  `godot/scripts/defense_obj.gd`(+`.uid`) `defense_placer.gd`(+`.uid`) `defense_panel.gd`(+`.uid`),
  `godot/assets/mat_defense_{tower,blockade,trap}.tres`, `godot/sim/mission_smoke.gd`,
  `tests/test_mission_smoke.py`, and `godot/scripts/mission.gd` (declared hook lines only — see R7).
  LEDGER.md untouched (parent integrates the row, W6/W7 idiom). uids minted with the engine's own
  ResourceUID.create_id()/id_to_text() (temp `sim/_uidmint.gd` probe, run and removed pre-commit).
  File hashes: obj 4619392e… placer 24668573… panel f9e9bba6… smoke 29c76a38… test ad86fdca…

## DoD — pytest tail + hygiene
```
$ python3 -m pytest tests/ -q            PYTEST_RC=0
........................................................................ [ 51%]
...................................................................      [100%]
139 passed in 4.76s
$ python3 tools/check_hygiene.py         HYGIENE_RC=0
check_hygiene: 0 hit(s)
```
135 prior tests green unchanged + 4 new test functions (the W8 machine rows parse inside the
existing engine-leg test — one engine invocation). Notes are informational (soft-250 + sanctioned
draws); errors 0. Ceilings: obj 227 / placer 181 / panel 185 ≤250 target; mission.gd 436 and
mission_smoke.gd 490 ride the gate's own first-line `# hygiene:` header rule (W7 precedent —
mission.gd at the cap at base, hook lines only; smoke kept whole as one test asset).

## Smoke transcript (godot/sim/mission_smoke.gd, `-s`, XDG_DATA_HOME temp, seed 11274)
rc=0, stderr EMPTY (0 bytes). Two independent runs byte-identical (cmp clean).
```
MISSION-SMOKE-SEED deck=["warden","deadeye","embercaller"]
MISSION-SMOKE-W8PLACE class=tower cost=100 green=200 tier=1
MISSION-SMOKE-W8UPGRADE cost=50 dps=22.10 green=150
MISSION-SMOKE-W8REPAIR missing=0.5 cost=38 green=112 hp=240.0
MISSION-SMOKE-W8REPAIR1 cost=1 green=111
MISSION-SMOKE-W8PLACE2 class=blockade cost=50 green=61
MISSION-SMOKE-W8CAP why=cap green=61 count=2
MISSION-SMOKE-W8SELL refund=19 green=80 count=1
MISSION-SMOKE-W8FREESLOT class=trap cost=80 green=0 charges=12
MISSION-SMOKE-W8PANEL classes=tower|blockade|trap gate=2
MISSION-SMOKE-W8PANEL-ACT refund=0 cost=50 green=30
MISSION-SMOKE-SPAWN t=1501 wave=0 alive=1
MISSION-SMOKE-ADVANCE d0=39.92 d1=35.21
MISSION-SMOKE-CORE hp=3750.0 max=5000.0
MISSION-SMOKE-KILL t=31 wave=0 green=32 xp=4 loot=1
MISSION-SMOKE-WAVE kills=3 green=76 xp=72 loot=3
MISSION-SMOKE-REFILL blue=100.0 max=100.0
MISSION-SMOKE-W8KILL t=82 green=+2 xp=+4
MISSION-SMOKE-ABILITY ability=unbreakable cost=45.0 blue=55.05 gated=1
MISSION-SMOKE-SWAP hero=warden
MISSION-SMOKE-F1SWAP hero=warden swap_blue=90.0 deadeye_max=90.0
MISSION-SMOKE-DOWN pawns=3 visible=0
MISSION-SMOKE-LOSE outcome=lose ack=5 seq=5
MISSION-SMOKE-OK
```
Leg binding (every number re-derived by tests/test_mission_smoke.py from towers.json /
economy.json / enemies.json / gatefall.json, never from literals there):
- (a) PLACE: green 300→200 drops EXACTLY the ballista base_cost 100; C7 cap + can_afford guard
  order and the single `green -= cost` write are source-truth-gated on mission.gd.
- (b) UPGRADE T1→T2: cost = int(100×0.5)=50 (ratios[0] ladder); dps RISES 14.40→22.10
  (dps row = tiers[1].damage×fire_rate from data; the T1 dps must be strictly lower — the
  upgrade actually powers the tower).
- (c) REPAIR: missing 0.5 → roundi(100×0.75×0.5)=38 (37.5 half-away-from-zero), hp tops to the
  T2 row 240; REPAIR1: missing 1/240 → roundi(0.3125)=0 → floor 1 (pinned max(…,1)).
- (d) CAP: harness writes defense_cap down to the live count (boot_probe license), the next
  place is refused why=cap with green UNCHANGED (61) and count unchanged — the pinned cap+1 row.
- (e) SELL: damaged blockade (missing 0.5) refunds roundi(50×0.75×0.5)=roundi(18.75)=19 through
  add_green; the freed slot re-accepts the trap at the can_afford EXACT-COST edge (green==80),
  trap charges = the data 12 (never fired — far lane, attribution hygiene for (g)).
- (f) PANEL: lists v1 classes tower|blockade|trap; gate at green==trap price enables exactly the
  two cheaper classes (2); its KeyN/KeyM presses route through placer/obj: full-HP sell refunds
  0 (the pinned R1 formula's literal reading: total_spent×0.75×0), place pays the data cost.
- (g) TOWER KILL: harness spawns one skitterling through the real `runner.spawn` C2 entry on the
  closed sub-lane; the upgraded tower's step-(3) dps tick drains it (t=82 frames, 22.1×82/60≥30)
  and the step-(4) death funnel awards exactly +2 green +4 xp — hero holds nothing, trap already
  sold: the tower_dps application site is the only damage source in that window.
- ALL prior W6/W7 legs byte-unchanged except where W8 legitimately moved the ledger (KILL green
  32 = 30+2; WAVE 76 = harness green base 30 + 3×2 + per_wave 40 — the formula rides the
  harness-tracked base, never a literal). LOSE commit unchanged (ack 5 = seq 5).

## Planted-reds
- SHIPPED (in-memory, no file touched): `test_defense_planted_red_ratio_literal_goes_red` injects
  `return x * 0.75` into the defense_obj text; the SAME literal gate flags exactly [0.75]. The
  gate over the shipped files passes — it demonstrably can fail.
- LIVE (file edited, run, restored): `sim_economy.repair_cost` roundi→floor swap (`int(...)`):
  smoke printed cost=37 (ledger stayed internally consistent — the binding instrument is the
  pytest re-derivation, exactly like the W6/W7 cost rows):
  ```
  RED_PYTEST_RC=1
  >       assert int(rep["cost"]) == want, "repair = base x ratio x missing: %s" % rep
  E       AssertionError: repair = base x ratio x missing: {'missing': '0.5', 'cost': '37', …}
  FAILED tests/test_mission_smoke.py::test_mission_smoke_engine_leg
  ```
  `git checkout godot/sim/sim_economy.gd` restored; 12/12 mission_smoke tests green again, suite
  139 green. The repair leg goes RED on a broken repair formula and only on that.
- The shipped funnel matcher (C12, W6) stayed GREEN untouched: mission.gd's step body and
  `_process(d)=step(d)` were not edited (place_defense is a new method outside the funnel).

## Source-truth gates (new)
- Zero cost/percent literals: every number literal in the three defense .gd files (comments and
  strings blanked by the hygiene gate's own blank_code — one mechanism) must be in the I2
  structural set {0,1,2,3,4,0.5} — a 0.75 or a 100 cannot pass.
- Single application sites (C3/I4): defense_obj calls upgrade_cost / repair_cost / sell_value /
  tower_dps at exactly one site each; the panel calls NO cost/fire static (only can_afford gates
  + the obj's next_upgrade_cost state read); mission.gd carries no defense cost math and exactly
  ONE `green -= cost`; place_defense pins the cap→afford→spend→record order.

## Readings (R-list; pinned table wins per MC 11274.1.9–.14 precedent)
- R1 FILE NAME: the pinned Modules row names `scripts/defense_placer.gd`; the brief's
  "defense_placement.gd" is the paraphrase — table wins. The W6 mission.gd hook comment already
  read "W8 (defense_placer) fills this".
- R2 GREEN IS NOT META: the brief's "spend via the shipped green mutator on GWGameState"
  contradicts its own instruction to check the pinned field lists — C5 green is read off the
  MISSION (mission.gd `var green`, W6), and the C6 [meta2] key list carries NO green key.
  GWGameState was therefore NOT extended (game_state.gd untouched): a green mirror there would
  create a second, unpersistable green store against C6 and start meta saves per placement.
  BN2-named `spend_gold` is the gold pool — I3 keeps gold/green distinct. Spend/credit writes:
  place in mission.place_defense (one `green -= cost`), upgrade/repair/sell one each in
  defense_obj (refund routed through add_green so green never exceeds cap).
- R3 BUILDABLE SLOTS: pinned C7 carries no slot list, so slots = the map's GROUND lane
  waypoints (file order, deduped, cores excluded) — the brief's "buildable slots from map data /
  lanes geometry" read literally and zero-new-numbers. Overlap validity = one defense per slot.
  Air lanes not buildable in v1 (building inside the flight corridor is undeclared mechanics).
  Free placement (DD2 §4, pads rejected) rides this data-derived set; a finer grid is map data.
- R4 FIRE MODEL: sustained dps — `dps() × delta` onto the NEAREST live entity inside the tier
  row's range (the pinned row words no more than "target + fire (SimCombat)"; the hero_combat
  _nearest idiom; plain 3D distance, F16 air y weighs naturally). No discrete projectile sim
  ships (none pinned; C4's ownerless-projectile rule is a snapshot-damage rule for when one does).
- R5 CLASS DISPATCH (pinned dict {tower,blockade,trap}): tower fires; blockade dps=0 (data
  fire_rate 0) and its "block" string has NO consumer — the pinned runner row is lane-walk and
  nothing attacks a defense in v1, so a blockade ships honestly inert beyond cap/hp/repair/sell;
  trap fires like a tower but drains 1 trap_charge per fire-second (charges = seconds of
  sustained fire); the rows' "slow"/"splash"/"pierce" strings are data for later waves (the
  hero_combat "ability effect fields are data" doctrine) — inventing a slow magnitude with no
  data field would break I2.
- R6 TIER INDEX + FLAT-TIER BUILD: tier is the 0-based tiers[] index (W3a's pinned
  upgrade_cost(base, tier, ratios) consumes it: ratios[0]=0.5 IS the T1→T2 rung); display tier =
  index+1. `place(class, tier)` accepts tier 1 only (DD2 flat-tier build; higher tiers ride the
  C3 ladder) — refused why="tier". place(class) resolves the FIRST towers.json row of the class
  (the tower class ships 3 families — the family picker is the panel's frontend row).
- R7 mission.gd carries ONLY declared hook lines: DEF_OBJ preload const, `defense_uid` var, the
  place_defense method (the pinned mission row names it) and the first-line hygiene header update.
  Funnel word-for-word intact; step_defenses untouched — records enter defense_list carrying
  their `tick` callable, which is how the W6 slot-(3) hook fires them.
- R8 PANEL SCOPE: functional greybox Control (plain VBox of Labels/Buttons — the full HUD panel
  styling is the separate frontend row); the pinned row's relic picker (F2-12 item_row) is NOT
  faked: scripts/item_row.gd does not exist (gear-panel wave); mission.relic_pool and the C5
  relics_assigned leg already ship from W6. Bridge input model: handle_press(code)/poll(presses)
  consume GWBridge relay codes (KeyM place / KeyE upgrade / KeyN sell — codes the W4 relay
  ships; Digit4 stays the hero-cast key); nothing polls Input; the scene keymap/mount is the
  HUD row's wiring (declared).
- R9 HARNESS LICENSE: cap write-down, green write at the trap price, and take_damage to set the
  C3 missing-ratio legs are direct drives of REAL entry points (boot_probe/W7 precedent) —
  nothing attacks defenses in v1 (same no-attacker reading as R5's blockade).
- R10 Nothing else in scope was rewritten: enemy_runner gained no lines (its shipped `damage`
  entry — "for later waves (W7 hero_combat / W8 defense_obj)" — is the damage sink), game_state/
  bridge/sim statics/wave data untouched; towers.json tiers==5 ×5 entries consumed as-is.

VERIFY_EXIT=0
