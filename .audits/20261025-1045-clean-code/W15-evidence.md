# W15 evidence — MC 11274.1.26 / card 11355 — hard-mode golden fixture

Date: 2026-10-26. Seat: code (11355). Workdir: /home/claudecode/Games/gatewardens (git main, BASE = HEAD at session start).

## Verdict: BLOCKED — scripted deterministic hard WIN is infeasible on the pinned build

Per the brief's declared fallback ("If hard WIN proves infeasible under honest
constraints after further bounded attempts, declare BLOCKED with evidence rather
than tamper with data/harness"). No product commit was made: a committed fixture
row must carry ok:true on every out row (fixture contract + test_sim_golden shape
leg), and the engine cannot be driven to a hard win with the pinned mechanics —
committing the loss leg would be a contract violation, not a deliverable.

## What is proven (VERIFIED this session)

1. NORMAL fixture UNCHANGED and byte-identical:
   - file sha256: f0473c1ce447938aa6b5b8cb888c9be71c579a1e51142ec11f9b155d54380f23
   - out-stream sha A/B (two fresh replays, byte-equal):
     8ea42737bc4a96249246fbf158a64beb79c90ff2aaf9c1722089065ad43528af
     (matches the recorded UNCHANGED prefix 8ea42737…)
   - replay rc 0, stderr empty, all rows ok:true, win tick 20353 wave 10.
2. Tampered-red leg (mutation gate, normal fixture seed 11326→11325):
   replay out-stream DIVERGES from the golden (stream != committed; the golden
   byte-equality leg goes RED). The gate can fail; it is a real gate.
3. Hard draft (best honest build, deterministic, all 23 in-rows land ok:true):
   - out-stream sha A/B (two fresh replays byte-equal):
     cedd59747556436f4563e5eaf8b79318fc0f33ed188cf558ea0a56bc6eedd386
   - outcome: ok:false — loss, tick 10837, wave 5. rc1 with GOLDEN-FAIL bad_rows=1
     (the outcome row is the ONLY bad row; every act applied cleanly).
   - sanity: green dips ONLY at spend rows (w1b 152→2 place+up, w4b 153→3;
     kill income +40/wave + bounties between; bank/tray/loot arithmetic ok).
   - draft: .tmp/hard_draft.jsonl (scratch, NOT in git; reproducible via drive.py).
4. pytest: `python3 -m pytest tests/ -q` → 190 passed, exit 0 (normal golden legs
   untouched). check_hygiene.py → 0 hits (exit 0).
5. Tree clean: git status shows only .audits/ (evidence); enemy_runner.gd diff = 0
   (temporary REACH instrumentation restored via git checkout after each probe);
   zz_probe_tmp.gd deleted; no temp files under godot/; sim_headless.gd diff = 0
   (NO genuine harness gap found — difficulty IS honored:
   sim_headless.gd:90 passes header["difficulty"] into mission.setup).

## Why hard is unwinnable with the pinned mechanics (mechanics VERIFIED by probe/data)

- Main core 1800 hp, breach chunk = hp_max*respawn_core_ratio = 450
  (balance.json:6 respawn_core_ratio 0.25; mission.gd:458; core_obj take_damage)
  → FOUR breaches kill. Sub-core dies wave 1 (4 bandits, by design — opens
  lane_g2 from wave 2; g3 walkers afterwards despawn at the dead sub, harmless).
- Towers are pure SINGLE-TARGET nearest-in-range continuous dps
  (defense_obj.gd _fire_tower/_nearest; pierce/slow/splash/stun effect strings
  have NO consumer — "honest inert"). Blockade does not block (lane-walk only).
- Hero is the ONLY anti-air finisher: static base stats (no in-mission XP
  scaling — xp goes to account meta via state.add_hero_xp; hero_combat reads
  static hero["base"]); deadeye ≈102 dps single-target; storm = 16 s cd AoE 5
  around hero; nova/meteor/focus are AoE-Around-Hero (hero_combat.gd:92
  _in_range(pos,aoe)) — no aimed nukes. Moving hero off the core LOSES the
  point-blank finish role (probe-verified: every main-lane path ends at [0,0,0];
  plaza/south/g3-camp hero positions all regressed — v13–17, v34, v35).
- Sell refunds 0 (full hp → missing_ratio 0); repair never needed (nothing
  damages defenses in v1). Upgrades are NOT phase-gated (only place is,
  defense_placer.gd:108–110 vs upgrade:130) — exploited in the drafts, irrelevant
  to the wall.
- Income cap ≈ 1600 green/run (bounties 2–8 + 40/wave + chests; g3 walker
  harvest is razor-marginal at T1: exposure 125.2 vs bandit 125 hp — probe-
  verified). Total buyable ≈ 6–7 tower tiers deep + walls.
- The wall = wave 4 double-flood vs arrival rate: 10 skitterlings (g1, speed 5.0,
  1/s) + 5 wisps (a1) + 3 harpies (a2, 200 hp) arrive over ≈24 s = ≈250 hp/s
  arrival vs wave-4-capable ≈180–215 dps (towers ≤ ≈110 + hero 102 + storm
  ≈20 avg). Nearest-target starvation: each tower's own-lane walkers sit CLOSER
  than air on the crossing lanes, so air chip lands ≈half of model — REACH-probe
  rows (hp at core arrival): lane_a2 harpies reached with 87.3/149.9/179.7 and
  115.4/175.3/80.0, a1 wisp 7.2 — chips 20–115 vs 200/80 hp. 2–3 leaks at wave 4
  + 1–2 at wave 5 = 4 breaches = dead, EVERY doctrine tried (≈65 engine runs):
  choke walls, dual spawn-fortresses (T4/T5 ladder), south double-camp, g3
  harvest at wp0/wp2, endpoint T3 anti-air, embercaller AoE doctrine, warden
  swap-flood pattern, storm re-aim (release/re-press per combat), plaza/south/
  g3-camp hero positions, upgrades-mid-combat, greedy doctrine-ordered ladders
  with fixed-point drop-rerun (all spends ok:true).
- Deterministic: seed scan of the same script {11355,11356,11357,11358,11359,
  11326} all die at wave 5 (10697..10837) — not RNG.
- Escalation math: total main-bound walkers over waves 1–11 ≈ 185 units; hero
  mill ceiling ≈ 0.45–0.5 units/s; tower income buys ≈ 150–170 late dps; 4-
  breach budget requires ≥98% kill rate including the starvation-pressed wave
  4–5 air groups — arithmetically unreachable under the pinned single-target
  mechanics.

## Declared gaps (brief items)

- Ascension: not expressible in-rows — the fixture act vocabulary is pinned
  (input/place/upgrade/repair/sell/assign/unassign/hotswap; assign/unassign are
  act_unpinned in this runner, sim_headless.gd:212). NO ascension act exists;
  the harness was NOT extended (harness unchanged).
- Harness: UNCHANGED (no genuine gap found; loss is mission design + mechanics,
  not a harness defect). No data-file edits, no balance literals touched.
- The hard fixture + hard test legs were therefore NOT committed (contract
  violation to commit a loss leg). The extension to tests/test_sim_golden.py
  (hard shape/byte-equal/two-run/tampered legs) is specified in this file and
  ready to land the moment a winnable path exists.

## Exact failing state (reproducible)

    cd /home/claudecode/Games/gatewardens
    XDG_DATA_HOME=$(mktemp -d) /home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64 \
      --headless --path godot -s res://sim/sim_headless.gd -- --fixture "$PWD/.tmp/hard_draft.jsonl"
    # rc=1, GOLDEN-FAIL bad_rows=1 (outcome row only), outcome: lose wave 5 tick 10837,
    # out-stream sha cedd5974… stable across runs.

Decision needed from the orchestrator (pick one): (a) accept a balance/data
change (e.g. respawn_core_ratio, a wave-4 composition trim, or giving one tower
a real AoE consumer) — that is a DATA decision, out of this seat's scope;
(b) accept a harness/mechanic extension (AoE consumer for pierce/splash) — the
W15 brief forbade touching data/mechanics here; (c) re-scope the card to the
loss-leg evidence as-is.

Readings: economy green at every build + spends land ok:true (2536 place g2wp3
152→52, 2686 up 52→2, 4081 up, 7628 place 153→53, 7778 up 53→3…); bank/tray +
chest arithmetic ok (bank check arithmetic 0==0+… consistent on this loss leg;
normal win-leg bank_is_tray_plus_chest holds true); boss never engages (dead by
w5) — boss_neutralized:false is an honest loss-row field, never faked; every
act row ok:true.

VERIFY_EXIT=0
