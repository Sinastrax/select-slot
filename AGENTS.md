# Working on select. slot.

The maintainer builds select. slot. for the combination of performance, appearance, and features they want to use on their own handhelds. These conventions apply across the repository.

## Delivering updates

- Deliver functional Anbernic H700 updates through **Settings → System → Check for Updates**, including builds the maintainer will test on hardware. Give the build a new OTA revision, follow [the publishing procedure](ONLINE_UPDATES.md), and verify the published manifest, ZIP size, and checksum. A pull-request artifact alone leaves delivery incomplete.
- Distribute Miyoo Mini updates as separate manual SD-card downloads. Keep them off the H700 OTA channel.
- Use **select. slot. [upstream version] Ver. [revision]** as the public release title. Keep technical identifiers compatible with installed updaters. Documentation and branding-only release renames do not need a new firmware revision.
- Describe only that version’s changes in its release notes. During release cleanup, keep the latest builds and confirmed improvements or useful rollback points. Preserve update compatibility when renaming releases.

## Interpreting hardware feedback

- The regular test devices are RG SP, RG34XXSP (first version), RG35XX H, and original Miyoo Mini. When the maintainer reports “works” or “tested,” apply that result to every compatible device in this lineup unless they specify an exception. An H700-only change therefore covers the three Anbernic devices.
- Record CI and package verification separately from a hardware result. Use **Tested** for devices covered by the maintainer’s confirmation. Give RG SP and RG35XXSP separate compatibility entries. Original Miyoo Mini results cover that model.
- Reproduce issues using the reported core, settings, and device. When integrating upstream or fixing another model, check the previously confirmed behavior on affected paths.

## Preserving device behavior

- Keep scaling choices per system, with Fit as the default. On Anbernic, turning Color Correction off preserves the selected shader effect. Pocket SGB uses mGBA, the SGB palette, and Pocket Color’s pixel separation and white tone.
- Preserve the original Miyoo Mini’s working mGBA display behavior and Onion boot, shutdown, sleep, and wake behavior. Keep its hardware-specific choices separate from the Anbernic build.
- Preserve the manifest-based System update and user configuration. Keep shortcut mappings when improving their documentation. The on-device guide should surface hard-to-discover actions with labels that fit the RG35XX H. Check related menus when a layout defect recurs.

## Maintaining the project front page

- Keep the README comprehensive. Include the compatibility table and testing status, inherited features and local changes, controls, installation and update paths, limitations, and visual references. Identify which build provides each feature.
- Credit original Slot, pvaibhav’s H700 fork, and deanmarano’s Miyoo port. Preserve upstream licenses and attribution when incorporating changes.
- Prepare the current repository before migrating to an official fork. Retain repository protections and the maintainer’s authorized workflow.
