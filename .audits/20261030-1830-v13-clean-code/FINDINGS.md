# Clean-code audit — Gatewardens post-v1.2.1 (MC 11721, findings-only) [type:plan]

Target: `e013a4b` (main, `git describe` = `v1.2.1-1-ge013a4b`) — v1.2.1 tag + G5-follow-up + R close.
READ-ONLY: zero repo edits (`git status` clean before/after; the only repo writes are THIS dir).
Instruments: the gate itself (`tools/check_hygiene.py`, read FIRST, its walk() = the universe),
my own census (`/tmp/hygiene-11721/census.py`, same walk dirs/SKIP_DIRS/CODE_EXTS/ceiling-class,
LOC = the gate's `text.split("\n")` metric at check_hygiene.py:200, + the two `tools/*.sh` the card
names), greps quoted per row. Pre-reads: `.audits/20261028-0758-clean-code/FINDINGS.md` (§5 pins
carried), `.audits/20261029-2100-v121-plan/V121-PLAN.md` §3 (constraints honored).
Depth proxy note: this run counts block indentation (tabs / 4-space runs, comment+blank lines
excluded). The prior audit's "mission.gd depth 12" is a different instrument — it counted a
51-space COMMENT-alignment row (its line 54); the true deepest CODE block in mission.gd is depth 4
(`sed`-verified: `\t\t\t\tand float(spawn_queue[0]["at"]) ...`). Carried numbers are re-measured,
never copied.
Length reason (file hygiene): one run's finding rows belong to one artifact; the seven DoD sections
are read together — kept whole, under 300 lines anyway.

## BASELINE (measured FIRST, this session)

- `python3 tools/check_hygiene.py` tail: `note: tools/check_hygiene.py 270 lines > soft 250` /
  `check_hygiene: 0 hit(s)` — **EXIT=0, 0 hits**; 12 soft-250 notes + sanctioned-draw notes.
- `python3 -m pytest --collect-only -q | tail -1`: **`283 tests collected in 0.35s`** — matches the
  README/RELEASE_NOTES "283 green" COUNT. (Full-suite green NOT re-run here — UNVERIFIED again at
  this tip, collection only. The prior audit's load-fragility SZ-1 row measured CLOSED:
  `tests/conftest.py:42` now `timeout=900` — raised 300→900 by clean-code W1 (commit 921c687,
  2026-10-28), ≥ the 6m10s worst-case wall that row measured.)
- Census (`census.json`, this dir): universe 114 files (.gd/.py + 2 .sh); 40 non-test `scripts/`+`tools/`
  sources, 37 sim kits, 35 tests.

## 1. SIZE (instrument: census.py = the gate's walk + ceiling class; gate verdict reconciled below)

**Hard class: NONE. Zero non-test source files > 400 LOC; zero files > 600; zero `# hygiene:`
header-exempt files exist** (`grep -rln "^# hygiene:" --include=*.gd --include=*.py` over godot/tools/
tests/server → empty; so no header buys any ceiling today). Gate and sweep AGREE (0 hits each side) —
no gate-vs-sweep finding.

NOTE rows (the zero-headroom and soft-zone set, measured `census.json`; depth = block nesting proxy):

| file | LOC | depth | note |
|---|---|---|---|
| godot/scripts/mission.gd | 400 | 4 | AT the 400 ceiling — cards still add ZERO lines (carried W4-watch row, still true) |
| godot/scripts/game_state.gd | 396 | 4 | 4 lines from ceiling (v1.2 F2 sell_bank grew it 365→396) |
| godot/scripts/hud.gd | 385 | 4 | grew 328→385 with G8 coach; 15 lines headroom |
| godot/scripts/defense_panel.gd | 371 | 4 | post-S 277, regrew +94 with G5 |
| godot/scripts/defense_placer.gd | 336 | 4 | G4/G5 additions |
| tests/test_data_schemas.py | 600 | 12 | AT the tests-600 ceiling — next leg added goes gate-RED (no header exempt exists) |
| tests/test_mission_clicks.py | 600 | 15 | AT the tests-600 ceiling, deepest file in the repo — same |
| tests/test_hub_scroll.py | 568 | 10 | soft |
| godot/sim/g4_range_ring_probe.gd | 358 | 6 | kit = NOTE row (largest kit, G4 wave) |
| godot/sim/sim_headless.gd | 317 | 7 | kit NOTE |
| godot/sim/v6_tween_probe.gd | 313 | 9 | kit NOTE (carried) |
| godot/scripts/defense_obj.gd 306 / hub.gd 290 / tools/check_hygiene.py 270 / godot/scripts/fx_director.gd 261 | — | — | soft-zone carry/NOTE |

## 2. DUPLICATION (one mechanism per concern; v1.2.1 files audited file-by-file)

Single-homes VERIFIED intact (each by quoted grep): `Label3D.new` — only `world_text.gd:23`
(grep over godot/); the 100px=1u scale formula — only `sprite_bank.make_sprite` (prior D-1 CLOSED:
`fx_director.gd:222` now `SPRITE_BANK.make_sprite(fx_id, h)`); the ONE placement application site —
`m.place_defense(` in scripts/ = `defense_placer.gd:256` alone (probes/harness call the mission API
directly by the declared harness license); `STRUCT_VALS`/`GOVERNED_LITERALS` one home (tests import:
`test_hud.py:31`, `test_hub.py:43`, `test_mission_smoke.py:36` `import check_hygiene as hyg`);
bridge input one feed point (the JS relay + native forwarder both route `bridge.on_key`, the
edge-trigger fix lives INSIDE that chokepoint — bridge.gd:58-66, not a second mechanism);
`GOVERNED_LITERALS` = the declared set, 17 entries (not duplication, it's the one home — but see
CR-1 for the doc that stopped counting it).

- **D-1 (P4, both sides cited):** the lit-translucent ground material (unshaded + TRANSPARENCY_ALPHA
  + albedo_color — byte-shape identical three assignments) has two builders:
  `godot/scripts/lane_bands.gd:81-86` `_band_material()` and `godot/scripts/range_ring.gd:93-98`
  `_ring_material()`. Each header claims "the ONE material shape"; repo-wide it is the SAME mechanism
  hand-rolled twice (color apart). Fix = one tiny shared builder (new presentation file or sprite_bank
  sibling); measure = one builder instead of two, LOC −4.
- **D-2 (P4, both sides cited):** the raw-`m.map_def` lane→spawner/"air" grouping reads a SECOND home:
  `mission_world.gd:108-111` (`air[String(lane.get("spawner"...))]` dict for the gate-eye wing) vs
  `wave_telegraph.gd:94-112` (`lane_rows` map, reads the same `"spawner"`/`"kind"` raw keys to group
  counts). Same public read of the same dropped-by-build_lanes key, two implementations. Fix = one
  shared read (mission_world is the natural home — telegraph already preloads mission-side modules);
  measure = dead-count −1 grouping site.
- **D-3 (P4, note-class):** v1.2.1 shipped the FOURTH inline by-id linear scan over a tables array:
  `hero_pawn.gd:86-90` `hero_name` (rows("heroes")) beside pre-existing `dummy_range.gd:67` and
  `mission_heroes.gd:15` (and `defense_placer.row_for_id` for towers). `GWTables` (sim_tables.gd)
  ships no `by_id` door — the door is the place this belongs. Not forced: pattern pre-dates v1.2.1.
- NOT duplications (declared and holding): the G2/G4 PrimitiveMesh choice is a mechanism LESSON shared,
  not a mechanism; PRESS map (panel) vs DISCRETE_KEYS (bridge) are relay-vs-routing; the telegraph's
  `_process` diff is the fx_director OBSERVER idiom reused (declared in-plan §G3).

## 3. DEAD CODE (grep-verified; S-split and G5 retargets checked for stranding)

- **DC-1 (P3): `defense_panel.gd:135` `selected_tier()` — ZERO callers.** Instrument:
  `grep -rn "selected_tier" godot tests --include=*.gd --include=*.py` → the def + ONE prose mention
  (`defense_placer.gd:162` comment). `git log -S "selected_tier(" --oneline` lists ONLY its creation
  commit (26575a1 W8) — a caller never shipped; it is the display-tier convention's named-but-unused
  accessor. Fix: delete + keep the comment's convention sentence pointing at `GHOST_TIER`/`tier_range`;
  measure = dead-count 1→0 (−5 LOC).
- **DC-2 (P4): the `MouseMiddle` relay leg has no consumer.** `grep -rn MouseMiddle godot tests tools
  --include=*.gd --include=*.py --include=*.html` → exactly two hits, both the relay's own tables
  (`bridge.gd:23` DISCRETE_KEYS, `:41` MOUSE_CODES); nothing routes it (panel PRESS has no entry).
  Pre-existing since the W4 relay, not v1.2.1-stranded. Check pin #7 (test_bridge_contract main.gd/
  shell tokens) BEFORE removing — it is relay surface. Measure = dead-count −1 code path.
- **SPLIT/G5 stranding: NONE found.** The S split left no wrapper behind (`defense_panel.gd` rows calls
  all route `rows_ui.*`; `test_mission_stale.py` retargeted, :173 `_p().rows_ui._rebuild_defense_rows()`).
  The G5 retargets stranded nothing live: `place_selected` (KeyM-legacy :148 + place route),
  `row_for` (`place():226` + `mission_smoke_w8.gd:38`, `test_lane_order.py:102`),
  `first_free` (`_arm():266`, tests), `slot_at` (`sim_headless.gd:203`, smoke), `occupied`/`classes`
  (internal + panel:104) all have callers (greps this session).
- **Uncalled-function sweep** (repo-wide, code-only corpus, parenless Callable refs + `connect` +
  test source-greps triaged): the only true zero-reference function is DC-1; `_on_*` handlers,
  `_at_rest`/`_release` (ui_tween `connect`s :55/:66), `_by_at` (`sort_custom(_by_at)` mission:314),
  `_fire_*` (dispatch dict), `_on_frame` (`process_frame.connect`, shot kits) all ALIVE by
  parenless/dynamic reference — each verified by quoted grep above.
- **Kit census:** every `godot/sim/*.gd` kit is pytest-referenced, transitively preloaded
  (`hub_probe.gd:30-33`, `mission_smoke.gd:31-32`), a documented manual leg (ARCHITECTURE §Verification
  kits for the v*-shot/v*-probe family), or ARCHIVED-with-label
  (`godot/sim/archive/v11_shot3.gd` first line `# SUPERSEDED — DO NOT USE`, test scan excludes the
  dir: `test_damage_numbers.py:454`). `g5_real_relay_probe` refs = a REAL leg
  (`test_g5_build_confirm.py:227-232 RELAY_PROBE`). **DC-3: none found beyond DC-1/DC-2**
  (instrument: kit×refs census + the sweep above).

## 4. CLAIM ROT (docs vs shipped code, post-R doc-sweep)

The R commit's doc-sweep (`git show --stat 9cbead9` = README + RELEASE_NOTES only — ARCHITECTURE.md
NOT touched by it) is where these survived:

- **CR-1 (P2): the governed-set count is stale — doc says 16, the gate ships 17.**
  `python3 -c "import check_hygiene...len(GOVERNED_LITERALS)"` → **17** (`defense_rows_ui.gd` joined
  at the S split, pin #10 honored in the gate). ARCHITECTURE claims **":210 the 16 governed gameplay
  files (…16 names…)"**, `:243` "the 16-file set", `:184` "NOT in the I2 16-file governed set".
  Three contradicting rows; fix = 17 + the list gains `defense_rows_ui` (replace-not-delete).
  Measure = doc-vs-gate grep agreement (today `grep -c 16-file docs/ARCHITECTURE.md` = 3 stale hits).
- **CR-2 (P3): ARCHITECTURE Modules table never learned v1.2.1 (nor v1.1's observer).** `grep -c`
  over docs/ARCHITECTURE.md: `lane_bands` **0**, `world_text` **0**, `wave_telegraph` **0**,
  `range_ring` **0** — four shipped scripts with no Modules row; `fx_director` appears only inside
  I7 (:248) — no row either (gap predates v1.2.1 — prior audit missed the CLASS, not the row).
  Stale rows: `mission_world.gd` (:176 "C7 map build + C5 core mirror" — owns now ALSO paint_arena,
  core emblem, `paint_spawn_gates` G1, `LANE_BANDS` G2 hook per its own header) and `hero_pawn.gd`
  (:181, no G7 crest/WORLD_H_HERO); the Scenes paint story :197-201 stops at v1.1. Fix = same-commit
  doc wave adding/rewriting these rows. Measure = the four greps 0→≥1, rows current.
- **Carried rows RE-MEASURED CLOSED (instruments):** prior CR-1 bombard T3 — FIXED
  (`sprite_bank.gd:92-93` `"bombard": {2:…T2.png, 3:…T3.png}` + header :10-12 rewritten W2);
  prior CR-2/CR-3 mission_world claims — FIXED (`mission_world.gd:48-51` "bank-null fallback material
  only", :141-142 icon_core "IS committed").
- **Claims VERIFIED TRUE at tip:** README "283 pytest green" count == `283 tests collected`;
  LEDGER:16 "confirm falls to first free slot" still TRUE post-G5 (`place_id:252-253` first_free
  fallback is the pinned standing behavior); the W17f row LEDGER:71 is the round-robin slot-order
  card (order still shipped, `_build_slots` round-robin intact); RELEASE_NOTES:204 carries the
  SUPERSEDED marker for the replaced press-place claim; "239 collected" era claims superseded by the
  dated chain 222→239→283, each tagged. **Full-suite 283-green re-run: UNVERIFIED this session**
  (collection count only; see BASELINE — the prior SZ-1 load-fragility row stays open).

## 5. REFRAGILITY — zoom-control pins the next owner-approved spec MUST build ON

(The three LOCKED camera items below are also §7 — named here as the zoom spec's inputs, per this
card's DoD. Re-pin #3 is SPENT, V121-PLAN D1/C-2: ANY row below moving needs a NEW owner grant.)

- **RF-1 `tests/test_hub_layout.py:337-342`** the `_cam_from_tscn` regex leg over
  `[node name="CameraRig"] transform = Transform3D(…)` + the frustum math at `:331 FOV_DEG = 75.0`,
  `:333 MARGIN = 0.92`, `_in_frustum :365-379` — every waypoint/core/spawner must project inside 92%
  of the half-FOVs. A zoom-IN crops a point → leg goes RED. The zoom spec's contract IS this gate.
- **RF-2 `tests/test_hub_layout.py:398-402`** the planted-red replace-TARGET string, the current rig
  row verbatim: `"transform = Transform3D(1, 0, 0, 0, 0.669, 0.743, 0, -0.743, 0.669, 0, 47.47, 42.79)"`
  (carried pin #3, re-pinned ONCE at v1.2 F6, declared LEDGER PIN row — the prior audit's
  `0.667/56.33/44.14` row measured MOVED; drift recorded, not rot). Any camera row edit must edit this
  string IN THE SAME COMMIT or the replace no-ops and `assert planted != read_text(...)` goes RED.
- **RF-3 `godot/sim/v1_world_probe.gd:40 MIN_MARGIN := 60.0`** + the frame-fail leg `:215` — the
  manual kit's twin of RF-1 (byte-pinned kit). Zoom changes margins → this row re-runs RED until the
  zoom spec re-declares the margin once, declared.
- **RF-4 shot kits `v1_world_shot / v5_fx_shot / v11_boss_shot`** capture their frame at the shipped
  D=64/pitch-48 rig; their machine legs assert node class/texture (suite-safe), but every committed
  LEDGER pixel row (v5fx_f92/v112-boss-* frames) is D=64-evidence — a zoom move ages those rows; the
  zoom card re-runs the kits at the new rig before claiming "same reads".
- **RF-5 the zoom-sensitive WORLD constants (NO test hardcodes them — they ride script consts, so the
  suite survives a zoom card; naming them so the spec re-declares each ONCE):** `BAND_Y 0.02`
  (lane_bands.gd:30), `RING_Y 0.05` (range_ring.gd:40) — the ground-ribbon z-fight margins;
  `GATE_EYE_Y 3.0/GATE_EYE_H 5.0` (mission_world.gd:40-41), `CORE_EMBLEM_Y 4.5/H 6.0` (:34-35),
  `BASE_Y 6.5/ROW_GAP 2.6/COUNT_LIFT 1.2` (wave_telegraph.gd:47-49),
  `CREST_Y 2.4/CREST_SHEET_H 1.2/CREST_NAME_DY 0.85/CREST_NAME_H 0.55` (hero_pawn.gd:30-33),
  `WORLD_H_HERO 3.0 / WORLD_H_UNIT 2.0 / WORLD_H_TOWER 4.0` (sprite_bank.gd:105-111). Instruments:
  greps for `0.02|0.05|BAND_Y|RING_Y|GATE_EYE|= 6.5` over tests/*.py + the g*-probes found NO literal
  height pins (hits are unrelated eps/step values); the riding legs are
  `test_hero_crest.py:226` (`absf(o0.y - float(HERO_PAWN.CREST_Y))` — const-read),
  g4 probe data-leg (scale == towers.json range NUMBER), `test_gate_eye.py:105`
  (`body.count("SPRITE_BANK.make_sprite(") == 1` source-truth). The screen-space `v6_tween_probe`
  rect pins are UI-layer: camera-INDEPENDENT, not zoom rows.

## 6. FIX LIST — parallel-safe waves (same-file rows in ONE wave; every row measured above)

| wave | row | sev | file(s) | fix (one sentence) | measurement that must improve |
|---|---|---|---|---|---|
| W1 | CR-1 | P2 | docs/ARCHITECTURE.md :184,:210,:243 | Rewrite the governed-set count and name-list to the gate's 17 (add defense_rows_ui). | grep: 3 stale "16-file" hits → 0; doc count == `len(GOVERNED_LITERALS)` |
| W1 | CR-2 | P3 | docs/ARCHITECTURE.md (same file — SAME wave by law) | Add Modules rows for lane_bands/world_text/wave_telegraph/range_ring/fx_director + de-stale the mission_world/hero_pawn rows and the :197-201 paint story. | the four `grep -c` = 0 → ≥1 each; rows match shipped headers |
| W2 | DC-1 | P3 | godot/scripts/defense_panel.gd (+ comment cite at defense_placer.gd:162) | Delete `selected_tier()` and re-point the tier-convention comment to `tier_range`/`GHOST_TIER`. | dead-count 1→0; panel LOC 371→366; suite green |
| W2 | D-2 | P4 | godot/scripts/mission_world.gd + godot/scripts/wave_telegraph.gd | Move the raw lane→spawner/air grouping into ONE shared read the telegraph calls. | grouping sites 2→1; both feature legs byte-green |
| W3 | D-1 | P4 | godot/scripts/lane_bands.gd + godot/scripts/range_ring.gd | Fold the two identical unshaded-alpha material builders into one presentation-file builder. | builder sites 2→1; LOC −4; band/ring probes byte-unchanged |
| W3 | DC-2 | P4 | godot/scripts/bridge.gd | Drop the `MouseMiddle` relay entry (codes table + mouse map) — after checking pin #7 covers the shell tokens, not this row. | dead relay path 1→0 |
| W4 | RF-1..5 | — | NO FILES | Zoom-spec input list (§5): the camera card re-pins RF-1/2/3/4 ONCE each, owner-granted, and re-declares each RF-5 const once. | per-pin LEDGER-declared drift, never silent |
| W4 | SZ | — | NO FILES | Watch: mission.gd 400 (zero-line rule), game_state 396, hud 385; test_data_schemas/test_mission_clicks AT the 600 test ceiling — the NEXT leg in either forces its split first. | LOC deltas at the next growth card |
| — | prior SZ-1 | — | tests/conftest.py:42 | **CLOSED, re-measured this session: engine-leg timeout now 900s (raised 300→900 by clean-code W1, 921c687 2026-10-28), ≥ the 6m10s worst-case the prior audit measured — no FIX row remains.** | was: timeout margin vs measured wall — margin now 900s ≥ 370s+ |

W1 ∥ W2 ∥ W3: file-disjoint (docs / panel+world+telegraph / bands+ring+bridge). A W2/W3 same-file
collision means neither pair runs together; the suite + hygiene gate 0 stays every wave's accept.

## 7. DO-NOT-TOUCH (byte-pinned; refactor MUST NOT move these — carry of §5-LOCKED ×11, re-measured at tip unless noted)

1. `tests/fixtures/mission_gatefall_normal.jsonl` sha `eafe3932…` / `_hard.jsonl` sha `5e37c4b0…`
   (`sha256sum` this session — match the LEDGER-pinned prefixes; golden legs never regenerate silently).
2. Git tags `v1`, `v1.1`, `v1.2`, `v1.2.1` — NEVER move (four exist: `git tag -l`; v1.1's one
   DA-fix move is the last-moved record, LEDGER DA-fix row).
3. `tests/test_hub_layout.py:337-342` camera regex + `:398-402` planted rig-row literal (= RF-2) —
   re-pin SPENT.
4. `tests/test_hub_layout.py:410-418` WorldEnvironment/ambient/ground-vs-sky literal rows.
5. `tests/test_hub_layout.py` source-text pins: `:312` `slot.add_child(war)` stacking family + the
   `pressed.disconnect`/`call_deferred`/`router.start_mission(` rows — hub/war_table mounting code
   stays in the pinned file.
6. `tests/test_mission_clicks.py:591` ext-rows count pin — **measured DRIFTED 4→5** (G3's declared
   append, V121-PLAN §G3/DA A4.2; the count moves ONLY with a declared scene-script add); `:596`
   planted-uid row; `:31-32` every ext uid == its `.uid` sidecar + stale-pair ban — mission.tscn
   edits remain APPEND-only.
7. `tests/test_bridge_contract.py:111` exact line `host.on_key = _js_relay` + `:116` no-`get_object`.
8. `tests/test_gear_persist.py:252/:260` save-format strings (`'"equipped_json": JSON.stringify(equipped)'`).
9. `tests/test_purity.py:39` EXPECTED_MODULES name-set over `sim/sim_*.gd`.
10. `tools/check_hygiene.py:80-85` GOVERNED_LITERALS (17 paths incl. defense_rows_ui) + STRUCT_VALS —
    the ONE home; `test_hud.py:31`, `test_hub.py:43`, `test_mission_smoke.py:36` import them;
    a governed-file split updates the set IN THE SAME COMMIT (pin #10 — S honored it).
11. `tests/test_defense_boundaries.py:88` MISSION_SCENE path literal (no scene moves).
12. v1.2.1-new, same family: `tests/test_hero_crest.py:394` source-pin `GW_TABLES.new().rows("heroes")`
    in hero_pawn.gd; `tests/test_gate_eye.py:105` `make_sprite(` count == 1 source-truth;
    `test_mission_stale.py` :52-53 `ROWS_GD = …/defense_rows_ui.gd` + `:173` sibling probe-call (the
    S split's declared same-commit retarget — the mechanism's pinned home is NOW defense_rows_ui.gd);
    the `LaneBand_<lane>`/`RangeRing` node-name contracts (BAND_PREFIX/RING_NAME — the probes read by
    name); `MAX_FX = 64` (fx_director.gd:75, RELEASE_NOTES promises it, g*-probes count against it).
13. `godot/sim/archive/v11_shot3.gd` — stays SUPERSEDED-labeled, never deleted (versioned-truth law).

VERIFY_EXIT=0
