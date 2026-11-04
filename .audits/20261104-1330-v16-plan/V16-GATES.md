# V16-GATES — v1.6 milestone acceptance roll-up (MC 12115 · V-G · 2026-11-04)

Evidence levels per row (fleet law): VERIFIED = observed/executed on the evidence named at that
row; TESTED = covered by a run automated check; INFERRED/UNVERIFIED would be said so — none are.
A1–A6 cite the OWNING card's wave log (the card that shipped the pillar); V-G re-measured its
own rows at the MERGED tip 18aca6c (branch card/12115, this tree). Evidence dir:
`.audits/20261104-1330-v16-plan/` (+ `evidence-12115/`).

| # | acceptance (plan §1, verbatim scope) | level | measurement, cited |
|---|---|---|---|
| A1 | SERVED (P1): build-phase frame shows a fortress diorama with real height, no void | VERIFIED | VA-wave.log (marker-first, TOP-STRIP void 17193→6911, CENTER checker→flagstone, keep+crest + gate plaques read LITERALLY). V-G re-capture at the merged tip: evidence-12115/census-build.txt TOP-STRIP void 17218→6596, delta 25209 px; Lane E AFTER literal "large rectangular stone paving slabs… low brick-textured walls… warm orange-brown tones" vs BEFORE "grid of square ground tiles… solid black background" (describe-v16-*.txt) |
| A2 | SERVED (P2): a placed Ballista reads as a 3D structure, turret re-aims; medallions stay UI-only | VERIFIED | VB-wave.log: EMPTY→structure silhouette +124 px, turret crop delta +24, panel medallion SAME FRAME; literal "three-dimensional tower-like structure assembled from primitives". (The V-G pair poses place NOTHING — the pair frame stays "Defenses 0"; the placement evidence is V-B's served leg, cited — the A2 frame is VB's, not V-G's.) |
| A3 | SERVED (P3): corridors read as in-world road; ghost arrows GONE | VERIFIED | VC-wave.log: ghost-cyan 719→6/1502→0/365→4 in the three declared crops. V-G re-shoot confirms at the same rects: PATH-A/B/C ghost 719→6 / 1502→0 / 365→4 (census-build.txt — the BEFORE rows byte-equal VC's, the AFTER rows byte-equal VC's AFTER run: the retirement holds on the merged tree) |
| A4 | SERVED (P4): hero readable at D=64, clearly so at D=56, NO new camera mechanic | VERIFIED | VD-wave.log + VH-wave.log (merged-tree re-tune): census HERO crop 0→262 px on the MERGED tip, VH Lane E literal "At the bottom opening (gate) of the keep stands a small dark grey figure". V-G pair frames re-show the figure at the keep gate (describe-v16-after-build.txt: "A tiny character sprite stands near the center with a small name label reading 'Bram Wardenfell'"). Camera: zero wheel events in v16-capture.cjs; camera_zoom.gd + CameraRig row 0 changed +/- lines vs 1271a6c (this session) |
| A5 | SERVED (P5): warm golden-hour mood, shadows read, themed HUD, zero rect moves | VERIFIED | VE-wave.log: panel grey 37786→51 px, void cool 64130→warm 69066; rect leg (13 rects byte-stable) TESTED in test_ui_theme.py; suite geom leg (test_mission_clicks) green in every card run incl. this one. V-G census rows: warm TOP-STRIP 10273→21038, SKY cool→warm void (census-build.txt) |
| A6 | SERVED (P6): static decor sells scale, within budget, zero RNG | VERIFIED | VF-wave.log: MultiMesh web raster PROVED (green 973 ON vs 15 same-camera CONTROL), budget 24 props/38 parts ≤ 40 pinned in test_decor.py (TESTED); frame-time ON==OFF 216.7 ms. V-G census DECOR at merged tip: void 45784→34085, pine 1688→973 — byte-equal VF's rows (deterministic, no drift) |
| A7 | TESTED: suite ≥ §5 projection at the final tree; hygiene 0; fixtures EMPTY; GOVERNED 17; mission.gd/test_mission_clicks ZERO new lines | TESTED | THIS card, this tree: `python3 -m pytest tests/ -q` = **358 passed rc=0** (evidence-12115/suite-committed.txt; ≥345 floor AND ≥ V-G's bar; the +0 V-G leg rides V-H's extended leg count — declared count row); `tools/check_hygiene.py` → 0 hit(s); `git diff f95e481..HEAD -- tests/fixtures/` = 0 lines; GOVERNED_LITERALS = 17 files (check_hygiene.py set parsed this session); mission.gd 400 (=AT), test_mission_clicks.py 600 (=AT), hud.gd 396 (≤396, the V-E WATCH max held); `git diff 1271a6c..HEAD -- godot/sim/` = the ONE declared V-C probe re-pin only |
| A8 | VERIFIED pair: EXACT two poses re-captured beside the BEFORE frames, 1280x720, zero wheel events | VERIFIED | v16-after-build.png / v16-after-defeat.png (this dir, owner pair) vs v16-before-build.png / v16-before-defeat.png. Route identity PROVEN mechanically: the v1.5 base re-export (1271a6c == v1.5 tag product bytes, diff EMPTY) run through the SAME v16-capture.cjs re-shot the archived frames — defeat FULL delta = 0 px (pixel-identical), build FULL delta = 122 px, ALL in the countdown glyphs (world-region deltas = 0; census-build/defeat.txt RECAP rows). Difficulty strict: BOTH sides normal — "Core 1000/1000 → 0/1000" quoted by the SAME Lane E reader both sides (describe-*.txt) |

## FRAME-TIME ROW (DA F-2, worded per the DA) — the perf guard of this milestone

Same rig (headless swiftshader chromium, 1280x720, one process per side), SAME script
(v16-capture.cjs), fresh export per side, rAF deltas 6 s, medians:

| pose | v1.5 base re-export (1271a6c) | merged v1.6 tip (18aca6c) | ratio |
|---|---|---|---|
| build | 150.0 ms (n=42) | 200.1 ms (n=30) | 1.33× |
| defeat | 150.0 ms (n=43) | 200.1 ms (n=30) | 1.33× |

**1.33× ≤ the 2× trigger → the presentation knobs (shadows-off fortress, 24 decor props,
≤30 fortress primitives) STAY AS SHIPPED; nothing to tone.** Declared: both medians are the
known swiftshader web floor (plan §18, no fps claim — 200 ms ≈ the same 5 fps class the served
build has always been); absolute ms drift across sessions (VF measured 216.7 ms on 2026-11-04
daytime), so the verdict rides the SAME-EVENING sequential pair above, machine rows in
served-run-after.log / served-run-before-recap.log.

## SHADOW FLIP-BACK — orchestrator decision, recorded here (V-G log row)

SHIPS **OFF** for v1.6. VA-wave.log:38-43 ruling: ambient is DISABLED at the scene row, default
casting painted PURE BLACK faces/shadows on web → fortress + decor ship cast_shadow OFF +
emission floor 0.3; "the flip is one word" but needs a V-E-class env re-tune first (VA-wave.log:148).
Flip-back = **v1.7 candidate**. V-G leg: the AFTER pair shows NO black-blob regression —
black-window px in the fortress regions AFTER: GATE 10→0, PATH-A 0→0, DECOR 45716→6, TOP-STRIP
17193→3 (BEFORE counts are the cool near-black v1.5 VOID inside the window, not blobs — V-E's
warm bg moved the void OUT of the window; census rows). Lane E saw no black blobs either
(describe-v16-after-*.txt).

## pck / stale-pck law (L2, kb e4aa7e1f) — md5 logged per frame

AFTER run: export md5 `f1c2b4f8c6424f5ba5c430ad59586ffd` = 7,457,200 B == served `PCK0/1/2` rows
(route / build-frame / defeat-frame), ERRS [] (served-run-after.log). BEFORE-rig run: export md5
`2bc2bb13d26a01ef2ee0ab98ca91967b` = 5,201,680 B == served per-frame rows (served-run-before-recap.log).
Two DIFFERENT md5s, every frame's served bytes == that side's on-disk export — a stale pck is
mechanically excluded. Fresh chromium per run = empty cache.

## Declared readings (V-G)

- "the exact two poses" = same route + zero wheel events: the camera is FIXED by law (L4), so
  pose identity IS route identity — PROVEN by the RECAP rows (defeat delta 0).
- Strict pair difficulty = normal (the BEFORE frames' core max 1000), NOT the (105,165) HARD
  route W1/W2 used — the (90,132) normal button (VE coord). VA/VF §7(g) deferred exactly this.
- The wall-clock to defeat differed (25 s base vs 41 s tip): the sim ROWS are byte-frozen
  (fixtures 0-diff, sim diff = the declared probe; outcome "lose" core 0/1000 BOTH sides) — the
  frame-driven pacing just runs at the (slower) render rate. Declared, not a law break.
- Defeat-side PANEL delta (64020 px) includes the themed panel + the world strip right of it —
  window reused per the locked rule, not re-tuned.
- V16-GATES.md + v16-capture.cjs + VG-wave.log + LEDGER row: this card's whole diff; ZERO
  product-code lines (post-commit proof in VG-wave.log §7).
