"""Strict ordered patch collector for the pinned Miyoo Slot 1.8.1 tree.

The feature modules use edit() in the specified import order. Each source
replacement must match exactly once. Only a validated set of files may be
emitted by apply_custom.py; runtime/install files are not touched here.
"""
from difflib import unified_diff

_source = None
_desired = {}
changes = {}
version_label = None

def configure(source, version):
    global _source, version_label
    if _source is not None:
        raise RuntimeError("Miyoo patch collector configured twice")
    _source = source
    version_label = version

def edit(path, operations):
    if _source is None:
        raise RuntimeError("Miyoo patch collector not configured")
    original = (_source / path).read_text()
    new = _desired.get(path, original)
    for before, after in operations:
        count = new.count(before)
        if count != 1:
            raise RuntimeError(
                f"{path}: expected exactly one match, found {count}: {before[:100]!r}"
            )
        new = new.replace(before, after, 1)
    diff = "".join(unified_diff(
        original.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}", n=4,
    ))
    if not diff:
        raise RuntimeError(f"{path}: no changes")
    _desired[path] = new
    changes[path] = diff
