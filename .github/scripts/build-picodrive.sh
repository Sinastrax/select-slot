#!/usr/bin/env bash
# Reproducibly build the pinned libretro PicoDrive core for H700 (Game Gear).
set -euo pipefail

out="${1:?usage: build-picodrive.sh SD_TREE SOURCE_RELEASE_DIR}"
release="${2:?usage: build-picodrive.sh SD_TREE SOURCE_RELEASE_DIR}"
work="${TMPDIR:-/tmp}/more-slot-picodrive"
commit=1890c2932234c9d30f4cd3851d02228baae8f09e
sha=123871ce468bc31f824df9273415215527ded2bdaadffd0503a97149aa06d523
emu_commit=a2dfc20ff507e4fd075cd325620bcea655e2c1f7
emu_sha=bd816079cfbf13c56a260c095d6b8e260c2f877e5b13f50d4e570b96e8b92830
dr_commit=dd762b861ecadf5ddd5fb03e9ca1db6707b54fbb
dr_sha=8f0be8a4aa27cd4ddaba41acbb845b1641964f2cc2f5a5f7b4b72f73368c1c12
fe_commit=9ed5822606dd7ff20a782a882e8fd611cb53ba88
fe_sha=458519aaa70916528e593f1f052aa45f704670fba094b409478a8197e6f076a7

fetch() {
  local url="$1" target="$2" expected="$3"
  curl -fsSL --retry 5 --retry-all-errors "$url" -o "$target.part"
  echo "$expected  $target.part" | sha256sum -c -
  mv "$target.part" "$target"
}

rm -rf "$work"
mkdir -p "$work" "$out/System/licenses" "$release"
src="$work/picodrive-$commit"
fetch "https://github.com/libretro/picodrive/archive/$commit.tar.gz" "$work/picodrive-src.tar.gz" "$sha"
fetch "https://github.com/digital-sound-antiques/emu2413/archive/$emu_commit.tar.gz" "$work/picodrive-emu2413-src.tar.gz" "$emu_sha"
fetch "https://github.com/mackron/dr_libs/archive/$dr_commit.tar.gz" "$work/picodrive-dr_libs-src.tar.gz" "$dr_sha"
fetch "https://github.com/irixxxx/libpicofe/archive/$fe_commit.tar.gz" "$work/picodrive-libpicofe-src.tar.gz" "$fe_sha"

tar -xzf "$work/picodrive-src.tar.gz" -C "$work"
mkdir -p "$src/pico/sound/emu2413" "$src/platform/common/dr_libs" "$src/platform/libpicofe"
tar -xzf "$work/picodrive-emu2413-src.tar.gz" -C "$src/pico/sound/emu2413" --strip-components=1
tar -xzf "$work/picodrive-dr_libs-src.tar.gz" -C "$src/platform/common/dr_libs" --strip-components=1
tar -xzf "$work/picodrive-libpicofe-src.tar.gz" -C "$src/platform/libpicofe" --strip-components=1

export CFLAGS="-mcpu=cortex-a53 -include $PWD/../.github/scripts/picodrive-glibc-2.17.h"
export CXXFLAGS="$CFLAGS"
export LDFLAGS="-flto-partition=one"
make -C "$src" -f Makefile.libretro platform=unix use_libchdr=0 \
  PLATFORM_TREMOR=1 PLATFORM_ZLIB=1 "GIT_REVISION=-${commit:0:7}" \
  -j"$(getconf _NPROCESSORS_ONLN)"

core="$src/picodrive_libretro.so"
file "$core" | grep -E 'ELF 64-bit LSB shared object, ARM aarch64'
install -m 644 "$core" "$out/System/picodrive_libretro.so"
sha256sum "$out/System/picodrive_libretro.so" | tee "$out/System/licenses/picodrive.sha256"

cp ../.github/assets/picodrive-LICENSE.txt "$out/System/licenses/"
cp ../.github/assets/picodrive-emu2413-MIT.txt "$out/System/licenses/"
cp ../.github/assets/picodrive-tremor-BSD.txt "$out/System/licenses/"
cp ../.github/assets/picodrive-headerless-files.txt "$out/System/licenses/"
cat > "$out/System/licenses/picodrive-notice.txt" <<NOTICE
PicoDrive libretro core, pinned commit $commit.
Game Gear support is provided by this core. Source and the pinned build dependencies
are included in the corresponding more. slot release source assets.
This core is subject to the non-commercial terms in picodrive-LICENSE.txt.
NOTICE

mv "$work"/picodrive-*-src.tar.gz "$release/"
cat > "$release/picodrive-src.meta" <<META
core_commit=$commit
core_sha256=$sha
emu2413_commit=$emu_commit
emu2413_sha256=$emu_sha
dr_libs_commit=$dr_commit
dr_libs_sha256=$dr_sha
libpicofe_commit=$fe_commit
libpicofe_sha256=$fe_sha
build=Makefile.libretro platform=unix use_libchdr=0 PLATFORM_TREMOR=1 PLATFORM_ZLIB=1
target=H700 aarch64 cortex-a53
META

echo "PicoDrive core installed; pinned source archives saved for distribution."
