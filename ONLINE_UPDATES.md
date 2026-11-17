# Online updates for the custom RGSP firmware

The firmware inherits Slot's existing **Settings → System → Check for Updates** interface.
Our `patches/rgsp-online-updates.patch` redirects that interface to **this repository's**
GitHub Releases. It does not fetch releases from pvaibhav's fork.

## How a custom update works

1. Connect the device to Wi-Fi and select **Settings → System → Check for Updates**.
2. The UI downloads `versions.json` from the latest stable GitHub Release for this repository.
3. The updater compares the embedded custom version with the release's version. It also
   understands the older pvaibhav version so users can migrate.
4. If you approve an update, the updater downloads the complete
   `slot-v<VERSION>-h700.zip`, checks its declared size and SHA-256 digest, and stages
   its `System/` contents in `System.new/`.
5. On restart the existing Slot launcher installs the staged `System/` files. Saves,
   ROMs and settings outside `System/` are not part of the update.

**Important:** SHA-256 protects against accidental download corruption. The checksum comes
from our same GitHub release, rather than from an independent signing key. This uses
the inherited Slot updater, not Unslot's separately signed `.pak` format.

## Complete builds only

Releases always contain all previous working Slot modifications and the pinned old mGBA
core (`c758314a639aa0066e7b65a8341448181b73c804`). The older core is rebuilt from
source by `.github/scripts/build-stable-mgba.sh` and replaces the upstream core before
the release archive is packaged. Its modified source is retained under `System/licenses/`.

The workflow checks that the new archive includes `System/slot`, its launcher, mGBA, gpSP,
Gambatte and the standard supporting files. Do not publish a partial hotkey or emulator-only
ZIP through this updater; the inherited launcher deletes `System/` files not listed
in the update manifest.

## Publishing a new release

- Update `.github/ota-version.txt` to the next `1.15.3-rgsp.N` version (or bump
  upstream version appropriately after rebasing and testing).
- Verify the full `Build custom Slot H700` GitHub Actions run succeeds on `main`.
- Create and push the exact matching `v<VERSION>` tag. The same workflow builds the
  complete package again, verifies the archive's digest and version, then publishes
  `slot-v<VERSION>-h700.zip` and `versions.json` to GitHub Releases.
- Verify the release on real H700 hardware before recommending it broadly.
- Updating from older firmware requires **one manual installation of the new full build**
  to switch the device's updater to this custom release channel.

BaseOS updates, when offered separately, still come from the official pvaibhav/BaseOS
project. No games, ROMs, copyrighted BIOS dumps or personal save files are distributed.
