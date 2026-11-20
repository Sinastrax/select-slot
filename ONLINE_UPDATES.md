# Online updates for select. slot.

The firmware inherits Slot's existing **Settings → System → Check for Updates** interface.
Our `patches/select-online-updates.patch` redirects that interface to **this repository's**
GitHub Releases. It does not fetch releases from pvaibhav's fork.

## Separate H700 test OTA

The `integration/slot-1.16.0-armgba` branch publishes complete test builds as GitHub
prereleases. Those builds embed a different manifest address, on the `test-ota` branch.
Each successful build publishes its ZIP and source archives, then advances only that test
manifest. The stable build continues to use GitHub's stable latest release and its
`.github/ota-version.txt`; a test build cannot become the stable updater's offer.

To enter the test channel from stable firmware, install the first test ZIP once using the
manual SD-card update method. After that, **Settings → System → Check for Updates** follows
the test manifest and installs later test builds. Test-channel builds keep following that
feed after update.

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

- Update [`.github/ota-version.txt`](.github/ota-version.txt) when shipping a **complete verified firmware release**, including maintenance releases. The existing updater recognizes technical identifiers such as `1.16.0-rgsp.N`; retain that identifier format for compatibility with older installed versions. The user-facing title follows **select. slot. [upstream version] Ver. [revision]**. Never bump the version for a documentation-only change.
- Update `RELEASE_NOTES.md` with **only the changes made since the previous release**. Keep the cumulative feature list in `README.md`.
- Verify the full `Build select. slot. H700` GitHub Actions run succeeds on `main`.
- A successful verified push build on `main` publishes `slot-v<VERSION>-h700.zip`,
  `versions.json`, and the corresponding mGBA source archive to GitHub Releases
  using the release's version-specific `RELEASE_NOTES.md`. An existing release
  is never overwritten, and manually built/tag-triggered artifacts cannot
  displace the newest H700 release.
- Verify the release on real H700 hardware before recommending it broadly.
- Updating from older firmware requires **one manual installation of the new full build**
  to switch the device's updater to this custom release channel.

The [H700 maintenance guide](H700_MAINTENANCE.md) documents the pinned patch order, non-destructive publisher and regression tests.

BaseOS updates, when offered separately, still come from the official pvaibhav/BaseOS
project. No games, ROMs, copyrighted BIOS dumps or personal save files are distributed.
