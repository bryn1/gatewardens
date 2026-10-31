# DA-verdict — G0 adversarial refutation of ZOOM_SPEC.md (MC 11792 / MC 11719) [type:devils-advocate]

Target: `.audits/20261031-1100-v13-zoom-plan/ZOOM_SPEC.md` @ spec tip `7bf18cf`; HEAD `59ffea6`
is the spec's own commit (verified: `git merge-base --is-ancestor 7bf18cf HEAD` + `git log`), so
no byte-pin surface moved since the spec was written. READ-ONLY honored: the only write by this
run is this file + `.tmp/` scratch. Suite base re-measured: `283 tests collected` (this session).
Every claim below is grep/measure evidence at the shipped tree; no speculation rows.
JUDGED-line reading: the task prompt carried NO `dod_judged_hash.py` command, so per the MC 3720
conditional ("if your prompt carries…") no `# JUDGED:` line applies to this verdict.

## FINDINGS

### P1-1 — the load_steps header bump is a REQUIRED second moved row; the spec never declares it. FIX-forcing.
- The shipped gate `tests/test_wave_telegraph.py:226-231` pins, relationally:
  `load_steps == ext_count + sub_count + 1` in `godot/scenes/mission.tscn`. Measured at tip:
  `load_steps=9`, 7 ext + 1 sub → `7+1+1=9` holds. The wiring ADDS one ext row → the header MUST
  become `load_steps=10` in the same commit.
- Precedent that "APPEND-only" always included this bump: `git show 0b49bba` (G3, the 4→5 declared
  add) contains `-[gd_scene load_steps=8 …] +[gd_scene load_steps=9 …]` beside its new ext row.
- A build that follows the spec's letter — §5 A5 "mission.tscn edit is APPEND-only (ext row + new
  `CameraZoom` node block…)" and §6 S3 "one commit: mission.tscn append (uid-bearing ext row +
  `CameraZoom` child node…)" — appends rows only, leaves the header at 9, and goes **RED** on
  `test_mission_tscn_mounts_the_telegraph_append_only` (its own docstring: a stale header is the
  Godot WARNING that pollutes every EMPTY-stderr gate — the stderr-empty kit legs fail too).
- §3's table title "Every byte-pinned row that zoom moves — exactly ONE" under-declares the move:
  exactly one BYTE-PINNED row (`test_mission_clicks.py:591` 5→6) PLUS one relational counter row.
- Exact correction: add to §6 S3's touch list and §5 A5 the literal row
  `[gd_scene load_steps=9 format=3] → load_steps=10` (declared; cite the G3 precedent 0b49bba),
  and amend §3's framing to "one byte-pinned re-pin + one relational header bump (test_wave_telegraph.py:226-231)".

### P1-2 — the A4 DEDUP leg is unsatisfiable by the design the spec states; the needed mechanism is undeclared. FIX-forcing.
- §1 gives `camera_zoom.gd` a plain `_unhandled_input` wheel reader and states the wheel does NOT
  enter GWBridge — so `bridge.on_key`'s rising-edge dedup (`bridge.gd:59-67`, verified) is
  structurally unavailable to it.
- One physical tick is itself a press+release PAIR (the spec's own §1 words; the shipped kit idiom
  `godot/sim/g5_real_relay_probe.gd:221-227` `_mouse()` dispatches `[true, false]`). Nothing in
  §1/§2 states that the node acts on `event.pressed` only, and NOTHING in the spec gives it any
  edge-guard at all.
- §5 A4 then requires: "`DEDUP` the same tick fed twice (engine forwarder + JS-relay path…) =
  STILL one step". Two fed ticks = two presses = **two steps** under the stated design — the leg
  cannot pass; the build either ships red or invents an undeclared mechanism mid-build. An invented
  held-style guard would duplicate `bridge.on_key`'s dedup semantics beside it (one-mechanism law)
  without the declaration §2 bothers to make even for the constants.
- Exact correction: §1/§2 must state the mechanism now: node acts only on `event.pressed == true`,
  and `camera_zoom.gd` owns a declared per-tick edge guard that collapses a duplicate arrival of
  the same tick within the step (name the semantics the DEDUP leg asserts, e.g. one step per
  event-frame per button_index); declare WHY it cannot reuse `bridge.on_key` (spec's own §1.1
  reasoning), and pin the guard with its own red-then-green leg in S4.

### P2-1 — A3 (place-at-distance) has no producing stage.
§5 A3 says the leg is a "kit row"; §6 S4's g6 kit rows are enumerated only
WHEELIN/WHEELOUT/DEDUP/BOUNDMIN/BOUNDMAX (§5 A4 list), and S5 owns "none new". No stage authors the
PLACE leg, while §4's whole click-mapping-under-zoom DoD rests on it. Correction: add a PLACE row
(wheel to D_MAX → arm → relay `MouseLeft` → count +1 at the ghost slot, `defense_placer.place_id`
ok:true; also run at D_MIN) to the S4 kit + the A4 row list.

### P2-2 — A2's byte-compare has no pre-change baseline capture.
§5 A2 "frame byte-compares the pre-change default frame" — no stage captures that baseline BEFORE
S3 lands the scene change (S1/S2 are file-disjoint and don't mention it; S5 runs after wiring).
Correction: S1 (or S2) stage adds "capture default-mission frame PNG + sha256 into this .audits
dir, pre-S3", and A2 names that file as the compare-basis.

### NOTES (taste/citation — never gate)
- N1: citation drift: rising-edge `on_key` cited "bridge.gd:63-71", measured `:59-67`; `main.gd`
  forwarder cited `:188-196`, measured `:188-197`. Content present at both.
- N2: §2 prints `û=(0,0.7428,0.6693)`; `normalize(origin)` measures `(0,0.7428,0.6695)` —
  transcription only; the spec's own instrument `/tmp/zoom-11792/dmin.py` runs and reproduces
  §2's numbers exactly (below).
- N3: FINDINGS §6 W4 (`.audits/20261030-1830-v13-clean-code/FINDINGS.md:195`) expects the camera
  card to "re-pin RF-1/2/3/4 ONCE each … re-declares each RF-5 const once". This spec instead keeps
  ALL those rows byte-identical (runtime-only zoom, D3-consistent, stricter) and declines RF-5
  re-declaration with reasoning + the A1 frames leg. Justified deviation, but it should cite W4 by
  name instead of staying implicit — the next verifier will otherwise call it out.
- N4: declared wheel-over-GUI blind spot is real: the DefensePanel column at x=904 (`mission.gd:180`)
  swallows wheel over its Controls — zoom will feel dead over the right column, owner-visible UX
  cost, declared.

## SURVIVED — refutation attempts that the shipped tree supported (spec claims VERIFIED here)
1. **Wheel single-feed**: `godot/web_shell.html` relays ONLY `keydown`/`keyup` (`:106-110`), zero
   wheel/scroll listeners (grep, this session); `bridge.gd:41-43` `MOUSE_CODES` carries LEFT/RIGHT
   only (WheelMiddle removed by DEAD-2, header comment), so wheel → `mouse_code` → `""` → dropped
   before `on_key` (`main.gd:195-203`). Wheel enters GWBridge ZERO times; the served engine-canvas
   path is its only feed and the spec honestly makes its arrival a MEASURED leg (A4), not a claim.
   The "wheel in DISCRETE_KEYS would be drained-and-dropped" logic holds (`mission.gd` one pump,
   `bridge.gd:64` gate). No double-feed path into GWBridge exists. CLAIM HOLDS.
2. **D_MIN=56 derivation**: re-derived independently with the gate's OWN
   `_cam_from_tscn/_map_points/_in_frustum` (imported from `tests/test_hub_layout.py`, not copied):
   D₀=63.909, D=56 GREEN (all points), D=48 RED, red edge crops `(34,0,30)` exactly as claimed;
   96/128/160 GREEN (out-bounded by readability, not frustum — anchor `enemy_anim.gd:40` "1 px ≈
   0.154 u" present). Spec's own instrument runs: `first failing D 52.41 / last passing 52.66`
   reproduced (0.25-step grid from D₀). My finer 0.01 sweep places the true red floor at ~52.47 —
   the spec's quoted endpoints are grid-anchored, the 56 choice stands with ≥3.3 u margin either
   way, and S1's "agree within 1 u" tolerance covers it. CLAIM HOLDS.
3. **The single re-pin**: `test_mission_clicks.py:591` `== 5` verified (chain 3→4→5 documented at
   the pin; §7 pin #6 makes a declared scene-script add the only legal mover). Full byte-pin sweep:
   I2 gate scans GOVERNED_LITERALS MEMBERS ONLY (`tools/check_hygiene.py:229`) and the test scans
   use explicit file lists (`test_mission_smoke.py:332 DEFENSE_GD`, `test_hub.py:250 HUB_LAYER`) →
   an ungoverned new file trips NOTHING, **17→17 stands**; `test_purity.py:39-45` filters `sim_*.gd`
   → g6 kits don't move it; root-children walks (`g1/g2 probes`, `v1_world_probe:155` walks CORE
   children) never touch a node parented `parent="CameraRig"`; no name collision (`CameraZoom`
   grep-zero); the `CameraRig` regex (`test_hub_layout.py:337-339`) needs header+transform adjacent
   — an appended block elsewhere is safe; the other 7 tscn-reading tests boot the scene, no textual
   counts; bridge pins `test_bridge_contract.py:111/:116` verified present and the design touches
   no bridge; RF-3 `MIN_MARGIN 60.0` byte-green holds (kit feeds no wheel → default rig).
   MISS: the load_steps header (P1-1). Everything else HOLDS.
4. **mission.gd at the 400-LOC ceiling**: measured 399 `wc -l` (gate metric 400 — FINDINGS §BASELINE
   explains the metric). Scene-script mount needs ZERO mission.gd lines — proven by the G3 precedent:
   `grep -i telegraph godot/scripts/mission.gd` is EMPTY while WaveTelegraph rides the tscn ext row.
   No preload/const row is forced. A7's two comment rewrites (`mission.gd:156`,
   `hero_controller.gd:11` — both rows exist verbatim) fit LOC-neutral. CLAIM HOLDS.
5. **Simpler alternative**: `project_*`/`unproject_*` = 0 occurrences in `godot/scripts/` (grep,
   matches §4's honest CONTRADICTED finding); the shipped hub wheel precedent
   (`hub.gd:34-44,:128-130` ScrollContainer + `test_hub_scroll.py:250` real WHEEL_DOWN via
   `root.push_input`) is reused, not duplicated; NO shipped rig param answers zoom (FOV untouched,
   rig rows F8-pinned). The new node is the minimal home — EXCEPT the undeclared dedup would be the
   duplicate mechanism (P1-2). CLAIM HOLDS.

## G0 DoD reconciliation
This doc names the attack surface G0 promised (D_MIN vs RF-1, node-local wheel reader vs
one-feed-point doctrine, 5→6 re-pin legality, envelope endpoints) and gates on it. The spec's
RETURN claims verified: READ-ONLY honored, six sections, ≤300 lines, suite-collection 283,
the §4 premise honestly self-flagged CONTRADICTED (verified true).

Two P1s would break the suite as the spec's build stages are written (P1-1: RED telegraph-mount leg
+ stderr-gate pollution; P1-2: unsatisfiable DEDUP leg). Corrections are exact and small; the
design core (wheel-only, runtime-only, 56/128/8, single byte re-pin) is sound and stays.

# VERDICT: FIX
