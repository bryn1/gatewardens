# ZOOM_SPEC — v1.3 camera zoom control (MC 11792) [type:plan, READ-ONLY]

REV c2 (2026-10-31, post-DA): DA-verdict FIX round applied — P1-1 declared `load_steps=9→10` header
bump (§3 row 2, S3, A5); P1-2 press-only wheel + declared per-tick edge guard (§1) with a buildable
DEDUP+distinct-ticks A4 leg; P2-1 PLACE leg gets its producing stage (S4); P2-2 pre-S3 baseline
capture feeds A2 (S1). Design core (wheel-only, 56/128/8, runtime-only, GOVERNED 17, single byte
re-pin) unchanged — DA verified it.

Repo `/home/claudecode/Games/gatewardens`, tip `7bf18cf` (origin/main; suite 283 green per card
preamble — collection-verified 283 in the base audit, full re-run is the build card's leg).
Owner grant MC 11719 (2026-10-30) verbatim: **"Go 1 and zoom control for 2."** — ZOOM ONLY.
D3 camera-pin doctrine otherwise STANDS: the rig's basis/pitch is immovable, the default D=64 rig
stays the default. Zero monetization forever (MC 11274.1).
READ-ONLY card: zero repo changes outside this `.audits/20261031-1100-v13-zoom-plan/` dir;
`git status --porcelain` empty apart from this dir (re-checked at return). NEVER spawned — leaf.
Pre-reads honored: `.audits/20261030-1830-v13-clean-code/FINDINGS.md` §5 (RF-1..RF-5) + §7
(DO-NOT-TOUCH ×13); `docs/ARCHITECTURE.md` (C4 camera row, bridge row, pin #3 story);
`tests/test_hub_layout.py` camera region; live camera/input code (main.gd, bridge.gd, mission.gd,
defense_panel.gd, defense_placer.gd, v1_world_probe.gd, g5_real_relay_probe.gd, web_shell.html).
Derivation instrument: `/tmp/zoom-11792/dmin.py` — the RF-1 gate's OWN `_cam_from_tscn`/`_map_points`/
`_in_frustum` math reused verbatim over the shipped `godot/data/maps/gatefall.json` (numbers below
are MEASURED this session, not guessed; the build card re-derives them engine-side — §6 S1).
Length reason: one spec, six DoD sections read together; under 300 lines.

## 0. SHAPE (one paragraph)

Zoom = a runtime, wheel-driven translation of the shipped `CameraRig` ORIGIN along its own frozen
line of sight. The `.tscn` rig row NEVER changes; the pitch/basis NEVER changes (D3); every wheel
tick steps a clamped distance `D ∈ [D_MIN, D_MAX]` around the byte-pinned default. The rig row
stays the ONE home of the default (the zoom node CAPTURES it at `_ready` — no `64` literal in code).
One new scene script + one append-only scene edit (with its declared §3 header bump) + one declared
re-pin row + new tests + a relay kit. No bridge change, no mission.gd code line, no shell change,
no HUD change.

## 1. INPUT DESIGN

**Primary and only shipped affordance: MOUSE WHEEL.** Wheel-UP = zoom IN (D decreases, toward the
map); wheel-DOWN = zoom OUT (D increases). One tick = one `ZOOM_STEP` (grid below); repeat ticks
are repeat steps (Godot sends a press/release pair per tick).

**+/− keys: NOT added.** Reasons, each measured at tip:
1. The key route would be a SECOND mechanism for one action beside the wheel (replace-do-not-add
   law), and every shipped key route ends in `mission.gd::step_bookkeeping`'s ONE press pump
   (`mission.gd:242`) — the pump is pinned ("one pump, routed, C12 (5)"). A second reader draining
   the bridge is forbidden; routing new codes THROUGH the pump needs code lines in `mission.gd`,
   which sits AT the 400-LOC hard ceiling (clean-code audit W4-watch: "cards still add ZERO lines").
2. The only existing pump-consumer that could host it, `DefensePanel.poll`, is build-phase-scoped
   (rows DISABLE through combat, G5b); zoom must work in both phases. Dead end by design, not by
   taste.
3. Wheel is already the repo's shipped engine-native presentation-input precedent: the hub
   `ScrollContainer` ("PanelScroll") reaches the DECK rows BY MOUSE WHEEL with zero bridge
   involvement (`hub.gd:34-44`, `:128-130`). Wheel-then-zoom rides the same class of input.
   If the owner later wants keys, the legal home is AFTER a `mission.gd` split (future card).

**Reading path (chosen design, smallest surface):** the new zoom node owns its own
`_unhandled_input(event)` and reads `InputEventMouseButton` with `button_index` in
`{MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN}`. The wheel does NOT enter `GWBridge`:
- the bridge's ONE-feed-point doctrine governs the KEY/gameplay-command relay (`bridge.on_key`,
  FINDINGS §2); wheel-as-presentation matches the ScrollContainer precedent, not the key relay;
- adding WHEEL codes to `DISCRETE_KEYS` would queue them into `presses` where the mission pump
  drains-and-drops them (§1.1) — actively hostile;
- `main.gd::_unhandled_input` (`main.gd:188-197`) maps mouse through `bridge.mouse_code` → today
  wheel hits `MOUSE_CODES.get(index,"")` → `""` → dropped (why zoom is exactly zero today —
  VERIFIED at tip: no wheel entry exists).

**PRESS-ONLY + DECLARED PER-TICK EDGE GUARD (c2, DA P1-2 — the mechanism, stated before build):**
one physical tick is itself a press+release PAIR — the shipped kit idiom dispatches
`[true, false]` per tick (`g5_real_relay_probe.gd:221-227` `_mouse()`, VERIFIED at tip). Therefore
`camera_zoom.gd` acts ONLY on `event.pressed == true` (releases ignored) AND owns a declared
per-tick EDGE GUARD: one step is accepted per event-frame per `button_index` — a duplicate arrival
of the SAME tick inside the step collapses to one step; two distinct ticks are two steps. The
guard is node-local `_unhandled_input` state by necessity: the bridge's rising-edge dedup
(`bridge.gd:59-67`) is STRUCTURALLY UNAVAILABLE to the wheel — this section shows wheel never
enters `GWBridge` — so reusing it is impossible, not merely unchosen; the node-local guard is
wheel-path-only and does not stand beside `on_key` as a duplicate key-queue mechanism. The A4
`DEDUP` leg pins exactly these two semantics (§5).

**WEB DOUBLE-FEED law (cited, binding):** on the served web export ONE physical event reaches
GDScript TWICE — the shell JS relay AND the engine's own canvas listener via `main.gd`'s forwarder
(`bridge.gd` G5b header, MC 11700, served-measured on the `19715d4` export: one KeyM press =
TWO places). Consequence that binds this spec: **press queues are rising-edge only** —
`on_key` appends only when the code is not already `held` (`bridge.gd:59-67`); no new input
mechanism may assume one arrival per physical event.
Wheel's actual served arrival is different and MUST BE MEASURED, NOT ASSUMED: `web_shell.html`
relays ONLY `keydown`/`keyup` (`:106-110`, `e.code` semantics; no `wheel` listener exists), so the
engine's canvas pipeline is the wheel's sole web feed — expected ONE arrival per tick. That
expectation is a leg, not a claim (§5 A4): the shipped kit idiom to EXTEND is
**`godot/sim/g5_real_relay_probe.gd`** — "boots the REAL mission, mounts the REAL `main.gd` script
as a relay object and feeds it SYNTHESIZED InputEvents: the closest production analogue runnable
under `-s`" — its `_key_press()`/`_mouse()` helpers (`:213-228`) build real
`InputEventKey`/`InputEventMouseButton` and push them through the real forwarder. The new kit
`godot/sim/g6_zoom_relay_probe.gd` clones that idiom with `button_index = MOUSE_BUTTON_WHEEL_UP/
DOWN`, dispatching via the real tree path (`root.push_input`) so the zoom node's OWN handler runs,
plus a `DEDUP` leg of the kit's own shape pinning the §1 edge-guard semantics: feed the same tick
twice (both live paths) and assert STILL exactly one step, AND two distinct ticks assert exactly
two steps — proving the design stays correct if the shell ever grows a wheel relay, and that the
guard never eats real input.

**Wheel-over-GUI blind spot, declared (not a gap):** Godot's viewport consumes mouse-button-class
events under GUI Controls before `_unhandled_input` — wheel over a list that swallows it SCROLLS
the list instead (shipped hub behavior), and wheel over the in-mission DefensePanel's Controls
(picker rows/buttons) is consumed there. Zoom therefore lives everywhere the wheel is not eaten —
consistent with the shipped hub scroll; the kits bypass GUI by direct dispatch, and the served
acceptance frame (§5 A1) is captured with the pointer over the play area.

## 2. ZOOM ENVELOPE

**Constants (ONE home: `godot/scripts/camera_zoom.gd`, the new rig-owner script):**
- `D_MIN := 56.0` — closest allowed rig distance (u)
- `D_MAX := 128.0` — farthest allowed rig distance (u)
- `ZOOM_STEP := 8.0` — u per wheel tick, applied around the CAPTURED default
- (`DEFAULT_D` is NOT a constant — captured from the scene at `_ready`; see proof-row.)

**GOVERNED_LITERALS: NO — the new file does NOT join the set; the pinned set stays the 17**
(`tools/check_hygiene.py:80-85`, pin #10: set changes are a same-commit governance event with the
three test importers). `camera_zoom.gd` joins the DECLARED-UNGOVERNED presentation-numbers doctrine
instead — the exact precedent family of `range_ring.gd`, `world_text.gd`, `sprite_bank.gd` and
`hero_pawn.gd`'s crest numbers ("presentation numbers live on this file, the declared ungoverned
doctrine", ARCHITECTURE rows): I2 guards gameplay ECONOMY literals (a camera distance cannot smuggle
a cost or ratio), and the file is new + declared in its header + given an ARCHITECTURE Modules row
in the wiring commit. The answer is explicit: **17 → 17, unchanged.**

**Camera math (stated formula; the gate itself is the oracle — reuse, not new mechanism):**
The rig sits at `O(D) = D · û` with `û = normalize(0, 47.47, 42.79) = (0, 0.7428, 0.6695)` taken
FROM the shipped row; forward is `−û`; basis frozen (pitch 48° unchanged — D3). A map point P
(ALL of `test_hub_layout._map_points()`: waypoints, main+sub cores, spawners, hero battle space)
stays framed iff, per the RF-1 `_in_frustum`: `along > 0` and
`ang_v ≤ 0.92·(75°/2)` and `ang_h ≤ 0.92·(hfov/2)`, `hfov = 2·atan(tan(37.5°)·1280/720)`.

- **Zoom-IN floor (DERIVED, measured this session):** sweeping D down from the shipped
  `D₀ = |origin| = 63.909`, the LAST passing step is **D = 52.66**; the FIRST red step is **52.41**,
  cropping waypoint `(34, 0, 30)` (lane waypoint, east edge). Step grid from the default:
  64−k·8 → 56, 48 (48 is deep inside red). `D_MIN := 56.0` = last grid line clear of the red floor,
  **3.59 u of safety margin**. Verified: all map points pass at 56.0.
- **Zoom-OUT cap:** the frustum gate passes to D ≥ 160 (checked 96/128/160 — all green), so the
  floor is not what bounds zoom-out; READABILITY does. Anchor (shipped measurement,
  `enemy_anim.gd:40`): at the D=64 rig `1 px ≈ 0.154 u`, so the declared 0.23 u walk-bob ≈ 1.5 px.
  Doubling the distance halves screen scale → the bob falls below 1 px at D = 2·D₀.
  `D_MAX := 128.0` = 2× the default, the stated readable-far limit. Verified: all points framed at
  128.0.
- The build card's S1 kit re-derives BOTH numbers engine-side through the shipped `Camera3D`'s own
  `unproject_position` (the `v1_world_probe` FRAME idiom — "the engine's own projection, not a
  re-derivation"), because the test-side frustum math is itself a re-derivation the kit must close.

**PROOF-ROW — DEFAULT D=64 stays byte-unchanged:** the shipped row
`transform = Transform3D(1, 0, 0, 0, 0.669, 0.743, 0, -0.743, 0.669, 0, 47.47, 42.79)`
(`godot/scenes/mission.tscn`, `|origin| = 63.909` = the "D=64" shorthand) is **NOT EDITED** — zoom
is runtime-only displacement; the scene file, `tests/test_hub_layout.py:331-342` (FOV_DEG 75.0,
MARGIN 0.92, the regex) and `:398-402` (planted rig-row literals) stay BYTE-IDENTICAL. The zoom
node reads its default from the scene at `_ready` and re-applies it untouched when zero wheel
events have arrived, so a fresh mission at zero input renders the identical frame (§5 A2 byte-
compares it). The new test file ADDS a source-truth byte-pin asserting the tscn row still equals
the shipped literal — locking the default against future drift (a NEW pin, declared here,
not a move of pin #3, which stays SPENT and untouched).

## 3. RE-PIN ARTIFACT

**What zoom moves: one byte-pinned re-pin + one relational header bump (pinned value,
planted-red-then-green) — declared here, both ride the S3 wiring commit:**

| row | file:line | old literal | new literal | derivation |
|---|---|---|---|---|
| `test_mission_tscn_uids_match_the_sidecars` ext-script-row count | `tests/test_mission_clicks.py:591` | `== 5` | `== 6` | count = #script ExtResource rows in `mission.tscn`; wiring APPENDS exactly one script ext row (camera_zoom.gd, uid attribute + committed `.uid` sidecar per the `:31-32` sidecar gate). Declared-drift chain is documented at the pin: 3→4 (V5 MC 11552), 4→5 (G3 MC 11696), **5→6 (this card, declared scene-script add — the only legal mover per §7 pin #6)**. Planted-RED first: the scene commit alone goes the leg RED (transcript kept); the retarget lands GREEN in the same commit. |
| `mission.tscn` header `load_steps` (relational, c2/DA P1-1) | `godot/scenes/mission.tscn:1` | `load_steps=9` | `load_steps=10` | `test_wave_telegraph.py:226-231` pins relationally `load_steps == ext_count + sub_count + 1` (measured at tip: 7 ext + 1 sub + 1 = 9 — VERIFIED). The APPENDED ext row FORCES the header to 10 in the same commit: a letter-only "APPEND-only" build leaves 9, goes RED on `test_mission_tscn_mounts_the_telegraph_append_only`, and the stale header's Godot WARNING then pollutes every EMPTY-stderr gate. Precedent: G3's declared 4→5 add (`commit 0b49bba`) shipped `-[gd_scene load_steps=8] +[...load_steps=9]` beside its ext row. Same red-then-green protocol as row 1: the scene-append-alone state is the planted RED for both legs; the bump + retarget land GREEN in the same commit. |

This is not a second byte re-pin — the header row is a derived counter held by a RELATIONAL pin,
not a literal-equality pin; §3's byte-identical contract below is unchanged.

**Rows that must stay BYTE-IDENTICAL (the fixtures-diff-EMPTY contract).** If any of these moves,
the zoom card is broken:
- `mission.tscn` `CameraRig` transform row + the whole `[node name="CameraRig"]` block (§2
  proof-row); the `:398-402` planted replace-TARGET string (pin #3 SPENT);
- `test_hub_layout.py:331-333` (`FOV_DEG 75.0`, `VIEW`, `MARGIN 0.92`), `:337-342` regex,
  `:410-418` lighting rows (pin #4);
- fixtures `mission_gatefall_normal.jsonl` (`sha eafe3932…`) / `_hard.jsonl` (`5e37c4b0…`) —
  `sha256sum` re-run at the build card's return must match (§7 pin #1); `godot/data/maps/
  gatefall.json` untouched;
- `godot/sim/v1_world_probe.gd:40` `MIN_MARGIN := 60.0` (RF-3): the kit never feeds wheel → runs at
  the default rig → this leg re-runs **byte-GREEN unchanged**; a RED here means the zoom leaked into
  the default frame (that IS the alarm — the spec does NOT re-declare the margin);
- shot kits `v1_world_shot / v5_fx_shot / v11_boss_shot` (RF-4): machine legs byte-green at the
  default rig; the committed LEDGER pixel rows REMAIN honest D=64 evidence because the default
  never moved — new zoomed frames are NEW rows, never re-labels;
- bridge pins `test_bridge_contract.py:111/:116` (§1 design touches no bridge, no shell);
- `v6_tween_probe` screen-rect pins (UI layer, camera-independent per RF-5) and every RF-5
  world-const (no zoom card re-declaration needed: RF-5's constants ride heights/sizes, a pure
  distance change re-projects them, it does not re-tune them — re-checked by A1's frames).
  Declared deviation cited BY NAME (c2/DA N3): FINDINGS §6 W4 (`FINDINGS.md:195`) expects the
  camera card to "re-pin RF-1/2/3/4 ONCE each … re-declares each RF-5 const once"; this card
  instead keeps ALL those rows byte-identical (stricter, D3-consistent — runtime-only zoom) and
  declines the RF-5 re-declaration; the deviation is DA-verified and proved by A1's frames +
  the byte-ident `git diff` rows of A5.

## 4. CLICK MAPPING UNDER ZOOM

**Engine-side path, named in shipped code:** `InputEventMouseButton` → `main.gd::_unhandled_input`
(`main.gd:188-197`) → `bridge.mouse_code` → `bridge.on_key` (ONE feed point, rising-edge,
`bridge.gd:59-67`) → `mission.gd::step_bookkeeping` ONE pump (`mission.gd:242`) →
`$DefensePanel.poll(presses)` → PRESS map `"MouseLeft": "confirm"` (`defense_panel.gd:72`, handled
`:140-145` armed-only) → `place_id(armed ghost slot)` (`defense_placer.gd:243`, the ONE gate
sequence; confirm falls to first-free `:252-253`, the pinned LEDGER:16 behavior).
**Honest finding, stated against the brief's premise (CONTRADICTED at tip):** the shipped placement
click does **NOT ride a screen→world projection** — `project_*`/`unproject_*` appear **ZERO times**
in `godot/scripts/` (grep this session, every file `:0`). The placement target is the discrete
ARMED GHOST SLOT — chosen by ArrowLeft/Right cycling over `placer.buildable()`, not by click
coordinates. Consequence: **placement is zoom-invariant BY CONSTRUCTION** — no mapping can drift
under zoom because no mapping exists. What rides the zoom is the RENDERED world: ghost and range
ring are world-space nodes (e.g. `RANGE_RING.show_ring(m, slots[ghost], radius)`,
`defense_placer.gd:215`) that the engine re-projects per frame (the `v1_world_probe` FRAME leg —
"through the SHIPPED Camera3D (`unproject_position`) … not a re-derivation" — is the existing
demonstration that world→screen follows the camera automatically). §5 A3 still LANDS a tower at
distance: a construction-proof is a property, so it gets a measured leg anyway.

**DOM-side path, named in shipped code:** `godot/web_shell.html` = canvas + the key relay ONLY
(`:96-110`, `keydown`/`keyup` → `window.gwHost.on_key`) — there is NO DOM-side HUD and no DOM
coordinates in the product; Playwright reads `window.__gwSnapshot` / `GW_STATE()` (C5), never
pixels. The HUD is IN-ENGINE Controls (`hud.tscn` + `hud.gd::_ignore_mouse`, MOUSE_FILTER_IGNORE
`:379-382`) laid out in viewport screen space (e.g. the panel at `Vector2(904,12)`,
`mission.gd:180`) — screen-space layout is a function of the VIEWPORT, not the camera, so zoom
cannot move it. Declared invariant for the build card: the diff touches NEITHER `web_shell.html`
NEITHER `hud.gd/hud.tscn` (DOM-side HUD coordinates: unaffected by absence + by design).

## 5. ACCEPTANCE LEGS (the build card's evidence file reproduces each with a level)

- **A1 SERVED FRAMES ×3 — default, zoomed-OUT (D_MAX), zoomed-IN (D_MIN):** served-browser (or the
  shot-kit boot idiom) frames after dispatching real/synthesized wheel ticks; in EVERY frame the
  lane bands (`LaneBand_<lane>` nodes) and the range ring (`RangeRing`) must still be ALIVE and
  PAINTED — the G2 **PrimitiveMesh law** (engine-managed primitives, no ArrayMesh hand-rolls) —
  asserted by node presence BY NAME (§7 pin #12 contracts) + pixel-visible via describe-image
  (game visuals = browser + describe-image verification, MC 11509 D3 scope row).
- **A2 DEFAULT-FRAME IDENTITY:** fresh mission, zero wheel input → frame byte-compares the
  **pre-S3 baseline captured by S1** (§6 S1 row: `baseline-default-D64.png` + its sha256 sidecar,
  stored in this `.audits/20261031-1100-v13-zoom-plan/` dir BEFORE the scene edit exists — the
  compare-basis is that file, not a post-change re-render; c2/DA P2-2) (runtime proof of §2's
  proof-row: default D=64 unchanged where it counts, the pixels).
- **A3 PLACEMENT AT DISTANCE:** wheel out to D_MAX, arm a picker row, relay `MouseLeft` → defense
  count +1 at the ghost slot (`place_id` ok:true); leg also runs at D_MIN (kit row, produced by
  S4's `PLACE` line — §5 A4 list; served spot check optional).
- **A4 RELAY MEASURED (new kit `g6_zoom_relay_probe`, §1 idiom):** `WHEELIN`/`WHEELOUT` one
  synthesized tick through the real forwarder = EXACTLY one step; `DEDUP` the same tick fed twice
  (engine forwarder + JS-relay path, the 19715d4 double-feed shape) = STILL one step, AND two
  distinct ticks = exactly two steps (both clauses pin the §1 press-only + edge-guard mechanism;
  the leg is its red-then-green pin — a build without the guard ships RED here);
  `PLACE` wheel to D_MAX → arm → relay `MouseLeft` → count +1 at the ghost slot, `place_id` ok:true,
  also run at D_MIN (this is §5 A3's producing row, c2/DA P2-1);
  `BOUNDMIN`/`BOUNDMAX` clamps at 56.0/128.0 (D never leaves the envelope, order of ticks
  irrelevant); kit is pytest-referenced (kit census law, FINDINGS §3 DC-3 rule).
- **A5 SUITE + GATE:** full pytest green **except** the declared §3 moves, each shown
  **planted-RED (transcript) then GREEN in the same commit** — both the `:591` byte re-pin AND the
  relational `load_steps=9→10` header bump (§3 row 2; the scene-append-alone state is the shared
  planted RED for both legs, c2/DA P1-1); suite count grows (283 → 283+N) and
  the README/RELEASE_NOTES/LEDGER count claims update in the SAME commit (claim-rot law);
  `tools/check_hygiene.py` 0 hits; every new file under its ceiling; `mission.tscn` edit is
  APPEND-only **plus its declared header bump** (ext row + new `CameraZoom` node block under
  `CameraRig` + header `load_steps=9→10` — the ONLY non-append line the diff may carry in that
  file); `camera_zoom.gd.uid` sidecar committed; **all other camera/fixture rows byte-identical →
  `git diff` over the pins of §3 shows EMPTY** (the fixtures-diff-EMPTY contract, sha rows re-run).
- **A6 ZERO-MONETIZATION ROW (MC 11274.1, forever):** the evidence file carries the literal row
  `monetization surface added: NONE` backed by the diff inventory (no shop/purchase/premium/currency
  string in any added line; the diff's file list is exactly the §6 owned-files list).
- **A7 DOC-SYNC (retired-claim law, same commit as wiring):** the F8 "never touched" claims get
  rewritten where they contradict shipped reality AFTER this card: `mission.gd:156` comment,
  `hero_controller.gd:11` comment (both LOC-neutral rewrites — mission.gd stays ≤ 400),
  `docs/ARCHITECTURE.md` C4 rig sentence (`:231`) + a new `scripts/camera_zoom.gd` Modules row +
  the camera-story line citing the MC 11719 grant ("zoom steps the rig origin along the frozen
  LOS; basis/default LOCKED, pin #3 still SPENT"). Grep `never touched` over docs+scripts → 0
  stale hits at return.

## 6. BUILD DECOMPOSITION (stages, owned files, order; DA-gate BEFORE build)

The future build card runs these; THIS card owns no repo file.

| stage | what | owned files (touch set) | checkable DONE |
|---|---|---|---|
| **G0 (BEFORE any build)** | devils-advocate gate on THIS spec | none (reads this file; writes its VERDICT doc) | c1 ran on c1 of this doc → `# VERDICT: FIX` (2 P1 + 2 P2, DA-verdict.md); its four exact corrections are applied in THIS c2. Build gate: a DA re-check of c2 lands `# VERDICT: SHIP` (same `.audits/` dir) before S1 — the cycle count/cap is the build card's task-gate law. Attack surface named: D_MIN derivation vs RF-1, node-local wheel reader vs the one-feed-point doctrine (ScrollContainer precedent), the 5→6 re-pin legality + the declared `load_steps` relational bump (§3 row 2), envelope endpoints, press-only + edge-guard dedup (§1) |
| **S1 ∥ S2** | S1 envelope sweep kit + **pre-S3 baseline capture** (c2/DA P2-2); S2 the zoom script (independent — S2 depends only on §2's constants) | S1: `godot/sim/g6_zoom_sweep_kit.gd` (new; v1_world_probe FRAME idiom, re-positions `CameraRig/Camera3D` in the booted mission, prints screen margins per D, asserts red at ≤52.41 and green at 56/128) + `baseline-default-D64.png` + sha256 sidecar in this `.audits/` dir (boots the UNMODIFIED mission, zero wheel input — captured BEFORE S3 exists) / S2: `godot/scripts/camera_zoom.gd` (new) | S1: kit printed margins agree with §2 within 1 u; pytest-referenced leg; baseline PNG + sha256 exist in this dir with pre-S3 timestamps. S2: compiles headless, W4 preload binding, no literal but the three §2 consts, press-only + §1 edge guard per its declaration, < 250 LOC, header states the ungoverned-presentation doctrine |
| **S3 (after S1+S2)** | wiring — one commit: `mission.tscn` append (uid-bearing ext row + `CameraZoom` child node under `CameraRig`) **WITH the declared header bump `load_steps=9→10` (§3 row 2 — required by the relational pin, G3 precedent 0b49bba; c2/DA P1-1)**, `camera_zoom.gd.uid`, the §3 `5→6` RETARGET (scene-append-alone planted-red transcript attached, shared by both §3 legs), §5 A7 comment/doc rewrites | `godot/scenes/mission.tscn`, `godot/scripts/camera_zoom.gd.uid`, `tests/test_mission_clicks.py` (:591), `godot/scripts/mission.gd` (comment only, LOC-neutral), `godot/scripts/hero_controller.gd` (comment), `docs/ARCHITECTURE.md`, `LEDGER.md` (PIN row + card row) | suite green apart from none (both §3 moves ride the same commit); §3 byte-ident list `git diff` EMPTY; ext-count AND `load_steps` relational legs RED-then-GREEN transcripts attached |
| **S4 (after S3)** | tests + relay kit: `tests/test_camera_zoom.py` (default-row byte-pin re-assert, envelope consts, wheel-not-in-bridge source-truth, kit-run lines) + `g6_zoom_relay_probe` kit rows `WHEELIN/WHEELOUT/DEDUP/PLACE/BOUNDMIN/BOUNDMAX` (DEDUP asserts BOTH clauses of §1's press-only+edge-guard: same tick fed twice = one step AND two distinct ticks = two steps; PLACE is the producing row for §5 A3 place-at-distance — c2/DA P2-1) + pytest wiring | `tests/test_camera_zoom.py`, `godot/sim/g6_zoom_relay_probe.gd`, the pytest test that runs the kit | full suite 283+N GREEN (all pre-existing lines byte-unchanged per §3); hygiene 0 hits |
| **S5 (after S4, serial)** | acceptance: A1 frames ×3 + describe-image, A2 default-frame identity, A3 place-at-distance, evidence file + VERIFY_EXIT, count rows synced | none new (evidence under this `.audits/` dir; README/RELEASE_NOTES count rows + LEDGER status line) | evidence file reproduces A1–A7 each with an evidence level; last line `VERIFY_EXIT=0` |

Parallel-safe: **S1 ∥ S2** (disjoint files, no shared artifact). S3 is the first join and the ONLY
stage touching `mission.tscn`/`test_mission_clicks.py` (shared-file law). S4 follows S3 (needs the
wired scene); S5 last, serial. Order law: G0 SHIP gate BEFORE S1 — no build commit without it.
Zero monetization (MC 11274.1 forever) binds every stage: the S5 diff inventory names the full
touch set above and nothing monetization-shaped exists in it.

## RETURN

Deliverable: this file, `.audits/20261031-1100-v13-zoom-plan/ZOOM_SPEC.md` (six sections per the
DoD; ≤300 lines; READ-ONLY honored — the repo's only new path is this directory, `git status
--porcelain` shows exactly it). One open item flagged, NOT silently chosen: the brief's §4 premise
("placement clicks ride camera projection") is CONTRADICTED by the shipped code (§4 finding) — the
spec plans against the shipped truth and keeps the placement-at-distance leg anyway.
VERIFY_EXIT=0
