# W17b evidence — HUD swallows every click → build phase UNCLICKABLE (card 11386, MC 11274.1.29)

Commit: `908c2196f7589714446ab17af73cdd113a9f272e` (author `frontend (11386)`, one commit, base 8fb10a7)
Verification run: 2026-10-26, this session, all engine transcripts executed here.

## 1. Mechanism proof — WHAT swallowed the clicks (file:line)

**The brief's prime suspect FALSIFIED first (as instructed to verify):** `$Root` was
NOT STOP. `godot/scenes/hud.tscn` carries `mouse_filter = 2` (IGNORE) on Root,
TopLeft, HeroBar, BossBar (lines 14/21/42/51) — shipped IGNORE since W10
(`d9214a2`). CanvasLayer/Window parentage is irrelevant to Control picking
(proven: a Button under the CanvasLayer and one under the Node3D mission root
pick identically — scratch6, replayable via the probe idiom).

**The actual swallow (engine-VERIFIED, headless):** the CODE-BUILT display
controls in `godot/scripts/hud.gd` kept the engine defaults — measured
defaults this card: Control=STOP, Label=IGNORE, **VBoxContainer=PASS**,
ProgressBar=STOP. The hero-slot builders never set a filter:

- `hud.gd:244` `VBoxContainer.new()` — hero slot container, **PASS(1)** by default
- `hud.gd:254/257` `ProgressBar.new()` — HpBar/BlueBar, **STOP(0)** by default

A Control on the top CanvasLayer that ANSWERS a click (PASS consumes for
itself/hits children; STOP consumes) starves every Control beneath it — the
defense panel mounted at the origin (`mission.gd` mount line, pre-fix had no
`panel.position`) sits under the HUD block, so clicks in the panel region
could die in HUD display chrome. Replay of the mechanism experiment on the
BASE-COMMIT tree (`git worktree` at 8fb10a7, same probe, one click point,
three HUD states — hero-slot zone):

```
point=(30,42) tower zone
IGNORE-mode tower fired=1 defenses=0     <- clicks reach the button
PASS-slots tower fired=0 defenses=0     <- slot VBox PASS: STARVED (the shipped default)
STOP-root tower fired=0 defenses=0      <- Root STOP: STARVED
```

The same starved click turns live the instant the overlay IGNOREs. Served
caveat declared honestly: at the full 1280×720 the HeroBar band (y≥540) and
TopLeft (labels IGNORE) do not cover the panel buttons, so the exact served
starve point additionally depends on the canvas scale/size in the journey
browser (CSS-scaled clicks land on scaled engine coords; the pre-fix panel at
the origin also made Upgrade/Repair/Sell/relic rows — all DISABLED pre-selection —
the first receivers for most grid points, which also places NOTHING). Both
classes are closed by the fix: no HUD Control can answer a click ANYWHERE at
ANY size (full IGNORE pass), and the panel is geometrically clear of every HUD
rect at the served size (no swallow surface even if a default regressed).
`web_shell.html` checked as a candidate DOM absorber: only the standard
canvas + `#status` loading div — not a click sink.

## 2. Fix (smallest correct)

1. `hud.gd` setup() ends with ONE `_ignore_mouse(self)` recursive pass
   (call `hud.gd:108`, helper `hud.gd:283-287`) — every Control under $Root
   takes `Control.MOUSE_FILTER_IGNORE` (enum refs, zero literals — I2 clean;
   mouse_filter is input presentation, not mission state — I4 untouched).
   INTERACTIVE-proof, not assumed: the probe asserts the read-only HUD owns
   **0 Buttons** (33 controls, 33 IGNORE, 0 buttons) — the pinned read-only
   row means no HUD control needs clicks, so IGNORE cannot swallow one; a
   future interactive control must opt back IN (declared in the code comment).
2. `mission.gd:180` mount sets `panel.position = Vector2(904, 12)` (right
   column; comment lines net-zero — mission.gd stays 399/400).
3. `mission.tscn` ext_resource `uid=` attributes resynced to the `.uid`
   sidecars (§4). No sim/balance/data touched.

## 3. Geometry after — panel vs HUD rects @1280×720 (engine read-back, root.size forced per E8)

Panel buttons (x,y,w,h) — every one fully on-screen, all disjoint from all 32 HUD display rects:

| control | x | y | w | h |
|---|---|---|---|---|
| Rows/Class_tower | 904 | 39 | 238 | 31 |
| Rows/Class_blockade | 904 | 74 | 238 | 31 |
| Rows/Class_trap | 904 | 109 | 238 | 31 |
| Rows/Upgrade | 904 | 144 | 238 | 31 |
| Rows/Repair | 904 | 179 | 238 | 31 |
| Rows/Sell | 904 | 214 | 238 | 31 |
| Rows/Assign relic | 904 | 280 | 238 | 31 |
| Rows/Unassign relic | 904 | 315 | 238 | 31 |

Key HUD rects: TopLeft 16,12,504,158 (ends x=520); HeroBar 16,540,744,168
(starts y=540, ends x=760); BossBar 380,12,520,64 (ends x=900, hidden except
boss wave); Banner 400,320,480,80 (hidden except outcome). Reading declared:
BossBar/Banner are visibility-gated overlays; x=904 keeps 4px clearance even
against the WIDEST HUD rect (BossBar ends 900.0) at any future panel height.
Greybox fit: panel column measures 238px wide inside the 376px right column
(1280−904) — fits with 138px right margin; no shrink needed.

## 4. Picking mechanism + legs (tests/test_mission_clicks.py, engine tier)

Mechanism (declared): the engine's OWN Viewport GUI picking —
`root.push_input(motion,press,release)` is the same pipeline a browser mouse
event enters on the web build (Window::push_input → Viewport hit-test by
global rect + mouse_filter, top CanvasLayer first); the Button that receives
a complete press emits `pressed`. Every button center was clicked that way:
each picked **itself** (exactly-one-receiver; disabled buttons landed NOWHERE),
and the 3 class clicks PLANTED real defenses (state check one bookkeeping
frame later — the served bug's signature was zero):

```
GWMICE-FILTER controls=33 ignore=33 buttons=0
GWMICE-PICK clicked=8 class_clicks=3 placed=3
GWMICE-OK
```

## 5. Export UID resync — proof

Pre-fix state (measured this session, before the re-export overwrote them):
the exported `mission.scn` (cache `133200997`, mtime 07:11) embedded the pair
`(res://scripts/phase_controller.gd, uid 7879729157668148986 = uid://dki88udyr8g1w)`
at byte 2555 and `(res://scripts/enemy_runner.gd, uid 971639032300980050 =
uid://n3w0umenqbws)` at byte 2608; both ids are NOT in this project's uid map,
so the served runtime logged exactly (reproduced live post-fix, same engine):

```
ERROR: Unrecognized UID: "uid://dki88udyr8g1w".
   at: get_id_path (core/io/resource_uid.cpp:214)
ERROR: Unrecognized UID: "uid://n3w0umenqbws".
   at: get_id_path (core/io/resource_uid.cpp:214)
```

mechanism: the tscn ext rows carried NO uid attribute → the editor resolved
them through its cache AT CONVERSION TIME and baked a stale id; the export
reuses the cached .scn while the source is unchanged. Fix: `mission.tscn` now
carries the sidecar uids explicitly (duidisb02w2tl / d4iftsrpsjard /
xpjka6ao86h0 == the three `.uid` files, asserted equal by the shipped test).
Re-export (`tools/export_web.sh`, rc 0) reconverted mission.scn (mtime 19:40)
because the source changed; post-fix byte-scan: suspect-id hits in all
exported scns + static/index.pck = **0**; good path+uid pairs present in
mission.scn (1 each) and pck (2 each); sweep of ALL 8 exported script
path+uid pairs across every exported scene: unknown-to-cache = **0** — the
served console-ERROR source is closed offline.

## 6. Planted-red transcripts (a gate that never went RED is no gate)

Engine tier (HUD/Root back to STOP after setup — the W17b regression), rc=1,
red on TWO legs:

```
GWMICE-FAIL filter /root/Mission/HUD/Root mf=0 (display overlay must IGNORE)
GWMICE-FAIL pick Class_tower receiver=0 extras=0
```

Source tier, all three gates shipped inside the suite and red when planted
(3 passing tests assert the reds):
- drop the `_ignore_mouse(self)` call → `test_hud_planted_red_missing_ignore_pass_goes_red`
- panel back to `Vector2(0, 0)` → `test_mission_mount_planted_red_origin_panel_goes_red`
- ext uid swapped to the stale `uid://dki88udyr8g1w` → `test_tscn_uids_planted_red_stale_uid_goes_red`
- plus the base-tree replay in §1 (PASS-slots/STOP-root starve, IGNORE fires).

## 7. Verification (this session, committed tree)

- `python3 -m pytest tests/ -q` → **200 passed** (192 prior + 8 new
  tests/test_mission_clicks.py, 506 lines ≤ 600), exit 0
- `python3 tools/check_hygiene.py` → **0 hits** (hud.gd 287 ≤ 400, mission.gd 399/400)
- engine probe stderr EMPTY (W4 ruling) in both modes
- git: ONE commit `908c2196f7589714446ab17af73cdd113a9f272e`, author
  `frontend (11386) <frontend@agent-town.local>`; LEDGER W17b row + engine
  facts E7 (headless push_input picking + same-frame add_child not pickable)
  and E8 (force served size via root.size under -s) appended in the same commit.
- Known limitation declared: the re-journey leg over the served build belongs
  to the orchestrator (LEDGER row updated); static/ is gitignored by shipped
  design (the W12 repro contract regenerates it byte-identically).

VERIFY_EXIT=0
