#!/usr/bin/env python3
"""Apply more. slot. branding to the H700 system boot and OTA update splash."""
import base64
from pathlib import Path
import sys
import zlib

from PIL import Image

SIZE = (514, 75)
BACKGROUND = (11, 14, 17)
FOREGROUND = (244, 245, 249)


def apply(system: Path):
    if not system.is_dir():
        raise SystemExit(f"Missing firmware System directory: {system}")
    source = Path(__file__).resolve().parents[2] / "branding" / "more-slot-wordmark.b85"
    encoded = "".join(source.read_text().splitlines())
    pixels = zlib.decompress(base64.b85decode(encoded))
    if len(pixels) != SIZE[0] * SIZE[1]:
        raise SystemExit("Corrupt more. slot. wordmark")
    mask = Image.frombytes("L", SIZE, pixels)
    wordmark = Image.composite(
        Image.new("RGB", SIZE, FOREGROUND),
        Image.new("RGB", SIZE, BACKGROUND),
        mask,
    )
    logo = system / "bootlogo.bmp"
    wordmark.save(logo, format="BMP")
    with Image.open(logo) as check:
        if check.format != "BMP" or check.mode != "RGB" or check.size != SIZE:
            raise SystemExit("Incorrect H700 boot wordmark BMP format")

    launcher = system / "launch_frontend.sh"
    source = launcher.read_text()
    old = 'say "UPDATING SLOT"'
    if source.count(old) != 1:
        raise SystemExit("Unexpected upstream update splash; refusing silent replacement")
    launcher.write_text(source.replace(old, 'say "UPDATING MORE. SLOT."', 1))
    print("Branded more. slot. boot image and OTA update splash")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: brand-more-h700-boot.py <upstream/card/System>")
    apply(Path(sys.argv[1]))
