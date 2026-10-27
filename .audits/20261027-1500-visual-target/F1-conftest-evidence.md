# F-1 conftest asset-import fix — evidence (MC card 11517 / workspace 11274, F-1 from MC 11466)

Date: 2026-10-27 (UTC). Seat: `code` subagent. Godot: `/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64` (4.7.2 stable).

## Finding (root cause)

`tests/conftest.py` `ensure_class_cache()` ran `godot --headless --import <path>` —
the positional form is a NO-OP in Godot 4.7.2: it exits 0, writes no `.godot/` and no
`.import`/`.ctex` sidecars. The imported shared checkout stayed green because its
editor cache was already warm; any editor-cache-free copy of the repo goes RED
(class_cache missing). The working form is `godot --headless --path <dir> --import`
(the form `run_probe_script` in the same file already uses).

## Fix (one focused change)

`tests/conftest.py` — one command line + its docstring; cache-hit fast path and every
other line untouched:

```diff
-    """`godot --headless --import godot/` exactly once per session (F14)."""
+    """`godot --headless --path godot/ --import` exactly once per session
+    (F14). The positional `--import <path>` form is a no-op in 4.7.2:
+    it exits 0 without writing .godot/ or .import sidecars."""
     global _class_cache_ready
     if _class_cache_ready:
         return
     proc = subprocess.run(
-        [GODOT, "--headless", "--import", repo_path("godot")],
+        [GODOT, "--headless", "--path", repo_path("godot"), "--import"],
```

## (a) PRISTINE clone — no editor cache — full suite

Command (fresh `git clone` of the repo to /tmp, then the suite):

```
$ git clone /home/claudecode/Games/gatewardens <clone-path>
$ cd <clone-path> && python3 -m pytest -q
```

Clone path: **CLONE_PATH_PLACEHOLDER** — transcript (full `pytest -q`):

```
CLONE_TRANSCRIPT_PLACEHOLDER
```

## (b) Normal workspace re-run — full suite

```
$ cd /home/claudecode/Games/gatewardens && python3 -m pytest -q
```

Transcript (full `pytest -q`):

```
WORKSPACE_TRANSCRIPT_PLACEHOLDER
```

## Concurrent-writer note (disclosed)

The first workspace pass during this session went 1 failed / 221 passed: a CONCURRENT
uncommitted edit from another card's work (MC 11520, `godot/scripts/sprite_bank.gd`)
was landing in the shared checkout while `ensure_class_cache` ran its first-ever real
import — the boot-probe leg raced the half-written file. The test passes alone
(`1 passed` for `tests/test_bridge_contract.py::test_boot_probe_boots_main_flow_headless`)
and the workspace re-run below is green with the same conftest fix. This card commits
ONLY `tests/conftest.py` + `LEDGER.md` + this evidence file; MC 11520's edits stay
untouched (orchestrator ratified 2026-10-27).

VERIFY_EXIT=VERIFY_PLACEHOLDER
