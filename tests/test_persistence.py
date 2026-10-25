"""W4 persistence gate (MC 11274.1.11 / card 11302).

Engine legs (BN4/I5): save_probe runs as TWO SEPARATE SUBPROCESSES —
invocation A mutates meta through the C13 mutators and asserts the ack,
invocation B (fresh process) reloads the SAME save file and checks the
meta round-trip incl. materials_json (F2-6). I5's byte-equality is the
FILE leg (load_save dict vs expected, byte-strict); the state leg
(from_save -> to_save) compares the *_json blobs semantically because
Godot JSON.parse float-normalizes every number — a named limitation
recorded in the probe header. The two processes
share the file via the XDG_DATA_HOME redirection the ARCHITECTURE
save_probe row names for the desktop leg; a corrupt-save leg proves the
C6 quarantine + I5 fresh-start rule.

Source-truth legs (number tier, no engine): every C13 mutator name in
godot/scripts/game_state.gd carries `mutated.emit` in its body (incl. the
BN2-named `spend_gold`); the C6 key list written by godot/scripts/
save_store.gd EQUALS the pinned list exactly — a DIFFERENT key list is a
test failure, and the pinned [meta2] list carries NO saved_ack row (C13
mirrors the in-memory write_seq into C5 saved_ack instead).

Readings recorded on the card trail (pinned table over brief paraphrase,
precedent MC 11274.1.9/.10):
- GWSaveStore API per the pinned Modules row: write(d:Dictionary)->bool,
  load_save()->Dictionary ({} = missing/corrupt/foreign), var write_seq;
  the brief's read()->dict|null paraphrase is not the pinned name.
- GWBridge is RefCounted per its pinned row (brief's Node pump superseded).
- Wiring is signal-to-callable via GWCompose.StateCommit.commit — the
  compose_test lambda form VERIFIED to leak a RefCounted cycle at exit.
"""

import os
import re
import subprocess
import sys
import tempfile

import pytest

import conftest
from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: comment/string blanking)

GAME_STATE = repo_path("godot", "scripts", "game_state.gd")
SAVE_STORE = repo_path("godot", "scripts", "save_store.gd")
PROBE = "res://sim/save_probe.gd"

# C6 pinned write surface: (section-literal, key) pairs, hero sections
# written as "hero:" + id. This set IS the contract — anything else fails.
C6_PAIRS = {
    ("meta", "schema_version"), ("meta", "asc_earned"),
    ("meta", "asc_spent_json"), ("hero:", "level"), ("hero:", "xp"),
    ("bank", "items_json"), ("meta2", "gold"), ("meta2", "deck_json"),
    ("meta2", "completed_json"), ("meta2", "materials_json"),
}

C13_MUTATORS = ["add_hero_xp", "spend_asc", "bank_add", "equip",
                "add_gold", "spend_gold", "add_material",
                "consume_material", "set_deck", "complete_mission"]

C5_KEYS = ["schema", "phase", "mission_id", "difficulty", "wave",
          "phase_kind", "wave_remaining", "alive", "green", "green_cap",
          "blue", "blue_max", "hero_id", "hero_hp", "hero_hp_max", "cores",
          "defenses", "defense_cap", "relics_assigned", "deck",
          "asc_points", "bank_count", "gold", "loot_pending", "equipped",
          "outcome", "boss_hp", "saved_ack", "t"]


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def run_probe(mode, data_home):
    """One fresh-process probe invocation (BN4: never two modes at once)."""
    env = dict(os.environ, XDG_DATA_HOME=str(data_home))
    return subprocess.run(
        [conftest.GODOT, "--headless", "--path", repo_path("godot"),
         "-s", PROBE, "--", mode],
        capture_output=True, text=True, timeout=300, env=env)


def save_file(data_home):
    return (os.path.join(str(data_home), "godot", "app_userdata",
                         "Gatewardens", "gatewardens.cfg"))


# ---------- engine legs: fresh-process A -> B round trip ----------

def test_save_probe_A_then_B_fresh_processes_roundtrip():
    if not os.path.exists(conftest.GODOT):
        pytest.skip("Godot binary not installed")
    conftest.ensure_class_cache()
    with tempfile.TemporaryDirectory() as home:
        a = run_probe("write", home)
        assert a.returncode == 0, "A rc=%d\n%s\n%s" % (
            a.returncode, a.stdout, a.stderr)
        acks = [int(n) for n in re.findall(
            r"SAVE-PROBE-A ack=(\d+)", a.stdout)]
        assert len(acks) >= 10, "C13 mutator acks missing: %r" % acks
        assert acks == sorted(set(acks)) and acks[0] >= 1, \
            "ack rows not strictly growing per mutator: %r" % acks
        final = re.search(r"SAVE-PROBE-A saved_ack=(\d+)", a.stdout)
        assert final, a.stdout
        # Monotonicity across the SECOND (post-row) writes: the refused
        # spend/consume negatives still emit per the pinned contract, so
        # the final ack sits strictly above the last emitted ack row.
        assert int(final.group(1)) > acks[-1], \
            "ack did not keep growing across the second write: %s <= %s" \
            % (final.group(1), acks[-1])
        assert "SAVE-PROBE-A negative=OK" in a.stdout, a.stdout
        assert os.path.isfile(save_file(home)), "write leg produced no file"

        # Invocation B: FRESH process, same file (BN4 — the whole point).
        b = run_probe("read", home)
        assert b.returncode == 0, "B rc=%d\n%s\n%s" % (
            b.returncode, b.stdout, b.stderr)
        assert "SAVE-PROBE-B roundtrip=OK" in b.stdout, b.stdout
        detail = re.search(r'SAVE-PROBE-B detail=(\{.*\})', b.stdout)
        assert detail and '"ok":true'.replace(" ", "") in \
            detail.group(1).replace(" ", ""), b.stdout


def test_corrupt_save_quarantines_and_fresh_starts_never_crashes():
    if not os.path.exists(conftest.GODOT):
        pytest.skip("Godot binary not installed")
    conftest.ensure_class_cache()
    with tempfile.TemporaryDirectory() as home:
        assert run_probe("write", home).returncode == 0
        path = save_file(home)
        # Leg 1 (I5, readable-but-garbage file): ConfigFile accepts the
        # file, every value defaults, the pinned schema guard fresh-starts
        # — B fails the round trip on default-vs-expected, NO crash.
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("]]not a ConfigFile[[ garbage")
        b = run_probe("read", home)
        assert b.returncode == 1, "garbage read must fail the round trip"
        assert "roundtrip=FAIL" in b.stdout, b.stdout
        # Leg 2 (C6, unreadable previous file): *.corrupt copy kept and
        # the fresh-start verdict is the no_save path.
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("]]not a ConfigFile[[ garbage")
        os.chmod(path, 0)
        try:
            b = run_probe("read", home)
            assert b.returncode == 1, "unreadable read must fail"
            assert "SAVE_LOAD_FAIL" in b.stderr, b.stderr
            assert "FAIL no_save" in b.stdout, b.stdout
            assert os.path.isfile(path + ".corrupt"), \
                "C6 quarantine copy (*.corrupt) missing"
        finally:
            os.chmod(path + ".corrupt", 0o600)


# ---------- source-truth legs (no engine) ----------

def _body(source, func):
    """Source lines of one func, up to the next top-level func/const block."""
    m = re.search(r"func %s\(.*?(?=\nfunc |\nstatic func |\nclass |\Z)"
                  % re.escape(func), source, re.S)
    assert m, "func %s missing" % func
    return m.group(0)


def test_signal_mutated_declared_and_every_c13_mutator_emits():
    code = hyg.blank_code(read(GAME_STATE), "gd")
    assert re.search(r"^signal mutated$", code, re.M), \
        "GWGameState must declare `signal mutated` (C13)"
    for name in C13_MUTATORS:
        body = _body(code, name)
        assert "mutated.emit()" in body, \
            "C13 mutator %s does not emit mutated" % name


def test_bn2_gold_mutator_is_named_spend_gold():
    code = hyg.blank_code(read(GAME_STATE), "gd")
    assert re.search(r"func spend_gold\(", code), \
        "BN2: the gold mutator must be named spend_gold"


def test_c6_key_list_is_exact_and_no_saved_ack_persisted():
    # The (section, key) grep runs on the RAW source: the pairs ARE string
    # literals, which blank_code would blank out. Comments carry no quoted
    # set_value("…") form, so no comment can forge a pair.
    code = read(SAVE_STORE)
    pairs = set(re.findall(
        r'set_value\(\s*"([^"]*)"[^,]*,\s*"([^"]+)"', code))
    assert pairs == C6_PAIRS, \
        "C6 key list differs from the pinned table: extra=%r missing=%r" % (
            pairs - C6_PAIRS, C6_PAIRS - pairs)
    # saved_ack is NOT a save field (pinned C6 [meta2] has no ack row;
    # C13 keeps it as the in-memory write_seq mirror into C5). Checked on
    # blanked code: the header comment names the ruling in prose.
    assert "saved_ack" not in hyg.blank_code(code, "gd"), \
        "save_store code must not persist saved_ack — pinned C6 has no key"


def test_c5_snapshot_carries_every_pinned_key():
    # Raw source again: the C5 keys are the dict-literal string keys.
    code = read(GAME_STATE)
    for key in C5_KEYS:
        assert '"%s":' % key in code, \
            "C5 key %r absent from snapshot_json" % key
