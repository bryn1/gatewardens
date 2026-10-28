PROBE: grep -c VERIFY_EXIT=0 /home/claudecode/Games/gatewardens/.audits/20261028-1500-v12-plan/F3-wave.log => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/test_relic_negatives.py => ^4df787b3136ea5aac838d9d5c03133fa3bdbec4665486b7400a539d51ddf8639
PROBE: grep -c F3 /home/claudecode/Games/gatewardens/LEDGER.md => ^2$

# 11609 close — F3 relic-assign negative tests (v1.2 W1)

Commit 860447b (author coder (11609), pathspec-only: tests/test_relic_negatives.py 353 L + LEDGER row + wave log).
TESTS-ONLY per plan F3: 5 legs (DUP double-assign, SELL-return, STALE dead-uid, REUSE, IDEM) GREEN on the
SHIPPED implementation — plan's "already correct" branch holds, NO P1 finding. Measured truths pinned: sell
refund of fresh T1+damage-relic = EXACTLY 0 per pinned formula; dead-uid assign refused "uid" rc0 + EMPTY stderr.
Planted-red BOTH legs in wave log (taken-guard removed -> DUP RED; sell-skips-remove_at -> SELL/STALE RED),
reverts byte-verified. ORCHESTRATOR re-measured at the combined W1 tree: pytest 229 passed 165.69s (my own
run), hygiene 0 hits, git diff --stat tests/fixtures/ EMPTY.

VERIFY_EXIT=0
