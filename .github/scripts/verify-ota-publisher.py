#!/usr/bin/env python3
"""Check the OTA publisher's embedded validation script and draft replacement.

A broken embedded Python statement previously passed H700 compilation but
prevented GitHub from publishing an otherwise complete release.
"""
from pathlib import Path
from textwrap import dedent
s = Path("../.github/workflows/publish-ota-from-build.yml").read_text()
anchor = '          python3 - "$current" <<\'PY\'\n'
assert s.count(anchor) == 1, "Missing release manifest validator"
body = s.split(anchor, 1)[1].split("\n          PY", 1)[0]
code = "\n".join(line[10:] if line.startswith("          ") else line for line in body.splitlines())
compile(code, "release_manifest_validator", "exec")
assert 'assert any("-" + n + "." in version' in code
assert 'gh release upload "$TAG"' in s and "--clobber" in s
assert 'gh release edit "$TAG"' in s and "--draft=false --latest" in s
assert 'gh release create "$TAG"' in s
print("PASS: OTA publisher parses Python manifest and replaces withdrawn drafts")
