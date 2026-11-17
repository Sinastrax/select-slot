#!/usr/bin/env python3
"""Check runtime OTA ZIP, out-of-band corresponding source, and manifest."""
from pathlib import Path
import hashlib, json, sys, zipfile

version = sys.argv[1]
root = Path("..")
meta = json.loads((root / "versions.json").read_text())["stable"]
assert meta["version"] == version
assert meta["tag"] == "v" + version
firmware = root / meta["zip"]
assert firmware.is_file()
assert firmware.stat().st_size == meta["size"]
assert hashlib.sha256(firmware.read_bytes()).hexdigest() == meta["sha256"]
src = meta["source"]
archive = root / src["file"]
assert archive.is_file()
assert archive.stat().st_size == src["size"]
assert hashlib.sha256(archive.read_bytes()).hexdigest() == src["sha256"]
assert src["file"].startswith("mgba-") and src["file"].endswith("-source.tar.gz")
with zipfile.ZipFile(firmware) as z:
    names = set(z.namelist())
    required = {
        "select-slot-h700/System/slot",
        "select-slot-h700/System/mgba_libretro.so",
        "select-slot-h700/System/gpsp_libretro.so",
        "select-slot-h700/System/gambatte_libretro.so",
        "select-slot-h700/System/launch_frontend.sh",
        "select-slot-h700/System/licenses/mgba-source-location.txt",
    }
    assert required <= names, sorted(required - names)
    assert not any(x.endswith("-source.tar.gz") for x in names), "Bundled unneeded source archive"
    link = z.read("select-slot-h700/System/licenses/mgba-source-location.txt").decode()
    assert f"/releases/download/v{version}/{src['file']}" in link
    assert src["sha256"] in link
    print(f"PASS: OTA {firmware.stat().st_size/1048576:.2f} MiB, source separately {archive.stat().st_size/1048576:.2f} MiB")
    assert firmware.stat().st_size < 22 * 1048576, "OTA payload is still larger than expected"
