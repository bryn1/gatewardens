# Gatewardens — Release Notes v1.6 (look-and-feel) — 2026-11-04

Length reason (file hygiene): the standalone committed release-notes body for the v1.6 GitHub Release
(MC 12121; GitHub-Release doctrine MC 11277/11509). The per-release history v1–v1.4 stays in
`RELEASE_NOTES.md`, the v1.5 body in `RELEASE-NOTES-v1.5.md`; this file supersedes those FOR v1.6
CLAIMS ONLY. Release tail note: this IS the committed body; the tag `v1.6` is cut by the orchestrator's
release card on the release commit — no tag exists before it.

Owner direction that opened the milestone, verbatim (`V16-BEFORE.md:1`): "far from a replica...
third person, resemble dungeon defenders" — ratified route LOOK & FEEL FIRST, six pillars, zero
sim movement. Clean-room wall: resemble means FORM + FEEL only; every asset here is original
procedural/engine geometry or a locally generated sheet, zero third-party game content.

## THE PAIR — what changed, in plain words

Same mission, same camera, same route, nothing built ("Defenses 0"), same "Core 1000 / 1000".
Two poses, shot before (v1.5) and after (v1.6) at the identical poses:
`v16-before-build.png` / `v16-before-defeat.png` → `v16-after-build.png` / `v16-after-defeat.png`
(both committed in `.audits/20261104-1330-v16-plan/`, the after-pair in `evidence-12115/shots/`).

**BEFORE:** a flat checkered tan board floating over a black void. The paths were translucent pale
arrow-strips laid on top of the ground. The only scenery — grass tufts, grey rocks, one flower — was
painted INTO the floor sheet, so nothing stood up. The hero was a tiny blue speck under an unreadable
name. The shop column was default grey-on-dark.

**AFTER:** the same board is a fortress. Large stone flagstone slabs with real thickness and a cliff
skirt hanging below them; a brick rim wall with a corner tower at each corner; a keep with four turrets
sitting under the main core at the centre; an arched gateway at each spawn mouth, with the keep-crest
and gate-plaque emblems redone to match; packed-earth roads where the arrows used to float; a line of
low pine trees and pale boulders standing along the top of the wall; warm brown evening light over the
whole scene instead of a black background; and a brown-and-cream themed shop column. The hero now
reads as a small standing figure at the keep gate with its name over it.

**What did NOT change:** no tower is placed in either frame, no enemy, no HUD element moved, the
camera never moved (zero wheel events, `camera_zoom.gd` 0 changed lines across the whole milestone —
measured `git diff 1271a6c..HEAD` this session), and no sim/economy/balance number moved.

**What shipped** — every claim below is cited to the wave log it was measured in
(`.audits/20261104-1330-v16-plan/`) and to the commit that landed it, not to a summary. File sizes are the gate metric `tools/check_hygiene.py` prints
(`len(read().split("\n"))`), measured here with `wc -l` + 1:

- **P1 The board became a fortress on stone** (MC 12081, commit `6b4427c`). NEW `godot/scripts/diorama.gd`
  (230 ln) builds 23 engine-managed primitives — measured `MAX_PRIMITIVES := 30` budget const at
  `diorama.gd:27`, probe rows `DG-COUNT n=23 max=30 · DG-CLASS boxes=9 cyls=14` — a plateau hanging
  BELOW the play plane (top face flush y=0, so the build grid and every slot coordinate are frozen,
  byte-pinned by the `DG-GROUND` leg), rim walls + 4 corner towers, a 2-tower gatehouse at every
  spawner and a keep box under the main core. `ground_arena` — the arena floor id — was REMAPPED (not
  added) to the new `ground_fortress.png` flagstone sheet in the ONE `sprite_bank` id map (`sprite_bank.gd:75`,
  measured this session); two new clean-room sheets (`ground_fortress.png`, `fortress_stone.png`) and
  three IN-PLACE icon redraws (`icon_core`, `icon_gate_eye`, `icon_gate_eye_air`) so the in-frame
  emblems match the architecture. Served proof (VA-wave.log §6): marker-first state read, then
  TOP-STRIP void 17193→6911 px, CENTER checker-grass 1625→0 px, and Lane E reading the keep+crest and
  the gate plaque LITERALLY where v1.5 read "circular gold token".
- **P2 A placed defense is a 3D structure that aims** (MC 12082, commit `33d5abe`). NEW
  `godot/scripts/tower_forms.gd` (239 ln) composes a form per `towers.json` id out of BoxMesh/CylinderMesh
  only, with a `Turret` child on the shooter classes (the DATA row's `class` decides, never a literal);
  NEW `godot/scripts/tower_aim.gd` (64 ln) is a root-mounted OBSERVER that reads published state and
  writes ONE thing — its own turret's yaw. `defense_obj._make_visual` is now a single delegation line:
  **the coin-medallion world path RETIRED** (`defense_obj.gd` 283 ln, net −23). The panel and HUD icons
  are untouched and still paint — pinned, not assumed (VB-wave.log: panel medallion row 257 px on the
  SAME served frame as the 3D forms). Served: EMPTY board → structure silhouette +124 px, and a
  two-frame turret-crop delta of +24 px with a closed-range control reading 0.
- **P3 The corridors are roads, not arrows** (MC 12110, commit `f1a2c51`). `lane_bands.gd` (113 ln) keeps
  the exact `LaneBand_<lane>` node contract and the same unit PlaneMesh segments, and REPLACES the
  material: `TRANSPARENCY_DISABLED`, albedo = the newly wired `ground_path` sheet × `ROAD_TINT
  Color(0.78, 0.66, 0.54)` — measured at `lane_bands.gd:104/45/46`; the translucent cyan `BAND_COLOR`
  now exists only as a header note naming what it retired. The re-pinned probe reddened under the OLD
  translucent shape FIRST (VC-wave.log §1, rc=1 "retired ghost-arrow mechanism crept back: BAND_COLOR").
  Served census at three declared crops (VC-wave.log §6, re-measured byte-equal on the merged tree by
  V-G): ghost-cyan 719→6, 1502→0, 365→4.
- **P4 The hero is a figure now** (MC 12083 commit `8af95e5`, re-tuned by MC 12114 commit `18aca6c`).
  `hero_pawn.gd` (213 ln) mounts a primitive-composed body per archetype (melee/ranger 6 BoxMesh parts,
  mage CylinderMesh robe + staff) that REUSES the shipped per-hero tints, inside the `WORLD_H_HERO` 3u
  door; the byte-pinned crest block is untouched and the main sheet stays hidden (declared, its G7 pin
  still green). The honest headline of that card: the first build painted NOTHING on web — the hero
  stands at the core position, so a ground-anchored figure is swallowed by the core/keep box. V-H is the
  merge-occlusion re-tune: `BODY_OFFSET := Vector3(0.0, 0.0, 6.5)` (measured at `hero_pawn.gd:82`), a
  presentation-only offset past the keep's near face. Served at the merged tree: HERO crop 0→262 px
  (evidence-12114/census-final.txt) and Lane E's literal "a small dark grey figure … at the bottom
  opening (gate) of the keep". No camera mechanic was added or moved (OD1 deferred, below).
- **P5 Golden hour, and the HUD is themed** (MC 12084, commit `908f337`). `mission.tscn` PROPERTY VALUES
  only — background `(0.055,0.065,0.085)→(0.165,0.105,0.06)`, ambient `(0.85,0.88,0.95)→(0.95,0.82,0.65)`,
  Sun `RotY(30)·RotX(-45) → RotY(55)·RotX(-20)` + `light_color (1, 0.72, 0.45)`; sun elevation 45°→20°
  by asin, no new resource and no second light. NEW `godot/scripts/ui_theme.gd` (68 ln) is the palette;
  `hud.gd` and `defense_panel.gd` took TWO lines each (measured 396 and 368 this session). The
  pixel-judge law held engine-side: all 13 pinned button/label rects byte-equal with the theme ON and
  OFF (`VETH-RECT-EQUAL count=13`), and the shipped click-route suite stayed green in every card run.
  Served: the panel column that read grey measured 37,786 → 51 grey px, and the void strip flipped
  cool 64,130 → warm 69,066.
- **P6 Rim decor sells the scale, for free** (MC 12111, commit `7c1fd62`). NEW `godot/scripts/decor.gd`
  (193 ln): a 100 % const layout table — measured by parsing it, 14 `TREES` rows + 10 `ROCKS` rows = 24
  props, 38 parts with `MAX_PROPS := 40` — every row on the rim-wall centerline OUTSIDE the play plane,
  zero RNG, zero per-frame code, one `Decor` container + three `MultiMeshInstance3D`. The card's LEG 1
  proved the class rasterizes on WEB (fresh-export pck md5s logged, DECOR-region pine-green 973 px ON vs
  15 px same-camera OFF-control) and the fallback never fired. Frame-time ON 216.7 ms == OFF 216.7 ms.
- **The owner pair + the gate roll-up** (MC 12115, commit `ad2256e`, ZERO product lines). The after-frames
  were re-shot through a committed, re-runnable capture script at the SAME poses, and the route itself was
  PROVEN by re-exporting the v1.5 base through the same script (defeat frame pixel-identical, 0 px; build
  frame 122 px, all countdown glyphs). Per-frame served pck md5 beside every frame (two different md5s —
  a stale pck is mechanically excluded). Merged-tree census at the same rects: TOP-STRIP void 17218→6596,
  DECOR region void 45784→34085 with pine 1688→973, FULL-frame delta 702,737 px. The DA-mandated
  frame-time row: 150.0 ms → 200.1 ms median at the same headless rig = **1.33×, under the 2× trigger, so
  the presentation knobs stay as shipped** (this is the known swiftshader web floor — NOT an fps claim
  about any real machine). Acceptance rows A1–A8 with evidence levels: `V16-GATES.md`.
- **Docs hygiene of the retired pins** (MC 12116, commit `3197a63`, probe rows only). The three stale
  sprite-era probe pins are re-truthed: the world probe's FLOOR row now pins the flagstone board, and the
  sprite probe's tower/gate legs pin the LIVE `TowerForm` container instead of a Sprite3D. The orphaned
  `WORLD_H_TOWER` const is gone with its mechanism (measured: 0 hits repo-wide).

**Tested at this tree** (re-measured by this docs pass, not inherited): `python3 -m pytest tests/ -q`
= **363 passed, rc=0** with `bash tools/export_web.sh` run first (my export: `index.pck` md5
`ec50e154e62eb67a9b85fddbf3faf6cd`, 7,457,488 B); `tools/check_hygiene.py` → **0 hit(s)** (25 soft
>250 notes, none of them new); `git diff f95e481..HEAD -- tests/fixtures/` = **0 lines**; the governed
-literal set is **17 files**; `godot/scripts/mission.gd` **400** and `tests/test_mission_clicks.py`
**600** on the gate metric, both AT their ceilings and carrying ZERO v1.6 lines; `hud.gd` 396;
`camera_zoom.gd` **0 changed lines** since the milestone kickoff `1271a6c`. New v1.6 test files:
`test_diorama.py` (5 legs), `test_tower_forms.py` (3), `test_hero_body.py` (2), `test_ui_theme.py` (2),
`test_decor.py` (5), plus `test_lane_bands.py` re-pinned to the road shape.

**Suite-count correction (this pass measured it, so it is written here rather than carried):** the
v1.3–v1.5 release notes all state "+5 with export, N green from a CLEAN checkout". At this tree the real
reconciliation is **+6**: with `static/` holding only its `.gitkeep`, `python3 -m pytest tests/ -q` answers
**357 passed, 1 FAILED, 1 skipped** — the failure is
`tests/test_scaffold.py::test_server_serves_placeholder_on_ephemeral_port`, which asks `GET /` for 200 and
gets 404 because `static/index.html` is the export (build-side, gitignored since W12) and that leg is NOT
export-gated the way `test_served.py` is. I measured the SAME red at the v1.5 tag `f95e481` in a scratch
worktree this session, so this is PRE-EXISTING, not something v1.6 broke. Treat the run-with-export
number (363) as the milestone's suite row, and the phrase "green from a clean checkout" as FALSE until a
test card gates that leg.

## Known limits (honest, and where each is declared)

- **Nothing in the fortress casts a shadow.** The scene Sun ships `shadow_enabled = true`, but every
  fortress and decor node sets cast-OFF with an emission floor 0.3 (V-A's served-leg ruling: with default
  casting, unlit faces and ground shadows painted PURE BLACK on the web frame because `env_greybox`
  ambient is DISABLED at the scene row — the plan's "ambient 0.6" premise was contradicted by the file).
  One const (`diorama.gd:73 SHADOW_CASTING := false`) is the flip-back; V-G audited the AFTER frames
  black-blob-free (0/6/3 fortress black px in the three declared crops).
- **The hero is a ~30 px dark silhouette at the default distance** and its arms merge into the torso
  block; head/torso/legs read, fingers don't (V-D §6b, restated V-H §limit b). The crest medallion + name
  still ride the pawn origin, i.e. behind/inside the keep, and read as a banner over the gate — that
  block is byte-pinned (P8) and no v1.6 card was allowed to move it.
- **The hero body rides 6.5 u camera-side of the sim position.** Cosmetic class, same as the old
  billboard sheets, widened by V-H to clear the keep. During a combat walk the figure leads the
  simulated position slightly (declared in both VD-wave.log and VH-wave.log).
- **The roads are flat tinted quads**, unshaded on purpose (deterministic albedo over the lit flagstones,
  and the probe pins UNSHADED); no baked shadow under them, no AO. One const owns the tint.
- **Frame cost moved the headless floor.** 150.0 → 200.1 ms median on swiftshader = 1.33×. That is the
  decision row, not a benchmark: no fps number from a real GPU was measured in this milestone, and none
  is claimed.
- **Census windows are reused, not re-tuned.** The defeat-side PANEL delta (64,020 px) therefore includes
  the themed panel plus the world strip to the right of it (declared, V16-GATES §9(e)).
- **Kit sparks did not paint in any v1.6 served window.** See NOT-SHIPPED-HERE — pre-existing, open.

## NOT SHIPPED HERE (named, so nobody reads it into the milestone)

- **Camera tracking / hero-following pan — DEFERRED by the OWNER.** Plan row 6 (OD1) was answered the
  same day, ruling verbatim: **"Defer tracking (Planner's rec)"** (owner, 2026-11-04, orchestrator
  channel; recorded in `V16-PLAN-c2.md` §6). Fixed framing stayed on purpose so the BEFORE/AFTER pair
  compares. The camera grant remains ZOOM-ONLY (MC 11719 verbatim "Go 1 and zoom control for 2"); the rig
  row is byte-locked.
- **3D bodies for enemies — DEFER (plan row 10).** Not one of the six ratified pillars; the v1.1 enemy
  billboards read acceptably and W1+W2 already carried ~6 builder surfaces. Re-opens only on an owner
  pillar-extension.
- **Shadow polish (cast-on look) — NOT shipped.** The fortress ships cast-OFF per the V-A ruling above;
  what shipped is the emission-floor substitute, not shadows. Anyone expecting crisper shadow-on looks
  in v1.6 is expecting something this tree deliberately did not ship.
- **Kit-spark cap-starvation — PRE-EXISTING, still open (WR 11897-F1).** v1.6 added no fx spawn site, and
  V-B's served windows painted 0 spark px while `test_kit_fx.py` stays green; V-B filed it as a finding
  rather than silently "fixing" it (VB-wave.log FINDINGS 3). Do not read "the spark was proven in v1.5"
  as "it paints in every served window today".
- **The committed tower sheets now have no world consumer (v1.7 art-slim candidate).** Since V-B, no
  shipped node path asks `sprite_bank` for a defense id — the only `texture_for`/`make_sprite` callers pass
  hero, enemy, fx, world or `icon_*` ids (measured by grep this session) — yet 11 `tower_*.png` sheets
  (T1/T2/T3) stay committed and the bank still ANSWERS the ids, pinned by `v11_sprite_probe`'s bank-map
  leg. They are dead weight in the pck, and the panel/HUD icons they were never used for ride separate
  `icon_*` ids. A future card may retire them; that is a data+pck-size card, not a doc claim.
- **Procedural sky, minimap, ready-up, per-tower keys, defense hp-tint, MAX_FX drop-priority, a second
  map — unchanged dispositions** (plan rows 11–17; grounds are in `V16-PLAN-c2.md` §2 and the v1.5 rows
  they inherit).

## How to build & run

Unchanged: `bash tools/export_web.sh` → serve `static/` with `python3 server/server.py`
(`GW_PORT`, default 8124) — see README one-liners. Run the suite AFTER the export (see the suite-count
correction above). The Windows desktop build comes from `bash tools/export_windows.sh`
(see RELEASE_NOTES.md W18 rows).
