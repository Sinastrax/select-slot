#!/usr/bin/env python3
"""Prebuild source checks for smaller OTA and slow-network compatibility."""
from pathlib import Path
s = Path("crates/slot/src/update.rs").read_text()
assert "DOWNLOAD_TIMEOUT: Duration = Duration::from_secs(300);" in s
assert "pub const STAGING: &str = \"System.new\";" in s
assert "pub fn verify(bytes: &[u8], release: &Release)" in s
assert "sha256" in s
assert 'REQUIRED: [&str; 5]' in s
assert "fn copy_into(" in s
workflow = Path("../.github/workflows/build-h700.yml").read_text()
assert "python3 ../.github/scripts/separate-mgba-source.py" in workflow
assert "python3 ../.github/scripts/verify-slim-ota-assets.py" in workflow
assert "mgba-source-location.txt" in Path("../.github/scripts/separate-mgba-source.py").read_text()
print("PASS: retained full verified OTA system and checksum, increased slow-Wi-Fi tolerance")
