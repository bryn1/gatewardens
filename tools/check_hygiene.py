#!/usr/bin/env python3
"""Gatewardens hygiene gate — stdlib only; exit nonzero on ANY hit (I9).

Rules (docs/ARCHITECTURE.md):
  ceiling   .gd/.py <= 400 lines HARD (250 soft -> informational note);
            files under tests/ <= 600; a first line "# hygiene: <reason>"
            exempts the hard ceiling (header reason); data/config files
            (every other extension) are exempt from ceilings entirely.
  tripwire  I1 monetization TRIPWIRE over a named-token list (NOT a
            closure, F2-4) across godot/ server/ static/ tools/ tests/
            CODE (.gd .py .cfg .godot .html .htm .js .css) with comments
            and string literals blanked BEFORE scanning (BN1 — a word in
            a comment can never trip it); identifier-aware, case-
            insensitive, whole-token matching (camelCase/snake_case
            split). Prose documents (.md) are NOT scanned.
  bare-rand BARE randf()/randi() (call not preceded by '.') = 0 hits in
            godot/ (F2-1/I6); receiver-qualified rng.randf()/rng.randi()
            is the sanctioned draw path — informational, never an error.
  autoload  no "[autoload]" section header in godot/project.godot (R3/C1).
  rename    VS_STATE / __vsSnapshot / vsHost = 0 hits, RAW text, in the
            I8 scope dirs godot/ server/ static/ (+ README.md if present).
            .audits/ and docs/ are prose and exempt (I8 names them).

The I2 number-literal whitelist arrives with the governed scene scripts
(W3+) and lands in this file then — no second gate beside this one.
"""

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# I1 token list, verbatim from ARCHITECTURE.md I1. Modes: "word" = the
# token equals one camel/snake word of an identifier; "phrase" = the
# token's words appear consecutively inside one identifier (cash_store,
# CashStore); "identifier" = the WHOLE identifier equals the token (shop).
TRIPWIRE = {
    "lockbox": "word", "purchase": "word", "cash_store": "phrase",
    "iap": "word", "paywall": "word", "wallet": "word", "monetize": "word",
    "buyback": "word", "gacha": "word", "premium": "word",
    "battle_pass": "phrase", "gem": "word", "gems": "word",
    "shop": "identifier", "price": "word", "key_count": "phrase",
    "real_money": "phrase", "timer_unlock": "phrase",
}

CODE_EXTS = {".gd": "gd", ".py": "py", ".cfg": "cfg", ".godot": "cfg",
             ".html": "html", ".htm": "html", ".js": "js", ".css": "css"}
SKIP_DIRS = {".git", ".godot", ".audits", ".tmp", "__pycache__",
             "node_modules", ".tools", "venv"}
I1_DIRS = ("godot", "server", "static", "tools", "tests")
I8_DIRS = ("godot", "server", "static")
VS_NAMES = ("VS_STATE", "__vsSnapshot", "vsHost")
IDENT_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
BARE_RAND_RE = re.compile(r"(?<![.\w])(?:randf|randi)\s*\(")
QUAL_RAND_RE = re.compile(r"\.\s*(?:randf|randi)\s*\(")


def blank_code(text, family):
    """Comments + string literals replaced by spaces; newlines kept so
    line numbers of the remaining CODE stay true (BN1 pre-pass)."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if c in "\"'" or (c == "`" and family == "js"):
            q = q3 = c * 3 if (family == "py" and text[i:i + 3] == c * 3) else c
            j = i + len(q3)
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text.startswith(q3, j):
                    break
                j += 1
            chunk = text[i:min(j + len(q), n)]
            out.append("".join(ch if ch == "\n" else " " for ch in chunk))
            i = j + len(q)
            continue
        if (c == "#" and family in ("gd", "py", "cfg")
                or (c == ";" and family == "cfg")
                or (c == "/" and nxt == "/" and family in ("gd", "js", "html"))):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
            continue
        if c == "/" and nxt == "*" and family in ("gd", "js", "css"):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            chunk = text[i:j]
            out.append("".join(ch if ch == "\n" else " " for ch in chunk))
            i = j
            continue
        if c == "<" and text.startswith("<!--", i) and family == "html":
            j = text.find("-->", i)
            j = n if j < 0 else j + 3
            chunk = text[i:j]
            out.append("".join(ch if ch == "\n" else " " for ch in chunk))
            i = j
            continue
        out.append(c)
        i += 1
    return "".join(out)


def words(ident):
    """camelCase/snake_case split, lowercased words of one identifier."""
    out = []
    for part in ident.split("_"):
        out.extend(w.lower() for w in
                   re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+", part))
    return out


def tripwire_hit(ident):
    low = ident.lower()
    if TRIPWIRE.get(low) == "identifier":
        return low
    w = words(ident)
    for token, mode in TRIPWIRE.items():
        if mode == "word" and token in w:
            return token
        if mode == "phrase":
            t = token.split("_")
            for k in range(len(w) - len(t) + 1):
                if w[k:k + len(t)] == t:
                    return token
    return None


def walk(base, accept_exts):
    hits = []
    if not os.path.isdir(base):
        return hits
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if os.path.splitext(name)[1].lower() in accept_exts:
                hits.append(os.path.join(dirpath, name))
    return hits


def rel(path):
    return os.path.relpath(path, REPO)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main():
    errors, notes = [], []
    for top in I1_DIRS:
        for path in walk(os.path.join(REPO, top), CODE_EXTS):
            # Ceiling class per the header + ARCHITECTURE row: .gd/.py only
            # ("every other extension exempt"); W12 hit the divergence when
            # the gitignored BUILD static/index.js (910 lines) tripped a
            # ceiling meant for source files.
            if os.path.splitext(path)[1].lower() in (".gd", ".py"):
                lines = read(path).split("\n")
                in_tests = rel(path).split(os.sep)[0] == "tests"
                ceiling = 600 if in_tests else 400
                exempt = lines[0].startswith("# hygiene:") if lines else False
                if len(lines) > ceiling and not exempt:
                    errors.append("%s:1: [ceiling] %d lines > %d" %
                                  (rel(path), len(lines), ceiling))
                elif len(lines) > 250 and not in_tests:
                    notes.append("note: %s %d lines > soft 250%s" %
                                 (rel(path), len(lines),
                                  " (exempt)" if exempt else ""))
            if path.endswith(".gd"):
                stripped = blank_code(read(path), "gd")
                for lineno, line in enumerate(stripped.split("\n"), 1):
                    if BARE_RAND_RE.search(line):
                        errors.append("%s:%d: [bare-rand] bare randf()/randi()"
                                      " — use rng.randf()/rng.randi() (F2-1)"
                                      % (rel(path), lineno))
                    for match in QUAL_RAND_RE.finditer(line):
                        notes.append("note: %s:%d sanctioned draw: %s(" %
                                     (rel(path), lineno,
                                      match.group(0).strip().lstrip(".")))
            text = blank_code(read(path), CODE_EXTS[os.path.splitext(path)[1].lower()])
            for lineno, line in enumerate(text.split("\n"), 1):
                for ident in IDENT_RE.findall(line):
                    token = tripwire_hit(ident)
                    if token:
                        errors.append("%s:%d: [tripwire] I1 token '%s' in %s"
                                      % (rel(path), lineno, token, ident))
    project = os.path.join(REPO, "godot", "project.godot")
    if os.path.isfile(project):
        for lineno, line in enumerate(read(project).split("\n"), 1):
            if line.strip() == "[autoload]":
                errors.append("godot/project.godot:%d: [autoload] present"
                              " — forbidden (C1/R3)" % lineno)
    i8_files = [p for top in I8_DIRS
                for p in walk(os.path.join(REPO, top), {""} | set(CODE_EXTS))]
    readme = os.path.join(REPO, "README.md")
    if os.path.isfile(readme):
        i8_files.append(readme)
    for path in i8_files:
        text = read(path)
        for lineno, line in enumerate(text.split("\n"), 1):
            for name in VS_NAMES:
                if name in line:
                    errors.append("%s:%d: [rename] VS bridge name '%s'"
                                  " (I8)" % (rel(path), lineno, name))
    for note in notes:
        print(note)
    for error in errors:
        print(error)
    print("check_hygiene: %d hit(s)" % len(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
