#!/usr/bin/env python3
"""Brand the original slot. boot wordmark and OTA splash before compilation.

Run against upstream/card/System so the frontend's include_bytes! embeds the
new asset and dist:device packages the same logo and updated launcher.
The original-style mark is stored as grayscale coverage; the device receives
an uncompressed 24-bit BMP. Custom Config/bootlogo.bmp remains untouched.
"""
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
    logo_source = Path(__file__).resolve().parents[2] / "branding" / "select-slot-wordmark.b85"
    raw = "".join(logo_source.read_text().splitlines())
    if len(raw) != 8967:
        raise SystemExit("Unexpected select. slot. wordmark source size")
    pixels = zlib.decompress(base64.b85decode(raw))
    if len(pixels) != SIZE[0] * SIZE[1]:
        raise SystemExit("Corrupt select. slot. wordmark")
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
    launcher.write_text(source.replace(old, 'say "UPDATING SELECT. SLOT."', 1))
    print("Branded source boot image (514x75 RGB BMP) and update splash")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: brand-h700-boot.py <upstream/card/System>")
    apply(Path(sys.argv[1]))
