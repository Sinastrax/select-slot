# Online updates for select. slot.

The firmware inherits Slot's existing **Settings → System → Check for Updates** interface.
Our `patches/select-online-updates.patch` redirects that interface to **this repository's**
GitHub Releases. It does not fetch releases from pvaibhav's fork.

## How a custom update works

1. Connect the device to Wi-Fi and select **Settings → System → Check for Updates**.
2. The UI downloads `versions.json` from the latest stable GitHub Release for this repository.
3. The updater compares the embedded custom version with the release's version. It also
   understands older pvaibhav and RGSP release versions so users can migrate.
4. If you approve an update, the updater downloads the complete
   `slot-v<VERSION>-h700.zip`, checks its declared size and SHA-256 digest, and stages
   its `System/` contents in `System.new/`.
5. On restart the existing Slot launcher installs the staged `System/` files. Saves,
   ROMs and settings outside `System/` are not part of the update.

**Important:** SHA-256 protects against accidental download corruption. The checksum comes
from our same GitHub release, rather than from an independent signing key. This uses
the inherited Slot updater, not Unslot's separately signed `.pak` format.

## Complete builds only

Every release contains all previous working Slot modifications and the pinned older mGBA
core (`c758314a639aa0066e7b65a8341448181b73c804`). The older core is rebuilt from
source by `.github/scripts/build-stable-mgba.sh` and replaces the upstream core before
the release archive is packaged. Its modified source is published as a separate GitHub release asset (`mgba-c758314a639aa0066e7b65a8341448181b73c804-source.tar.gz`) next to each firmware ZIP; a small source/license notice is retained in `System/licenses/`.

Every release preserves all previous working changes. The workflow checks that the new archive includes `System/slot`, its launcher, mGBA, gpSP,
Gambatte and the standard supporting files. Do not publish a partial hotkey or emulator-only
ZIP through this updater; the inherited launcher deletes `System/` files not listed
in the update manifest.

## Publishing a new release

- Update `.github/ota-version.txt` only when shipping a **functional firmware update**. Retain technical version identifiers and previous-release links for OTA compatibility. Preserve support for historical `-rgsp.N` and `-custom.N` update identifiers. The published Ver. 5 still uses `v1.16.0-rgsp.5`. Its installed updater cannot yet parse `-select.N`, so the next functional update must retain a suffix the existing firmware recognizes (for example `v1.16.0-custom.6` if upstream remains 1.16.0). Only later releases can switch to `-select.N` safely. The public title is always **select. slot. [upstream version] Ver. [revision]**.
- Update `RELEASE_NOTES.md` with **only the changes made since the previous release**. Keep the cumulative feature list in `README.md`.
- Verify the full `Build select. slot. H700` GitHub Actions run succeeds on `main`.
- A successful verified build on `main` publishes `slot-v<VERSION>-h700.zip` and
  `versions.json` to GitHub Releases with title **select. slot. [upstream version] Ver. [revision]** and
  the change-only notes from that build's `RELEASE_NOTES.md`. The separate tag workflow
  can publish the same tagged release when used.
- Verify the release on real H700 hardware before recommending it broadly.
- Updating from older firmware requires **one manual installation of the new full build**
  to switch the device's updater to this custom release channel.

BaseOS updates, when offered separately, still come from the official pvaibhav/BaseOS
project. No games, ROMs, copyrighted BIOS dumps or personal save files are distributed.
