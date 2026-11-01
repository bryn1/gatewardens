# Gatewardens — Release Notes v1.5 (make-it-sing) — 2026-11-01

Length reason (file hygiene): this is the standalone committed release-notes body for the v1.5
GitHub Release (MC 11909 brief; GitHub-Release doctrine MC 11277/11509). The per-release history —
v1 through v1.4, with its own known-limits and supersede annotations — stays in `RELEASE_NOTES.md`;
this file supersedes it FOR v1.5 CLAIMS ONLY, and the carry-forward rows below name exactly which
older claims it retires.

Release tail note: this section IS the committed release-notes body; the tag `v1.5` is cut by the
orchestrator's release card on the release commit — no tag exists before it.

The make-it-sing wave: the two state crossings the player makes most — **"I equipped a kit"** and
**"I picked up loot"** — became VISIBLE, through existing mechanisms only. Assigning a kit now
paints a spark at the tower (engine-pinned AND pixel-proven in the served web build), every item
row and the loot toast render per-rarity COLORS authored as DATA, and the projectiles of the
towers you placed LAST no longer silently starve — a real shipped defect since 2026-10-29, found
by an honest re-baseline and fixed inside the milestone. No sim, economy or balance moved: the one
data change is a presentation key (`rarity.json` `colors` — never sim input, golden fixtures
byte-pinned EMPTY in every card's diff), the camera did not move at all, and zero monetization
ships here or ever: **No shop. No loot boxes. No timers. No monetization, ever — by owner ruling
2026-10-25** (MC 11274.1; the README row and the shipped structural guard + tripwire gate are
unchanged, 0 hits at this tree).

**What shipped** — every claim below is cited to the wave log it was measured in
(`.audits/20261101-0843-v15-plan/`), not to a summary:

- **Assigning a kit SPARKS at the tower — and it paints in the web build** (MC 11876 + MC 11894).
  The fx director gained one UNCONDITIONAL kit-crossing observation pass (first-sight of a relic
  going 0→uid on a published defense row spawns exactly ONE spark through the ONE existing spawn
  site; the kit assign happens in the build phase, where nothing drops, so a drops-guarded pass
  would ship dead — the plan's DA-verified rule, honored). Engine rows pin the whole shape (5 KF
  legs, cap-respecting, zero writes, symmetric unassign stays deliberately silent). The served
  proof: state marker first (`relics_assigned=1` before any pixel), then the burst-window census —
  **41 of 48 frames carry tower-window deltas, peak 88 px, a 5-frame pulse 88/76/67/84/81 = the
  shipped twinkle visibly pulsing**, control-vs-control 0 px, the pre-fix same window 0–4 px (the
  census can go red), plus a Lane-E vision literal read of the star at the medallion base. —
  WK-wave.log + WK2-wave.log
- **…and the web-fx P1 that sat UNDER it is fixed — root-caused INVERTED** (MC 11894). The v1.4-era
  reading "fx sheets ship as empty web textures" was wrong: the EMPTY texture was produced by THIS
  milestone's own first-cut "hardening" line — the web build answers an empty VRAM stub to
  `get_image()`, so rebuilding a texture from it swapped HEALTHY bank sheets for 0x0 ones and
  killed EVERY fx sprite on web. The fix is one consumer line (delete the rebuild; the bank sheet
  IS the texture); assets and import params were touched ZERO — changing them would have masked
  the real bug. A regression-killer plant (re-adding the rebuild) goes RED. — WK2-wave.log
- **Rarity colors are DATA and they light everything** (MC 11877 + served-append). One lowercase
  `#rrggbb` per ladder name, authored in `rarity.json`'s own ladder array (none invented);
  `item_row.gd`'s tint mechanism — shipped since v1 waiting for exactly this key — needed ZERO
  code lines, the loot toast rides the same data door through one read-only accessor (zero
  literals). Served proof: the mission toast reads pixel-EXACT `#4b7bd4` (the `powerful` color,
  315-px census, Lane-E literal read first), and the hub bank's six rarity chips were pixel-censused
  through shipped clicks on a seeded save — six distinct per-rarity colors in ladder order. Colors
  never enter the sim: the golden fixtures stayed byte-identical. — WQ-wave.log (+ §SERVED-APPEND)
- **The towers you placed LAST fire visibly too** (MC 11901). A real shipped defect, live since
  2026-10-29 (G6): the fires pass allocated every leftover effects slot to the FIRST-placed towers,
  so the last-placed ones — hailspires in the probe — spawned projectile fx ZERO times. The fix
  rotates the walk's start cursor per frame: every eligible tower leads within n frames. The
  fairness leg is pinned in-suite: RED pre-fix (6132 bolts to the first towers, 0 ice to the last),
  GREEN post-fix (first ice on a live node at frame 317), and the planted-red re-REDs byte-
  identically when the cursor is removed. Cap value, drop-priority, license data and damage
  numbers are all verified ZERO-DIFF — the pinned cost rules did not move. — WF-wave.log
- **The fx probe got the honest re-baseline v1.4 declared NOT RUN — and it found the defect**
  (MC 11897 + MC 11906). Run at the final tree, the kit was deterministically RED; attribution by
  counter-runs at era tips pinned the break to G6 byte-exactly (the pre-G6 tip BYTE-REPRODUCES the
  2026-10-27 green baseline — the baseline was real, the harness is honest). The kit's own scenario
  geometry was then fixed (a probe hailspire stood ~1 m outside its own range of the kill zone —
  no allocation policy could have greened it), and the kit runs GREEN: ART n=4 paths=pinned,
  CAP/SETTLE/TEARDOWN/OK print, rc=0, stderr EMPTY, byte-stable. The wrapper test now pins ALL
  THREE baseline transcripts (2026-10-27 green, 2026-11-01 measured-red, W-G green) with sha256 —
  a future overwrite goes RED mechanically; the green re-pin showed the old rows REDDENING first.
  — WR-wave.log (VERDICT FAIL-as-measured) + WG-wave.log
- **The verification layer deepened where v1.4's mutation pass proved it thin** (MC 11878 +
  MC 11879). `static_app` — previously reached by the suite only via subprocess — now has 8
  IN-PROCESS legs (byte-exact serves, the exact C10 refusal bodies, the chmod-000 OSError branch
  with an IN-PROBE guard that fails LOUD under a privileged uid, and the exact lstrip-boundary
  mutant killer via an UPPERCASE-X name); the 13 surviving mutants at that branch die at the next
  sweep. The hygiene gate's blank_code TRUE residual (the css family + the js block-comment
  branch) got two MUST-FIRE controls appended AT the existing positive-controls home — and both
  named P3 survivors die PRECISELY (1F/31P, target leg named) through the file's own mutant seam.
  — WT1-wave.log + WT2-wave.log
- **The served-leg harnesses are committed** — the IDBFS seeded-save injection idiom
  (`wq-bank-seed-gen.gd`, `wq-bank-leg-11877.cjs`) and the archived burst frames live beside the
  logs, so both served pixel legs re-run from this tree. — WK2-wave.log + WQ-wave.log §SERVED-APPEND

**Promised vs shipped** — the honest rows per the GitHub-Release doctrine:

- **The kit-presentation promise — kept, and its own first cut is on the record.** v1.4's probe
  FINDING ("no presentation exists; future work must re-pin, cannot ride the green") was paid:
  W-K shipped the presentation and the re-pin proof shows the OLD asserts REDDENING on the new
  tree before any re-pin. The milestone's first cut ALSO shipped the web-kill bug described above
  — found by the same card's own served leg, root-caused inverted by the follow-up card, fixed,
  regression-planted. Both builds' transcripts stand in the logs; nothing was quietly replaced.
- **Camera: v1.3's zoom row stands unchanged.** ZOOM remains the ONLY rig move the owner granted
  (MC 11719 verbatim "Go 1 and zoom control for 2"); `camera_zoom.gd`'s `D_MIN 56.0 / D_MAX 128.0 /
  ZOOM_STEP 8.0` did not move this milestone — the plan's frozen-constraint row names them, and
  every v1.5 card's camera diff is EMPTY. (The wheel zoom itself shipped AT v1.3, not here.)
- **DEFERRED (6) — end-state rows, grounds re-checked at this tip (V15-PLAN-c2 §2):**
  1. **Tower hp tint — DEFER stands.** Nothing in production gameplay damages a defense in v1
     (the damage path lands only on cores; `defense_obj.take_damage` has no production caller —
     re-grepped at tip). A live tint can never paint; RE-OPENS when any tower-targeting
     mechanic lands. — V15-PLAN-c2 §2 row 4
  2. **Minimap — DEFER stands.** The reference's own condition: "Defer — value arrives when map
     2+ or bigger arenas ship." One map ships. — V15-PLAN-c2 §2 row 6
  3. **D2 spawn-mouth shimmer — DEFER, stays parked** (owner-deferred as before; an authored-
     shader need; no new owner artifact — disposing it differently would manufacture consent).
     — V15-PLAN-c2 §2 row 7
  4. **MAX_FX drop-priority re-ordering — DEFER, stays an honest known limit** (see Known
     limits): re-ordering the cap's drop priority changes a PINNED cost rule — owner-ruling
     territory, not a presentation milestone's call. — V15-PLAN-c2 §2 row 8d
  5. **F-5 (VM350 `python3 -m venv` broken) — DEFERRED out of repo scope** — a host fact worth
     fixing fleet-wide; it belongs on the fleet infra board, not in this repo. — V15-PLAN-c2 §2
     row 2d (named so the map is complete, not dropped)
  6. **"First maps AS the tutorial" — DEFER** — needs map CONTENT (one map ships); the G8 coach
     banner carries the first-mission teaching in the shipped one-map product. Content class,
     not this milestone. — V15-PLAN-c2 §2 row 8e
- **REJECTED (1): per-tower interaction keys (Q/R/Z)** — there is NO per-tower mode mechanic to
  key into (towers.json tiers carry range/dps only — no mode/cooldown field): a key would paint a
  mechanism that has no source, the same class as the v1.4 cd-overlay REJECT. The selection ring
  and the panel rows already answer "which tower". — V15-PLAN-c2 §2 row 8b
- **Ready-up / early wave start — OWNER-DECISION OD1, ENDS AS DEFER.** The question (should an
  early-wave control ship at all, and at what bonus?) was filed to the owner with a recommendation
  to defer and a minimal ruling shape if wanted (a data-keyed bonus, tested boundaries named);
  **no owner answer arrived before this release, and the plan's default-if-silent governs: DEFER —
  no ruling = no mechanic.** The row stays parked exactly as at v1.4. — V15-PLAN-c2 §6
- **The kit probe's GREEN is scenario-conditional — said plainly** (see Known limits). The GREEN
  kit proves the fx plumbing end-to-end in ITS scenario; it is not a promise that every projectile
  burst survives a saturated live battle.

**Known limits, stated as they are**

- **The kit GREEN rides the probe's own kill-zone geometry.** The ART leg goes green because the
  probe's first hailspire now stands where its (pinned) range covers the run-in kills (WG-wave.log
  documents the measured miss). In a live saturated wave the 64-slot cap still lets the hp-drop
  pairs (spark + damage number, G6's "numbers count") spend the cap BEFORE the fires pass; what
  v1.5 fixed is FAIRNESS of the leftover slots (every tower leads within n frames), not the cap or
  the priority (both pinned — the DEFERRED row 4 above).
- **Starvation direction, corrected: the hp-drop pairs starve the TRACERS, not the other way
  around.** An older carry-forward row claimed the reverse direction (the NUMBERS losing slots to
  the tracers/sparks) — MEASURED exactly backwards (WR-wave.log §5: sparks + numbers are
  emitted first within the frame; tracers eat the leftover, the last-placed towers ate nothing at
  all until W-F). The 64-slot cap itself, drop-past-cap-never-queue, is unchanged and stays the
  declared cost discipline. This row RETIRES the old direction wording wherever it stands outside
  frozen release history.
- **The bank fills on a WIN only.** Bank rows exist only after a victory banks the chest (a defeat
  banks nothing; the training-dummy range has no loot path) — the served bank census therefore ran
  on a DECLARED seeded save produced by the shipped mutators (harness-side injection; product bytes
  unchanged). Users see colored rows as soon as they win a mission. — WQ-wave.log §3b +
  §SERVED-APPEND
- **Kit UNASSIGN paints nothing — declared.** The symmetric poof was cut to keep the leg smallest
  and is pinned so (`una_sparks=0`); assign is the painted crossing. — WK-wave.log
- **The GDScript sim is NOT mutation-covered** (carried from v1.4, still true): the declared
  substitute ships — planted-red transcripts (every v1.5 card carries its red rows) + the golden
  fixtures. — v1.4 RN section + this milestone's logs
- **Suite count depends on the web export, by design**: **345 pytest green** with `static/`
  present, **340 from a clean checkout** — `test_served`'s 5 web legs module-skip without the
  export (the same +5 reconciliation idiom as v1.3/v1.4, re-quoted at this milestone; DOCS-wave.log
  carries this card's single suite run). `check_hygiene: 0 hit(s)`, golden fixtures byte-pinned,
  GOVERNED_LITERALS 17.
- Carried forward from v1.2.1/v1.4 (still true at v1.5): the kill-blow number "is a lower bound";
  "A kill right at the core's door shows no final number"; "…telegraph numbers are small at a
  1280-px window"; "The build ghost is a slot marker, not a translucent tower silhouette"; the
  tower-row tints are "subtle-but-measurable"; and "`static/` (the browser build) is gitignored by
  design" — regenerate with `bash tools/export_web.sh`.

**How to build & run** — unchanged: `bash tools/export_web.sh` → serve `static/` with
`python3 server/server.py` (see README one-liners); the Windows desktop build comes from
`bash tools/export_windows.sh` (see RELEASE_NOTES.md W18 rows).
