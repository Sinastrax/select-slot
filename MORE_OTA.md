# more. slot. test OTA channel

More.slot has its own test OTA feed at the `more-slot` branch's `versions.json`. Test 4
established that feed. Every later More.slot test update is delivered from a running More.slot
test installation through **Settings → System → Check for Updates**.

Pull requests and feature-branch builds do not publish or advance the feed. A complete, verified
build is published only after it reaches `more-slot`; publishing updates only that branch's test
manifest. Test releases are prereleases and never use GitHub's latest-release URL.

The stable select.slot updater uses its separate stable manifest. It cannot see More.slot test
releases, and More.slot test releases cannot change the stable select.slot feed. Build artifacts
in GitHub Actions are internal build outputs; user-facing test updates are through OTA.

The OTA contains a complete `System/` update, not a partial core patch. The RG35XX H is the
primary test target.
