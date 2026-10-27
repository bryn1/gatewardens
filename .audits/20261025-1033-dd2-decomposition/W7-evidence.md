# W7 evidence — heroes: hero_controller + hero_combat + greybox pawn (MC 11274.1.14 / card 11321)

## Commits
- W7 build: `f51b966` (author `code (11321)`), 13 files changed, 571 insertions(+), 22 deletions(-):
  `godot/scripts/hero_controller.gd`(+`.uid`) `hero_combat.gd`(+`.uid`) `hero_pawn.gd`(+`.uid`),
  `godot/scenes/hero_pawn.tscn`, `godot/assets/mat_hero_{warden,deadeye,embercaller}.tres`,
  `godot/sim/mission_smoke.gd`, `tests/test_mission_smoke.py`, and `godot/scripts/mission.gd`
  (declared hook lines only — see Scope). LEDGER.md untouched (parent integrates the row, W6 idiom).
  uids minted with the engine's own ResourceUID.create_id()/id_to_text() (W6 idiom; a temp
  sim/_uidmint.gd probe was created, run and removed before the commit).

## DoD — pytest tail + hygiene
```
$ python3 -m pytest tests/ -q            PYTEST_EXIT=0
........................................................................ [ 53%]
...............................................................          [100%]
135 passed in 4.33s
$ python3 tools/check_hygiene.py         HYGIENE_EXIT=0
check_hygiene: 0 hit(s)
```
131 prior tests green unchanged + 4 new test functions (engine-leg row parsing extends an
existing test). Notes printed by the gate are informational (soft-250 notes + sanctioned-draw
notes); errors = 0. File ceilings: hero_controller 107 / hero_combat 133 / hero_pawn 30 /
mission_smoke 317 / test_mission_smoke 231 / mission.gd 410 = hard-400 exceeded by +7 DECLARED
hook lines, carried under the gate's own `# hygiene:` first-line header rule (the W6 file sat
exactly on the cap, no headroom existed; alternative was rewriting W6 lines — the extension
doctrine forbids).

## Smoke transcript (godot/sim/mission_smoke.gd, `-s`, XDG_DATA_HOME temp, deterministic seed 11274)
rc=0, stderr EMPTY (0 bytes). Two independent runs byte-identical.
```
MISSION-SMOKE-SEED deck=["warden","deadeye","embercaller"]
MISSION-SMOKE-SPAWN t=1501 wave=0 alive=1
MISSION-SMOKE-ADVANCE d0=39.92 d1=35.21
MISSION-SMOKE-CORE hp=3750.0 max=5000.0
MISSION-SMOKE-KILL t=31 wave=0 green=302 xp=4 loot=1
MISSION-SMOKE-WAVE kills=3 green=346 xp=72 loot=3
MISSION-SMOKE-REFILL blue=100.0 max=100.0
MISSION-SMOKE-ABILITY ability=unbreakable cost=45.0 blue=55.05 gated=1
MISSION-SMOKE-SWAP hero=warden
MISSION-SMOKE-F1SWAP hero=warden swap_blue=90.0 deadeye_max=90.0
MISSION-SMOKE-DOWN pawns=3 visible=0
MISSION-SMOKE-LOSE outcome=lose ack=5 seq=5
MISSION-SMOKE-OK
```
- (a) KILL: MouseLeft held — the hero primary attack kills a live wave-0 skitterling at t=31
  frames after the breach (rng seed pinned 11274); green/xp/loot move by exactly one
  skitterling's data awards through the pinned step-(4) death funnel; check-(4) formulas now
  count hero_kills + harness kills (346 = 300 + 3*2 + 40 with per_wave 40; 72 = 60 + 3*4 with
  wave_xp 60 — engine-side exact asserts hold; the pytest leg re-derives cost/caps from
  heroes.json).
- (b) ABILITY: Digit4 (no swap alias; the W4-added code) casts warden ability 4 — blue spends
  EXACTLY mana_cost (engine asserts tick-then-spend equality to 1e-9:
  min(100+3.0*dt,100) − 45 == 55.0 after the cast frame, 55.05 after the gate frame);
  second cast cooldown-gated (blue moves by regen only, cooldowns[3] still > 0).
- (c) DOWN: F2-9 all-down path unchanged with the pawn rig live — pawns=3, visible=0.
- (d) F1SWAP: F2 (warden→deadeye) with harness blue 130 above every cap: tick clamps 130→100,
  the C4 swap clamp bites at exactly min(100, 90) = deadeye blue_max (float-equal assert);
  F1 returns to warden; pawn visuals toggle with the active hero both ways
  (rig.pawns[id].visible — hidden old, shown new).

## Planted-red
SHIPPED (in tests/test_mission_smoke.py, no file touched): `test_hero_combat_planted_red_gate_removal_goes_red`
deletes the in-memory copy of the cooldown-gate line — the same matcher reports RED
(raises); green run proves the matcher passes on the real file. The W6 shipped funnel planted-red
stays green untouched.
LIVE (this wave, full engine leg):
```
sed -i 's/if float(cds\[i\]) > 0\.0:/if float(cds[i]) < 0.0:/' godot/scripts/hero_combat.gd
$ XDG_DATA_HOME=$(mktemp -d) godot --headless --path godot -s res://sim/mission_smoke.gd --
rc=1  stderr 0 bytes
...
MISSION-SMOKE FAIL second cast not cooldown-gated: blue=10.05 cd=25.0
```
The second cast fired (blue 55.05 − 45 = 10.05) — leg (b) went RED exactly at the cooldown gate.
File restored (diff-identical to backup), full suite re-green afterwards.

## Engine facts learned this wave (candidates for the LEDGER E-list)
- E6: on a CharacterBody3D, `var velocity` SHADOWS the built-in property -> GDScript parse
  error; under `-s` the probe's _init aborts with the uncaught error and the process HANGS
  while node `_process` spams the null-child errors every frame (compounds W6 fact (c)).
  The smoke's `root.add_child(m)` makes the mission node processed once the tree gets frames,
  so ANY setup-chain parse error shows as a hang + `Node not found: "HeroRig"` spam, not a rc!=0.
  Renamed to `vel`; manual velocity integration (like enemy_runner) keeps the file physics-free.
- Engine headless `-s` boot of the full mission scene + ~7k sim steps runs in ~0.5 s on this
  host — the W6/here 1700-frame guards and the 300 s pytest timeout are never near their caps.

## Readings (declared; pinned table wins per MC 11274.1.9-.13 precedent)
- R1 Jump key: the bridge relay (W4 — out of this wave's file scope) carries no Space code, so
  the greybox jump rides the held `Enter` code; bridge.held is the input source, no second
  input mechanism. Widening the relay with Space is a one-line ruling for a controls wave.
- R2 Ability presses Digit1..Digit4 are consumed at HELD level (combat takes no presses), so
  mission step-(5) drains the bridge exactly as W6 shipped and the F1-F3 + Digit1-3 hot-swap
  press-aliases stay intact. Digit4 (added by W4 for the hero row) has no swap alias.
- R3 Targeting per the row's wording: nearest live entity inside the data range; plain 3D
  distance (air lanes ride their authored waypoint y per F16, so melee range never contains a
  flyer — no fly-flag branch exists in hero files). aoe>0 abilities hit every entity within
  the radius of the hero stand; aoe==0 single-hits the nearest at primary range.
- R4 Ability damage = base.ability_power x dmg_scale (attacks: base.damage x dmg_scale);
  crit applies to every hero hit through hero_hit, one rng.randf() draw per hit. dmg_scale==0
  abilities (stun/taunt/barrier data) pay blue + cooldown and land no hit — effect semantics
  are later-wave data, inventing them here would be undeclared mechanism.
- R5 Pawn scene shape: pinned Scenes row names pawn_<archetype>.tscn x3; W6 shipped ZERO
  per-entity .tscn files (enemy/core visuals are code + .tres assets — the same idiom applies):
  ONE greybox pawn scene parameterized by hero id, tinted by the fixed palette
  mat_hero_<id>.tres (heroes.json carries no color field — "data if present, else fixed
  palette", brief-sanctioned). Archetype meshes ride the 3090 art wave.
- R6 Pawn sync rule = ACTIVE hero AND hp>0: a same-tick hp write (all-down) lands before the
  sync, so the all-down stand shows zero pawns even though step() no longer runs after the
  outcome (F2-9 tick). The camera rig is never moved or re-parented (F8): pawns are children
  of the rig body; hot-swap hides the old pawn and shows the new one.
- R7 mission.gd carries ONLY declared hook lines: HERO_RIG preload const, the setup rig block
  (+3 comment lines), $HeroRig.step(delta) as the funnel slot-(2) call inside step_hero, and
  the first-line `# hygiene:` header (ceiling exemption, see DoD). The pinned funnel word-for-
  word intact — the shipped source-truth matcher stayed green untouched.
- R8 Hero stand = main core position (map data, no literals); enemies never damage heroes
  (the pinned runner row is lane-walk only), so the down-states in the smoke stay
  harness-driven per the boot_probe precedent, now with the hero->enemy damage direction real.

VERIFY_EXIT=0
