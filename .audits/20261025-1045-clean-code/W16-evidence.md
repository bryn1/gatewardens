# W16 clean-code refactor run — evidence (MC 11274.1.28 / card 11384)

Base commit: fa22655da33513f1bda79b7577e9036c3d7ae601 (main). One commit
follows this evidence; its own sha is the commit this file rides in —
the parent message carries it for binding (a commit cannot contain its
own id).

ZERO BEHAVIOR CHANGE LAW — VERIFIED (all legs run THIS session, post-tree):

- Golden anchors, byte-identical pre/post (sha256):
  - mission_gatefall_normal.jsonl file  eafe3932f7d30898… | out-stream 1cbf3f44532f39b8…
  - mission_gatefall_hard.jsonl   file  5e37c4b089209e64… | out-stream d6d2adc30125af2d…
  (fixtures untouched in the diff; golden replay legs green inside the 192.)
- sim/mission_smoke.gd machine rows: post-tree stdout BYTE-IDENTICAL vs the
  pre-change capture (706->154 driver + 3 legs; `.tmp/w16/mission_smoke.out(F)`,
  diff empty; stderr EMPTY both runs, rc=0 both).
- sim/hub_probe.gd machine rows: post-tree stdout BYTE-IDENTICAL vs the
  pre-change capture (673->215 driver + 4 legs; stderr EMPTY, rc=0).
- sim/sim_parse_probe.gd rows BYTE-IDENTICAL (12 modules, SIMPARSE-DONE 12, stderr EMPTY).
- boot_probe: its SNAP row is SAVE-STATE-derived (bank/gold/deck read the
  user:// file), so the honest A/B is clean-boot: pre-change tree (git
  worktree at fa22655) vs post-change tree, fresh temp XDG dir each ->
  BOOT rows BYTE-IDENTICAL, stderr 0 bytes both. Fresh-dir determinism
  proven x2 post-change.
- save_probe: rc=1 (BN4 two-call idiom) + rows BYTE-IDENTICAL vs BEFORE.

Per-finding BEFORE/AFTER (LOC = hygiene count = wc+1; NEST = max leading
tab depth — the nesting proxy):

| finding | file | before LOC/NEST | after LOC/NEST | verdict |
|---|---|---|---|---|
| F1 exemption abuse | sim/mission_smoke.gd | 707/4 (# hygiene: header) | 154/4 (no header; legs 159+236+182) | SPLIT, all ≤250 |
| F1 exemption abuse | sim/hub_probe.gd | 674/4 (# hygiene: header) | 215/4 (no header; legs 84+190+111+185) | SPLIT, all ≤250 |
| F1 header-exempt sweep | scripts/mission.gd | 564/4 (# hygiene:) | 400/4 (no header; collabs 77+83+65) | SPLIT; 400 = hard ceiling exactly, soft-250 note kept — the root carries the 24 C5-readable fields + the pinned place_defense/HUD/panel hook lines the source gates read (accepted, declared) |
| F4 array-door copies | mission.gd _load_array | 4 call sites + 6-line door | 0 (GWTables.rows) | DEDUP |
| F4 array-door copies | defense_placer / blacksmith_ui / dummy_range / hub_probe._rows | 1 + 2 + 1 + 4 call sites + 4 doors | 0 (all ride sim_tables.rows, ONE door) | DEDUP (game_state._roster_ids STAYS raw — the W13 seeding amendment, comment made true) |
| F4 search-loop copies | hero_combat._nearest/_in_range, defense_obj._nearest | 3 identical loops | ONE loop in enemy_runner.nearest/in_range; 3 thin delegators | DEDUP |
| F4 list-build copies | blacksmith_ui.refresh / tinkerer_ui._fill x2 / gear_panel_ui.refresh / defense_panel relic leg | 4 identical 6-line builds | ONE loop in scripts/bank_list.gd (25 L); 4 call sites (test_hub gate moved: users must preload bank_list.gd, bank_list preloads item_row.tscn; planted-red duplicate-renderer leg unchanged and still RED-capable) | DEDUP |
| F3 gate gaps | tools/check_hygiene.py | 220/0: no i2 rule, exemption uncapped | 268/0: [i2-literal] rule over 16 governed files + ABS 600 cap on header exemptions + STRUCT_VALS/LITERAL_RE ONE home | NEW RULES (below, planted-red) |
| F3 STRUCT_VALS home | tests/test_hub.py, tests/test_hud.py, tests/test_mission_smoke.py | 3x copied set + regex | 0x copies — all import check_hygiene (semantics unchanged: the tests' 40 legs green, blank_code idempotent where inputs arrive pre-blanked) | DEDUP |
| F2/F5 stale rows | docs/ARCHITECTURE.md | validate_probe row, "NO start" economy row, validate() myth, loot_pickup file row, test_waves name, test_hygiene name, scenes wish-list, js-phrase, game_state mutator list, harness list, mission/item_row rows | TRUE rows (starter W13/865b668; sim_parse_probe+boot_probe+smoke+hub rows incl. W14 legs cite 1067391; loot = mission.step_loot+toast W11; bank_list/mission_world/mission_heroes/mission_relics/hero_pawn rows added) | TRUTH PASS |
| F5 comment polish | main.gd boot blocks, hud.gd:13, phase_controller :12/:100, game_state :33/:292/:320, defense_placer REFERENCE NOTE, sim_parse_probe header, mission_smoke "price" x3 | trail/validate_probe/price prose | declared readings; pytest-schema-layer truth; cost | DONE |

Size-neutral closures (stated): sim_tables.gd 44->64 (the ONE rows() door
+ header truth — the dedupe TARGET, growth IS the home); enemy_runner.gd
110->137 (receives the ONE search loop); check_hygiene 220->268 (rule +
cap); test files ±5 (delegation). defense_obj 281->275, hero_combat
150->137, blacksmith 188->169, placer 190->180, dummy 118->110,
defense_panel 242->235 shrank.

I2 planted-red (gate can go RED — transcript):
    planted: var _w16_planted_gate_proof := 42.5   # in hero_combat.gd
    run:     python3 tools/check_hygiene.py  -> rc=1
    row:     godot/scripts/hero_combat.gd: [i2-literal] non-structural number literals [42.5] — costs/ratios ride the data (I2)
    restored: hero_combat.gd -> check_hygiene rc=0, 0 hits (transcript files
              .tmp/w16/i2_planted.out / i2_restored.out)

Ceiling-exemption abuse proof (new rule vs the PRE-split tree):
    new tools/check_hygiene.py run over the fa22655 tree (worktree):
    godot/sim/hub_probe.gd:1: [ceiling] 674 lines > 600 — a header exemption never reaches past the absolute ceiling (W16)
    godot/sim/mission_smoke.gd:1: [ceiling] 707 lines > 600 — a header exemption never reaches past the absolute ceiling (W16)
    check_hygiene: 2 hit(s)  (rc=1; .tmp/w16/ceiling_abuse.out)
    post-split tree: 0 hit(s), notes only, mission.gd note lost "(exempt)".

R-list (renames/vocabulary this run applied): mission_smoke W8 comment
prose "price" -> "cost" x3 (comments only — rows byte-identical proves
it); defense_obj "Next ladder rung's price" -> "cost"; "reading on the
trail" -> "declared reading" (phase_controller x2, main.gd, hud.gd,
sim_parse_probe); "declared R-list finding" -> "declared W9 finding"
(game_state); defense_placer REFERENCE NOTE block -> one-line name
contract. No public identifier renamed (pinned crossings untouched).

OPEN findings (measured but NOT in this run's scope — stay open):
P3-12 main.gd:33-36 dead stub; P4-16 golden comparator fragility;
P4-17 dead data fields (slow/block magnitudes); P4-18 save_probe
quit-without-return tail; README stale status line (W17 release rows);
P4-14 monetization-vocab raw-scan alignment (half).

DoD: `python3 -m pytest tests/ -q` -> 192 passed (exit 0);
tools/check_hygiene.py -> 0 hits (rc 0, notes only); ONE commit
(author code (11384)); anchors + machine rows above byte-identical;
I2 planted-red + ceiling-abuse transcripts included.
VERIFY_EXIT=0
