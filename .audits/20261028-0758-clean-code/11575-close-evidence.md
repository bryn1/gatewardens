PROBE: grep -c VERIFY_EXIT=0 /home/claudecode/Games/gatewardens/.audits/20261028-0758-clean-code/W1-wave.log => ^1$
PROBE: grep -c VERIFY_EXIT=0 /home/claudecode/Games/gatewardens/.audits/20261028-0758-clean-code/W2-wave.log => ^1$
PROBE: grep -c VERIFY_EXIT=0 /home/claudecode/Games/gatewardens/.audits/20261028-0758-clean-code/W3-wave.log => ^1$
PROBE: grep -c v11_boss_shot /home/claudecode/Games/gatewardens/docs/ARCHITECTURE.md => ^3$
PROBE: grep -c "bombard=T3" /home/claudecode/Games/gatewardens/godot/sim/v11_sprite_probe.gd => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898565664341697a32f20ecda7458d379be65b668bf2d6f3912

# 11575 close — clean-code refactor run (W1-W3 over FINDINGS.md)

Base: audit 11574 (verified). Waves, each = one code child, files-disjoint, sequenced:
- W1 921c687 (P2/P3): conftest engine-leg timeout 300->900s (SZ-1; margin ~2.4x the audit's measured
  6m10s leg), fx_director -> ONE sprite_bank.make_sprite factory (D-1; formulas verified identical
  before merge, fx ids absent from TIER_TEXTURES = pure reuse), CR-2 comment rewords. 218->217 LOC fx.
- W2 0ffb086 (P1 CR-1): committed-but-unwired bombard T3 skin wired into TIER_TEXTURES; header claim
  rewritten to truth; doc sweep (53 greybox hits, none falsified, RELEASE_NOTES history untouched).
  New probe leg 3c SPRITEBANK-TIER3 path-pinned + planted-RED proven (rc=1 removing the entry, revert
  green). Orchestrator re-ran probe: SPRITEBANK-TIER3 bombard=T3.
- W3 5304d87 (DC-1/KC-1): docs/ARCHITECTURE.md §Verification kits homes the orphan boss-shot kit
  (grep 0 -> 3 hits; kit unchanged, ran green from home); v11_shot3 git-mv'd to sim/archive/ with
  SUPERSEDED header (R status, byte-identical body), parse rc=0 + declared-command green from new home.
ZERO behavior change law HELD at every wave (orchestrator re-measured independently at each):
golden fixtures byte-identical (eafe3932/5e37c4b0), pytest 222 passed re-run by the closing seat at
W1 tree (168.97s), W2 tree (164.68s) AND W3 tree (162.91s), hygiene 0 hits at every wave,
zero sim/sim_*.gd logic modules touched in any wave (git show --stat).
Open rows by design: W4 = owner watch (mission.gd AT 400, depth 12 — no card needs it past; split
rides its own wave ONLY when some card needs to grow it). Honest limits per wave in wave logs.

VERIFY_EXIT=0
