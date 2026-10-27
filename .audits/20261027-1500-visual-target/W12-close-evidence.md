PROBE: sha256sum /home/claudecode/Games/gatewardens/godot/scripts/sprite_bank.gd => ^eae89add941647e6a132be4fa3790ba5766e4cd91b8159d035042674ca9ea5bb
PROBE: grep -c 'SPRITEBANK-OK' /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-orchestrator-w12.log => ^1$
PROBE: grep -c 'TIER ballista=T2 hailspire=T3' /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/gen/probe-orchestrator-w12.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898

# W12-close (MC 11520) — orchestrator close evidence (V1.1-b tier wiring)

Child commit: 0be1f6841ec3 (author "code (11520)", one commit, explicit 17
paths; card 11517's commit 740d64c beneath, untouched — coexistence held).

## Measured BY THE ORCHESTRATOR at the committed tree
- Probe re-run (own command, gen/probe-orchestrator-w12.log): 9 rows +
  SPRITEBANK-TIER ballista=T2 hailspire=T3 + SPRITEBANK-GATEART blockade=sprite
  trap=sprite + SPRITEBANK-OK rc 0. Tiers proven through the shipped
  defense_obj.upgrade(); sheets pinned by RESOURCE PATH (child found and fixed
  a false-green oracle assert — lesson stored in fleet memory).
- python3 -m pytest -q -> 222 passed in 152.37s (child baseline 222 before/after).
- tools/check_hygiene.py -> 0 hit(s).
- Fixtures byte-identical: eafe3932… / 5e37c4b0… (measured again this session).

## Mechanism read
sprite_bank.gd: texture_for(id, tier=1); TIER_TEXTURES for the 3 shooters, T1
fallback on unknown tier (bombard T3 honestly reads its T1 sheet — no T3 sheet
committed, so no fake art); gate_blockade/barbed_snare now sprite-backed;
warden_breaker stays mesh. defense_obj refreshes the visual once in the
upgrade() leg (same slot, remove+add+free) — one bank, three callers, no
second render path, 1-arg call shape intact.

## DoD rows (card 11520 brief)
1. (id,tier)-aware bank, fallback, blockade/snare exit greybox — probe + read. VERIFIED.
2. upgrade repaint via shipped leg — probe TIER rows through defense_obj.upgrade(). VERIFIED.
3. probe extended, old GREYBOX row retired honestly, planted-red RED beside green
   (child transcripts W12-probe-{green,red}.log committed). VERIFIED.
4. gates 222/222 + hygiene 0 + fixtures byte-identical — re-run by me. VERIFIED.
5. LEDGER V1.1-b row in the commit + this evidence. VERIFIED.

VERIFY_EXIT=0
