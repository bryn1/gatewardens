# V5 combat FX via the visual-only observer — build evidence (MC card 11552 / milestone 11462 / workspace 11274)

Date 2026-10-28 (UTC). Sole writer, shared checkout /home/claudecode/Games/gatewardens.
Binary: /home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64 (4.7.2).
Knut route = the PROBE read-backs below (repo not projects.yaml-bound; same route as cards
11466/11520/11517/11530/11549). The grepped logs are COMMITTED under gen/ in this same commit.

PROBE: grep -c V5FX-OK /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-v5-fx-green.log => ^1$
PROBE: grep -c V5FX-ART /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-v5-fx-green.log => ^1$
PROBE: grep -c V5FX-SETTLE /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-v5-fx-green.log => ^1$
PROBE: grep -c V5FX-FAIL /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-v5-fx-red.log => ^1$
PROBE: grep -c SHOT-OK /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v5-fx-shot.log => ^3$
PROBE: grep -c fx_director /home/claudecode/Games/gatewardens/godot/scenes/mission.tscn => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/scripts/fx_director.gd => ^823022b70f3467393
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/sim/v5_fx_probe.gd => ^db88fd6403a55b82d
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_hard.jsonl => ^5e37c4b089209e64

## What shipped (ONE commit, the sim diff is ZERO files)

- godot/scripts/fx_director.gd (NEW) — visual-only Node3D observer. One fx_step(delta)
  pass compares its own last-frame snapshot against the sim's PUBLISHED fields; it never
  writes a sim object, wires a signal, or touches step order. Detection:
  FIRE->TRACER = the defense's own current nearest target (its public dps()/bonus_row()/
  pos reads + runner.nearest) lost hp this frame by >= dps*delta*0.5 (the sim's exact
  applied amount, halved for float margin) — declared reading: the sim ships NO per-shot
  cooldown field (fire is sustained dps x delta), so the target-lost-the-frame-damage test
  IS the observable "shot this frame"; a blockade (dps 0) never qualifies. Tracer art per
  data id: ballista=fx_proj_bolt, hailspire_tower=fx_proj_ice, bombard=fx_proj_bolt
  (bomb T3 sheet is a LATER VISUAL-TARGET row; the bolt standing in for both is the
  brief's declared reading). DAMAGE->SPARK = any tracked entity hp dropped between
  frames (hero hits qualify too). DESPAWN->POOF = the brief's "vanished with hp<=0"
  realized observationally: the runner drains dead AND arrived inside the same mission
  step, so an outside observer never catches hp<=0 in the LIVE entities array — death is
  the despawn whose last-known pos is NOT at the lane's final waypoint (a breacher is
  consumed AT the waypoint, hp>0; a future hp<=0 despawn still poofs via the primary
  hp check). Cost discipline: MAX_FX 64 live nodes, past the cap NEW fx are DROPPED.
  All fx nodes are children of the director — mission cleanup frees every fx with it.
- godot/scenes/mission.tscn — THE MOUNT (exact line): the new LAST scene child
  "[node name=\"FxDirector\" type=\"Node3D\" parent=\".\"]" (script row id 3b_fx;
  load_steps 7->8). The root's _process runs step() first, then the director observes
  the finished frame — no sim step is reordered; E5-safe (no _ready read: a "defense_list
  in m" guard rides v11_shot3's own mission-detection idiom). mission.gd / enemy_runner.gd
  / defense_obj.gd / mission_world.gd are NOT in the diff — `git show --stat` proves it.
- godot/scripts/sprite_bank.gd — the 4 fx ids joined THE ONE id->file TEXTURES map
  (same preload pattern as the V4 icons; no parallel fx system). 8 fx png .import
  sidecars committed (the bank is now their first code loader, the V1.1-a precedent).
- godot/sim/v5_fx_probe.gd (NEW) + godot/sim/v5_fx_shot.gd (NEW) + their .uid sidecars.
- tests/test_mission_clicks.py — the script-ext-rows pin 3 -> 4 (NET-ZERO file lines;
  DECLARED test-contract update: the scene legitimately ships a 4th script row now; the
  planted-red stale-uid leg and the per-row sidecar check are untouched and still pass).

## Probe legs (sim/v5_fx_probe.gd — gen/probe-v5-fx-green.log, rc 0, EMPTY stderr)

Boots the REAL Main.tscn, enters the mission through the shipped router, drives
mission.step AND fx_director.fx_step in lockstep (E5: -s dispatches no _process —
the probe pumps both by hand, mission root first, the exact live tree order).
- V5FX-MOUNT: the node exists as the mission root's scene child, script resource_path
  pinned to res://scripts/fx_director.gd, index after EnemyRunner.
- V5FX-TRACER n=848 / V5FX-SPARK n=318 / V5FX-POOF n=5 in a real fight (6 shooters =
  2 per family at the lane_g1 run-in, fed enemies) — counters are director-published
  plain vars (read-only for probing, brief row 5).
- V5FX-ART n=4: all four sheets seen on LIVE fx nodes pinned by committed RESOURCE PATH
  (bolt/ice/spark/poof) — the bank is never the oracle (V1.1-b lesson).
- V5FX-CAP live_max=63 <= 64 pinned from the probe's own constant (the mechanism
  cannot move the expected value; high-water proves the cap bound was tested near its edge).
- V5FX-SETTLE (leak row): live_max=63, then with the SIM FROZEN (zero new damage -> zero
  new fx) the child count walks back to baseline 0 in 12 settle frames.
- V5FX-TEARDOWN: m.free() frees the director with every fx (is_instance_valid false).
- Harness license (declared in the probe header): the breach leg costs 25% of core
  hp_max PER reach (balance.respawn_core_ratio — hp_max-proof, VERIFIED this card:
  a 5x-sturdier core still died at the 4th breach ~frame 1044), so the probe HOLDS the
  main core topped-up every frame; green lever funds the place leg; spawn rows fed.

## Planted red (gen/probe-v5-fx-red.log, rc 1)

PROJ_FOR mis-pin in fx_director.gd ("hailspire_tower" -> fx_proj_bolt): the probe went
RED at the pinned ART row — "V5FX-FAIL fx sheet never seen on a live node
(id=fx_proj_ice path=res://assets/v11/fx_proj_ice.png)" — the probe does NOT read the
director's map, so a wrong id cannot self-agree. Reverted; green re-run (a second green
run reproduced every row).

## Pixel proof (gen/v5fx_f92.png f180 f270 + gen/v5-fx-shot.log, rc 0)

sim/v5_fx_shot.gd = the v11_shot3 capture path (real hub click through the shipped
router) with the director mounted BY mission.tscn (the script adds no fx code path) and
6 towers firing; feed on lane_g1; captures taken only on frames with live fx nodes,
printed with the counters: f92 live=3 (tracers 2, spark 1), f180 live=20 (tracers 216,
sparks 72, poofs 1), f270 live=30 (tracers 605, sparks 213, poofs 3).
HONEST READ (I looked at the PNGs, plus 4x nearest-neighbour crops): f180 and f270
clearly show the orange fx_proj_bolt tracers between the guns and the walk line and
bright spark dots on the hit enemies; f270 additionally shows the cyan fx_proj_ice
shards south of the cluster (the hailspire guns). CAVEAT, stated honestly: the brown
fx_poof_death smoke reads near-identical to the brown enemy sheets at the 58/46-unit
camera distance — its PRESENCE at f180/f270 is carried by the printed counters
(poofs=1/3 at capture), not by my eyes at that zoom.

## Regression rows (all VERIFIED this session, after the change)

- pytest 222 passed BEFORE this card = 222 passed AFTER (222 = 222; no test file count
  change; the one edited test keeps its line count under the 600 gate).
- check_hygiene 0 hits; v4_icon_probe EXIT=0 (7 rows), v6_tween_probe EXIT=0 (9 rows),
  v11_sprite_probe EXIT=0 (9 rows), all EMPTY stderr.
- Golden fixtures byte-identical: eafe3932f7d30898… / 5e37c4b089209e64… (the sim diff
  is zero files, so the golden replays cannot shift — and they did not).
- git show --stat: mission.gd / enemy_runner.gd / defense_obj.gd / mission_world.gd
  absent from the commit (the binding ruling: sim READ-ONLY).

VERIFY_EXIT=0
