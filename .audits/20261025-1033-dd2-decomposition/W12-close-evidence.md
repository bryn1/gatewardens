PROBE: stat -c %s /home/claudecode/Games/gatewardens/tests/test_served.py => ^[1-9][0-9]{2,}$
=== W12 close evidence (orchestrator independently re-ran) ===
stat test_served.py => 6119
orchestrator re-run 2026-10-26: pytest => 180 passed exit 0 (test_served GREEN not skipped, export present); hygiene => 0 hits; commit da64196 (author code (11331))
repro VERIFIED: 9-file set + index sha 2d122612 identical A/B (measured stronger: all nine byte-identical); served contract incl token-substitution + parsed-asset 200s + JSON 404; planted dead-shell RED proof; no static artifacts committed (static/.gitkeep only)
DECLARED deviations accepted: check_hygiene.py ceiling-scope one-hunk fix (gate had diverged from its own header + pinned row; red case measured) + README build/serve one-liner; server untouched
DOC-SYNC by closing seat: ARCHITECTURE static/ lines rewritten (committed -> gitignored; 'web export x2' = reproducibility passes, not artifact commitment) — retired claim removed same commit per contradicted-finding law
VERIFY_EXIT=0
