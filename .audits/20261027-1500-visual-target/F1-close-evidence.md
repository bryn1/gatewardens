PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/conftest.py => ^f57625ae279240e8aab582a6eb15bf4593d0997a46a22c7e5f91e12d8b65a334
PROBE: grep -c '"--path", repo_path("godot"), "--import"' /home/claudecode/Games/gatewardens/tests/conftest.py => ^1$
PROBE: grep -c 'VERIFY_EXIT=0' /home/claudecode/Games/gatewardens/.audits/20261027-1500-visual-target/F1-conftest-evidence.md => ^1$
PROBE: sha256sum /home/claudecode/Games/gatewardens/tests/fixtures/mission_gatefall_normal.jsonl => ^eafe3932f7d30898

# F1-close (MC 11517) — orchestrator close evidence

Child commits: 740d64c (fix, one line + docstring) + 83312c9 (evidence finalize),
author code (11517), coexistence with 11520 honored (explicit paths; the replay
side-effect is disclosed and harmless — attribution note kept on the trail).

## Measured BY THE ORCHESTRATOR this session
- diff read: ensure_class_cache now `[GODOT, "--headless", "--path", repo_path
  ("godot"), "--import"]`; fast path intact; smallest correct change.
- PRISTINE verification (the load-bearing leg), MY OWN clone:
  git clone /home/claudecode/Games/gatewardens -> /tmp/f1-verify @ 83312c9,
  bash tools/export_web.sh EXPORT_RC=0, then python3 -m pytest -q ->
  "222 passed in 156.32s". The class_cache-missing red class is GONE from a
  clean checkout. (Bare pytest without export is by-design module-skip/404 —
  the repo's documented fresh-checkout sequence is export-first; child's
  LEDGER row initially overclaimed bare-clone 222 and self-corrected in
  83312c9 — honest, kept visible.)
- Workspace re-run at the tree: child 222; orchestrator 222 at 11520 close.
- Fixtures byte-identical (eafe3932…). conftest sha pinned above.

## DoD (card 11517)
Fix in working form + pristine clone green via documented sequence + workspace
green + evidence VERIFY_EXIT=0. VERIFIED at the strongest level (clean clone,
orchestrator-executed).

VERIFY_EXIT=0
