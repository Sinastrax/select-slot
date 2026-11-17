# Online updates for Custom slot

The firmware inherits Slot's existing **Settings → System → Check for Updates** interface.
Our `patches/rgsp-online-updates.patch` redirects that interface to **this repository's**
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

Releases always contain all previous working Slot modifications and the pinned old mGBA
core (`c758314a639aa0066e7b65a8341448181b73c804`). The older core is rebuilt from
source by `.github/scripts/build-stable-mgba.sh` and replaces the upstream core before
the release archive is packaged. Its modified source is retained under `System/licenses/`.

Every release preserves all previous working changes. The workflow checks that the new archive includes `System/slot`, its launcher, mGBA, gpSP,
Gambatte and the standard supporting files. Do not publish a partial hotkey or emulator-only
ZIP through this updater; the inherited launcher deletes `System/` files not listed
in the update manifest.

## Publishing a new release

- Update `.github/ota-version.txt` to the next `1.15.3-custom.N` version (or bump
  upstream version appropriately after rebasing and testing).
- Update `RELEASE_NOTES.md` with **only the changes made since the previous release**. Keep the cumulative feature list in `README.md`.
- Verify the full `Build Custom slot H700` GitHub Actions run succeeds on `main`.
- A successful verified build on `main` publishes `slot-v<VERSION>-h700.zip` and
  `versions.json` to GitHub Releases with title **Custom slot. Ver. [version]** and
  the change-only notes from that build's `RELEASE_NOTES.md`. The separate tag workflow
  can publish the same tagged release when used.
- Verify the release on real H700 hardware before recommending it broadly.
- Updating from older firmware requires **one manual installation of the new full build**
  to switch the device's updater to this custom release channel.

BaseOS updates, when offered separately, still come from the official pvaibhav/BaseOS
project. No games, ROMs, copyrighted BIOS dumps or personal save files are distributed.
