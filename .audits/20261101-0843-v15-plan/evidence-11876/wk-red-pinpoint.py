# W-K leg 1 (MC 11876): evaluate the OLD test_kit_fx.py asserts INDIVIDUALLY
# against the new tree's probe output (pytest short-circuits at rc; the
# re-pin-proof leg needs the per-leg verdict). Old probe body, old assert
# expressions — verbatim from tests/test_kit_fx.py at HEAD.
import sys, tempfile
sys.path.insert(0, "tests")
import test_kit_fx as old
from pathlib import Path

with tempfile.TemporaryDirectory() as td:
    proc = old._run_probe(Path(td), "/home/claudecode/Games/.tools/godot/"
                                "Godot_v4.7.2-stable_linux.x86_64")
out = proc.stdout
print("PROBE rc=%d stderr=%r" % (proc.returncode, proc.stderr))
boot = old._only(out, "KF-BOOT")
pres = old._only(out, "KF-PRESENT")
finding = [ln for ln in out.splitlines() if ln.startswith("KF-FINDING ")]
checks = [
    # old file :384-385
    ("KF-PRESENT live_after_assign == 0", pres["live_after_assign"] == "0"),
    # old file :386
    ("KF-PRESENT live_after_pump == 0", pres["live_after_pump"] == "0"),
    # old file :387
    ("KF-PRESENT swapped == 0 and parented == 1",
     pres["swapped"] == "0" and pres["parented"] == "1"),
    # old file :388
    ("KF-PRESENT sparks_delta == 0", pres["sparks_delta"] == "0"),
    # old file :389
    ("KF-PRESENT ack unchanged", int(pres["ack"]) == int(boot["ack"])),
    # old file :391-395 exact string
    ("KF-FINDING exact NONE string",
     finding == ["KF-FINDING kit_presentation=NONE kit_fx_delta=0 "
                 "kit_live_after_pump=0 kit_node_changed=0"]),
]
red = 0
for name, ok in checks:
    print(("GREEN  " if ok else "RED    ") + name)
    red += 0 if ok else 1
print("KF-PRESENT leg verdict: %s" % ("RED" if any(not ok for n, ok in checks[:5]) else "GREEN"))
print("RED count: %d" % red)
