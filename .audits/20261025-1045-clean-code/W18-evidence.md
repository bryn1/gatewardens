# W18 evidence — Windows desktop export (MC 11437, workspace 11274)

Run date 2026-10-27. Sole writer: code (11437). Repo /home/claudecode/Games/gatewardens.
Godot: /home/claudecode/Games/.tools/godot/Godot_v4.7.2-stable_linux.x86_64 (v4.7.2.stable.official.ed1daf0bf).
Templates: ~/.local/share/godot/export_templates/4.7.2.stable/ (windows_release_x86_64.exe 109,268,480 B present).

## DoD row 1 — export runs from a clean build/, exe > 80 MB, starts with MZ

Command (repo root, build/ removed first — `rm -rf build && bash tools/export_windows.sh`):

    Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org
    ... savepack ...
    [ DONE ] savepack
    a979c386a4b29b7df79eedb33dccbe82dd2dd68268e842fd0a290b8ff1ef37a3  /home/claudecode/Games/gatewardens/build/Gatewardens.exe

Full transcript: W18-export-run.log (this dir). Output of the verification block:

    $ ls -la build/
    -rw-r--r-- 1 claudecode claudecode 109372280 Oct 27 10:26 Gatewardens.exe   # ONE file, no sidecar .pck -> embed_pck APPLIED (schema default would emit .pck)
    $ sha256sum build/Gatewardens.exe
    a979c386a4b29b7df79eedb33dccbe82dd2dd68268e842fd0a290b8ff1ef37a3  build/Gatewardens.exe
    $ head -c 2 build/Gatewardens.exe | od -c | head -1
    0000000   M   Z
    $ python3 <PE header parse>
    MZ + PE@0x80 machine=0x8664 = AMD64 (x86_64)

109,372,280 B = ~104 MB > 80 MB. MZ VERIFIED, PE sig VERIFIED, machine AMD64 VERIFIED.

## DoD row 2 — exactly one Windows preset, embed_pck=true, x86_64-only; KEY-NAME CHECK

export_presets.cfg: one `[preset.1]` name="Windows Desktop" platform="Windows Desktop",
[preset.1.options] carries binary_format/embed_pck=true and binary_format/architecture="x86_64"
(Godot 4.x Windows schema: the architecture is the ONE binary_format/architecture string key —
"architectures/x86_32|arm64 false" IS the same fact in this schema: the enum selects exactly one arch).
Brief's key check (wrong key = silently ignored, default would export anyway) — NEGATIVE PROBE RUN:
setting binary_format/architecture="arm64" and re-exporting produced
`probe machine=0xaa64 -> ARM64 (key is LIVE)` (export_rc=0), i.e. the engine HONOURS the key; cfg
restored verbatim to "x86_64" (grep count 1 after restore; shipped exe is 0x8664). embed_pck is proven
live by the single-file output (default false emits a sidecar Gatewardens.pck — none exists).
Version keys proven live too: "Gatewardens" and "1.0.0" found UTF-16LE inside the exe's version resource.
binary_format/modify_executable_name=true is the engine default, written explicitly; codesign empty
(codesign/enable=false); icons default (application/icon="").

## DoD row 3 — script runs from repo root, echoes sha; build/ gitignored

`bash tools/export_windows.sh` ran from the repo root (the run above); its last line is the
sha256sum echo (transcript above). After export + the arm64 probe:

    $ git status --short (build/ absent = gitignored)
     M .gitignore
     M LEDGER.md
     M README.md
     M RELEASE_NOTES.md
     M godot/export_presets.cfg
    ?? tools/export_windows.sh

(no `build/` entry; .gitignore gained `build/` with the same-law-as-static comment.)

## DoD row 4 — docs honest, hygiene line untouched

git diff excerpts:

    +Windows desktop build (W18, built by `bash tools/export_windows.sh` → `build/`, artifacts never
    +committed): the double-click `Gatewardens.exe` asset ships on the [release
    +page](https://github.com/bryn1/gatewardens/releases); saves live in `%APPDATA%\Godot\app_userdata\Gatewardens`.

    +**Windows download** — the v1 release page carries a Windows zip asset: unpack
    +and double-click `Gatewardens.exe` (Windows 10/11, 64-bit; one self-contained
    +file, no installer). Saves live in `%APPDATA%\Godot\app_userdata\Gatewardens`.
    +Unsigned-build caveat stated as it is: SmartScreen may warn — the build is
    +unsigned, no malware, click More info > Run anyway.

The release-notes hygiene one-liner (`check_hygiene: 0 hit(s)` intro paragraph) and the README
status/hygiene line are untouched (diff shows insertions only, none of their hunks).

## DoD row 6 — suite + hygiene re-run at THIS tree (after all edits, before commit)

    $ python3 -m pytest -q
    222 passed in 152.18s (0:02:32)   # W18-final-suite.log, SUITE_EXIT=0
    $ python3 tools/check_hygiene.py
    check_hygiene: 0 hit(s)            # exit 0 (soft-250 notes informational, pre-existing)

## Limitations stated honestly

- The .exe was not EXECUTED on Windows (no Windows host in this card's scope); the header checks
  (MZ, PE machine 0x8664, embedded pck single-file, version resource) are the deterministic proofs
  shipped here. Runtime-on-Windows claim: UNVERIFIED.
- The release-page zip asset is attached by the orchestrator after this commit (README/release
  notes describe it as the delivery path, per the brief).

VERIFY_EXIT=0
