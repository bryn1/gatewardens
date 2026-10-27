# W12 batch-2 wiring evidence (V1.1-b, MC 11520 / milestone 11462 / workspace 11274)

Visual-only build: the 8 committed batch-2 PNGs (minus enemy_skitterling_run.png,
the later animation card) now flow through the SAME sprite_bank -> three
draw-sites mechanism; towers get their tier skins, gate_blockade/barbed_snare
exit the greybox. sim/economy/save data, tests and the golden fixtures untouched.

## 1. Mechanism (replace-not-add, same bank, same three callers)

- godot/scripts/sprite_bank.gd is now (id, DISPLAY-tier)-aware:
  `texture_for(id, tier = 1)` — TEXTURES keeps the BASE sheet of every sprited
  id (T1 skins, tier-agnostic sheets, heroes, enemies; gate_blockade +
  barbed_snare added), TIER_TEXTURES adds ONLY the committed _T2/_T3 shooter
  skins. Unknown tier falls back to the base sheet (bombard T3 -> reads T1;
  no bombard T3 sheet is committed), so a tiered id is never null once its T1
  exists. warden_breaker: no entry anywhere -> stays null (mesh). The 1-arg
  call shape keeps working via the default tier (hero_pawn/enemy_runner and
  the V1.1-a probe rows unchanged). enemy_skitterling_run.png is NOT wired.
- godot/scripts/defense_obj.gd: _make_visual now asks the bank at
  (id, tier + 1); the existing upgrade() leg calls _refresh_visual() once —
  the same slot swaps the scene-tree child (remove_child old + add_child new
  + free; the mission's defense_list entry only ever reads obj.node). No new
  node type, no second render path.
- 8 new PNG .import sidecars committed from
  `Godot_v4.7.2 --headless --path godot --import` (rc 0) — clean-checkout
  determinism, same law as batch 1.

## 2. Headless render proof — sim/v11_sprite_probe.gd extended

cmd: Godot_v4.7.2 --headless --path godot -s res://sim/v11_sprite_probe.gd

The new TIER leg upgrades a placed ballista ONCE and a placed hailspire
TWICE through the SHIPPED defense_obj.upgrade() entry point and asserts the
LIVE tree node carries the expected sheet, pinned by its committed RESOURCE
PATH — not through the bank. (Gate history, kept honest: the first planted-red
plant — dropping the hailspire T3 key — stayed GREEN against a bank-as-oracle
assertion, because the broken map is self-consistent via the T1 fallback.
The probe was rewritten to pin the path, and the same plant then went red.
A check that never failed is not a check.)

GREEN transcript (W12-probe-green.log, stderr 0 bytes) beside the RED one
(W12-probe-red.log, same plant: hailspire T3 key dropped from TIER_TEXTURES;
stderr 0 bytes):

```
GREEN (rc 0)                          RED (rc 1)
SPRITEBANK-TEX n=12 px=512            SPRITEBANK-TEX n=12 px=512
SPRITEBANK-HEROES n=3                 SPRITEBANK-HEROES n=3
SPRITEBANK-SWAP active=1 ...          SPRITEBANK-SWAP active=1 ...
SPRITEBANK-TOWERS n=3                 SPRITEBANK-TOWERS n=3
SPRITEBANK-TIER ballista=T2           SPRITEBANK-FAIL tier sheet:
   hailspire=T3                          hailspire_tower T3
SPRITEBANK-GATEART blockade=sprite
   trap=sprite
SPRITEBANK-ENEMIES n=6 boss_greybox=1
SPRITEBANK-FLIP right=flipped left=plain
SPRITEBANK-OK
```

Every V1.1-a row kept its green semantics; the old GREYBOX row is retired
HONESTLY: blockade/trap are now Sprite3D on their sheets (GATEART row), and
only warden_breaker stays mesh — asserted live in the ENEMIES row
(boss_greybox=1). Post-restore re-run at the committed tree: rc 0, the full
9 rows + OK, stderr empty (the file in this dir is the final-tree capture).

## 3. Gates at the committed tree

- python3 -m pytest -q: BEFORE editing 222 passed in 152.25s; AFTER at this
  tree 222 passed in 154.43s — SAME green count (baseline 222).
- tools/check_hygiene.py -> 0 hit(s).
- golden fixtures byte-identical:
  mission_gatefall_normal.jsonl sha256 eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912
  mission_gatefall_hard.jsonl  sha256 5e37c4b089209e64e26395237830bc16a1cf62aa3b9a6d427be2f361f970f628
- LEDGER.md V1.1-b row lands in this commit.

## 4. Coexistence fact (declared)

The shared checkout concurrently carries card 11517's tests/conftest.py fix
(orchestrator coexistence note). This commit stages ONLY its own paths
(explicit git add); conftest.py and its evidence are NOT in it. The post-edit
222-green suite above ran with their conftest edit present in the tree.

## DoD rows (card 11520)

1. texture_for(id, tier=1): T2/T3 shooters, T1 fallback, blockade/snare
   sheets, warden_breaker null, 1-arg shape intact — bank read + probe
   GREEN/RED legs. VERIFIED.
2. upgrade() repaints the live node at the new tier — probe TIER leg drives
   the shipped entry point. VERIFIED (rc 0 green, rc 1 on planted-red).
3. Probe extended, planted-red beside green both transcripts here. VERIFIED.
4. Suite 222 = 222 before/after, hygiene 0, fixtures byte-identical. VERIFIED.
5. LEDGER row in this commit. VERIFIED (git show).

VERIFY_EXIT=0
