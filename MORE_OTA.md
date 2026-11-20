# more. slot. test OTA channel

`more. slot.` uses a test-only update feed. Its firmware points to the `more-slot` branch's
`versions.json`, and the workflow publishes each tested build as a GitHub prerelease. It never
uses GitHub's latest-release URL and never publishes a test build as stable.

## First installation

The current stable select.slot. firmware does not offer more.slot. test prereleases. Install the
first downloadable `more. slot.` test ZIP manually on the testing handheld. That build is then
configured to check the isolated test feed at **Settings → System → Check for Updates**.

## Later test updates

When a newer more.slot. build is published, its prerelease manifest is written to the `more-slot`
branch. Devices already running a more.slot. test build read only that manifest and download the
matching tagged ZIP after the usual confirmation. Stable select.slot. devices continue to read the
stable latest-release manifest and cannot see these test updates.

The ZIP is a complete `System/` update, not a partial core patch. Test only on a device you can
restore manually. The initial target is the Anbernic RG35XX-H.
