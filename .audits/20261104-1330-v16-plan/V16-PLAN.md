SUPERSEDED 2026-11-04 (MC 12072 DA-gate-r1 FIX): DO NOT USE — live version: V16-PLAN-c2.md (this dir)
# V16-PLAN — v1.6 "look-and-feel" (MC 12072 · plan seat · 2026-11-04)
PLAN VERDICT: READY-FOR-DA

Base: `1271a6c` = v1.6 kickoff (BEFORE-frames + ratified pillars committed; verified `git log -1` this session). READ-ONLY over the repo except this dir. Versioned-truth: a NEW plan for a NEW milestone — V15-PLAN-c2 stays v1.5 history. Length reason: one plan, one subject (V14/V15 precedent).
Owner direction, verbatim (V16-BEFORE.md:1): "far from a replica... third person, resemble dungeon defenders" — ratified route: LOOK & FEEL FIRST. Clean-room wall: resemble = FORM + FEEL only; original procedural/3090-authored assets, zero Dungeon Defenders art/models/names.

## 0 THE TWO BEFORE FRAMES — what this milestone must move (read_image this session)

Both frames are 1280x720 served captures of the v1.5 web build (`v16-before-build.png` sha256 7b111321…, `v16-before-defeat.png` sha256 02953714…):
- **F-BUILD**: a FLAT checkered tan board (baked `ground_arena.png` — viewed this session: checker
  tiles, grass tufts, rocks, flowers; NO height, NO architecture) floating over a BLACK VOID (the
  void paints at the frame's top edge). Paths = translucent pale arrow-strips (the G2 lane_bands,
  `BAND_COLOR Color(0.55,0.8,1.0,0.30)` — lane_bands.gd:31). Towers = coin-medallion billboards
  (`tower_*_T1.png` via sprite_bank). The hero is a ~8-px speck, crest barely readable at D=64.
  Flat cool ambient (mission.tscn `env_greybox`: ambient 0.6 cool-white, bg `Color(0.055,0.065,
  0.085)`), no shadows read; HUD grey/white default text over translucent dark panels.
- **F-DEFEAT**: same board, "DEFEAT" center, Core 0/1000, RETURN TO HUB — identical flatness.
Every card below cites one of these observations; the LAST wave re-shoots these two poses.

## 1 GOAL + TESTABLE ACCEPTANCE — what the player SEES different in v1.6

v1.5 made the two state crossings sing; the WORLD around them still reads as a flat greybox board
in space. v1.6 = the six ratified pillars (P1 arena-height+fortress / P2 real tower structures /
P3 in-world paths / P4 hero-forward readability / P5 lighting+materials+themed HUD / P6 decor),
shipped as VISUAL LAYERS ON the frozen sim — zero sim/economy/balance/camera-constant movement
(suite ≥ 345 proves the sim never moved; fixtures byte-pinned; camera diff EMPTY).

Milestone acceptance (release-tail leg, orchestrator-driven):
- A1 SERVED (P1): build-phase frame shows a fortress diorama with real height and no void — state
  marker ("Build: wave 1 in…") first, then silhouette census vs F-BUILD + describe-image read.
- A2 SERVED (P2): a placed Ballista reads as a 3D structure standing ON the world, its turret
  visibly re-aims in combat (two-frame crop census moves; kit-spark/tracer fx hooks reused, NOT
  rebuilt); medallions still paint in the panel (UI-only).
- A3 SERVED (P3): the lane corridors read as in-world road; the translucent ghost arrows are GONE
  (alpha-band census at a band segment goes from ~0.30-alpha cyan to opaque road — can go red).
- A4 SERVED (P4): at default D=64 the hero is a readable body (silhouette census + vision read
  "humanoid figure"), clearly so at D=56 (shipped wheel). NO new camera mechanic — 56/128/8 frozen.
- A5 SERVED (P5): warm golden-hour mood on the geometry (shadows read) + themed HUD palette;
  EVERY panel button keeps its exact rect (pixel-judge law: test_mission_clicks geom leg + the
  shipped click-route re-shoot — routes unchanged).
- A6 SERVED (P6): static decor (trees/rocks) sells scale at the board rim, within the declared
  budget (§3 V-F); count leg ≤ budget in-suite; zero RNG (bare-rand law untouched).
- A7 TESTED: full suite green at the final tree ≥ the §5 projection; `check_hygiene` 0 hits;
  `tests/fixtures/` diff EMPTY; GOVERNED_LITERALS 17; mission.gd/test_mission_clicks ZERO new lines.
- A8 VERIFIED pair: the final wave re-captures the EXACT two poses → `v16-after-build.png` /
  `v16-after-defeat.png` beside the BEFORE frames (same 1280x720 viewport, zero wheel events).

## 2 DISPOSITIONS — every candidate row, grounds read THIS session (tree 1271a6c)

| # | candidate row | disposition | grounds (frame observation or repo truth cited) |
|---|---|---|---|
| 1 | **P1 ARENA: terrain HEIGHT + fortress identity, grid frozen** | **SHIP — W1, card V-A** | F-BUILD: flat board in void, no architecture. Shape: the play plane becomes the FORTRESS TOP (stone flagstones) and the height lives OUTSIDE/BELOW the grid — cliff skirt + rim walls + gatehouses at the 3 spawners + keep body under the main core — so placement coords/cells/ranges never move (slots are DISCRETE candidates from `defense_placer._build_slots` — there is NO ground raycast to break; `paint_arena` already never touches the ground transform, mission_world.gd:47-48 comment). Geometry = engine-managed PrimitiveMesh boxes/cylinders ONLY (kb 2d5274003: runtime ArrayMesh NEVER rasterizes on web; G2 lesson pinned in lane_bands.gd:1-20) through the shipped `build_cores` visual-mount hook (mission_world.gd:82-97 precedent). |
| 2 | **P2 TOWERS as real 3D structures, visibly rotating/firing** | **SHIP — W1, card V-B** | F-BUILD: medallion coins = `tower_*_T1.png` Sprite3D via `defense_obj._make_visual` → `SPRITE_BANK.make_sprite` (defense_obj.gd:143 `node = _make_visual()`). Ship: procedural primitive-composed forms per class + tier (new ungoverned file owns all size numbers — I2 keeps defense_obj.gd GOVERNED-clean, BN1 idiom) + a root-LAST aim driver that READS published state only (runner.entities + `bonus_row()` range door — the fx_director/selection_ring observer doctrine, one mechanism family reused). Firing fx = the shipped tracers/spark unchanged ("do NOT rebuild the kit mechanism"). |
| 3 | **P2b medallions survive as UI icons** | **SHIP — rides V-B by exclusion** | HUD/picker icons ride SEPARATE `icon_*` ids in the SAME bank map (sprite_bank.gd:46-53); V-B remaps only the WORLD visual, so `icon_ballista`… stay byte-untouched — test_family_picker/test_icon_states stay green untouched. |
| 4 | **P3 PATHS in-world; ghost arrows retire** | **SHIP — W2, card V-C (after V-A)** | The ghost arrows ARE the G2 translucent bands (lane_bands.gd:31; F-BUILD strips). Ship REPLACE-not-add-beside: the same LaneBand_<lane> node contract + same unit PlaneMesh segments (the web-raster-proven shape) repaint with an OPAQUE baked-road material; `ground_path.png` is COMMITTED AND UNWIRED (sprite_bank.gd:63-66: wiring was blocked because "NO lane mesh exists" — V-C ships the road mesh, so the blocking premise dies; declared premise change). |
| 5 | **P4 HERO body readable (active hero-forward)** | **SHIP — W1, card V-D** | F-BUILD: hero is an ~8-px speck; the pawn is one billboard sheet (hero_pawn.gd:64 `make_sprite(id, WORLD_H_HERO)`). Ship: primitive-composed body per archetype (boxes/cylinders; the per-hero `mat_hero_*.tres` tints REUSED), crest + `hero_name()` door unchanged (P8 legibility shipped). Rides hero_pawn's OWN swap idiom (:67 `: $Visual.visible = false`). |
| 6 | **P4b camera that KEEPS hero+action composed (tracking/pan)** | **OWNER-DECISION — OD1 (§6)** | The ratified grant is ZOOM-ONLY: MC 11719 verbatim "Go 1 and zoom control for 2" (ARCHITECTURE C4), rig basis/default LOCKED (pin #3 SPENT), and V16-BEFORE.md:8 "control law: no new zoom mechanic". Hero-centered composition needs rig TRANSLATION off the frozen LOS line = a pan = not granted. No artifact = no mechanic; this plan ships P4's READABILITY half and files the framing half honestly. |
| 7 | **P5 LIGHTING + MATERIALS (warm low-poly mood)** | **SHIP — W1, card V-E** | `env_greybox` is a 4-value sub_resource (mission.tscn:13-19) and the Sun already ships `shadow_enabled = true` (:33) — nothing was ever themed. V-E edits scene PROPERTY VALUES (warm ambient/bg, sun angle/color) — no new ext_resource rows, no load_steps bump, camera rig row byte-ident. |
| 8 | **P5b themed HUD palette (click contracts frozen)** | **SHIP — rides V-E, second leg** | Pixel-judge law honored: theme = StyleBox/palette builder in a NEW ungoverned file; hud.gd gets ≤ 2 call lines (394/400 measured this session — WATCH row, extract-first rule named: the banner/coach block is the extractable if it tips); button rects must NOT move (test_mission_clicks geom leg :429 is the contract; that file stays ZERO lines). |
| 9 | **P6 WORLD-DECOR, instanced static, perf budget declared** | **SHIP — W2, card V-F (after V-A)** | F-BUILD: scale sellers are baked grass specks in the ground texture only. Decor = static stacked-primitive props placed DETERMINISTICALLY (no RNG — bare-rand ban untouched); MultiMeshInstance3D is the pillar's word but is UNPROVEN on web (kb 2d5274003 class-risk) → V-F leg 1 is a web raster proof with a DECLARED fallback to one-node-per-prop (the lane_bands idiom, proven); budget declared ≤ 40 decor nodes, zero per-frame scripts. Placement needs V-A's rim shape → W2. |
| 10 | 3D bodies for ENEMIES (DD enemies are 3D) | **DEFER** | Not among the six ratified pillars (binding brief list); v1.1 billboards read acceptably (boss pixel-proven, ARCHITECTURE v11_boss_shot row); W1+W2 already carry ~6 builder surfaces — the ceiling. RE-OPENS only on an owner pillar-extension. |
| 11 | Procedural-SKY material / gradient sky (the void) | **DEFER (folded coverage)** | The void is moved by V-A (cliff skirt + ground skirt below the fortress) + V-E (background color) — a ProceduralSkyMaterial is web-UNPROVEN (same class as row 9's MultiMesh); revisit only if the owner wants sky ART. |
| 12 | Minimap | **DEFER — v1.5 grounds stand** | V15-PLAN-c2 §2 row 6: reference's own condition "value arrives when map 2+ ship"; `godot/data/maps/` = ONE file (ls this session). |
| 13 | ready-up / early wave call | **DEFER — not re-filed** | v1.5 OD ended default-if-silent DEFER (RELEASE-NOTES-v1.5.md:125-129); no new owner artifact — re-filing without one would manufacture consent. |
| 14 | per-tower interaction keys (Q/R/Z) | **REJECT — stands** | V15-PLAN-c2 §2 8b: towers.json tiers carry range/dps only — a key paints a mechanism that has no source. |
| 15 | defense hp-tint | **DEFER — stands** | No production caller damages a defense (RN v1.5 deferred-row 1, re-grepped at that tip); a live tint can never paint. |
| 16 | MAX_FX drop-priority re-order | **DEFER — stands** | PINNED cost rule (V15-PLAN §2 8d; RN v1.5 known-limits row); v1.6 adds ZERO fx spawn sites (V-B reuses existing tracers/spark), so saturation math is untouched by design. |
| 17 | a second map / bigger arena | **DEFER** | R4 one-map ruling stands; decor/fortress authored data-driven (reads map_def), so map #2 later costs data only. |
| 18 | zoom constants; 7 fps headless reality; suite/ceiling floors | **CONSTRAINT rows (not cards)** | D_MIN 56/D_MAX 128/STEP 8 frozen (camera_zoom.gd:45-47); ≥600 ms input pacing + state-marker-first (WK2 idiom); suite ≥ 345, mission.gd AT 400, test_mission_clicks AT 600, hud.gd 394/400 (all measured this session, §3 law L1). |

## 3 WAVES — per-card brief sketches

PLAN LAWS riding every card (own git worktree; full suite green AT the card tree + hygiene 0 hits
+ fixtures diff EMPTY; pathspec-only commit; OWN LEDGER row in OWN commit; children never spawn):
- **L1 CEILING LAW** (gate metric `len(read().split("\n"))`, check_hygiene.py:200-212 — measured
  this session): mission.gd **400/400** and test_mission_clicks.py **600/600** = ZERO net lines
  (drivers/visuals mount by CODE via the build_cores hook — the lane_bands precedent — the
  `ext_resource` pin 7 at test_mission_clicks.py:591 never moves); hud.gd **394/400** (V-E, ≤ +2,
  extract-first named); mission_world.gd 172 / sprite_bank.gd 145 / defense_obj.gd 306 GOVERNED
  (V-B ≤ 2 lines, zero literals); camera_zoom.gd + CameraRig row byte-UNTOUCHED (camera diff EMPTY).
- **L2 SERVED-VERIFY-FIRST LAW** (kb 2c3ab44b): engine probes prove nothing about web paint. Every
  SHIP visual card: `bash tools/export_web.sh` → serve `static/` via `server/server.py` (loopback
  127.0.0.1) → headless chromium 1280x720 → shipped clicks at ≥600 ms pacing → STATE MARKER first
  → PIXEL census (distinct-colors / silhouette delta vs the NAMED BEFORE frame, crops named per
  card) → describe-image LITERAL read quoted.
- **L3 PLANTED-RED LAW**: every new check shows it can go RED (staged-first, byte-verified revert);
  a re-pinned assert must show the OLD shape REDDING first (V15 W-K F-B precedent).
- **L4 CAMERA LAW**: the ONLY camera authority is camera_zoom.gd as shipped; D 56/128/8 frozen; no
  card adds pan/rotate/pitch/tracking (OD1 is the only path).
- **L5 TEXTURE/MESH LAW**: textures are committed PNGs + .import, wired through the ONE sprite_bank
  id map, served-proven; NEVER `get_image()`-rebuild anything (kb ab9e1c8b); geometry stays
  engine-managed PrimitiveMesh (kb 2d5274003); no runtime ArrayMesh on any web-painted node.
- **L6 CLEAN-ROOM LAW**: original forms/textures only; no DD names in files, docs, commits or art
  prompts beyond the owner's own quoted words already in V16-BEFORE.md.
- **L7 SIM-CONTRACT FROZEN**: zero edits to sim/, phase data, towers.json, gatefall.json; lane
  reads only (build_lanes records / raw_lane_rows / map_def public reads); fixtures diff EMPTY.
- **L8 LEDGER LAW**: each card writes its own LEDGER row in its own commit; the orchestrator lands
  cards SEQUENTIALLY (pick order declared before each wave); a textual EOF conflict resolves
  KEEP-BOTH (v1.4 F1 / v1.5 §3 precedent). sprite_bank.gd / mission_world.gd are the other shared
  files — same keep-both rule, distinct lines per card (declared §4).

### W1 — four DISJOINT cards, parallel-safe (lane pre-flight `lane-load.sh 4`, orchestrator duty)

**V-A — FORTRESS PLATEAU (P1, the milestone HEART)**
- Files: NEW `godot/scripts/diorama.gd` (static builder: cliff skirt + rim walls + 3 gatehouses +
  keep box under the main core — all BoxMesh/CylinderMesh, presentation consts ON this file,
  ungoverned sprite_bank doctrine); NEW committed clean-room textures `godot/assets/v11/
  ground_fortress.png` (+ cliff/stone sheet; the 3090 artifact lands in the SAME commit as its
  .import); `sprite_bank.gd` (remap `ground_arena` TEXTURES row to the new flagstone PNG —
  replace-not-add, one line); `mission_world.gd` (one `DIORAMA.build_fortress(m)` hook in
  `build_cores`; the paint_arena consumer line rides the remapped id, zero edits); NEW
  `tests/test_diorama.py` (LB-OK probe idiom: node counts/AABB sane, ground plane transform
  byte-pinned, zero-sim-diff source-truth); LEDGER.md row. ZERO mission.gd / camera / fx lines.
- Legs: engine (fortress node count, ground transform byte-equal vs scene row — the grid-frozen
  proof); source-truth (no runtime ArrayMesh, no get_image — grep leg); planted-red (hook removed
  → probe RED). V-A WITHOUT its PNGs lands NOTHING (no fake art, the v1.1 rule; risk 4).
- SERVED (P1): START→mission shipped route; marker = "Build: wave 1 in N s"; census regions =
  TOP-STRIP (void→rim), CENTER (checker→flagstone), CORE-REGION (box→keep); describe-image literal
  read; frames archived in the card's audit dir.

**V-B — TOWER STRUCTURES + AIM (P2)**
- Files: NEW `godot/scripts/tower_forms.gd` (primitive-composed forms for the 5 world ids, tier
  variants = height/additions; a child node `Turret` on the shooters; ALL sizes consts here,
  ungoverned); `godot/scripts/defense_obj.gd` (`_make_visual` → `TOWER_FORMS.build(self)` —
  ≤ 2 lines, ZERO literals, GOVERNED honored); NEW `godot/scripts/tower_aim.gd` (root-LAST
  OBSERVER, code-mounted from the build_cores hook: aim `Turret` yaw at the nearest LIVE entity
  within `bonus_row().range` — READS only `runner.entities` + the bonus-row door, writes ONLY its
  own visual's transform (the fx_director read-only doctrine reused; tracers/sparks stay in
  fx_director, 337/400 ZERO lines)); NEW `tests/test_tower_forms.py` (form per class id; turret
  on shooters; yaw tracks a planted entity, zero-writes idle when no target; source-truth: driver
  touches no sim mutator — the selection_ring shape; planted-red: yaw inverted → RED).
- Re-pin risk DECLARED: any suite leg pinning the world-node CLASS (Sprite3D/MeshInstance) reddens
  first (L3 re-pin proof) — test_place_refusals' node leg (is_instance_valid + parented, :130-135)
  passes a container Node3D BY SHAPE (declared, not assumed — the leg runs in the card's suite run).
- SERVED (P2): place Ballista (panel row click arms → click places, G5 shipped route); marker =
  DEFENSES row + "defenses 1"; tower-slot silhouette census vs F-BUILD medallion; combat two-frame
  turret crop-delta (aim moves); kit-assign spark still paints (the shipped WK2 census window
  re-runs — reuse, red-free); vision literal "3D tower structure"; the panel medallion icon still
  paints in the SAME frame (UI-only proof).

**V-D — HERO BODY (P4a)**
- Files: `godot/scripts/hero_pawn.gd` (setup_pawn: primitive-composed body per archetype — the
  MATS hero tints REUSED; card declares whether the sheet survives as face-decor; crest block
  byte-untouched, P8 shipped); NEW `tests/test_hero_body.py` (body child per deck hero; silhouette
  within the WORLD_H_HERO≈3u door; zero-sim-writes source-truth; crest consts byte-pinned); LEDGER
  row. ZERO lines: camera_zoom.gd, mission.tscn, hero_controller (visibility swap already moves
  children — the crest precedent proves it walks for free).
- Planted-red: body builder returns null → leg RED; revert byte-verified green.
- SERVED (P4): default D=64 — hero-region silhouette census vs F-BUILD's ~8-px speck +
  describe-image "readable humanoid figure" literal; then ONE wheel-UP step to D=56 (shipped zoom)
  close read; camera row diff EMPTY (grant proof archived).

**V-E — LIGHTING + MATERIALS + THEMED HUD (P5+P5b)**
- Files: `godot/scenes/mission.tscn` (ONLY property values: env background/ambient → warm
  golden-hour, Sun color/angle; sub_resource id + load_steps + ext rows UNCHANGED — the :591 pin-7
  leg stays green); NEW `godot/scripts/ui_theme.gd` (ungoverned palette + StyleBoxFlat builder:
  panel bg, button tints, header tone); `godot/scripts/hud.gd` (≤ 2 apply lines, WATCH 394→≤396) +
  `godot/scripts/defense_panel.gd` (≤ 2 lines, 365/400, GOVERNED — Color string-hexes blanked by
  BN1, the defense_rows_ui:255 precedent); NEW `tests/test_ui_theme.py` (palette resolves; button
  rect UNCHANGED pin — pixel-judge law pre-checked engine-side); LEDGER row.
- Planted-red: theme apply removed → theme leg RED; a rect-shifting plant → the geom pin leg RED.
- SERVED (P5): full shipped journey (place/upgrade/zoom) at ≥600 ms pacing — every click answers
  (routes byte-ident); warm-mood + palette census where BEFORE read grey; crest/toast LEGIBILITY
  re-read — the vision read must SPELL "Bram Wardenfell" (the P8 lesson: re-theme can kill contrast).

### W2 — after V-A lands (shape + shared lines): two DISJOINT cards, parallel-safe (`lane-load.sh 2`)

**V-C — IN-WORLD PATHS (P3)**
- Files: `godot/scripts/lane_bands.gd` (the SAME node contract + unit PlaneMesh segments repaint
  with an OPAQUE road material: albedo = newly wired `ground_path` id + warm tint; the translucent
  BAND_COLOR ghost-arrow visual RETIRES — replace-not-delete, the cyan alpha dies in this commit;
  AIR lanes stay unbanded, G1 cue); `sprite_bank.gd` (wire the committed `ground_path.png` id —
  the :63-66 blocking comment rewritten TRUE with a replace-not-delete premise-change note);
  `tests/test_lane_bands.py` (RE-PIN `mat=1` RED-FIRST to the opaque road shape — L3; LB-BANDS
  counts/segs UNCHANGED); LEDGER row.
- Planted-red: opacity plant (alpha 0.30 back) → re-pinned leg RED.
- SERVED (P3): build-phase frame; marker row first; band-segment crop census: alpha-cyan ≈ gone vs
  F-BUILD, road reads earth-tone opaque; vision literal "worn road, no translucent arrows".

**V-F — WORLD DECOR (P6)**
- Files: NEW `godot/scripts/decor.gd` (≤ 40 static props: stacked-primitive trees/rocks along the
  V-A rim/plots, DETERMINISTIC layout consts — no RNG); `mission_world.gd` (+1 hook);
  `sprite_bank.gd` (decor ids ONLY if the fallback fires); NEW `tests/test_decor.py` (count ≤
  budget; determinism (two builds identical); zero `randf`/`randi` source-truth); LEDGER row.
  FIRST leg = WEB RASTER PROOF of the chosen node class (MultiMesh, fallback declared, L5).
- Planted-red: budget plant (41 props) → leg RED.
- SERVED (P6): rim-region silhouette delta vs F-BUILD + scale vision read; build-phase frame-time
  row (7 fps is the known floor, no fps CLAIM — decor adds zero per-frame code, that IS the budget).

### W3 — one final wave (sequential after ALL merges): the BEFORE/AFTER pair + gates roll-up

**V-G — RE-CAPTURE + MILESTONE GATES (no product-code change)**
- Files: NEW `.audits/20261104-1330-v16-plan/v16-capture.cjs` (reproducible two-pose capture:
  1280x720, zero wheel events; pose 1 = build-phase countdown visible; pose 2 = wave 1 undefended
  → DEFEAT screen — the exact F-BUILD/F-DEFEAT routes); the two `v16-after-*.png` frames;
  `V16-GATES.md` (A1..A8 reproduced with an EVIDENCE LEVEL per line, census numbers + quoted
  vision reads, cited to each card's log); LEDGER row. Final gate RUN (≥ §5 projection) is HERE.
- Acceptance law: this card PAIRS the BEFORE frames with the SAME poses — the owner's before/after
  answer is this artifact; nothing ships on "it compiles".
- Release tail (RN v1.6 body, README AT tag, ARCHITECTURE rows for the new files, docs grep-to-zero,
  tag/export/VM120/GitHub-Release doctrine) = the orchestrator's, not a plan card.

## 4 FILE-OVERLAP MATRIX + parallel safety

| file | V-A | V-B | V-D | V-E | V-C | V-F | V-G |
|---|---|---|---|---|---|---|---|
| scripts/diorama.gd (new) | ✔ | — | — | — | — | — | — |
| scripts/tower_forms.gd + tower_aim.gd (new) | — | ✔ | — | — | — | — | — |
| scripts/hero_pawn.gd | — | — | ✔ | — | — | — | — |
| scripts/ui_theme.gd (new) / hud.gd / defense_panel.gd | — | — | — | ✔ | — | — | — |
| scripts/lane_bands.gd / tests/test_lane_bands.py | — | — | — | — | ✔ | — | — |
| scripts/decor.gd (new) + test_decor.py (new) | — | — | — | — | — | ✔ | — |
| scripts/defense_obj.gd (≤2 ln) / tests/test_tower_forms.py (new) | — | ✔ | — | — | — | — | — |
| tests/test_diorama / test_hero_body / test_ui_theme (new) | ✔ / — / — | — | ✔ | ✔ | — | — | — |
| scripts/sprite_bank.gd | ✔ ground line | — | — | — | ✔ path line | ✔ (fallback only) | — |
| scripts/mission_world.gd (hook lines) | ✔ | ✔ (aim mount) | — | — | — | ✔ | — |
| scenes/mission.tscn | — | — (code-mount) | — | ✔ (VALUES only) | — | — | — |
| assets/v11/*.png (+.import) | ✔ | — | — | — | (ground_path already committed) | ✔ (fallback only) | — |
| tests/ new files per card | ✔ | ✔ | ✔ | ✔ | (re-pin) | ✔ | capture+gates |
| LEDGER.md | ✔ own row | ✔ own row | ✔ own row | ✔ own row | ✔ own row | ✔ own row | ✔ own row — known EOF race, sequential landing KEEP-BOTH (L8) |
| mission.gd (400) / test_mission_clicks.py (600) / camera_zoom.gd / fx_director.gd / sim/ | — | — | — | — | — | — | — ZERO lines by design (L1) |

sprite_bank.gd and mission_world.gd are shared ACROSS waves — W2 lands after W1 merges (pick order
V-A → V-B → V-D → V-E, then V-C → V-F, then V-G; keep-both only at cherry-pick time). W1's four
cards share no file. Lane pre-flight sized 4, then 2 (orchestrator duty; this plan never spawns).

## 5 SUITE-COUNT MATH — baseline MEASURED at v1.5 tag: 345 with export / 340 clean (the test_served
5-leg module-skip reconciliation idiom; RN v1.5 known-limits row). Floor NEVER below 345 at any card.

| card | new pytest legs | projection (with-export) |
|---|---|---|
| baseline (1271a6c) | — | **345** |
| V-A | +1..2 (probe leg + ground-pinned/source-truth) | 346–347 |
| V-B | +2..3 (forms / aim / source-truth) | 348–350 |
| V-D | +2 (body / crest-pin) | 350–352 |
| V-E | +1..2 (theme / rect-pin) | 351–354 |
| V-C | +0..1 (band file re-pin is count-neutral; +1 road-shape possible) | 351–355 |
| V-F | +1 (budget/determinism) | 352–356 |
| V-G | +0 (harness + gates roll-up) | **352–356** |

A card landing BELOW its bar is honest only with a named count line in its wave log (V15 rule).

## 6 OWNER-DECISION (exactly one row)

**OD1 — hero-forward TRACKING (the P4b half of "third person").**
Question: *Should the camera actively keep the hero+nearest action composed (a follow/pan), when
the shipped grant is ZOOM-ONLY and "no new zoom mechanic" is a control law?* Grounds: MC 11719
verbatim "Go 1 and zoom control for 2"; rig pin #3 SPENT; V16-BEFORE.md:8.
Recommendation: **DEFER for v1.6.** The body+crest+shipped-wheel (P4a/V-D) answer readability, the
look-and-feel waves need camera-STABLE frames to be comparable to the BEFORE poses, and a tracker
is exactly the new camera mechanism the control law forbids without a fresh artifact.
If the owner wants it, the MINIMAL ruling that keeps every law literal: one chat line granting
"CameraRig origin MAY offset along the FROZEN LOS toward the ACTIVE hero's x/z, D clamped to the
shipped 56..128, basis/FOV byte-frozen, wheel authority preserved" — ONE translation axis inside
the existing mechanism family, its own tiny card, never smuggled into a visual card.
Default-if-silent: **DEFER** (no ruling = no mechanic; P4 ships readability only).

## 7 RISKS

1. **Web-raster class (the G2 killer)**: all NEW geometry is PrimitiveMesh-managed (L5); MultiMesh
   is the one UNPROVEN node → V-F leg 1 raster-proves or falls back.
2. **7 fps served transience**: state-marker-first + ≥600 ms pacing + crops (L2); every census's
   control = the archived BEFORE frame (a census that cannot go red is not one).
3. **Re-theme kills crest/toast legibility** (P8 lesson): V-E's served leg must SPELL the hero name;
   failure = tone tweak in ui_theme.gd (data-like, one file).
4. **Art dependency**: V-A/V-C/V-F carry clean-room 3090 renders; PNG+`.import`+bank-line land in
   ONE commit or the card does not (v1.1 no-fake-art rule; WK2 web-texture law).
5. **Shared-line landings** (sprite_bank/mission_world/LEDGER): declared pick order + keep-both;
   a card editing ANOTHER card's line is the defect path, pathspec commits catch it.
6. **Node-shape test drift**: V-B changes the world-node class — suite node legs redden LOUD
   (re-pin RED-first, L3); named candidates: test_place_refusals node leg, test_kit_fx rows
   (position-based, expected GREEN), test_served journey (click routes unchanged).
7. **Decor perf**: budget ≤40 nodes + zero per-frame code; no card adds a light (I7 unchanged).
8. **Scope ceiling**: eight SHIP rows / six cards is the whole wave; the DEFER column is the ceiling
   honored — shipping rows 10-17 too would be the DA-gate FIX waiting.

*End: dispositions 8 SHIP rows across 6 cards (the six pillars + P2b, V-A…V-F) / 7 DEFER / 1 REJECT
/ 1 OWNER-DECISION / 1 CONSTRAINT row; waves W1 = V-A ∥ V-B ∥ V-D ∥ V-E, W2 = V-C ∥ V-F (after V-A),
W3 = V-G; suite 345 → 352–356 projected. Next gate: DA on THIS file (orchestrated — no spawn here).*
