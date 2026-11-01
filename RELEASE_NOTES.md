# Gatewardens — Release Notes

Length reason (file hygiene): one file, one subject — the release history. The sections are
chronological and the GitHub-Release doctrine makes them additive (a retired claim is annotated
where it stands, never deleted), so splitting would separate each release from its own corrections.

## v1.4 (read-the-state) — 2026-10-31 (release tail: this section IS the committed release-notes
body per the GitHub-Release doctrine; the tag `v1.4` is cut by the orchestrator's release card on
this commit — no tag exists before it).

The read-the-state wave: the battlefield now tells you WHICH tower is selected, WHICH rows you
can afford and WHICH phase locks them, the hero's name finally SPELLS — and the verification
layer got mutation-measured and positive-controlled so the green means what it says. No sim,
economy or data moved (golden fixtures byte-pinned EMPTY in every card's diff), the camera did
not move at all, and zero monetization ships here or ever: **No shop. No loot boxes. No timers.
No monetization, ever — by owner ruling 2026-10-25** (MC 11274.1; the README row and the shipped
structural guard + tripwire gate are unchanged, 0 hits at this tree).

**What shipped** — every claim below is cited to the wave log it was measured in
(`.audits/20261031-1830-v14-plan/`), not to a summary:

- **The selected tower wears the ring** (MC 11837). The ONE ground ring the build ghost already
  used now also rides your SELECTION: click a tower's panel row and the ring lies flat at that
  tower at its own tier's range, read from the tower data — a new selection tone
  (`SELECTED_COLOR`), the G4 yellow staying the ARMED tone. Priority is shipped and declared:
  **armed ghost > selected > hidden** — an armed row with no placeable ring hides (the armed
  state wins, never falls through), disarm falls back to the standing selection, and the shipped
  deselect/sell reset hides it. One ring node, zero new node types, zero sim fields; the driver
  is a scene mount, so `mission.gd` gained ZERO lines at its 400 ceiling. Planted-red: flipping
  the priority went RED exactly on the priority row. — P5-wave.log
- **…and its web render is pixel-proven** (MC 11852). The served browser paints the selected
  ring: the tower-region census reads 19 px at baseline → **1555 px while selected (+1536 ring
  px at the tower)**, ARMED-over-SELECTED priority and the Escape fallback both measure, and the
  shipped sell-teardown returns the census to baseline. An earlier "ring missing on web" finding
  was ROOT-CAUSED as a repro artifact (the old script's 4th click hit world ground — the shipped
  select route is the panel row), never papered over: product files are byte-identical, the
  fixed repro is committed. Planted-red ON WEB: hiding the selected branch drops the census to
  19. — P5b-wave.log
- **Tower rows read their state** (MC 11854). Unaffordable row → **RED** (`ff6666`); a phase
  that is not build → **GREY** (`808080`); affordable + build phase → neutral. The cost signal
  wins the overlap: an unaffordable row answers RED even mid-combat. This is presentation ONLY —
  under every painted state the shipped refusals stay the only enforcement (the drilled-to-RED
  rows still answer `why:"green"`, the grey-locked rows `why:"phase"`, zero writes, ack unmoved).
  Honest history row, kept unedited: the FIRST build had the two halves worded swapped; the
  orchestrator recut to the plan-row map ("the PLAN row governs (it is the DA-ratified artifact;
  my card brief was the drifted side)") and both transcripts stand in the log. No cooldown
  states shipped — that half was REJECTED because no build-cooldown state exists in the sim. —
  P6-wave.log
- **…served-HUD confirmed** — all three states paint through shipped-route clicks (row-bg pixel
  census: RED-dominant shift on the unaffordable pair, grey-neutral on the combat-locked rows,
  cost-first precedence held), with the honest tint note under Known limits. — P6-wave.log
  §SERVED-HUD
- **The hero crest SPELLS now** (measure first, MC orchestrator leg; fix MC 11835). v1.2.1's
  crest claim was measured, not trusted: at the default view in a 1280-px window it is
  **ILLEGIBLE** (name glyph blocks ~4–5 px; no magnification spelled a single hero name). The
  fix rode the ONE crest mechanism — name height **0.55 → 1.1** (x2), a stronger **outline (10)**,
  and the name band lifted above the pawn's shield crown (0.85 → 2.55, the re-shoot round's one
  const nudge after the shield was found to occlude the middle of the name). The served
  re-shoot: **"Bram Wardenfell" SPELLS in full above the pawn** — shield occlusion cleared,
  outline contrast holds on the floor. Camera untouched (ZOOM-only grant honored — diff EMPTY). —
  P4-wave.log + P8-wave.log
- **The place-refusal matrix** (MC 11829, tests-only): every gate that refuses a placement —
  combat phase (BOTH shipped routes), occupied/off-list slot, unknown id, insufficient green,
  cap-full — now refuses under test, each row asserting green / defense list / save-write /
  ghost UNCHANGED, and a passing BUILD-phase control row proves the matrix is not vacuous. The
  cap guard had NO test caller anywhere before this. Planted-red: dropping the phase guard at
  BOTH sites made the combat key-route really place for real (red transcript beside the green).
  — P1-wave.log
- **Hygiene got positive controls** (MC 11838, tests-only): 30 crafted MUST-FIRE controls for
  every gate detector (per-family comment blanking, the tripwire in all three match modes, the
  walk coverage-count, the planted-tree 5-error-class main() transcript) — because the mutation
  pass below proved that absence-only tests let condition-inversions survive. Two demonstrated
  survivors re-run LIVE now die RED; the shipped-tree absence legs are kept for the contract,
  never credited as detectors. The gate file itself stayed byte-untouched. — P9-wave.log
- **Mutation kill-rate MEASURED over the pure-Python tier** (MC 11831): mutmut 3.8.1 over
  `tools/check_hygiene.py` (516 mutants → kill-rate **20.4% of generated / 37.8% scored**) and
  `server/static_app.py` (**89.3%**), with every survivor named and triaged (harmless-equivalent
  vs test-gap) and five findings routed as new work — the absence-only-claims finding became the
  positive-controls card above, not a silent shrug. Zero repo change: the run mutates copies. —
  P3-wave.log
- **The kit probe landed a FINDING, not a shrug** (MC 11857, tests-only): the V12-PLAN:297 debt
  (a kit-presentation leg promised and never executed) was paid as RUNNING behavior over the
  real mission — and the honest result is **kit presentation is NOT implemented** (see Known
  limits). The leg is pinned to ACTUAL shipped behavior (assign hp_max 400→403 EXACT from data,
  hp clamped-not-healed, full revert on unassign, a second kit REFUSED "taken" — never
  silently replaced), with a non-vacuity control proving the same instrument observes a real
  shipped effect begin and end. — P7-wave.log
- **The served-leg harnesses are committed** — the fixed web repro and its census
  (`ring-leg-11852.cjs`, `ring-census-11852.py`) and the HUD row-leg script
  (`icon-leg-11854.cjs`) live beside the logs, so the pixel legs re-run.

**Promised vs shipped** — the honest rows per the GitHub-Release doctrine:

- **Tower hp tint: the plan promised it, it did NOT ship — DEFERRED, with the reason.** The v1.4
  plan disposed this row SHIP in round 1; the devils-advocate gate round 1 found the live damage
  source does not exist (nothing in production gameplay damages a defense in v1 — the honest cut
  was "a live hp tint can never paint in a real mission"), and the orchestrator call RE-DISPOSED
  the row, verbatim: "RE-DISPOSE the hp-tint row — DEFER with reason 'no damage-source for
  defenses in v1 (DA P1-A); ships only dead presentation; re-opens the moment any
  tower-targeting mechanic lands'" (V14-PLAN §2/§7). No live hp tint shipped in v1.4.
- **Kit presentation: not implemented** — a probe FINDING, not a promise kept; see Known limits.
- **Ready-up / early wave start: DEFERRED** — it is a NEW sim mechanic whose early-call bonus is
  a balance number the owner has never ruled (DD-reference row 12, priority P4); no owner
  artifact opens it.
- **Minimap: DEFERRED** — the reference's own condition stands: "Defer — value arrives when map
  2+ or bigger arenas ship"; one map, one rig, the whole arena reads.
- **Mid-mission abandon: REJECTED — the existing ruling holds.** Owner 2026-10-28, verbatim
  **"rec on all 3"**, ratified END-ONLY — "NO mid-mission exit control ships" (LEDGER:93/95) —
  and the refusal is TESTED (the negative mid-mission leg + a source-truth pin), so reopening
  needs a NEW owner artifact; none exists. Reload already loses nothing.
- **Camera: v1.3's zoom row stands unchanged.** ZOOM is still the ONLY rig move the owner
  granted (MC 11719 verbatim "Go 1 and zoom control for 2"); v1.4 moved NOTHING camera-side —
  every card's camera diff is EMPTY in its log.

**Known limits, stated as they are**

- **The GDScript sim is NOT mutation-covered.** mutmut mutates Python; the sim is GDScript, and
  no GDScript mutation tool is in play. The DECLARED substitute ships: the planted-red rule
  (every card above carries its red transcript) + the golden fixtures. A GDScript mutation
  harness beside them is a new mechanism for an already-covered risk — its own design card only
  if the owner asks. — P3-wave.log §8
- **The row tints are subtle-but-measurable.** The vision read-back of the served HUD sees the
  unaffordable/locked rows as DISTINCT in direction ("uniform dark charcoal" vs "lighter
  brownish-tan") but names the hue softer than "red" at this tint — honest row, kept: the states
  are measurable and user-visible, not loud. — P6-wave.log §SERVED-HUD
- **Kits have no presentation effect (FINDING, pinned).** Assigning a kit to a tower changes its
  stats but paints nothing: the shipped assign/unassign writers are pure state crossings and the
  fx director spawns only from enemy/fire observation. The probe rows pin the MEASURED ZERO, and
  a source-truth leg bans presentation calls in the writer bodies — a future implementation must
  RE-PIN those rows, it cannot ride the old green. (This is the same shape as the deferred hp
  tint: presentation without a mechanism is exactly what the pins refuse to fake.) —
  P7-wave.log
- **Suite count depends on the web export, by design**: **324 pytest green** with `static/`
  present, **319 from a clean checkout** — `test_served`'s 5 web legs module-skip without the
  export (the v1.3-era 287-with-export / 282-clean reconciliation, +5, re-quotes at this tag).
  `check_hygiene: 0 hit(s)`, golden fixtures byte-pinned. — this card's single suite run at the
  tip, quoted in DOC-TAIL.log
- Carried forward from v1.2.1 (still true at v1.4 EXCEPT the hero-crest half, retired above by
  MC 11835): the kill-blow number "is a lower bound"; "Damage numbers share one effects pool"
  (the 64-slot cap); "A kill right at the core's door shows no final number"; "…telegraph numbers
  are small at a 1280-px window" (the telegraph half — unchanged, P8 moved only crest consts);
  "The build ghost is a slot marker, not a translucent tower silhouette"; and "`static/` (the
  browser build) is gitignored by design" — regenerate with `bash tools/export_web.sh`.

## v1.3 (zoom) — 2026-10-31 (RELEASED: tag + GitHub Release)

The zoom wave: the mouse wheel moves the camera between a 2× overview and a
close view that never crops a path corner — the ONE camera move the owner
granted — landing on a clean-code pass over the v1.2.1 base (audit: 0 hard
size findings; the duplicate material builder and the duplicate air-grouping
folded to one home each; the dead `selected_tier` accessor retired; docs
de-staled; byte-identical probe transcripts prove zero behavior change).
Nothing sim, economy or data moved (golden replays byte-identical), and zero
monetization ships here or ever: **No shop. No loot boxes. No timers. No
monetization, ever — by owner ruling 2026-10-25.**

**What shipped**

- **Mouse-wheel zoom** — scroll OUT for the overview: the rig distance
  doubles from the shipped D=64 default to D=128 (2×, the readable-far limit —
  at farther distances the enemies' walk-bob falls under a pixel). Scroll IN
  to the close floor D=56, which never crops a path corner: the floor is
  DERIVED from the shipped framing-gate math (the same frustum margin the
  camera test enforces), whose first crop point 52.4 stays BELOW it — every
  waypoint, core, spawner and hero battle-space point measures inside the
  margin at 56 and beyond (the crop at 52.4 was re-measured on the shipped
  gate, not assumed). One wheel tick = 8 units; both ends clamp.
- **The default view is byte-identical to v1.2.1** — the camera row in the
  scene file is NOT edited; zoom is runtime-only displacement that CAPTURES
  the shipped default from the scene at startup, and a fresh mission at zero
  wheel input renders a pixel-identical capture against the pre-change
  baseline (byte-identical PNG, sha256 `0a40d116…`, verified again after the
  mount shipped).
- **Wheel-only by design — no keys** — +/− keys were deliberately NOT added:
  every shipped key route ends in the mission's one press pump (a second
  reader is the forbidden second mechanism), and the wheel is the repo's
  existing engine-native presentation-input precedent — the hub list already
  scrolls by wheel. See Known limits for what that means for touchpads and
  the web build.
- **No HUD change** — the HUD is in-engine Controls laid out in viewport
  screen space, a function of the window, not of the camera; zoom cannot move
  it, and nothing HUD-side shipped this wave.

**Promised vs shipped** — the camera ships EXACTLY as granted: distance only,
pinned in every other way. Owner grant MC 11719 (2026-10-30) verbatim:
**"Go 1 and zoom control for 2"** — ZOOM ONLY. Pan, rotate and pitch remain
NOT granted: the rig's basis stays byte-locked, the shipped default row stays
byte-identical, and the LOCKED frustum pin #3 stays SPENT and untouched. Of
v1.2.1's deferred row "player zoom / camera controls" only the zoom half is
now shipped; the spawn-mouth shimmer / painted-lane treatments stay deferred.

**Known limits, stated as they are**

- **Zoom is wheel-only by design** — touchpads work (they emit wheel
  events), there is no keyboard zoom. On the served web build one physical
  KEY reaches the game twice (the shell-JS + engine double-feed,
  served-measured at MC 11700), so the wheel path is NODE-LOCAL by design
  with a per-tick guard: the same tick arriving twice is still one step, two
  distinct ticks are two steps — both clauses pinned by the shipped relay
  kit. Wheel-over-GUI: over a Control that consumes the wheel (the hub list,
  the build panel's rows) it scrolls or acts there instead of zooming —
  consistent with the shipped hub scroll, not a bug.
- Carried forward from v1.2.1 (still true, quoted from that section — except the hero-crest
  half, RETIRED at v1.4 MC 11835: the crest was measured ILLEGIBLE (P4-wave.log) and fixed
  x2+outline (P8-wave.log), served re-shoot spells the hero name in full):
  the kill-blow number "is a lower bound"; "Damage numbers share one effects
  pool" (the 64-slot cap); "A kill right at the core's door shows no final
  number"; "The hero crest and telegraph numbers are small at a 1280-px
  window" (crest half retired v1.4; the telegraph half stands); "The build ghost is a slot
  marker, not a translucent tower
  silhouette"; and "`static/` (the browser build) is gitignored by design" —
  regenerate with `bash tools/export_web.sh`.

**Suite**: 287 pytest green, `check_hygiene: 0 hit(s)`, golden fixtures
byte-identical.

## v1.2.1 (readability) — 2026-10-30 (RELEASED: tag v1.2.1 + GitHub Release)

The readability wave: the battlefield now tells you at a glance where you are,
where mobs come from, which paths they take, where you can build and what your
click will do. Nine player-facing changes on the v1.2 base — no economy, sim or
data changes (golden replays byte-identical), and zero monetization ships here
or ever: **No shop. No loot boxes. No timers. No monetization, ever — by owner
ruling 2026-10-25.**

**What shipped**

- **Spawn-gate eyes** — every one of Gatefall's three spawn gates now wears an
  eye marker over its mouth, so you see where mobs come from without
  memorizing the map. The two gates that also send flying enemies wear the
  WINGED eye; the ground-only gate wears the plain one. Original art, painted
  for this game.
- **Lane bands** — a lit, translucent road is painted on the ground along
  every ground lane from its gate toward the cores. Air lanes deliberately
  carry no band on the floor: the winged eye above their gate is their cue.
- **Wave telegraphs at the gates** — during each build phase, every gate that
  will open shows a small billboard stack: the actual enemy portraits of the
  upcoming wave and how many of each will march through that gate (air
  carriers ride above the ground list). The previews clear the moment combat
  starts, and return updated next build phase.
- **Heroes read as heroes** — your active hero now renders bigger than the
  small mobs it fights, and wears a name crest above its head: the hero's own
  portrait and name. The crest follows the F1–F3 swap, so you always know
  which hero is on the field.
- **A coach banner that tells you what to do now** — on your first mission the
  banner teaches while you play: at the opening build phase "BUILD: tower
  buttons on the right panel — click arms, click again places"; during the
  first fight "FIGHT: both mouse buttons hit, F1-F3 swap heroes"; at the next
  build "NEXT WAVE: watch the gate billboards". After that it stays quiet, and
  a victory or defeat banner always wins over the coach.
- **Damage numbers on every hit** — every hit you land floats a number over
  the enemy it touches, from your heroes AND from your towers, kill blow
  included. (The kill-blow number has an honest limit — see Known limits.)
- **Build flow you can see** — pressing a tower button no longer silently
  drops a tower on a hidden slot. It ARMS the pick and a build ghost appears
  on the first free build slot; ◀/▶ (arrow keys) cycle the ghost through the
  open slots, a left-click (or M) confirms the placement, and a right-click
  (or Esc) cancels the whole thing. The old keyboard shortcut is untouched:
  M with nothing armed still places the classic way.
- **Yellow range ring while building** — while a build ghost is armed, a
  translucent yellow ring lies flat on the ground showing exactly how far the
  armed tower's first-tier range reaches, read from the tower data. No ghost
  armed, no ring; the Gate Blockade (which has no range) correctly shows
  none.
- **Web build rendering fix** — the lane bands and the range ring now actually
  paint in the browser build: the web renderer could not draw the first
  version of their geometry, and both were rebuilt on a mesh path that it
  draws, pixel-verified in the served browser.

**Known limits, stated as they are**

- **The kill-blow number is a lower bound.** The game drains a dead enemy
  before the visual layer ever sees the killing hit, so the final number is
  the enemy's remaining hp at the last observation — equal to or less than
  the blow that actually killed it (the overkill part is unobservable). Every
  non-lethal number is exact.
- **Damage numbers share one effects pool.** They ride the same 64-slot cap
  as tracers and sparks, so on a very busy wave some numbers can be starved
  out. A missing number does not mean the hit didn't land.
- **A kill right at the core's door shows no final number.** An enemy taken
  down within half a step of its lane's end reads to the eye as a breacher,
  not a death, and breachers render no kill number by design.
- **The hero crest and telegraph numbers are small at a 1280-px window** —
  small they were; the ship-time comfort that they were nonetheless READABLE was MEASURED at
  v1.4 and found FALSE for the crest half *(SUPERSEDED: P4-wave.log read the crest ILLEGIBLE —
  glyph blocks ~4–5 px, no magnification spelled a single hero name — and MC 11835 fixed it on
  the same mechanism: height x2 + outline + band lifted above the shield crown; the served
  re-shoot spells "Bram Wardenfell" in full, P8-wave.log §RESHOOT-VERDICT. The
  telegraph-numbers half remains true — P8 left TEXT_PX/OUTLINE_PX untouched.)*
- **The build ghost is a slot marker, not a translucent tower silhouette.**
  The yellow range ring plus the slot marker show where the tower will stand;
  a see-through tower figure is not shipped.
- **`static/` (the browser build) is gitignored by design** — a fresh clone
  has no web artifacts; regenerate them with `bash tools/export_web.sh`.
- **Not shipped this round (deferred by design):** player zoom / camera
  controls — the camera numbers are a locked pin and moving them needs a new
  owner ruling — and the spawn-mouth shimmer / painted-lane treatments. The
  gate eyes and lane bands ARE the v1.2.1 treatment.

**Suite**: 283 pytest green, `check_hygiene: 0 hit(s)`, golden fixtures
byte-identical.

## v1.2 (quality-of-life) — 2026-10-29 (RELEASED: tag c95798b + GitHub Release with native Windows build, VM120-verified)

The six-card QoL milestone on the GA base (V12-PLAN, owner ruling 2026-10-28
verbatim "rec on all 3"): getting back to the hub and selling the banked loot
stop being reload/manual chores, the shop reaches every tower family, enemies
walk with motion, and the camera reads closer and steeper.

**What shipped**

- **Return to hub, END-ONLY (F1, MC 11623)** — a RETURN TO HUB button on BOTH
  mission-end screens (victory AND defeat); no mid-mission exit control ships,
  per the owner END-ONLY ruling; the reload route stays, the `_end_mission`
  save commit is untouched.
- **SELL ALL (F2, MC 11622)** — the gear panel sells every bank row for the
  total quoted from rarity.json's `sell_value` ladder BEFORE anything is
  applied: ONE confirm dialog, shown = paid (one mechanism — SimInventory
  `bulk_sell` behind both the quote and the mutator).
- **Relic-assign negative tests (F3, MC 11609)** — tests-only hardening that
  closes the stale-uid-across-sell gap; zero product-code change.
- **Shop family picker (F4, MC 11616)** — bombard + hailspire are selectable
  in the build bar; every pick rides the ONE existing placement path
  (`place_id` → the same gate sequence), all five icon badges now live.
- **Procedural enemy walk (F5, MC 11610)** — a step-bob + roll sway from the
  distance walked, VISUAL LAYER ONLY: sim rows, hitboxes and golden fixtures
  byte-identical.
- **Camera D=64 pitch-48 (F6, MC 11649)** — the rig moved to the re-derived
  transform (characters +10.2%, all 33 frustum points hold with wider margin);
  LOCKED pin #3 re-pinned ONCE per the owner's documented grant — any further
  camera move needs a NEW owner ruling.

**Suite**: 239 pytest green, `check_hygiene: 0 hit(s)`, golden fixtures
byte-identical.

## v1.1 (visuals) — 2026-10-28

The greybox is gone. v1.1 replaces placeholder art with an original
stylized set generated on the fleet's 3090 — Dungeon Defenders 2 used as a
**style reference only**, every asset generated original (clean-room held;
prompts + sha256 manifests per asset in `.audits/20261027-1500-visual-target/`).

**What shipped**

- **Chunky unit sprites** — 3 heroes and all 7 enemy types (grunts AND the
  warden_breaker boss), all painted on-style and wired through ONE sprite map
  (`sprite_bank.gd`); the last greybox (the boss) retired too — the primitive
  path stays only as the null-fallback for future ids.
- **T1→T3 tower art** — ballista, bombard and hailspire each visibly
  repaint on upgrade (tier skins wired through the shipped `upgrade()` call,
  path-pinned probes + live pixel proof).
- **The world** — flat grey plane replaced by a framed cartoon arena board;
  the cores ride their wolf-crest emblem; camera nudged in (bounded by the
  shipped frustum gate, +3.55%, all 33 lane/core points held with ≥60 px margin).
- **HUD & shop icons** — gold-rimmed badges on the build bar, emblems beside
  the green/wave/core counters; every label byte-identical at rest.
- **Combat FX** — projectile tracers, hit sparks, death poofs — a visual-only
  observer reading sim state from OUTSIDE (zero sim edits, proven by diff).
- **Menus move** — tab-switch slide+fade tween and button hover/press
  feedback via one shared helper; at-rest layout pixel-stable (byte tests green).
- **Native proof** — fresh `Gatewardens.exe` re-verified on the VM120
  Windows 11 / RTX 2060 seat: byte-identical transfer, live boot, and a
  deterministic 1280×720 @ 60 FPS movie-mode capture; served web build
  pixel-verified with the new art. Suite still 222 green, hygiene 0,
  golden fixtures byte-identical.

**Known limits, stated as they are**

- The death poof's brown doesn't visually separate from brown enemy sprites
  at the fixed camera — its presence is carried by counters, not pixels.
- The outgoing tab still hard-cuts on switch (a shipped probe asserts the
  previous station hidden synchronously; deferring it would be a logic change).
- The build bar ships three class buttons (family picker is a declared later
  row), so two of the five icon badges are registered but not yet visible.
  *(FIXED v1.2 MC 11616, 2026-10-28: the family picker shipped — bombard +
  hailspire are selectable in the build bar via the ONE existing placement
  path; all five icon badges are now visible.)*
- Deeper camera zoom than +3.55% is gated by the shipped frustum-margin test
  — an owner decision, not a silent change. *(That decision was taken at
  v1.2 F6, MC 11649: the rig moved to D=64/pitch-48 under the ONE documented
  re-pin of LOCKED pin #3, owner grant 2026-10-28; any further move needs a
  NEW owner ruling.)*
- Served-web frame rate is honest-by-instrument: the native 60 FPS render
  path is VERIFIED (movie capture); headless-browser measurement is
  throttle-capped (~6 fps on a STATIC screen = the harness, not the game).

**Promised vs shipped**: this milestone promised V1–V7 visual rows; all seven
shipped with the caveats above. Enemy walk-cycle animation and per-tier
blockade/snare skins were NOT in scope and are not claimed.

## v1 (GA) — 2026-10-27

The full loop ships: fresh boot → hub → War Table starts the NORMAL mission
(Gatefall) → defend the cores through 10 waves + the wave-11 boss → win
banner → loot into the gear bank → reload → hub: bank, gold, materials,
equipped gear and ascension all persist. Wave 11/11 victory, equip-by-click
and persistence are browser-VERIFIED served (evidence pointers at the bottom);
the headless suite is 222 pytest green and the hygiene gate reads
`check_hygiene: 0 hit(s)` at this release.

**No shop. No loot boxes. No timers. No monetization, ever — by owner ruling 2026-10-25.**

**Windows download** — the v1 release page carries a Windows zip asset: unpack
and double-click `Gatewardens.exe` (Windows 10/11, 64-bit; one self-contained
file, no installer). Saves live in `%APPDATA%\Godot\app_userdata\Gatewardens`.
Unsigned-build caveat stated as it is: SmartScreen may warn — the build is
unsigned, no malware, click More info > Run anyway.

## What shipped

- **Hub, six stations** — War Table (mission select), Gear (bank list + hero
  equip slots), Blacksmith (item Upgrade / Evolve / Reroll, gold + material
  costs), Tinkerer (mod transfer), Training Dummies (DPS test), Ascension
  (meta-point spending). All six tabs render on the served build.
- **Heroes & combat** — three heroes: Bram Wardenfell (melee), Sila Deadeye
  (ranger), Ysolde Embercaller (mage); each with two mouse attacks and four
  abilities on blue mana, plus hot-swap (F2) and XP/levels. Holding BOTH
  mouse buttons (primary + secondary attacks) plus a held skill key is the
  real win lever (see Known limits g).
- **Defenses** — five data classes: Ballista, Bombard and Hailspire towers,
  the Gate Blockade, the Barbed Snare trap. Placement on lane-derived build
  slots (at v1 the panel's place button dropped the tower onto the next open
  slot, spread round-robin across the ground lanes — SUPERSEDED at v1.2.1
  MC 11700: a tower-button press now ARMS a build ghost you cycle and
  confirm, right-click cancels; the old instant route survives only as the
  M-with-nothing-armed legacy shortcut, never as the panel's behavior);
  green economy from kills + wave completions; T1→T5
  upgrades; repair/sell on the cited wiki formulas; per-map defense cap.
- **Mission** — Gatefall with main + sub cores, ground + air lanes,
  alternating build/combat phases, 10 waves + a boss wave. NORMAL victory is
  browser-verified served; HARD ships data + a byte-stable headless golden
  win fixture (not browser-verified in v1).
- **Loot** — direct enemy drops + one free Victory Chest per win (no keys, no
  timers). Rarities as the data ladder reads: Worn → Sturdy → Powerful →
  Epic → Mythical → Legendary. Material drops (Torn Hide, Iron Bar, Ember
  Core, Aether Crystal) feed the Blacksmith and Tinkerer.
- **Gear + persistence** — equip by clicking a bank row then a hero slot
  (browser-verified served); equipped gear, bank, gold, materials and
  ascension survive a full page reload (W17g round-4 `equipped_json` save
  key; item-void P1 closed and served-verified).
- **Ascension** — account-wide points per hero level over Offense / Defense /
  Utility trees; a +1 click at the station persists across reload.
- **Web export** — the whole game runs in the browser from a Godot 4.7.2 web
  export served by the repo's own `server/server.py`.
- **Verification shipped with the product** — 222 pytest (headless sim
  numbers, byte-pinned golden replays, engine-tier UI gates with planted-red
  proofs) + the `check_hygiene` monetization/structure gate at 0 hits.

## Known limits (stated as they are)

- **(a) Return-to-hub after a mission is END-ONLY.** *(FIXED v1.2 MC 11623,
  2026-10-28: the v1 claim "a page reload is the only route back" — `open_hub`
  boot-only — is retired: a RETURN TO HUB button ships on both mission-end
  screens, victory AND defeat, per the owner END-ONLY ruling 2026-10-28;
  deliberately NO mid-mission exit control; the reload route stays.)* The
  mission-end save still commits at `_end_mission` — nothing is lost by
  reloading.
- **(b) Bank loot now sells in bulk: SELL ALL behind one total-gold
  confirm.** *(FIXED v1.2 MC 11622, 2026-10-28: the v1 claim that a full bank
  had no bulk salvage is retired — the gear panel's SELL ALL sells every bank
  row for the total quoted from rarity.json's `sell_value` ladder BEFORE it is
  applied, ONE confirm dialog, shown = paid, per owner ruling 2026-10-28.)*
  One normal win banks ~150 items (the golden fixture pins loot_events:148),
  which is the pile this serves; the gear panel also SCROLLS into the hero
  equip rows (W17g). The Blacksmith's Upgrade/Evolve/Reroll
  services (they spend gold + materials), the mission-side defense Sell, and
  equip's replace-to-bank return path for the item it replaces all stay
  unchanged.
- **(c) Reload-race risk right after the win banner.** Reloading within ~1s
  of the win banner CAN race the IndexedDB flush; a patient reload persists
  (measured both ways in the journey evidence).
- **(d) Relics: banked, not fully wired end-to-end in v1.** Relic items DO
  drop into the bank (`medallion_of_the_gate` rows, RELIC section, seen
  served post-win). The gear panel equips weapon/armor/ring only — refusing
  a relic onto a hero slot is the data-declared slot contract — and the
  mission-side Assign-relic positive path was NOT click-verified in v1:
  "not fully verified", not "unreachable".
- **(e) Selling a defense at full durability refunds 0.** The pinned wiki
  formula scales the refund by missing health — BY DESIGN; noted so the 0 is
  not mistaken for a bug.
- **(f) Greybox cosmetics.** Row labels can overlap in tall lists; the hub
  shows a centered "Gatewardens — Hub" label; the meta row is unstyled. Full
  HUD styling is a named follow-on. *(SUPERSEDED for art by v1.1: unit/tower/
  enemy/HUD art + the world texture shipped 2026-10-28 — the row-label overlap
  in tall lists and the unstyled meta row REMAIN true.)*
- **(g) The win lever is undiscoverable by design-accident.** Holding BOTH
  mouse buttons (primary + secondary attacks) plus a held skill key is real
  gameplay the UI never teaches — the golden replay pins it; players
  discover it.

## How to build & run

- Godot **4.7.2** (with matching web export templates) and `python3`.
- Build the web client: `bash tools/export_web.sh` → `static/` (build
  artifacts are never committed; the script regenerates them).
- Serve: `python3 server/server.py` (honors `GW_PORT`, default **8124**) →
  open `http://<host>:8124/` in a browser.
- Dev checks at this release: `python3 -m pytest -q` (324 green on the v1.4 read-state wave with
  the web export present — 319 from a clean checkout, the test_served 5-leg module-skip
  reconciling +5 as at every tag; 287 green on the v1.3 zoom wiring; 283 at v1.2.1;
  239 at v1.2; the v1 GA tag counted 222) and
  `python3 tools/check_hygiene.py` (`check_hygiene: 0 hit(s)`).
- Served controls (current at v1.2.1, from the verified journey): mouse click
  = attack / interact, hold BOTH mouse buttons = the heavy combo, WASD = hero
  move, F1–F3 = swap heroes; building: a tower-button press ARMS the ghost,
  ◀/▶ (arrow keys) cycle the slot, left-click or M places, right-click or Esc
  cancels (M with nothing armed keeps the legacy instant place),
  E / N = upgrade / sell selected defense.

## What the claims stand on

Served browser verification: `.audits/20261025-1045-clean-code/A9-journey-final.md`
(victory 11/11, ascension-click persists, zero console errors) and
`.audits/20261025-1045-clean-code/W17g-evidence.md` (scroll reaches the DECK
hero rows, equip-by-click served, equipped gear + bank persist across reload).
Suite/hygiene re-runs for these docs:
`.audits/20261025-1045-clean-code/RELEASE-DOCS-evidence.md`.
