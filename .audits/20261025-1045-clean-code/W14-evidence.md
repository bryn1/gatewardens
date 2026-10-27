# W14 behavior-close — evidence (MC 11274.1.25 / card 11341, code seat)

Commit: `1067391` (main), author `code (11341) <code@agent-town.local>` — ONE commit,
12 files changed, 750 insertions(+), 71 deletions(-):

    godot/scripts/defense_obj.gd  godot/scripts/defense_panel.gd
    godot/scripts/dummy_range.gd  godot/scripts/hub.gd
    godot/scripts/mission.gd      godot/scripts/ascension_ui.gd (NEW)
    godot/sim/hub_probe.gd        godot/sim/mission_smoke.gd
    godot/sim/sim_inventory.gd    tests/test_hub.py
    tests/test_hub_layout.py      tests/test_mission_smoke.py

## Gate rows

- Full suite: `python3 -m pytest tests/ -q` -> `190 passed in 23.27s`, EXIT=0
  (baseline pre-W14: `190 passed in 21.49s`, EXIT=0 — same count: the rewritten
  DUMMY/XP gates ride the new behavior inside their existing functions; every
  W14 leg rides the existing engine-tier legs' new machine rows).
- `python3 tools/check_hygiene.py` -> `check_hygiene: 0 hit(s)` (soft notes only;
  growth of the EXEMPT test assets declared in the R-list, NO new exemption).
- Golden byte-anchor (never touched — `git show HEAD^:...jsonl` == worktree):
  - fixture file sha256 PRE `f0473c1ce447938aa6b5b8cb888c9be71c579a1e51142ec11f9b155d54380f23`
    POST `f0473c1ce447938aa6b5b8cb888c9be71c579a1e51142ec11f9b155d54380f23`
  - out-row stream (`grep '"kind":"out"' | sha256sum`) PRE
    `8ea42737bc4a96249246fbf158a64beb79c90ff2aaf9c1722089065ad43528af`
    POST `8ea42737bc4a96249246fbf158a64beb79c90ff2aaf9c1722089065ad43528af`

## Per-leg machine rows (all re-derived by pytest from the shipped data)

hub_probe (rc 0, stderr EMPTY — capture 2026-10-26 10:47 UTC, post-commit tree):

    HUB-PROBE-BOOT bank=2 gold=911 mats=torn_hide:3,iron_bar:3,ember_core:2,
    HUB-PROBE-EQUIP bank_after_first=1 bank_after_swap=1 returned=1 equipped=twin_fang relic_refused=1 bank_after_relic=2 unknown_refused=1
    HUB-PROBE-UPGRADE cost=40 mats_dropped=torn_hide:2,iron_bar:1, upgraded=1 rarity=worn gold_left=871
    HUB-PROBE-EVOLVE from=worn to=sturdy cost=600 refused=1 gold_left=271
    HUB-PROBE-REROLL cost=120 stats_changed=1 mods_kept=1 rarity=powerful gold_left=151
    HUB-PROBE-TINKERCAP refused=1 gold_unchanged=1 mods_unchanged=1
    HUB-PROBE-TINKER moved=1 cost=150 mats_dropped=torn_hide:1,ember_core:1, source_mods=0 target_mods=1 gold_left=1
    HUB-PROBE-DUMMY xp_paid=0 meta_untouched=1 absorbed=34.00 dps=34.00 invulnerable=1   <- P3-11
    HUB-PROBE-WAR maps=gatefall:[normal,hard,] start=gatefall difficulty=hard
    HUB-PROBE-PANELS open=blacksmith
    HUB-PROBE-ASC earned=1 refused_unknown=1 refused_over=1 spent=1 available=0 station=visible   <- P1-3
    HUB-PROBE-RELIC assigned=1 refused_taken=1 refused_uid=1 refused_relic=1 refused_phase=1 refused_none=1 unequip=1 pool_intact=2 hp_delta=3.0 save_roundtrip=2 asc_kept=1 effect_blue=102.0   <- P1-2 + effect site
    HUB-PROBE-CHEST bank_before=5 bank_after=6 gold_untouched=1 rarity=powerful shown=6
    HUB-PROBE-OK

Re-derivations (tests/test_hub.py): earned == ascension.json points_per_level;
effect_blue == heroes.json warden base.blue_max 100 + reservoir per_point.val 2
(spent 1) = 102.0 — proven at the mission site AND through snapshot_json;
hp_delta 3.0 == orb_of_the_deep primary=hp (items.json) x scripted ilvl 3;
save_roundtrip=2 = both relic rows read back through save.load_save() ->
from_save() into a fresh GWGameState (plus asc_earned/asc_spent kept).

mission_smoke W14 rows (rc 0, stderr EMPTY):

    MISSION-SMOKE-W14PANEL mount=1 class=tower cost=100 refund=0 green=300
    MISSION-SMOKE-F1SWAP hero=warden swap_blue=90.0 deadeye_max=90.0
    MISSION-SMOKE-W14SWAP hero=warden digit2_cast=1 blue_drop=34.95 f2_hero=deadeye

P1-1: KeyM enters the SHIPPED bridge, mission step (5) relays it to
panel.poll, tower lands for EXACTLY towers.json base_cost 100 (start_green
300 from gatefall.json), undo sell through the SAME panel refunds the pinned
R1 full-HP 0; W8 panel legs now drive the SAME mounted panel (second
instantiation deleted). P1-4: held Digit2 casts warden ability 2 — pytest
asserts blue_drop == heroes.json mana_cost(35) minus exactly one regen tick
(blue_regen 3.0/60 = 0.05 -> 34.95) and the active hero NEVER changes; the
follow-up F2 press DOES swap (warden -> deadeye).

hub layout (test_hub_layout.py, six stations): GWLAYOUT-STRUCT
slot_parents=PanelSlot x6, GWLAYOUT-BTN x=6 strictly increasing, GWLAYOUT-OK.

## Planted reds (a gate that never went RED is not a gate)

RED #1 — digit collision, captured BEFORE the P1-4 fix
(.tmp/w14/red_digit.gd, boots the real mission scene):

    RED-DIGIT collision: Digit2 press swapped hero warden -> deadeye (cast=true)   rc 1

GREEN rerun post-fix (captured 2026-10-26 10:36 UTC):

    GREEN-DIGIT: Digit2 kept hero warden (cast=true)   rc 0

RED #2 — equip(unknown uid), captured BEFORE the P2-10 fix
(.tmp/w14/red_equip.gd; the RED row was produced by the probe's ORIGINAL
assert before the probe-side clause fix — product state, not probe state):

    RED-EQUIP: unknown-uid equip ok=true (raw true) bank=1 equipped={ "weapon": {...uid 999999...} }   rc 1

GREEN rerun post-fix (captured 2026-10-26 10:36 UTC):

    GREEN-EQUIP: unknown-uid refused ok=false, bank=1 equipped untouched   rc 0

## R-list (declared readings)

- P1-2 "persists via save": per pinned C11 the ASSIGNMENTS are mission-local
  (relics_assigned is a mission mirror); what persists is the C13 bank side —
  proven by the round-trip row (fresh state from the save file carries both
  relic rows, the next mission's relic_pool rebuilds from that bank).
- P1-3 effect site: smallest honest live consumer = mission._build_heroes
  applying SimProgression.asc_modifier onto the freshly-parsed mission-local
  hero rows (zero literals, single site; every base-stat reader inherits).
  Station refusal display only greys buttons; spend_asc's gates ARE the
  refusals (probe calls them directly too).
- P1-4 byte-anchor proof: every golden Digit2 press (ticks 14 / 16894 /
  19440) lands while active==1, and the removed Digit-as-swap alias called
  _try_swap(1) which early-returns on i == active — removing it is a byte-
  NOOP on the golden stream (confirmed by the identical out-row sha above).
  Digit1-4 remain hero_combat ABILITY held-codes; the hub-side Digit station
  map is untouched.
- P3-11 reading: the brief's "bounded per dummy-range wording" names no data
  source (A6 declares the dummies as the DPS test only); a literal cap would
  break I2, so the honest single-site bound is ZERO — the faucet is CLOSED.
  The row proves meta byte-stability across a strike (heroes JSON compare +
  gold); C13 write_seq unmoved follows (mutated is emitted by no strike path).
- step (5) mirror: relics_assigned recomputes at its ONE site in
  step_bookkeeping (plus the assign/unassign crossings refresh it for
  keyboardless callers) — the C5 row value stays fresh without a second
  accounting path.
- Harness licenses used (boot_probe drive-real-entry-points, declared):
  mission_smoke green write-back after the W14 undo-sell, hub_probe
  phase_kind flip for the phase refusal, win_pending; probe-side Vector3
  positions for the second tower (no balance literal — I2 gate scopes the
  shipped layer; test assets encode expected numbers).
- Test-asset growth: hub_probe 673, mission_smoke 706, mission.gd 563 — all
  under EXISTING `# hygiene:` headers (no new exemption), check_hygiene 0
  hits; growth is the new legs' asserts, not refactoring.
- LEDGER.md W14 status row is the orchestrator's to land (W13 pattern:
  865b668 code + separate 817f8d2 LEDGER row).

VERIFY_EXIT=0
