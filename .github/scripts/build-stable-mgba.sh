#!/usr/bin/env bash
# Reproduce the older mGBA core verified on the RG SP / RG34XXSP.
# The release must contain THIS core, not the newer one built by upstream dist:device.
set -euo pipefail
out="${1:?usage: build-stable-mgba.sh PATH_TO_SD2_TREE}"
commit="c758314a639aa0066e7b65a8341448181b73c804"
source_dir="target-device/mgba-old/source"
build_dir="target-device/mgba-old/build"
mkdir -p "$source_dir" "$out/System/licenses"
git -C "$source_dir" init -q
git -C "$source_dir" fetch -q --depth 1 https://github.com/libretro/mgba "$commit"
git -C "$source_dir" checkout -q --detach FETCH_HEAD
python3 - "$source_dir" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1])
p = src / "src/core/CMakeLists.txt"
data = p.read_text()
a, b = "rewind.c\n\tscripting.c\n\tsync.c", "rewind.c\n\tsync.c"
assert a in data, "mGBA source change: scripting list missing"
p.write_text(data.replace(a, b, 1))
p = src / "src/platform/libretro/libretro.c"
data = p.read_text()
for line in ('const char* const projectVersion = "0.11-dev" GIT_VERSION;\n',
             'const char* const projectName = "mGBA";\n'):
    assert line in data, "mGBA source change: expected duplicate missing"
    data = data.replace(line, "", 1)
p.write_text(data)
p = src / "CMakeLists.txt"
data = p.read_text()
marker = "file(GLOB RETRO_SRC ${CMAKE_CURRENT_SOURCE_DIR}/src/platform/libretro/*.c)"
assert marker in data
data = data.replace(marker, marker + '\n\tlist(REMOVE_ITEM RETRO_SRC "${CMAKE_CURRENT_SOURCE_DIR}/src/platform/libretro/memory.c")', 1)
marker = 'add_library(${BINARY_NAME}_libretro SHARED ${CORE_SRC} ${RETRO_SRC} ${CORE_VFS_SRC})'
assert marker in data
data = data.replace(marker, marker + '\n\ttarget_sources(${BINARY_NAME}_libretro PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/util/vfs/vfs-fd.c)', 1)
p.write_text(data)
PY
cmake -S "$source_dir" -B "$build_dir" \
  -DLIBMGBA_ONLY=ON -DBUILD_LIBRETRO=ON -DENABLE_SCRIPTING=OFF \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-flto=auto"
cmake --build "$build_dir" --target mgba_libretro --parallel "$(getconf _NPROCESSORS_ONLN)"
core="$build_dir/mgba_libretro.so"
if nm -D -u "$core" | grep -E ' U (VFileOpenFD|VFileFromFD)$'; then
  echo "Older mGBA has unresolved VFS symbols" >&2
  exit 1
fi
file "$core" | grep -E "ARM aarch64|ARM64|aarch64"
install -m 644 "$core" "$out/System/mgba_libretro.so"
sha256sum "$out/System/mgba_libretro.so" | tee "$out/System/licenses/mgba-stable.sha256"
printf 'commit=%s\nsource=https://github.com/libretro/mgba/tree/%s\ncustom_fix=legacy-libretro-cmake-compatibility\n' \
  "$commit" "$commit" > "$out/System/licenses/mgba-$commit.meta"
# MPL-2.0 permits the matching source to be distributed separately from the binary.
# Archive the *modified* build tree, including the CMake/libretro compatibility fixes.
# The CI release publishes this exact source archive beside the firmware ZIP.
tar -czf "mgba-$commit-source.tar.gz" -C "$source_dir" --exclude=.git .
install -m 644 "$source_dir/LICENSE" "$out/System/licenses/mgba-LICENSE.txt"
printf 'mGBA source: https://github.com/Sinastrax/select-slot/releases/tag/v%s\\n' "${SLOT_RELEASE_VERSION:-1.16.0-rgsp.30}" > "$out/System/licenses/mgba-source-location.txt"
echo "Stable mGBA core installed and corresponding source packaged"
