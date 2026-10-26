"""W11 golden-simulation gate (MC 11274.1.19 / card 11326).

tests/fixtures/mission_gatefall_normal.jsonl carries the C12 fixture
encoding: LINE 1 header {"schema","seed","map","difficulty"}, then
in-rows {"kind":"in","tick","act","args"} and committed expected
out-rows {"kind":"out","tick","ev",...,"checks":{...},"ok":true}; the
sim steps at the pinned DT (1.0/60.0); goldens regenerate only via
`sim_headless.gd -- --fixture <path> --regen` (the harness echoes the
raw authored header/in lines verbatim, since Godot JSON reads every
number as a float — an int 1 in the fixture would round-trip 1.0).

Laws exercised here (ledger/contract ids in sim_headless.gd comments):
 - E3: under `-s` the verdict is rc + EMPTY stderr (the engine banner
   goes to stdout; the compared stream is the JSON rows only).
 - C12: one canonical JSON object per row; JSON.stringify sorts keys,
   which is what makes the byte stream stable.
 - C13/E5: the run owns a temp user:// (XDG_DATA_HOME redirect, the
   save_probe idiom) — ack/write_seq mirror in the outcome row.
 - The pinned golden's win is the boss CONSUMED at the core on wave 11
   (a breach is not a kill, C12 step 4 death-only: no boss crystal);
   boss_neutralized + outcome_win + win_at_last_wave encode it.

Gate legs: (1) fresh replay of the committed fixture: rc 0, empty
stderr, every row ok:true, and the replayed out-row stream BYTE-EQUAL
(sha256 on both sides) to the committed rows; (2) two fresh runs are
byte-stable against each other; (3) mutation leg — one tampered byte
in a fixture copy (the seed digit) must NOT reproduce the golden.
"""

import hashlib
import json
import os

import conftest
from conftest import repo_path

SIM = "res://sim/sim_headless.gd"
FIXTURE = repo_path("tests", "fixtures", "mission_gatefall_normal.jsonl")


def _out_stream(stdout: str) -> str:
    """The compared byte stream: JSON row lines only (E3: the engine
    banner shares stdout and is not part of the golden)."""
    return "".join(l + "\n" for l in stdout.splitlines()
                   if l.startswith('{"') and '"kind"' in l
                   and '"kind":"in"' not in l
                   and '"schema"' not in l)


def _fixture_out_rows() -> str:
    with open(FIXTURE, encoding="utf-8") as fh:
        return "".join(l for l in fh if '"kind":"out"' in l)


def _replay(fixture: str, tmp_path_factory) -> "subprocess":  # noqa: F821
    # Each replay gets its own temp user:// (C13/E5 save writes land
    # there, never on a developer profile).
    data_home = tmp_path_factory.mktemp("gw-golden-user")
    return conftest.run_probe_script(SIM, ["--fixture", fixture],
                                     data_home=data_home)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_golden_fixture_shape():
    with open(FIXTURE, encoding="utf-8") as fh:
        lines = [l.rstrip("\n") for l in fh if l.strip() != ""]
    header = json.loads(lines[0])
    assert header == {"schema": 1, "seed": 11326, "map": "gatefall",
                      "difficulty": "normal"}
    n_in = n_out = 0
    for line in lines[1:]:
        row = json.loads(line)
        assert row["kind"] in ("in", "out")
        if row["kind"] == "in":
            n_in += 1
            assert isinstance(row["tick"], int)
            assert row["act"] in ("input", "place", "upgrade", "repair",
                                  "sell", "assign", "unassign", "hotswap")
        else:
            n_out += 1
            assert row["ok"] is True
    assert n_in > 0 and n_out > 0
    assert json.loads(lines[-1])["ev"] == "outcome"


def test_golden_replay_matches_committed(class_cache, tmp_path_factory):
    proc = _replay(FIXTURE, tmp_path_factory)
    assert proc.stderr == "", "E3: stderr is the verdict channel"
    assert proc.returncode == 0, "golden replay must exit 0"
    stream = _out_stream(proc.stdout)
    rows = [json.loads(l) for l in stream.splitlines()]
    assert rows and all(r["ok"] is True for r in rows)
    committed = _fixture_out_rows()
    assert _sha(stream) == _sha(committed), (
        "replayed out-rows diverge from committed: %s != %s"
        % (_sha(stream), _sha(committed)))


def test_golden_is_stable_across_runs(class_cache, tmp_path_factory):
    a = _out_stream(_replay(FIXTURE, tmp_path_factory).stdout)
    b = _out_stream(_replay(FIXTURE, tmp_path_factory).stdout)
    assert a != "" and _sha(a) == _sha(b)


def test_golden_red_on_tampered_fixture(class_cache, tmp_path_factory):
    """Mutation leg (verify-discipline: a gate that never went RED is
    not a gate): one flipped byte — the last seed digit — must not
    reproduce the golden (RNG-shaped loot/crit stream shifts)."""
    with open(FIXTURE, encoding="utf-8") as fh:
        text = fh.read()
    assert '"seed":11326' in text
    tampered = text.replace('"seed":11326', '"seed":11325', 1)
    assert tampered != text
    bad = tmp_path_factory.mktemp("gw-golden-tamper") / "fixture.jsonl"
    bad.write_text(tampered, encoding="utf-8")
    proc = _replay(str(bad), tmp_path_factory)
    stream = _out_stream(proc.stdout)
    diverged = (proc.returncode != 0 or proc.stderr != ""
                or stream != _fixture_out_rows())
    assert diverged, "tampered fixture still reproduced the golden"
