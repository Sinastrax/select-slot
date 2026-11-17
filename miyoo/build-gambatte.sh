#!/bin/sh
# Build an xrgb8888 Gambatte libretro core for the Miyoo ARMv7 runtime.
set -eu
source_archive="$1"
output="$2"
work="$3"
mkdir -p "$work"
tar -xzf "$source_archive" -C "$work" --strip-components=1
cd "$work"
# platform=unix avoids makefile's device-specific hardcoded cross compiler,
# while CC/CXX/AR select the port's pinned ARMv7 hard-float toolchain.
make -f Makefile.libretro -j2 \
    platform=unix VIDEO_RGB565=0 \
    CC=arm-linux-gnueabihf-gcc \
    CXX=arm-linux-gnueabihf-g++ \
    AR=arm-linux-gnueabihf-ar \
    CFLAGS="-O3 -fPIC -mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard" \
    CXXFLAGS="-O3 -fPIC -mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard" \
    LDFLAGS="-shared"
cp gambatte_libretro.so "/src/$output"
