PROBE: stat -c %s /home/claudecode/Games/gatewardens/.audits/20261025-1045-clean-code/W17d-evidence.md => ^[1-9][0-9]{3,}$
=== W17d close evidence (orchestrator re-ran; runtime leg = orchestrator re-journey NOW after re-export) ===
stat W17d-evidence.md => 7486
orchestrator re-run: pytest 206 passed exit 0; hygiene 0 hits; commit 940ecc6 (author code (11396))
ROOT CAUSE DEEPER THAN BRIEF: JavaScriptBridge.get_object = Godot 3 API ABSENT in 4.7.2 (ClassDB probe on shipped wasm) -> host null -> on_key never assigned; fix get_interface(gwHost)+property-path assignment host.on_key=_js_relay; E1 anchor proven load-bearing
CHILD CORRECTED ORCHESTRATOR PREMISES x2 by engine measurement: no .dispatch on the proxy (zero wasm string hits), synchronous null return (no promise) - gates reflect MEASURED truth; comment-carried token false-green in own gate caught+fixed (code-line exact match)
engine-level browser proof shipped (probe=exact fix code + shipped shell, all 3 dispatch routes reach _on_js_key); served runtime = orchestrator journey leg now
VERIFY_EXIT=0
