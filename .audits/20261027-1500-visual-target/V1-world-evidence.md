# V1 stylized world — build evidence (MC card 11559 / milestone 11462 / workspace 11274)

Date 2026-10-28 (UTC). Sole writer, shared checkout /home/claudecode/Games/gatewardens.
Binary: /home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64 (4.7.2).
Knut route = the PROBE read-backs below (repo not projects.yaml-bound; same route as cards
11466/11520/11517/11530/11549/11552). The grepped logs are COMMITTED under gen/ in this same commit.

PROBE: grep -c V1W-OK /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v1world-probe-green.log => ^1$
PROBE: grep -c V1W-FLOOR /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v1world-probe-green.log => ^1$
PROBE: grep -c V1W-AABB /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v1world-probe-green.log => ^1$
PROBE: grep -c V1W-CORE /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v1world-probe-green.log => ^1$
PROBE: grep -c V1W-FRAME-PT /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v1world-probe-green.log => ^33$
PROBE: grep -c V1W-FAIL /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v1world-probe-red.log => ^1$
PROBE: grep -c V1W-OK /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v1world-probe-red.log => ^0$
PROBE: grep -c SHOT-OK /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/v1world-shot.log => ^1$
PROBE: grep -c ground_arena /home/claudecode/Games/gatewardens/godot/scripts/sprite_bank.gd => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/sim/v1_world_probe.gd => ^08d287bb88731b3eb
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/scripts/mission_world.gd => ^ee10189288cf1a7f
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_hard.jsonl => ^5e37c4b089209e64
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/assets/mesh_plane.tres => ^444811330d919f17
PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/assets/mat_ground.tres => ^ce235deaa387281f

## What shipped (ONE commit; zero logic change)

- godot/scripts/sprite_bank.gd — "ground_arena" joins THE ONE id->file TEXTURES map (the
  ground material albedo is its only consumer, no parallel preload path). HONEST CUT (the
  brief's stated row): ground_path.png is deliberately NOT wired — NO lane mesh exists (the
  lanes are waypoint DATA only, C7; grep MeshInstance3D.new finds exactly the defense/enemy/
  core sites), so painting it would author a new visual mechanism, not repaint a surface.
- godot/scripts/mission_world.gd — the map-build file the brief names as the visuals mount:
  (a) make_core now hangs one icon_core Sprite3D billboard (via sprite_bank.make_sprite,
  null-safe) on EVERY core node at local y 4.5, world height 6u — the parented core box
  STAYS (visual-only, V1 row: the emblem rides it); (b) paint_arena(m) duplicates the Ground
  material_override, sets albedo_texture = texture_for("ground_arena"), albedo_color =
  ARENA_MODULATE Color(0.9, 0.9, 0.95) (the light modulate, stated per brief),
  texture_repeat = OFF, and mounts it — 1:1 over the whole plane, PlaneMesh UVs cover it,
  the board is NOT seamless. ENGINE FACT (VERIFIED via ClassDB dump, probe-first-red):
  4.7.2 material texture_repeat is a BOOL property (default true), not the 4.x enum.
  build_cores calls paint_arena once per mission build (DECLARED comment rides the call).
- godot/scenes/mission.tscn — CameraRig transform ONLY: origin (0,58,46) -> (0,56.33,44.14),
  the 2.5-unit view-axis shift = +3.55% zoom. Basis, FOV (default 75), node order, all four
  script rows (incl. 3b_fx) and the Ground node are byte-untouched.
- NOT touched at all: godot/scripts/mission.gd, enemy_runner.gd, fx_director.gd, every .json
  data file, mat_ground.tres + mesh_plane.tres ON DISK (sha256s above byte-equal to the
  baseline b15c2e3 copies — git show proves). The ground plane AABB and node transform are
  pinned by the probe at (-80,0,-80, 160,0,160) @ origin, pre == post == pinned.
- tests/test_hub_layout.py — DECLARED update of the planted-red fixture string to the new
  rig transform (the sky-aimed plant still trips the gate; the frustum leg re-reads the
  tscn line itself). No other test edited.

## Framing: the honest number (brief rule 3)

The shipped W13 frustum gate (test_hub_layout.py, MARGIN 0.92 of each half-FOV, card 11332)
is the binding ceiling, NOT the 60px probe margin: at baseline the worst point spawn_c /
lane_g3:wp0 (34,0,30) already sits at 95.0% of that gate, so the maximum zoom the shipped
gate allows is +4.58% (solved by bisection: s<=3.19 units along the view axis). Shipped
s=2.5 (+3.55% zoom) keeps the model ratio at 0.9887 (1.1% under the gate — deterministic
float arithmetic, verified by the suite). The brief's 10-18% band does NOT fit the shipped
lanes at any margin: the gate would have to move, which is an owner call, not this card's.
The ENGINE truth (the probe's own unproject through the shipped Camera3D, the 4.7.2 rig
basis is slightly skewed — the 0.92 model is conservative for it) prints the full margin
table in gen/v1world-probe-green.log: n=33 points (every lane waypoint, every lane end,
all three spawners, both cores, hero battle space), px_min=(370.2,229.1) px_max=(950.2,606.4),
min_margin=113.6px worst=lane_g3:wp0, floor pinned 60.0 — every point inside with ~2x the
required margin. FRAME-PT rows pin min/max screen coords per point.

## PROBE: godot/sim/v1_world_probe.gd (boot = v4_icon_probe idiom, E5 + W13 facts re-shown)

First runs went RED and taught the engine facts (fleet discipline, no green-washing): the
router-added mission never dispatches _ready under -s; cam.current only turns on with
viewport handling (MainLoop._process pump, v4 frame-2 idiom); root.size must be set AT the
pump (a -s size set in _init projected into a 64px canvas — the tell: px_max (61.9,56.2));
String(AABB) has no such constructor (pins are component-wise numeric); adjacent string
literals are illegal in GDScript.
Green run (gen/v1world-probe-green.log, rc 0, EMPTY stderr, V1W-OK):
  V1W-FLOOR tex=res://assets/v11/ground_arena.png repeat=off modulate=(0.9, 0.9, 0.95, 1.0)
  V1W-AABB pos=(-80, 0, -80) size=(160, 0, 160) origin=0,0,0 unchanged=1
  V1W-CORE n=2 emblem=res://assets/v11/icon_core.png parented=1 (billboard + y + scale pinned)
  V1W-FRAME n=33 ... min_margin=113.6 worst=lane_g3:wp0 floor=60.0
Pins are COMMITTED RESOURCE PATHS + literal numerics — never read back through the mechanism
(bank-as-oracle lesson). Planted-red (user arg "planted", fixed argv): the FLOOR expectation
switches to the other committed sheet ground_path.png; RED rc 1 naming the exact paths,
V1W-OK count 0 (gen/v1world-probe-red.log), reverted, green re-run.

## PIXEL: godot/sim/v1_world_shot.gd — xvfb opengl3, gen/v1world_shot.png + v1world_zoom.png

v5_fx_shot capture idiom UNCHANGED in mechanics (real click on "Start gatefall — normal",
shipped router, 6 shooters at the lane_g1 run-in, feed, held core — the v5 declared license);
FxDirector mounted BY the tscn (live=3 tracers=24 sparks=9 poofs=1 at capture — V5 leg
co-existence shown for free). The 512x512 crop is centred on the core's own unprojected
screen pos (core@(640.0,390.5)). LOOKED AT (both PNGs opened): the framed board reads as a
warm cartoon arena floor (tan/cream checker, tufts, rocks); the BUSH BORDER is visible at the
chosen camera along the FAR (top) edge of the ground crossing the upper frame; the near and
side borders are off-frame (the 160-unit plane extends well past the viewport at this camera
— honest statement per brief, plane never resized). The gold wolf-crest emblem is clearly
visible riding the blue core box in the full frame and unmistakable in the zoom crop; the
sub-core rides its smaller crest too. Unit sprites read readable against the modulated board.
Ground-vs-background contrast leg preserved (test_mission_lighting_row_exists green).

## Suite + probes + hygiene + fixtures (all re-run ON THE FINAL TREE)

- pytest: 222 passed (post-change; baseline green at b15c2e3 per the brief, the ONLY test
  edit is the DECLARED planted string).
- v11_sprite_probe exit 0 + OK, v6_tween_probe exit 0 + OK, v4_icon_probe exit 0 + OK,
  v5_fx_probe exit 0 + OK — all headless, ALL stderr byte-empty (V5 not orphaned: the
  CameraRig/mission_world change keeps its 4 script rows and tree order intact).
- check_hygiene: 0 hits (mission.gd byte-untouched at its 400-line ceiling; the mount rides
  mission_world.gd instead — noted in its header).
- fixtures: eafe3932.../5e37c4b0... byte-identical (PROBE lines above).
- v1_world_probe: green rc 0 EMPTY stderr + planted-red rc 1 (fixed argv "planted").

## Known limits / remaining risks

- Zoom is +3.55%, below the brief's ~10-18% ask: the shipped W13 0.92-frustum gate binds at
  +4.58%; deeper zoom needs an owner ruling on that gate (or a rig RE-AIM, e.g. pitch, which
  changes the composition beyond this card's ask). The probe margin table proves the engine
  frame itself holds 60px up to much deeper zooms — the conservative test model is the cap.
- The camera nudge is small enough to be visually subtle in the pixel shot; the emblem and
  board are the V1 readability wins at this stage.

VERIFY_EXIT=0
