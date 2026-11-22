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
SLOTPLUS_COMMIT="0e85ed2b82dd1baf57ac10139c25f58a2365c09e"
for asset in slot_gg_back.png slot_gg_front.png slot_gg_plugged.png; do
  curl -fsSL --retry 5 --retry-all-errors \
    "https://raw.githubusercontent.com/nelynes/slotPlus/${SLOTPLUS_COMMIT}/assets/${asset}" \
    -o "$source_dir/assets/$asset"
done
gzip -dc "$root/patches/unslot-more-slot-gamegear.patch.gz" > "$patch_file"
git -C "$source_dir" apply --check "$patch_file"
git -C "$source_dir" apply "$patch_file"
for asset in gg_board.png gg_cart.png gg_clear.png gg_interior.png gg_neutral.png; do
  test -s "$source_dir/assets/$asset"
done
for asset in slot_gg_back.png slot_gg_front.png slot_gg_plugged.png; do
  test -s "$source_dir/assets/$asset"
done
test -s "$source_dir/licenses/gamegear-cartridge-art.txt"

printf 'Prepared unslot %s with more.slot Game Gear, OTA and compatibility changes\n' "$UNSLOT_COMMIT"
