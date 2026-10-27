# F-1 conftest asset-import fix — evidence (MC card 11517 / workspace 11274, F-1 from MC 11466)

Date: 2026-10-27 (UTC). Seat: `code` subagent. Godot: `/home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64` (4.7.2 stable).

## Finding (root cause)

`tests/conftest.py` `ensure_class_cache()` ran `godot --headless --import <path>` —
the positional form is a NO-OP in Godot 4.7.2: it exits 0, writes no `.godot/` and no
`.import`/`.ctex` sidecars. The imported shared checkout stayed green because its
editor cache was already warm; any editor-cache-free copy of the repo went RED
(class_cache missing, the 10-11-failure class). The working form is
`godot --headless --path <dir> --import` (the form `run_probe_script` in the same
file already uses).

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

Clone path: **/tmp/f1-clone** — `git clone /home/claudecode/Games/gatewardens /tmp/f1-clone`
of the fix commit `740d64c` (the clone proof must run against a COMMITTED fix, so the
evidence body finalizes in a follow-up commit of evidence/LEDGER wording only — zero
test-relevant files; amending `740d64c` was impossible because the concurrent card
11520 had already committed `0be1f68` on top and an amend would have rewritten its
history).

### Bare clone, suite as-is (first run after `git clone`, no editor cache, no export)

```
1 failed, 216 passed, 1 skipped in 153.73s (0:02:33)
FAILED tests/test_scaffold.py::test_server_serves_placeholder_on_ephemeral_port
```

The class_cache-missing class (the original 10-11 failures) is GONE — fixed by the
one-line conftest change (the run itself generated `.godot/` + the batch-2
`.import` sidecars). The ONE remaining failure and the ONE skip are the
PRE-EXISTING build-side export class, untouched by F-1 and by design (W12 law,
.gitignore): `static/` carries the gitignored web export only, so
`test_scaffold`'s "/" request legitimately 404s and `test_served.py` (5 tests)
module-SKIPS with the explicit reason naming the fix — run `bash tools/export_web.sh`
first. The W12 DoD's own documented fresh-checkout procedure is export-then-suite;
run verbatim below.

### Fresh clone + the documented repro sequence (export first, then the suite)

```
$ cd /tmp/f1-clone && bash tools/export_web.sh && python3 -m pytest -q
```

export: `EXPORT_RC=0` (web templates 4.7.2.stable installed). Full `pytest -q`
transcript:

```
........................................................................ [ 32%]
........................................................................ [ 64%]
........................................................................ [ 97%]
......                                                                   [100%]
222 passed in 152.87s (0:02:32)
```

## (b) Normal workspace re-run — full suite

```
$ cd /home/claudecode/Games/gatewardens && python3 -m pytest -q
```

Full `pytest -q` transcript:

```
........................................................................ [ 32%]
........................................................................ [ 64%]
........................................................................ [ 97%]
......                                                                   [100%]
222 passed in 153.91s (0:02:33)
```

## Concurrent-writer note (disclosed)

The first workspace pass during this session went 1 failed / 221 passed: a CONCURRENT
uncommitted edit from another card's work (MC 11520, `godot/scripts/sprite_bank.gd`)
was landing in the shared checkout while `ensure_class_cache` ran its first-ever real
import — the boot-probe leg raced the half-written file. The test passes alone
(`1 passed` for `tests/test_bridge_contract.py::test_boot_probe_boots_main_flow_headless`)
and the workspace re-run above is green with the same conftest fix. This card commits
ONLY `tests/conftest.py` + `LEDGER.md` + this evidence file; MC 11520's edits stay
untouched (orchestrator ratified 2026-10-27). The 8 untracked batch-2
`.import` sidecars in the shared checkout are test-runtime byproducts of this fix
working as intended (same 8 appear in the clone); committing them belongs to V1.1-b,
not F-1.

VERIFY_EXIT=0
