"""G8 first-session coach banner gate (MC 11692 / V121-PLAN §G8, Rev 2).

Two tiers, one idiom per repo (test_hud / test_mission_smoke precedent):
- ENGINE: run godot/sim/hud_coach_probe.gd under `-s` over an isolated
  user://. The probe boots the REAL mission scene through mission.setup —
  the PRODUCTION mount order (PhaseController.setup before the HUD mount,
  mission.gd:153 -> :168-171) — so the BOOT row proves the bootstrap path
  (Rev 2/DA A2: a connect can never see the wave-0 build edge). Rows:
  the line is VISIBLE at build w0, SWITCHES at the combat edge, the build
  w1 telegraph line shows (and HOLDS), waves >= 2 are SILENT, and a win
  planted during wave-0 combat still reads VICTORY (outcome > coach —
  the negative priority leg). EMPTY stderr, one pinned seed 11274.
- SOURCE TRUTH: the phase_changed connect is the ONLY new signal wiring;
  the bootstrap line rides inside setup(); and the three copy strings are
  the plan's VERBATIM (copy is contract — strings, so I2 is untouched).
Planted reds: bootstrap removal -> the BOOT source gate goes RED; the
coach-beats-outcome inversion -> the priority source gate goes RED (in
pytest, test_hud idiom). The two ENGINE planted-red transcripts (same
mutations run against the real probe in an isolated fa131fc tree) ride
.audits/20261029-2100-v121-plan/G8-wave.log beside the green run.
test_hud.py is the I4 gate and stays byte-UNCHANGED.
"""

import re
import sys

import conftest
from conftest import repo_path

sys.path.insert(0, repo_path("tools"))
import check_hygiene as hyg  # noqa: E402  (reuse: blank_code)

PROBE = "res://sim/hud_coach_probe.gd"
HUD_GD = repo_path("godot", "scripts", "hud.gd")

# The plan §G8 copy strings, VERBATIM (Rev 2, em-dash included).
COPY_BUILD = ("BUILD: tower buttons on the right panel — "
              "click arms, click again places")
COPY_FIGHT = "FIGHT: both mouse buttons hit, F1-F3 swap heroes"
COPY_TELEGRAPH = "NEXT WAVE: watch the gate billboards"


def _raw():
    with open(HUD_GD, encoding="utf-8") as fh:
        return fh.read()


def _code():
    return hyg.blank_code(_raw(), "gd")


def _row(out, tag):
    hits = [line for line in out.splitlines() if line.startswith(tag + " ")]
    assert len(hits) == 1, "%s row count=%d\n%s" % (tag, len(hits), out)
    head = hits[0].split(" text=")[0]
    fields = dict(kv.split("=", 1) for kv in head.split(" ")[1:])
    if " text=" in hits[0]:
        fields["text"] = hits[0].split(" text=", 1)[1]
    return fields


def _rows(out, tag):
    return [line for line in out.splitlines() if line.startswith(tag + " ")]


def _kv(line):
    head = line.split(" text=")[0]
    fields = dict(kv.split("=", 1) for kv in head.split(" ")[1:])
    if " text=" in line:
        fields["text"] = line.split(" text=", 1)[1]
    else:
        fields["text"] = ""
    return fields


# ---------- engine tier: production boot under -s ----------

def test_coach_engine_leg(tmp_path, class_cache):
    proc = conftest.run_probe_script(PROBE, (), tmp_path)
    assert proc.returncode == 0, \
        "probe rc=%d\nOUT:%s\nERR:%s" % (proc.returncode, proc.stdout,
                                         proc.stderr)
    assert "GWCOACH-OK" in proc.stdout, proc.stdout
    assert proc.stderr == "", \
        "-s probe stderr must be EMPTY (W4 ruling):\n%s" % proc.stderr
    out = proc.stdout

    # BOOT leg: production mount order, bootstrap path — the wave-0
    # build line is VISIBLE (text + shipped banner_shown() read-back).
    boot = _row(out, "GWCOACH-BOOT")
    assert boot["text"] == COPY_BUILD and boot["shown"] == "1", boot

    # The line SWITCHES at the combat edge (signal route, not bootstrap).
    combat = _row(out, "GWCOACH-COMBAT")
    assert combat["text"] == COPY_FIGHT and combat["shown"] == "1", combat

    # Build w1: the telegraph line shows once and HOLDS (a later refresh
    # inside the same build cannot change it).
    w1 = _row(out, "GWCOACH-W1BUILD")
    assert w1["text"] == COPY_TELEGRAPH and w1["shown"] == "1", w1
    hold = _row(out, "GWCOACH-W1HOLD")
    assert hold["text"] == COPY_TELEGRAPH, hold

    # Silence rows: w1 combat (telegraph REPLACED by nothing), then
    # nothing on waves >= 2 (build + combat).
    silent = [_kv(line) for line in _rows(out, "GWCOACH-SILENT")]
    assert [(s["wave"], s["phase"]) for s in silent] == \
        [("1", "combat"), ("2", "build"), ("2", "combat")], silent
    for s in silent:
        assert s["text"] == "" and s["shown"] == "0", s

    # Priority NEGATIVE leg: win during wave-0 combat -> VICTORY, not
    # the (live, coach_fight-verified) coach line.
    pri = _row(out, "GWCOACH-PRIORITY")
    assert pri["outcome"] == "win" and pri["text"] == "VICTORY", pri
    assert pri["shown"] == "1", pri

    # Row ORDER honors the run (the coach reflects state, never leads it).
    lines = out.splitlines()
    idx = {tag: min(i for i, ln in enumerate(lines)
                    if ln.startswith(tag)) for tag in (
        "GWCOACH-BOOT", "GWCOACH-COMBAT", "GWCOACH-W1BUILD",
        "GWCOACH-W1HOLD", "GWCOACH-SILENT", "GWCOACH-PRIORITY",
        "GWCOACH-OK")}
    assert idx["GWCOACH-BOOT"] < idx["GWCOACH-COMBAT"] < \
        idx["GWCOACH-W1BUILD"] < idx["GWCOACH-W1HOLD"] < \
        idx["GWCOACH-SILENT"] < idx["GWCOACH-PRIORITY"] < \
        idx["GWCOACH-OK"], idx


# ---------- source truth ----------

def test_coach_copy_strings_match_the_plan():
    raw = _raw()  # RAW: blank_code blanks the very strings this gate sees
    for const, want in (("COACH_BUILD_W0", COPY_BUILD),
                        ("COACH_FIGHT_W0", COPY_FIGHT),
                        ("COACH_TELEGRAPH_W1", COPY_TELEGRAPH)):
        m = re.search(r'const %s := "(.*)"' % const, raw)
        assert m is not None, "coach const %s missing from hud.gd" % const
        assert m.group(1) == want, \
            "%s copy drifted from the plan:\n got %r\nwant %r" \
            % (const, m.group(1), want)


def _setup_body(code):
    m = re.search(r"func setup\(mission\)[\s\S]*?\n\n", code)
    assert m is not None, "the setup(mission) hook vanished"
    return m.group(0)


def _bootstrap_ok(code):
    # The G8 bootstrap: a local assign from the public reads ONLY.
    return "_coach = _coach_for(String(m.phase_kind), int(m.wave))" \
        in _setup_body(code)


def test_coach_bootstraps_inside_setup():
    assert _bootstrap_ok(_code()), \
        "hud.setup does not bootstrap the coach — the wave-0 build edge " \
        "fires before the HUD exists and would be lost (DA A2)"


def test_phase_changed_is_the_only_new_signal_wiring():
    raw = _raw()
    assert raw.count(".connect(") == 1, \
        "hud.gd wired more than the one existing signal"
    # The QUOTED $"../X" node-path form is mandatory for `..` segments
    # (the unquoted $../X is a GDScript PARSE ERROR — VERIFIED 4.7.2 via
    # --check-only, which is what cost this card its first two gate runs).
    assert '$"../PhaseController".phase_changed.connect(_on_phase_changed)' \
        in raw, "the later edges must ride the EXISTING phase_changed"


# ---------- planted reds: every gate proves it can fail ----------

def test_planted_red_bootstrap_removal_goes_red():
    planted = _code().replace(
        "\t_coach = _coach_for(String(m.phase_kind), int(m.wave))\n",
        "", 1)
    assert planted != _code(), "plant missed"
    assert not _bootstrap_ok(planted), \
        "planted-red: BOOT source gate stayed green without the bootstrap"


def test_planted_red_priority_inversion_goes_red():
    # Coach-beats-outcome inversion: the coach return is hoisted ABOVE
    # the outcome branch. The priority gate reads: inside banner_text the
    # VICTORY/DEFEAT return must come BEFORE the _coach return. RAW text
    # (blank_code blanks the very "VICTORY" string this gate locates;
    # the banner_text body carries neither comment trap — verified at
    # authoring).
    def _first_returns(body):
        vic = body.find('return "VICTORY"')
        coach = body.find("return _coach")
        assert vic != -1 and coach != -1, "banner_text shape vanished"
        return vic < coach

    raw = _raw()
    m = re.search(r"func banner_text\(\)[\s\S]*?\n\n", raw)
    assert m is not None and _first_returns(m.group(0)), \
        "baseline priority broken — the real gate is vacuous"
    planted = raw.replace(
        m.group(0),
        'func banner_text() -> String:\n\tif _coach != "":\n'
        '\t\treturn _coach\n\tif m == null:\n\t\treturn ""\n'
        '\tif m.outcome != null:\n\t\treturn "VICTORY" if '
        'String(m.outcome) == "win" else "DEFEAT"\n\treturn _coach\n\n', 1)
    m2 = re.search(r"func banner_text\(\)[\s\S]*?\n\n", planted)
    assert not _first_returns(m2.group(0)), \
        "planted-red: priority gate stayed green with coach beating outcome"
