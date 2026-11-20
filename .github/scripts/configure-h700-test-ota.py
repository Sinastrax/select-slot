#!/usr/bin/env python3
"""Point a test-channel H700 build at its isolated manifest branch."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
source = root / "crates/slot/src/update.rs"
text = source.read_text()
stable = 'pub const LATEST: &str = "https://github.com/Sinastrax/select-slot/releases/latest/download/versions.json";'
test = 'pub const LATEST: &str = "https://raw.githubusercontent.com/Sinastrax/select-slot/test-ota/versions.json";'
assert text.count(stable) == 1, "Stable OTA manifest URL not found exactly once"
source.write_text(text.replace(stable, test, 1))
assert test in source.read_text()
print("Configured isolated test OTA manifest")
