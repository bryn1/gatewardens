# Gatewardens — Release Notes

## v1.1 (visuals) — 2026-10-28

The greybox is gone. v1.1 replaces placeholder art with an original
stylized set generated on the fleet's 3090 — Dungeon Defenders 2 used as a
**style reference only**, every asset generated original (clean-room held;
prompts + sha256 manifests per asset in `.audits/20261027-1500-visual-target/`).

**What shipped**

- **Chunky unit sprites** — 3 heroes, 6 enemy types, all painted on-style
  and wired through ONE sprite map (`sprite_bank.gd`); the last greybox
  (warden_breaker enemy) retired.
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
- Deeper camera zoom than +3.55% is gated by the shipped frustum-margin test
  — an owner decision, not a silent change.
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
  slots (panel place falls to the first free slot, spread round-robin across
  the ground lanes); green economy from kills + wave completions; T1→T5
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

- **(a) No in-game return to hub after a mission.** `open_hub` is boot-only;
  a page reload is the only route back. The mission-end save still commits
  at `_end_mission` — nothing is lost by reloading.
- **(b) A full bank has no bulk-sell.** One normal win banks ~150 items (the
  golden fixture pins loot_events:148). The gear panel now SCROLLS into the
  hero equip rows (W17g), but there is no item salvage service in the shipped
  sim: what exists is the Blacksmith's Upgrade/Evolve/Reroll services (they
  spend gold + materials), the mission-side defense Sell, and equip's
  replace-to-bank return path for the item it replaces.
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
- Dev checks at this release: `python3 -m pytest -q` (222 green) and
  `python3 tools/check_hygiene.py` (`check_hygiene: 0 hit(s)`).
- Served controls (from the verified journey): mouse click = attack /
  interact, hold BOTH mouse buttons = the heavy combo, WASD = hero move,
  F2 = hero hot-swap, M / E / N = place / upgrade / sell selected defense.

## What the claims stand on

Served browser verification: `.audits/20261025-1045-clean-code/A9-journey-final.md`
(victory 11/11, ascension-click persists, zero console errors) and
`.audits/20261025-1045-clean-code/W17g-evidence.md` (scroll reaches the DECK
hero rows, equip-by-click served, equipped gear + bank persist across reload).
Suite/hygiene re-runs for these docs:
`.audits/20261025-1045-clean-code/RELEASE-DOCS-evidence.md`.
