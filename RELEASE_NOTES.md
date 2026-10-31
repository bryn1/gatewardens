# Gatewardens — Release Notes

## v1.3 (zoom) — 2026-10-31

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
- Carried forward from v1.2.1 (all still true, quoted from that section):
  the kill-blow number "is a lower bound"; "Damage numbers share one effects
  pool" (the 64-slot cap); "A kill right at the core's door shows no final
  number"; "The hero crest and telegraph numbers are small at a 1280-px
  window"; "The build ghost is a slot marker, not a translucent tower
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
  readable, not big. Scaling them is a later knob, not this round.
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
- Dev checks at this release: `python3 -m pytest -q` (287 green on the v1.3 zoom wiring; 283 at v1.2.1;
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
