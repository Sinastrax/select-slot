#!/usr/bin/env python3
"""Validate the sole H700 release job's embedded manifest validator.

Previously, a duplicate workflow-run publisher could force-move a tag and
delete a draft release. The audited builder now owns publishing. Catch broken
embedded Python and dangerous publication operations before building.
"""
from pathlib import Path

workflow = Path("../.github/workflows/build-h700.yml").read_text()
verify_step = workflow.split(
    "      - name: Validate the test build manifest\n", 1
)
assert len(verify_step) == 2, "H700 verified release job missing"
validate = verify_step[1].split(
    "      - name: Publish a prerelease without changing stable releases\n", 1
)
assert len(validate) == 2, "H700 release checksum/publication ordering broken"
anchor = "          python3 - <<'PY'\n"
assert validate[0].count(anchor) == 1, "Missing H700 embedded release validator"
body = validate[0].split(anchor, 1)[1].split("\n          PY", 1)[0]
code = "\n".join(
    line[10:] if line.startswith("          ") else line
    for line in body.splitlines()
)
compile(code, "h700_manifest_validator", "exec")
assert 'assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["sha256"]' in code
assert 'assert manifest["tag"] == "v" + version' in code
assert 'assert manifest["version"] == version' in code

publish = validate[1]
assert 'gh release view "$tag"' in publish
assert "leaving it unchanged" in publish
assert 'gh release create "$tag"' in publish
assert "--prerelease" in publish and "--latest" not in publish
assert "--notes-file RELEASE_NOTES.md" in publish
assert "release/versions.json" in publish
assert "release/upstream/source-release/mgba-c758314a639aa0066e7b65a8341448181b73c804-source.tar.gz" in publish

for forbidden in ("gh release delete", "git/refs/tags/", "force=true", " -X DELETE", " --force"):
    assert forbidden not in publish, f"Unsafe H700 publishing operation: {forbidden}"
assert "needs: build-h700" in workflow
print("PASS: single H700 publisher validates checksums, preserves tags and includes mGBA source")
