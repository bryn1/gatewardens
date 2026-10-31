"""v1.4 P9 hygiene POSITIVE CONTROLS (MC 11838 — F-1, routed from P3 §5c).

The P3 mutation pass (P3-wave.log §5b/§5c): the in-process hygiene universe
asserted ABSENCE only — the shipped corpus is clean by design, so a blank_code
that misfires, empties itself or skips a comment family stays GREEN, and walk
returning NOTHING stays GREEN (165/173 hygiene survivors, condition-inversions
among them: walk 2/7/12, blank_code 15-23, G-STRSCAN/G-PY clusters). This file
is the POSITIVE CONTROL: every core detector the module exposes gets crafted
input that MUST fire it, asserting the expected shape — blank_code per family
(gd #, //, /* */, comment-at-EOF, escape-in-string, newline keep; py triple
quote; js backtick + gd pass-through; cfg ';'; html '<!--'), words, the
tripwire in ALL THREE modes (identifier / word / phrase, with the negatives
that keep each mode honest), literal_violations, walk (coverage count > 0 on
a planted tmp tree, ext case, SKIP_DIRS), rel, read (non-UTF-8 replace), the
BARE_RAND regex, and main() driven over a planted tmp repo: every error class
fires, the BN1 comment rule CANNOT trip, soft notes fire.

Absence legs stay (the shipped tree must be 0 hits and the scan universe must
be non-empty) — this file ADDS the firing half, it never removes the calm one.

ONE MECHANISM: every leg imports and calls the gate's OWN functions (the same
in-process idiom test_purity/test_bridge_contract ride — sys.path + import),
no copy of any predicate, no new production mechanism. GW_HYGIENE_MUTANT_DIR
is a TEST-ONLY sys.path shim (importlib load of a scratch COPY of the gate)
used solely to PROVE these legs go RED against inverted detector predicates —
the P3 survivors re-run live; the repo copy is byte-untouched (card DoD).
"""

import os
import sys

import conftest
from conftest import repo_path

_MUTANT_DIR = os.environ.get("GW_HYGIENE_MUTANT_DIR", "")
if _MUTANT_DIR:
    # Mutation-proof seam (tests only): load the scratch COPY of the gate by
    # path so the RED transcripts can be quoted; default path unchanged.
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "check_hygiene_mutant",
        os.path.join(_MUTANT_DIR, "check_hygiene.py"))
    hyg = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(hyg)
else:
    sys.path.insert(0, repo_path("tools"))
    import check_hygiene as hyg  # noqa: E402  (reuse: the gate's own functions)

I1_DIRS = ("godot", "server", "static", "tools", "tests")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


# ---------- blank_code: gd family (the F-1 named fixture set) ----------

def test_gd_hash_comment_blanks_to_eol_lines_kept():
    text = 'var x = 1  # note about gems\nvar y = 2\n'
    out = hyg.blank_code(text, "gd")
    assert "gems" not in out
    assert "var x = 1" in out and "var y = 2" in out
    assert len(out) == len(text)                      # G-SPINE: nothing lost/added
    assert out.count("\n") == text.count("\n")         # line numbers stay true
    first = out.split("\n")[0]
    assert first.rstrip() == "var x = 1"               # code prefix intact,
    assert first == text.split("\n")[0].split("#")[0] + \
        " " * (len(text.split("\n")[0]) - len(text.split("\n")[0].split("#")[0]))


def test_gd_double_slash_comment_blanked():
    text = 'var x = 1  // cash_store here\nvar y = 2\n'
    out = hyg.blank_code(text, "gd")
    assert "cash" not in out and "store" not in out
    assert "var y = 2" in out and len(out) == len(text)


def test_gd_line_comment_pair_ending_text_is_blanked():
    # P3 G-NXT-IDX (blank_code 9/12): the // pair is observable only when it
    # ENDS the text — crafted fixture per the F-1 reading.
    text = "var x = 1 //"
    out = hyg.blank_code(text, "gd")
    assert "/" not in out
    assert out == "var x = 1   "


def test_gd_block_comment_blanked_newlines_kept():
    text = "a /* multi\nline gem */ var z = 3\n"
    out = hyg.blank_code(text, "gd")
    assert "gem" not in out and "var z = 3" in out
    assert out.count("\n") == text.count("\n")
    assert len(out) == len(text)


def test_gd_block_comment_unclosed_runs_to_eof():
    text = "var a = 1 /* unclosed wallet tail"
    out = hyg.blank_code(text, "gd")
    assert "wallet" not in out and "var a = 1" in out
    assert len(out) == len(text)


def test_gd_string_with_escaped_quote_blanked():
    # G-STRSCAN escape guard (blank_code 41/42/45): the string must END at the
    # REAL closing quote, not the escaped one.
    text = 'var s = "a \\" b gems"\nvar t = 2\n'
    out = hyg.blank_code(text, "gd")
    assert "gems" not in out
    assert "var t = 2" in out and len(out) == len(text)
    assert out.count("\n") == 2


def test_gd_single_quote_string_blanked():
    text = "var s = 'premium name'\nvar u = 3\n"
    out = hyg.blank_code(text, "gd")
    assert "premium" not in out and "var u = 3" in out
    assert len(out) == len(text)


# ---------- blank_code: the other families (F-2 gap, same controls) ----------

def test_py_triple_quote_family_blanked():
    # G-PY (blank_code 25-37): the triple-quote branch never ran in-process.
    text = 'import x\n"""\nhidden gems purchase\n"""\ny = 2\n'
    out = hyg.blank_code(text, "py")
    assert "gems" not in out and "purchase" not in out
    assert "import x" in out and "y = 2" in out
    assert out.count("\n") == text.count("\n")


def test_py_plain_string_blanked():
    text = "x = 'wallet here'\ny = 1\n"
    out = hyg.blank_code(text, "py")
    assert "wallet" not in out and "y = 1" in out


def test_js_backtick_string_blanked():
    text = "let a = `premium thing`; // rest of line\n"
    out = hyg.blank_code(text, "js")
    assert "premium" not in out and "rest" not in out
    assert "let a =" in out


def test_gd_backtick_is_not_a_string():
    # The family guard must NOT leak backtick blanking into gd (mutants 18/21/23).
    text = "var a = `premium`;\n"
    out = hyg.blank_code(text, "gd")
    assert "`premium`" in out            # gd has no template strings: pass-through


def test_cfg_semicolon_and_hash_comments():
    text = "name=One # hash cmt\nval=2 ; semi cmt\nnext=3\n"
    out = hyg.blank_code(text, "cfg")
    assert "cmt" not in out
    assert "name=One" in out and "val=2" in out and "next=3" in out


def test_html_comment_blanked_elsewhere_passthrough():
    text = "<i>x<!-- hidden gems -->y</i>\n"
    out = hyg.blank_code(text, "html")
    assert "gems" not in out and "x" in out and "y" in out
    unter = "<p>tail <!-- open"
    assert "open" not in hyg.blank_code(unter, "html")
    assert "<!-- keep -->" in hyg.blank_code("<!-- keep -->", "gd")


# ---------- words + tripwire_hit: all three modes ----------

def test_words_split_camel_and_snake():
    assert hyg.words("cashStore") == ["cash", "store"]
    assert hyg.words("CashStore") == ["cash", "store"]
    assert hyg.words("cash_store") == ["cash", "store"]


def test_tripwire_identifier_mode_exact_only():
    assert hyg.tripwire_hit("shop") == "shop"
    assert hyg.tripwire_hit("SHOP") == "shop"
    assert hyg.tripwire_hit("shop_id") is None
    assert hyg.tripwire_hit("my_shop") is None


def test_tripwire_word_mode_fires():
    assert hyg.tripwire_hit("purchase_count") == "purchase"
    assert hyg.tripwire_hit("MyGem") == "gem"


def test_tripwire_phrase_mode_fires_consecutive_words():
    assert hyg.tripwire_hit("get_cash_store_total") == "cash_store"
    assert hyg.tripwire_hit("CashStore") == "cash_store"
    assert hyg.tripwire_hit("battle_pass_id") == "battle_pass"


def test_tripwire_negative_controls_stay_quiet():
    for ident in ("store", "keeper", "priceless", "gemstone", "cash",
                  "store_cash", "iaplayer", "timer"):
        assert hyg.tripwire_hit(ident) is None, ident


# ---------- literal_violations: the I2 walker ----------

def test_literal_violations_positive_and_structural_clean():
    assert hyg.literal_violations("var a = 7.5\n") == [7.5]
    assert hyg.literal_violations(
        "var a = 0.5\nvar b = 3\nvar c = 4.0\nvar d = 0.0\n") == []


def test_literal_in_comment_or_string_not_flagged():
    # BN1 interaction: the blanking pre-pass must run before the literal grep.
    assert hyg.literal_violations("var a = 1.0  # 9.9 in a comment\n") == []
    assert hyg.literal_violations('var s = "cost 12.5"\nvar a = 2.0\n') == []
    assert hyg.literal_violations("var a = 2.5\n") == [2.5]   # non-vacuous pair


# ---------- walk / rel / read: the scanner plumbing ----------

def test_walk_positive_coverage_nested_case_and_skips(tmp_path):
    root = str(tmp_path)
    write(os.path.join(root, "a.gd"), "var a = 1\n")
    write(os.path.join(root, "sub", "b.PY"), "x = 1\n")        # ext case-insensitive
    write(os.path.join(root, "sub", "deep", "c.gd"), "var c = 3\n")
    write(os.path.join(root, "sub", "notes.md"), "# prose\n")  # non-code: never
    write(os.path.join(root, "__pycache__", "skip.gd"), "var s = 1\n")
    write(os.path.join(root, ".godot", "hide.gd"), "var h = 1\n")
    found = hyg.walk(root, hyg.CODE_EXTS)
    assert len(found) == 3                                     # COVERAGE COUNT > 0
    assert {os.path.relpath(p, root) for p in found} == \
        {os.path.join("a.gd"), os.path.join("sub", "b.PY"),
         os.path.join("sub", "deep", "c.gd")}


def test_walk_missing_dir_yields_empty(tmp_path):
    assert hyg.walk(os.path.join(str(tmp_path), "nope"), hyg.CODE_EXTS) == []


def test_rel_is_repo_relative(tmp_path, monkeypatch):
    monkeypatch.setattr(hyg, "REPO", str(tmp_path))
    got = hyg.rel(os.path.join(str(tmp_path), "godot", "x.gd"))
    assert got == os.path.join("godot", "x.gd")


def test_read_replaces_invalid_utf8(tmp_path):
    # G-READ-BOUND (read 2/3/5/6/9/10): observable only on non-UTF-8 bytes.
    p = write_bytes(os.path.join(str(tmp_path), "raw.bin.txt"), b"caf\xe9 \xff gem")
    out = hyg.read(p)
    assert "\ufffd" in out and "caf" in out and "gem" in out


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)
    return path


# ---------- BARE_RAND_RE: the gate's own compiled pattern ----------

def test_bare_rand_regex_bare_yes_qualified_no():
    assert hyg.BARE_RAND_RE.search("var x = randf()")
    assert hyg.BARE_RAND_RE.search("var x = randi ()")
    assert not hyg.BARE_RAND_RE.search("var x = rng.randf()")
    assert not hyg.BARE_RAND_RE.search("var x = my.rng.randi()")
    assert not hyg.BARE_RAND_RE.search("var xrandf = 1")
    assert hyg.QUAL_RAND_RE.search("var x = rng.randf()")


# ---------- main(): the ceiling / note / tripwire walkers over a planted repo ----------

def plant_repo(tmp_path):
    root = str(tmp_path)
    write(os.path.join(root, "godot", "bad.gd"),
          "var x = randf()\nvar y = rng.randf()\nvar purchase_id = 1\n")
    write(os.path.join(root, "godot", "long.py"), "x = 1\n" * 400 + "x = 1")
    write(os.path.join(root, "godot", "project.godot"), '[autoload]\n')
    write(os.path.join(root, "godot", "renamed.gd"), "var VS_STATE = 1\n")
    write(os.path.join(root, "server", "soft.py"), "y = 2\n" * 299 + "y = 2")
    return root


def test_main_fires_every_error_class_on_planted_tree(tmp_path, monkeypatch,
                                                      capsys):
    monkeypatch.setattr(hyg, "REPO", plant_repo(tmp_path))
    rc = hyg.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "check_hygiene: 5 hit(s)" in out
    assert "[bare-rand]" in out and "godot/bad.gd:1" in out
    assert "[tripwire] I1 token 'purchase' in purchase_id" in out
    assert "[ceiling] 401 lines > 400" in out and "godot/long.py" in out
    assert "[autoload]" in out and "godot/project.godot:1" in out
    assert "[rename] VS bridge name 'VS_STATE'" in out
    assert "sanctioned draw: randf(" in out           # the QUAL note fires too
    assert "server/soft.py 300 lines > soft 250" in out  # soft note fires


def test_main_comments_cannot_trip_bn1(tmp_path, monkeypatch, capsys):
    root = str(tmp_path)
    write(os.path.join(root, "godot", "quiet.gd"),
          "# shop cash_store gems purchase\n// premium wallet\n"
          "/* lockbox */\nvar peace = 1\n")
    monkeypatch.setattr(hyg, "REPO", root)
    rc = hyg.main()
    out = capsys.readouterr().out
    assert rc == 0 and "check_hygiene: 0 hit(s)" in out  # BN1: prose is blanked


def test_main_ceiling_boundary_exact_400_stays_green(tmp_path, monkeypatch,
                                                     capsys):
    # boundary: exactly 400 lines must NOT fire (> vs >= honesty).
    root = str(tmp_path)
    write(os.path.join(root, "godot", "edge.py"), "x = 1\n" * 399 + "x = 1")
    monkeypatch.setattr(hyg, "REPO", root)
    assert hyg.main() == 0
    assert "check_hygiene: 0 hit(s)" in capsys.readouterr().out


# ---------- absence legs on the SHIPPED tree (kept, per the card) ----------

def test_shipped_scan_universe_is_nonempty():
    # F-1's "coverage-count > 0" row: a walk that returns NOTHING is a defect,
    # never a pass — pin the shipped universe positive BEFORE the 0-hit claim.
    total = sum(len(hyg.walk(repo_path(top), hyg.CODE_EXTS))
                for top in I1_DIRS)
    assert total >= 50


def test_gate_zero_hits_on_shipped_tree(capsys):
    rc = hyg.main()
    out = capsys.readouterr().out
    assert rc == 0 and out.rstrip().endswith("check_hygiene: 0 hit(s)")
