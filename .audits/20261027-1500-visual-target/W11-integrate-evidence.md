# W11-integrate evidence — V1.1-a batch-1 sprites into the mission renderer
MC card 11466 / milestone 11462 / workspace 11274 · identity `code (11466)` · 2026-10-27
Brief: /tmp/w11-integrate-brief.md · Visual target: VISUAL-TARGET.md rows V2/V3 (same dir)

## What changed (one commit, draw layer ONLY)

- `godot/scripts/sprite_bank.gd` (NEW, 63 L) — the ONE batch-1 sprite map: unit id -> committed
  512px sheet under `godot/assets/v11/`, plus the ONE billboard factory (`make_sprite`) and the
  ONE facing mechanism (`face`) the three draw sites share. A null answer = no committed sheet =
  the caller keeps its greybox (no fake art, no second render path). Sheet names differ from data
  ids (`hailspire_tower` -> `tower_hailspire_T1.png`), so the map is explicit, never a stem rule.
- `godot/scripts/hero_pawn.gd` — `setup_pawn` asks the bank; a committed sheet mounts as a
  billboard Sprite3D child and the greybox `$Visual` capsule is HIDDEN (not freed — the W6
  destroyed-core visibility idiom). Unknown ids keep the tint fallback.
- `godot/scripts/defense_obj.gd` — `_make_visual()` asks the bank on `trow["id"]` before the
  W6/W8 class meshes. `gate_blockade`/`barbed_snare` have no sheet -> mesh, unchanged.
- `godot/scripts/enemy_runner.gd` — `spawn()` asks the bank on `row["enemy_id"]` before the
  ground/air primitives; `warden_breaker` keeps the mesh. Facing: read at spawn from the first
  lane step and re-applied every tick through `SPRITE_BANK.face()` (the ONE mechanism; a no-op
  on greybox nodes).
- `godot/sim/v11_sprite_probe.gd` (NEW, 170 L) — the headless render proof (below).
- 12 × `godot/assets/v11/*.png.import` + 2 × `.gd.uid` sidecars committed (clean-checkout
  determinism — see Limitations for the import-form fact).
- `LEDGER.md` — the V2/V3 batch-1 wiring row.

Unchanged by design: `sim/`, economy, save format, every test/fixture, all positions/coords/
hitboxes (sprite nodes mount on the same record `pos`; `ent["node"]`/`obj.node` keep the same
add/move/free lifecycle the tests already use). `git show --name-only` lists exactly the files
above + the evidence dir.

Facing reading (declared): the mission camera maps world +x to SCREEN right (mission.tscn
CameraRig basis (1,0,0)·(0,.667,.667)·(0,-.746,.746)). Hero/tower sheets face RIGHT as generated
-> never mirrored. Enemy sheets face LEFT -> flip_h only when the walk steps toward +x.
Footprint reading: Sprite3D maps 100 px to one world unit at scale 1, so scale = world_h/
(tex_h/100) with world_h = 2.0 (pawn/enemy capsule) and 4.0 (tower capsule, authored scale.y 2).
INFERRED label on the exact world height: the probe asserts node/texture/flip/position, not the
rendered pixel height (headless dummy rasterizer has no pixels to measure).

## DoD rows, with evidence

**Baseline BEFORE any edit** (brief-mandated): `python3 -m pytest -q` at commit 08a3d2b —
`222 passed in 157.28s`. This is the count the change had to preserve.

### (1) 12 sprites render for their entity, greybox gone for those 12 — TESTED (headless render proof)
`godot/sim/v11_sprite_probe.gd` boots the REAL `res://Main.tscn`, enters the mission through the
SHIPPED router (`main.start_mission("gatefall","normal")`), and asserts on the live scene tree:

```
SPRITEBANK-TEX n=12 px=512        # all 12 sheets load, authored 512x512
SPRITEBANK-HEROES n=3             # each pawn's Sprite3D carries its bank texture, $Visual hidden
SPRITEBANK-SWAP active=1 visible=deadeye   # F2 hot-swap through the bridge repaints
SPRITEBANK-TOWERS n=3             # placed towers (place_defense) mount the sheet
SPRITEBANK-GREYBOX blockade=mesh trap=mesh # row 2
SPRITEBANK-ENEMIES n=6 boss_greybox=1      # spawned enemies carry their sheet
SPRITEBANK-FLIP right=flipped left=plain   # ONE facing mechanism, live through runner.step
SPRITEBANK-OK
```
rc=0, stderr 0 bytes (transcript: W11-probe-green.log / W11-probe-green.stderr.log beside this
file). Harness license declared in the probe header (core x5 sturdier, green written to fund the
place legs — the mission_smoke precedent); everything else drives real entry points.

**Gate-red proof** (a gate that never went red is not a gate): bank key `gale_harpy` renamed ->
`SPRITEBANK-FAIL sheet missing or not 512px: gale_harpy`, rc 1 (W11-probe-red.log). Restored
(sha256 of sprite_bank.gd after restore bde17b0ab03c085364b9c62173d527540de37d1fa850bf8442c3f23b191f8e1f).

**Export bake** (the shipped build carries the art): `tools/export_web.sh` at this tree ->
`static/index.pck` contains all 12 `res://.godot/imported/<name>.png-<hash>.ctex` entries
(counted per name, 12/12).

### (2) gate_blockade / barbed_snare keep greybox — TESTED
SPRITEBANK-GREYBOX row: both placed through `place_defense`, their `obj.node` asserted NOT a
Sprite3D (MeshInstance3D kept). `warden_breaker` likewise (boss_greybox=1).

### (3) count unchanged, hygiene 0, fixtures byte-identical — VERIFIED at the final tree
- `python3 -m pytest -q` (after the last source edit): **222 passed in 148.41s** — equals the
  pre-edit baseline (222). No test/fixture file is in the commit.
- `python3 tools/check_hygiene.py` -> `check_hygiene: 0 hit(s)` (soft notes only: defense_obj.gd
  286 L > soft 250, under the 400 hard ceiling; the pre-existing notes untouched).
- sha256 (identical to the brief's pins, byte-for-byte):
  `eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912  tests/fixtures/mission_gatefall_normal.jsonl`
  `5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628  tests/fixtures/mission_gatefall_hard.jsonl`

### (4) LEDGER row — DONE
Status-table row "BUILD V1.1-a sprite wiring (MC 11466 …)" appended in the same commit.

### (5) this file ends VERIFY_EXIT=0 — DONE

## Findings / limitations (honest)

- **F-1 (P2, pre-existing, NOT introduced here):** `tests/conftest.py::ensure_class_cache` runs
  `godot --headless --import <path>`; the positional form is a NO-OP for assets in 4.7.2 — VERIFIED:
  it exits 0 and creates neither `.godot/` nor any `.import`/`.ctex` (clean-copy experiment: 0
  files after it). The working form is `godot --headless --path <dir> --import` (it produced the
  12 sidecars + 24 cache files here). Consequence measured on tar/archive copies with NO editor
  cache: pre-change HEAD = **10 failed / 207 passed** (the engine tier, the LEDGER's known W3b
  class), candidate = **11 failed / 206 passed** — the +1 is `test_hud_smoke_is_byte_stable`, the
  same missing-import cause (PNG preloads are unresolvable in an environment where the import
  step never ran; NO PNG-based art can work there, and the engine tier is red there at HEAD too).
  The fleet's actual gate (this shared checkout, imported cache) is 222/222. Fix is a tests/
  change (conftest's import form) — OUT OF THIS CARD'S SCOPE ("do not touch any test/fixture");
  recommend the orchestrator file it as a follow-up.
- F-2: the shipped build path is unaffected by F-1 (export imports before packing — the 12 ctex
  entries above are the proof; VERIFIED).
- F-3: batch-1 sheets are T1-only; tower tier changes keep the T1 sheet until the T2/T3 art rows
  ship (VISUAL-TARGET V3 tier growth is a later pass). Blockade/trap/boss stay greybox by design.
- F-4: the 100 px = 1 world-unit sizing rule is the documented Sprite3D behaviour, and the exact
  rendered height is INFERRED (no pixels under the headless dummy rasterizer); the served + VM120
  screenshot rows of V1-V7 belong to the later passes named in VISUAL-TARGET "Delivery".

VERIFY_EXIT=0
