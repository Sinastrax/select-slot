#!/usr/bin/env python3
"""Permit slow 2.4 GHz Wi-Fi downloads without changing the OTA protocol."""
from pathlib import Path
p = Path("crates/slot/src/update.rs")
s = p.read_text()
old = "pub(crate) const DOWNLOAD_TIMEOUT: Duration = Duration::from_secs(120);"
new = "pub(crate) const DOWNLOAD_TIMEOUT: Duration = Duration::from_secs(300);"
assert s.count(old) == 1, "Unexpected upstream OTA timeout; review before changing"
p.write_text(s.replace(old, new, 1))
print("OTA download tolerance: 120 -> 300 seconds")
