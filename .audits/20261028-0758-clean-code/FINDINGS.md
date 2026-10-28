# Clean-code audit — Gatewardens post-v1.1 (MC 11574, findings-only) [type:hygiene]

Target: origin/main tip `a780837b` (tag v1.1 at the DA-fix tip per LEDGER tag-move row; HEAD==origin/main VERIFIED).
READ-ONLY: no repo edits; scratch `/tmp/hygiene-11574/`; census artifact `size-census.json` (this dir).
Priority per CONFIG: P0 > P1 > P2 > P3 > P4. Doctrine: MC 11318 clean-code-after-milestone.
File >150 L: the DoD names 5 mandatory categories + kit census + WAVES — splitting would scatter one run's rows.

## BASELINE (tails recorded FIRST, this session)

- `python3 tools/check_hygiene.py` tail:
  `note: godot/sim/v6_tween_probe.gd 313 lines > soft 250` / `note: tools/check_hygiene.py 268 lines > soft 250` /
  `check_hygiene: 0 hit(s)` — **EXIT=0, 0 hits — matches the card** (3 sanctioned-draw notes + 2 soft notes).
- `python3 -m pytest -q` tail:
  `FAILED tests/test_hub_scroll.py::test_scroll_reaches_hero_slots_engine_leg` /
  `FAILED tests/test_hub_scroll.py::test_equip_click_path_engine_leg` /
  `FAILED tests/test_sim_golden.py::test_golden_replay_matches_committed` /
  `FAILED tests/test_sim_golden.py::test_golden_is_stable_across_runs` /
  `FAILED tests/test_sim_golden.py::test_golden_red_on_tampered_fixture` /
  **`5 failed, 217 passed in 2081.59s (0:34:41)`** — CONTRADICTS the card's "222 green" claim (measured, this box).
  Isolation (VERIFIED): the golden replay run by hand exited **rc=0, stderr EMPTY, 215 rows — logic green** but took
  **6m10s real / 3.8s user CPU** vs `conftest.py:44` `run_probe_script(timeout=300)`; box load-average 8–12.8 (nproc 14)
  during the run. Class: environment/scheduler stall, NOT sim logic. The suite's green is load-fragile → row SZ-1.

## 1. SIZE (instrument: `/tmp/hygiene-11574/size_census.py`, the gate's own walk + ceiling-class rule)

Universe = gate `walk()` (tools/check_hygiene.py:60-61,168-177: dirs `godot server static tools tests`,
`SKIP_DIRS`, ext `CODE_EXTS`) restricted to `.gd/.py` (the gate's ceiling class, :197) minus `tests/` (non-test law);
`.gd.md`: none exist (find instrument, 0 hits). LOC = `text.split("\n")` — the gate's exact metric (:198).
**Measured: 64 files; >400 LOC: 0; >600: 0; ≤400: 64 (none-listed). 401–600 rows: NONE — none found.**
Soft zone 251–400: 9 files — mission.gd **400 (AT the ceiling, depth 12 — the tightest)**, defense_panel.gd 373,
game_state.gd 365, hud.gd 328, sim_headless.gd 317, v6_tween_probe.gd 313, defense_obj.gd 306, hub.gd 290,
check_hygiene.py 268 (full rows in size-census.json).

## 2. DUPLICATION / second mechanism

- **one implementation per concern HOLDS on all four known mechanisms (VERIFIED, instruments below):**
  - sprite lookup: `scripts/sprite_bank.gd` TEXTURES/TIER_TEXTURES + `texture_for` is the ONLY id->texture map
    (grep `res://assets` over `godot/**/*.gd` → outside sprite_bank only `.tres` mesh/material preloads + sim-kit
    path pins, §3). No second id->texture dict in scripts/.
  - tween/scale: `create_tween` appears ONLY in `scripts/ui_tween.gd` (:48,:79) — zero Tween refs in any other
    script (grep instrument). hub.gd:52 + defense_panel.gd:47 both preload the one mechanism.
  - fx creation: `fx_director.gd:_spawn_fx` (:187) is the only visual-fx node spawner; the other `.new()` spawners
    (defense_obj:291, enemy_runner:59, mission_world:91,117 greybox MeshInstance3D; hud:174 TextureRect;
    sprite_bank:115 the shared make_sprite) are not fx paths.
  - timing/format: `*_text()` helpers exist only in hud.gd (:192-241); `%02d`/`pad`/fmt-helper grep = 0 hits repo-wide.
- **D-1 (P3, two sites cited):** `godot/scripts/sprite_bank.gd:118` `s.scale = Vector3.ONE * (world_h / (float(tex.get_height()) / 100.0))`
  vs `godot/scripts/fx_director.gd:197` `s.scale = Vector3.ONE * (h / (float(tex.get_height()) / 100.0))` — the 100px=1u
  scaling formula is hand-rolled a second time beside the ONE factory (fx_director:184's own comment says "like make_sprite").
  Fix rides W1 (make `_spawn_fx` call `SPRITE_BANK.make_sprite`).
- **D-2 (not a finding — LOCKED, two sites cited):** probe kits pin raw sheet paths beside the bank —
  `godot/sim/v4_icon_probe.gd:22-31` (ICON_PATHS) and `godot/sim/v1_world_probe.gd:42-44` vs `godot/scripts/sprite_bank.gd:22-70`
  (TEXTURES). Deliberate by the fleet lesson recorded in LEDGER:80 ("pins are concrete committed RESOURCE PATHS,
  never the mechanism as oracle"): the probe must not ask the bank what it claims. NOT duplication to remove.

## 3. DEAD CODE

**Probe-kit census (godot/sim/, gate-LOC + depth; "pytest" = referenced by a tests/ or tools/ file, VERIFIED grep).**
Harnesses/probes are entry points (`-s res://sim/X.gd`), so "uncalled" for them = unreferenced by ANY test/tool/prose file.

| kit | LOC | what it proves (header) | pytest ref | recommend |
|---|---|---|---|---|
| boot_probe.gd | 78 | Main.tscn boots headless to hub (W5) | 3 files | KEEP |
| gw_compose.gd | 52 | core-trio ONE wiring (F2-5) | 7 files | KEEP |
| hub_probe.gd (+_equip 84/_mission 185/_services 190/_stations 111) | 215 | hub stations/equip/relic/services legs (W9+W16 split) | test_hub.py loads the root (legs preload-transitively, hub_probe.gd:30-33) | KEEP — all legs live |
| mission_smoke.gd (+_flow 236/_swap 182/_w8 159) | 154 | mission flow/swap/defense legs (W6-W11+W16) | 7 files (root) | KEEP — all legs live |
| save_probe.gd | 195 | save round-trip, fresh-process B-leg (BN4/I5) | 8 files | KEEP |
| sim_parse_probe.gd | 47 | parse leg, every sim module, stderr=true signal | test_purity.py:79 | KEEP |
| sim_headless.gd | 317 | C12 golden replay runner | test_sim_golden.py | KEEP |
| sim_tables/economy/combat/wave/inventory/loot/progression.gd | 64/36/72/31/166/129/61 | pure sim modules (NOT kits — game code) | via sim + game preloads | KEEP |
| v11_sprite_probe.gd | 215 | sheets+tier+gate-art+boss path-pinned render rows | manual per-card (LEDGER:76-78 re-run rows) | KEEP — the sprite contract's only machine leg |
| v4_icon_probe.gd | 211 | 8 icon ids resolve, SHOP/HUD placement, byte texts | manual (LEDGER:80) | KEEP — icons' only leg |
| v6_tween_probe.gd | 313 | tween start/at-rest/mid/settle + rect-pinned geometry | manual (LEDGER:79) | KEEP — motion's only leg |
| v5_fx_probe.gd | 200 | fx counters/cap/settle/teardown, MOUNT row | manual (LEDGER:81) | KEEP — fx counters' only leg |
| v1_world_probe.gd | 223 | arena floor + AABB pinned + core emblem + 33pt frame | manual (LEDGER:82) | KEEP — framing's only leg (also carries test_hub_layout's twin gate) |
| v11_shot3.gd | 96 | first runtime PIXEL proof (MC 11462 close) | none outside sim/ comments + LEDGER | **ARCHIVE** — supersession chain: v5_fx_shot ("the v11_shot3 capture path"), v1_world_shot ("the v5_fx_shot capture path"), v11_boss_shot ("the v1_world_shot capture path") each rerun the SAME capture mechanism + more; v11_shot3's unique legs (button-click boot + mission pixels) exist verbatim in all three successors. Archive keeps git history; the chain is recorded in each header. |
| v5_fx_shot.gd | 121 | fx visible in served frames (tracers/sparks at capture) | none outside successors + LEDGER | KEEP — fx-PIXEL leg (probe counts ≠ pixels) |
| v1_world_shot.gd | 126 | arena crest + fx in one frame | none outside successor + LEDGER | KEEP — V1 pixel leg |
| v11_boss_shot.gd | 130 | boss BILLBOARD pixel proof (DA-fix) | **NONE** (see DC-1) | KEEP pending owner: its boss-sheet pixel leg ONLY this kit has; but see DC-1 |

**DC-1 (P2, measured):** `godot/sim/v11_boss_shot.gd` — the ONLY repo source with ZERO text references anywhere
(whole-repo grep excl. .git/.godot/.audits/.tmp/build: hits only inside built binaries build/Gatewardens.exe + static/index.pck
and its own file; no test, no tool, no LEDGER line, no other kit names it). It still holds a unique leg:
boss-billboard PIXEL proof (:86 "SHOT-FAIL boss node is not a Sprite3D (greybox)") that no other kit or pytest leg
reproduces. Its last recorded run is the LEDGER:84 DA-fix row (gen/v112b-frame.png UNTRACKED). Recommendation:
KEEP + wire it into the suite or a documented per-tag manual leg (owner call which), NOT archive — archiving drops
its unique leg. Do not delete before the owner ruling.
**DC-2 (none found, instrument):** uncalled-function scan (regex `func` defs in all `godot/scripts/*.gd` + `godot/sim/*.gd`,
searched for `name(`/`.name(`/`"name"` across .gd/.tscn/.cfg/.py/.json/.md/.html/.js/.tres incl. same-file callers) —
**0 uncalled** (engine virtuals excluded).
**DC-3 (none found):** orphan modules in scripts/ — every `godot/scripts/*.gd` has a res:// ref or class stem outside self.

## 4. CLAIM ROT

- **CR-1 (P1, file:line + contradicting fact):** `godot/scripts/sprite_bank.gd:11-12` — header claims "bombard T3 has no
  committed skin -> reads T1". CONTRADICTED: `godot/assets/v11/tower_bombard_T3.png` IS committed (git log: 50d59e2
  "bombard T3 tier skin", 2026-10-27) — yet `TIER_TEXTURES` (:82) has NO `"bombard" 3` entry, so at the live tier-3 the
  tower still renders T1. Two-horned: a stale false claim + an actually-missing wiring (the committed skin is dead weight,
  shipped in the pck, never displayed). Fix = add the entry OR state why unwired; update the header either way. (The
  header itself postdates the asset: last touched eccd5d6 2026-10-28.)
- **CR-2 (P3, file:line + contradicting fact):** `godot/scripts/mission_world.gd:38-39` — comment says `mat_ground.tres`
  "on disk stays the greybox". CONTRADICTED: `docs/ARCHITECTURE.md:63` and LEDGER:84 state "no shipped id is greybox
  since the DA-fix boss sheet" — mat_ground.tres IS the greybox fallback material the bank-null path uses, but calling the
  ON-DISK ground material "the greybox" while the V1 runtime override ships every boot reads stale to a newcomer; and
  `godot/scripts/mission_world.gd:99` "no committed sheet" for `icon_core` is FALSE (icon_core.png committed and wired
  at sprite_bank TEXTURES) — the sentence's conditional ("no committed sheet, no child, no crash") describes a null
  case that no longer exists for the ids it rides. Reword-only.
- **CR-3 (P3):** `godot/sim/v11_boss_shot.gd:16` "a greybox frame cannot pass quietly" + `docs/ARCHITECTURE.md:228`
  ("greybox meshes only in v1") — fine in context but see CR-1: with T3 unwired the docs' blanket "shipped = sprited"
  story has the same hole; sweep in W2 must re-grep `greybox` after the CR-1 fix (replace-not-delete law).
- Clean (instrument: grep `greybox` 30 hits + `no committed sheet` 3 hits + probe headers read; boss sheet assets
  `ls godot/assets/v11`): the OTHER greybox mentions (hero_pawn, defense_obj, probe rows) all correctly describe the
  null-fallback MECHANISM (kept by design, ARCHITECTURE:63) — not rot. v11_sprite_probe's boss leg is CURRENT
  (path-pinned `boss_sheet=1`, :179-183). No "no committed sheet" text left true-but-about-a-committed-id except CR-2's.

## 5. REFACTOR-BLOCKING TEST SMELLS — pins, all LOCKED (intentional per LEDGER; refactor waves may not move them)

1. **LOCKED** `tests/test_mission_clicks.py:591` `assert len(_ext_rows(read_text(MISSION_TSCN))) == 4` — the
   mission.tscn 4-script-row pin (3->4 moved ONCE, declared, LEDGER:81).
2. **LOCKED** `tests/test_mission_clicks.py:596` planted-red replaces a real uid row in MISSION_TSCN — follows any uid move.
3. **LOCKED** `tests/test_hub_layout.py:337-341` `_cam_from_tscn` regex over `[node name="CameraRig"] transform =
   Transform3D(...)` + `:398-401` the planted-red literal `Transform3D(1, 0, 0, 0, 0.667, 0.667, 0, -0.746, 0.746, 0, 56.33, 44.14)`
   — rig-string pin (V1 card moved it ONCE, declared, LEDGER:82).
4. **LOCKED** `tests/test_hub_layout.py:410-418` WorldEnvironment/ambient/background/albedo literal rows (mission.tscn +
   mat_ground.tres) — greybox-LIT + ground-vs-sky contrast gate.
5. **LOCKED** `tests/test_hub_layout.py:290-306` — `_stacking_violations` reads hub.gd SOURCE TEXT (`add_child(root_box)`,
   `slot.add_child(war...)`, `VBoxContainer`/`HBoxContainer` ctor substrings): a mission/hub script REFACTOR that moves
   the mounting code must keep these literals in hub.gd itself.
6. **LOCKED** `tests/test_hub_layout.py:318-325` hub.gd `pressed.disconnect(fn)`/`fn.call_deferred()` + war_table.gd
   `router.start_mission(` source-text pins (F-2 single-mechanism).
7. **LOCKED** `tests/test_bridge_contract.py:104-113` main.gd token pins + exact CODE line `host.on_key = _js_relay`;
   `:117` `'call("get_object"' not in main.gd`.
8. **LOCKED** `tests/test_gear_persist.py:251-258` game_state.gd/save_store.gd literal save-format strings
   (`'"equipped_json": JSON.stringify(equipped)'`, `count('"equipped_json"') >= 2`) + planted removal.
9. **LOCKED** `tests/test_purity.py:39,58-60` `EXPECTED_MODULES` name-set over sim/ `sim_*.gd` listing — renaming/moving
   a sim module breaks it.
10. **LOCKED** `tools/check_hygiene.py:78-83 GOVERNED_LITERALS` path-set + tests importing STRUCT_VALS from the gate
    (test_hud.py:40, test_mission_smoke.py:321) — a SPLIT of a governed file must update the set in the same commit.
11. **LOCKED** `tests/test_defense_boundaries.py:88` MISSION_SCENE res:// path literal rides a harness string — any
    mission scene move re-pins it.
    Smell statement for the refactor waves: items 3,5,6,7,8 pin SOURCE TEXT/scene text — splitting those files moves the
    pinned string, so the refactor must keep the pinned literal in the pinned file (or re-pin in the same commit, LEDGER-
    declared, ONCE). `== 4`/`== 12`-style counts (1,3) are structural-count pins: never hand-bump without a LEDGER row.

## FIX-list (wave-splittable; every row MEASURED above)

| row | prio | file(s) | what | measured |
|---|---|---|---|---|
| CR-1 | P1 | sprite_bank.gd:82 + :11-12 | wire bombard T3 entry (or declare unwired) + fix header claim | png committed 50d59e2; map entry absent |
| SZ-1 | P2 | tests/conftest.py:44 (+300s legs) | raise engine-leg timeout margin (300s < 6m10s measured wall here) OR mark load-fragile legs; suite green claim not reproducible under load | 5 failed/217; golden rc0 logic-green, 6m10s real, 3.8s CPU |
| DC-1 | P2 | godot/sim/v11_boss_shot.gd | give the kit a documented home (manual-leg doc or pytest wiring) — zero refs repo-wide; unique boss-pixel leg | grep 0 text refs |
| D-1 | P3 | fx_director.gd:197 + sprite_bank.gd:118 | one scale formula: _spawn_fx via make_sprite | two cited sites |
| CR-2/CR-3 | P3 | mission_world.gd:38-39,:99; ARCHITECTURE sweep | comment reword + post-CR-1 greybox grep-to-zero | cited lines |
| KC-1 | P4 | godot/sim/v11_shot3.gd | archive (supersession chain in 3 headers) | 0 unique legs |

## WAVES (sequential; one code child each; files-disjoint)

- **W1 (P2+P3, tests/ + fx + sprite docs):** conftest timeout margin for engine legs (SZ-1) + D-1 fx scale-formula reuse +
  CR-2 comment rewords. Files: tests/conftest.py, godot/scripts/fx_director.gd, godot/scripts/mission_world.gd (comments).
  Accept: full suite green + v5_fx_probe rows unchanged (counters byte-stable).
- **W2 (P1, sprite):** CR-1 bombard T3 wiring-or-declaration + sprite_bank header fix + ARCHITECTURE/greybox grep-to-zero.
  Files: godot/scripts/sprite_bank.gd, docs/ARCHITECTURE.md. Accept: v11_sprite_probe + v4/v1_world probes green,
  suite 222, hygiene 0, golden fixtures byte-identical.
- **W3 (P2/P4, sim/ kits):** DC-1 v11_boss_shot home decision executed (doc leg in LEDGER/runbook OR pytest wiring) +
  KC-1 v11_shot3 archive (git mv keeps history). Files: godot/sim/v11_boss_shot.gd, godot/sim/v11_shot3.gd(+.uid),
  LEDGER.md/runbook. Accept: hygiene 0, suite green, purity/parse legs green.
- **W4 (watch, no files):** owner call on mission.gd AT the 400 ceiling (depth 12) — W1-W3 must not push it past; if a
  future card needs it over, the split (sim core vs mount helpers) rides its own wave with pins 1-6 of §5 re-pinned once.

VERIFY_EXIT=0
