#!/usr/bin/env python3
"""Keep the required modified mGBA corresponding source as a release asset.

The archive is *published alongside* every OTA firmware release, not discarded.
The on-device System/ tree retains an exact versioned URL to that source and
its revision metadata. Keeping a large source tar.gz inside the *runtime*
firmware previously doubled the size of every wireless update.
"""
from pathlib import Path
import hashlib
import sys

version, tree = sys.argv[1:]
assert version.startswith("1.16.0-rgsp."), version
root = Path(tree)
assert root.is_dir(), "Missing full H700 firmware tree"
sha = "c758314a639aa0066e7b65a8341448181b73c804"
name = f"mgba-{sha}-source.tar.gz"
source = root / "System" / "licenses" / name
destination = Path("..") / name
assert source.is_file() and source.stat().st_size > 100_000, "Missing modified mGBA source"
assert not destination.exists(), "Refuse to replace existing corresponding-source artifact"
source.rename(destination)
assert destination.is_file() and not source.exists()
source_url = f"https://github.com/Sinastrax/select-slot/releases/download/v{version}/{name}"
record = (
    "Corresponding modified mGBA source (separate release asset)\n"
    f"Source: {source_url}\n"
    f"Commit: {sha}\n"
    f"SHA-256: {hashlib.sha256(destination.read_bytes()).hexdigest()}\n"
    "The matching source archive is published alongside the complete OTA ZIP.\n"
)
(root / "System" / "licenses" / "mgba-source-location.txt").write_text(record)
print("Excluded separate mGBA source from runtime firmware:", name)
print(f"Source asset: {destination.stat().st_size / 1048576:.2f} MiB")
