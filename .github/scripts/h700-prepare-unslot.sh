#!/usr/bin/env bash
set -euo pipefail

UNSLOT_COMMIT="3043c411c25b7fd1cdfe94cc295b59a45ccdbc61"
root="$(cd "$(dirname "$0")/../.." && pwd)"
source_dir="$root/upstream"
patch_file="$(mktemp)"
trap 'rm -f "$patch_file"' EXIT HUP INT TERM

if [ -e "$source_dir" ]; then
  echo "Refusing to reuse an existing upstream directory" >&2
  exit 1
fi
git clone --quiet --no-checkout https://github.com/cloudwithax/unslot.git "$source_dir"
git -C "$source_dir" checkout --quiet --detach "$UNSLOT_COMMIT"
test "$(git -C "$source_dir" rev-parse HEAD)" = "$UNSLOT_COMMIT"
gzip -dc "$root/patches/unslot-more-slot-gamegear.patch.gz" > "$patch_file"
git -C "$source_dir" apply --check "$patch_file"
git -C "$source_dir" apply "$patch_file"
mkdir -p "$source_dir/assets" "$source_dir/licenses"
cp "$root/.github/assets/gamegear/gg_"*.png "$source_dir/assets/"
cp "$root/.github/assets/gamegear/NOTICE.txt" "$source_dir/licenses/gamegear-cartridge-art.txt"

printf 'Prepared unslot %s with more.slot Game Gear, OTA and compatibility changes\n' "$UNSLOT_COMMIT"
