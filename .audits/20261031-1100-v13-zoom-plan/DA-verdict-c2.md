# DA-verdict-c2 — G0 ROUND 2, adversarial re-check of ZOOM_SPEC REV c2 (MC 11792) [type:devils-advocate]

Target: `.audits/20261031-1100-v13-zoom-plan/ZOOM_SPEC.md` REV c2 (committed `963776d`). Round-1
`DA-verdict.md` (FIX, 2 P1 + 2 P2) is background — NOT re-litigated (wheel-only, envelope 56/128/8,
runtime-only, GOVERNED 17, single byte re-pin, no simpler mechanism = settled); this pass attacks
ONLY the four fixes, against the shipped tree, with measurements. READ-ONLY honored: the only repo
writes by this run are THIS file + `.tmp/`. Repo tip `963776d`; suite re-collected **283** this
session (`pytest --collect-only`). JUDGED-line reading: this prompt carried no `dod_judged_hash.py`
command, so per the MC 3720 conditional no `# JUDGED:` line applies (same as round-1).

## SURFACE-SAFETY (precondition for the fix-checks to mean anything)
- The three spec-era commits `59ffea6`/`116d90d`/`963776d` touch ONLY
  `.audits/20261031-1100-v13-zoom-plan/` files (`git show --stat`, this session). No product byte
  moved since the round-1 tip `7bf18cf`; `git merge-base --is-ancestor 7bf18cf HEAD` = YES.
  ⇒ every §2/§3 byte-pin and §5 RED-test the fixes cite is measured AT the live tip, not a stale one.

## FINDINGS ON THE FIXES

### FIX P1-1 — `load_steps=9→10` declared row: VERIFIED consistent + red-then-green buildable. HOLDS.
- **Consistent EVERYWHERE it is referenced.** §3 re-pin table row 2 (declares `9→10`, cites
  `test_wave_telegraph.py:226-231`, G3 precedent `0b49bba`); §6 S3 (`...WITH the declared header bump
  load_steps=9→10 ... required by the relational pin, G3 precedent 0b49bba`); §5 A5 (`both the :591
  byte re-pin AND the relational load_steps=9→10 header bump`). All three agree — no section left
  saying "APPEND-only" as if the header were untouched (round-1's exact defect, now closed).
- **Relation math MEASURED at tip.** `test_wave_telegraph.py:226-231` pins `steps == ext + sub + 1`
  (n_res counts `[ext_resource ` + `[sub_resource ` only — NODES are excluded, and mission.tscn
  carries 10 node blocks, which correctly do NOT count). Measured: `load_steps=9`, 7 ext + 1 sub +
  1 = 9 ✓. Appending one Script ext row → 8 ext + 1 sub + 1 = **10** → the header MUST become 10.
  The spec's derivation and the G3 precedent `git show 0b49bba` (`-load_steps=8 +load_steps=9`
  beside its Script ext row, and it did NOT touch the CameraRig transform — verified empty grep) both
  check out. HOLDS.
- **Red-then-green names a state that is ACTUALLY buildable and goes RED on named tests.** The
  "scene-append-alone" state (6th Script ext row appended, neither retarget applied) goes RED on
  BOTH named tests, and both exist at tip:
  1. `test_mission_clicks.py:591` — `assert len(_ext_rows(...)) == 5`; `_ext_rows` regex matches
     `type="Script" uid="..."` rows only (verified: tip = 5 Script rows of the 7 ext: the 2 non-Script
     are `Mesh` + `Material`). The append makes it 6 → **RED** (and `_uid_consistency_violations` on
     the line-586 assert trips first if the sidecar isn't yet present — still RED either way).
  2. `test_mission_tscn_mounts_the_telegraph_append_only` (`:208`) — the stale header `9 != 8+1+1`
     fails the `:226-228` relation → **RED**; its docstring carries the very reason the spec cites
     ("a stale header is the Godot WARNING that would pollute every EMPTY-stderr gate").
  ⇒ the shared planted-RED is real, on two named tip-present tests with correct relation math. HOLDS.

### FIX P1-2 — press-only + per-tick edge guard: VERIFIED buildable + field-matched. HOLDS (2 NOTES below).
- **The brief's decisive probe — is the guard keyed on a field Godot 4 wheel events actually carry?
  YES.** The guard keys on `button_index` (§1: `one step ... per button_index`; §1: read
  `button_index in {WHEEL_UP, WHEEL_DOWN}`, act only `event.pressed == true`). The shipped authority
  for "what a wheel event is" in THIS repo/Godot 4.7 (`config/features=PackedStringArray("4.7",...)`)
  is `tests/test_hub_scroll.py:249-251`: `InputEventMouseButton.new(); ev.button_index =
  MOUSE_BUTTON_WHEEL_DOWN; ev.pressed = true` — it sets **`button_index`**, NOT `wheel_vertical/
  wheel_horizontal`, and dispatches it through `get_tree().root.push_input`. And the shipped consumer
  `main.gd:195-197` reads exactly `button.button_index`. So the brief's `-1`/`wheel_vertical` concern
  does NOT apply to the shipped event model: the guard's key field is carried. Buildable without
  invention. The bridge's own `mouse_code(button_index)`→`""`→drop path (`bridge.gd:76-77`,
  `MOUSE_CODES` has LEFT/RIGHT only, `:41-43`) confirms wheel is dropped today (§1's "zero zoom" —
  re-verified) and would be the collision to avoid. HOLDS.
- **DEDUP leg satisfiable as written.** A4 feeds "the same tick twice" (one frame) → guard collapses
  to one; "two distinct ticks" (kit steps `_m.step(DT)` between, per the cited g5 `_mouse()` `:222-228`
  idiom) → two steps. The kit owns both knobs, so both clauses are pinnable. HOLDS.
- **NOTE N-A (P3, forward-looking, not gating):** the guard is declared "per **event-frame**" but the
  spec never names the frame-source the node reads to tell "same frame" from "across frames." The
  standard Godot 4.7 primitives for this (`Engine.get_process_frames()` / `get_viewport().
  get_frames_drawn()` / a `_process` tick) are conventional, not exotic invention — so this is not a
  build-blocker — but naming the frame-source in §1 would make the guard "buildable from spec alone."
  Separately: the shipped web export relays ONLY `keydown`/`keyup` (`web_shell.html:109-110`, verified
  no wheel listener), so **today wheel has exactly one feed** and a frame-keyed guard is correct for
  the shipped product; a *future* shell wheel relay that fires cross-frame would slip a per-frame
  guard (the §1 double-feed law the same section warns of). The mechanism that matches a cross-frame
  double-feed is the **held/rising-edge style** `bridge.on_key` uses (`bridge.gd:59-67`, reset on the
  release edge, frame-independent). Recommend §1 state the guard is held-reset-style OR add a
  cross-frame clause to A4's DEDUP leg. Honest dissent recorded; does not gate the shipped build.

### FIX P2-1 — S4 produces the PLACE leg: VERIFIED stage owns the file. HOLDS.
§6 S4 owns `godot/sim/g6_zoom_relay_probe.gd` and enumerates its rows
`WHEELIN/WHEELOUT/DEDUP/PLACE/BOUNDMIN/BOUNDMAX`, with `PLACE` named "the producing row for §5 A3
place-at-distance — c2/DA P2-1"; §5 A4 lists `PLACE` ("this is §5 A3's producing row") and §5 A3
points back to "produced by S4's PLACE line". The named stage OWNS the file the row lives in. The §4
click-mapping chain it exercises is cited correctly at tip: `defense_panel.gd:72` =
`"MouseLeft": "confirm"`, handled armed-only at `:140-145`; `defense_placer.gd:243 place_id(...)`;
first-free fallback `:252-253`; `:215 RANGE_RING.show_ring(m, slots[ghost], radius)` — all digit-
correct this session. HOLDS.

### FIX P2-2 — S1 baseline capture feeds A2: VERIFIED stage owns the file. HOLDS.
§6 S1 owns `baseline-default-D64.png` + sha256 sidecar in THIS `.audits/` dir, captured by booting the
UNMODIFIED mission with zero wheel input **BEFORE S3 exists**; §5 A2 names THAT file as the
compare-basis ("not a post-change re-render; c2/DA P2-2"). S1's own kit needs no S2/S3 artifacts, so
the earlier stage genuinely owns what the later A2 leg consumes. HOLDS.

### FINDING P2-3 — whole-doc: A5 "count claims update in the SAME commit" CONTRADICTS the §6 stage split. Not P1.
§5 A5 (line 251-252) states the claim-rot law verbatim: "suite count grows (283 → 283+N) and the
README/RELEASE_NOTES/LEDGER count claims update **in the SAME commit**". But §6 puts the count-GROWING
commit in **S4** (`full suite 283+N GREEN`, new test files) and the count-CLAIM sync in **S5**
(`README/RELEASE_NOTES count rows + LEDGER status line`). S4 and S5 are distinct serial stages =
distinct commits ⇒ at the tip of S4's commit `README.md:9`/`RELEASE_NOTES.md:81` still read
"283 green" (both strings verified present this session) while the suite is 283+N — a one-commit
claim-rot window that the spec's OWN "same commit" law forbids. It is NOT a code-correctness P1
(self-heals at S5 before the card closes; knut verifies the TIP, which is consistent), but it is an
internal spec contradiction that forces the builder to choose a reading.
- Exact correction (choose one, in the next in-place amendment): (a) move `README`/`RELEASE_NOTES`
  count rows into **S4's** owned-files so A5's literal "same commit" is satisfiable; OR (b) amend A5
  to "…update in the SAME BUILD CARD, in the last wiring stage (S5), before close." Either closes it.

### NOTE N-B — A7 grep-to-zero scope: correctly scoped, no defect (raised for the next verifier).
`grep -rn 'never touched' docs/ godot/scripts/` returns 5 hits; A7 names exactly the two CAMERA claims
to rewrite (`mission.gd:156`, `hero_controller.gd:11` — both exist verbatim at tip) + the ARCHITECTURE
C4 sentence `:231`. The other 3 (`dummy_range.gd:64`, `mission_world.gd:47`, `mission_heroes.gd:21`)
are about a station / ground node / C1 table — they do NOT contradict zoom and stay TRUE. A7's line-267
wording is "0 **STALE** hits," which correctly scopes to the camera claims — so it does NOT demand
deleting true unrelated claims. Flagged only so a mechanical "grep → 0 hits" reading isn't mistaken for
the spec's actual "0 stale hits" intent. No finding.

## SURVIVED (refutation attempts the shipped tree refuted — fixes stand)
1. No product byte moved since round-1 tip (surface-safety above) — the fixes' cited RED tests and
   byte-pins are all live at `963776d`.
2. `load_steps` relation math excludes nodes; the 10 node blocks don't inflate it; 7+1+1=9 at tip,
   8+1+1=10 after the append; G3 precedent byte-matches the pattern and didn't touch CameraRig.
3. Wheel guard keys on `button_index` — carried by Godot 4.7 wheel events (shipped
   `test_hub_scroll.py:250` + `main.gd:197`) — so P1-2's "guard on a field wheel lacks" trap does not
   fire.
4. §6 S3 owning `mission.tscn` does NOT collide with §3's CameraRig-transform / pin-#3 SPENT forbid:
   §6/§5 A5 restrict the edit to APPEND-only + the ONE header line ("the ONLY non-append line the diff
   may carry"); the CameraZoom child block + top-section ext row don't touch the transform row, and
   round-1 established the `test_hub_layout.py:337-342` regex needs only header+transform adjacency.
   S3's other owned files (`mission.gd`/`hero_controller.gd` comment-only, `test_mission_clicks.py`
   :591 = the declared-mover pin #6) are all legal under §7.

## G0 ROUND-2 DoD reconciliation
All four round-1 corrections are APPLIED and each was checked against the shipped tree with a
measurement (relation math, `_ext_rows` semantics, wheel field-carriage, stage-owned files, §4
citation digits). One new internal inconsistency (P2-3, count-claim same-commit) and three honest
notes (N-A frame/held style; N-B grep scope) surfaced. **No P1 or P0 remains on the fixes.** The
design core the fixes ride stays as round-1 SHIP'd it.

# VERDICT: SHIP
