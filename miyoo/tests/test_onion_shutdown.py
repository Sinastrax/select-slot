import importlib.util
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('onion_shutdown', root / 'onion_shutdown.py')
shutdown = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shutdown)


class OnionShutdown(unittest.TestCase):
    def run_handoff(self, *, onion=True, model='283', status=0, off_order=True, native=False):
        with TemporaryDirectory() as tmp:
            card = Path(tmp)
            binary = card / '.tmp_update/bin'
            binary.mkdir(parents=True)
            if onion:
                marker = card / '.tmp_update/onionVersion/version.txt'
                marker.parent.mkdir()
                marker.touch()
            detect_key = binary / 'detectKey'
            detect_key.write_text(
                '#!/bin/sh\n'
                'test "$1" = 116 || exit 2\n'
                'if [ -e "$SD/released" ]; then exit 1; fi\n'
                'touch "$SD/released"\n'
            )
            detect_key.chmod(0o755)
            if native:
                detect_key.write_text(
                    detect_key.read_text().replace(
                        'then exit 1;', 'then rm -f "$SD/.offOrder"; exit 1;'
                    )
                )
                (binary / 'shutdown').write_text(
                    'test -f "$SD/shutting_down" || exit 2\n'
                    'test ! -f "$SD/.offOrder" || exit 3\n'
                    'echo called >> "$SD/native-shutdown"\n'
                    'exit 7\n'
                )
                checkoff = binary.parent / 'checkoff'
                checkoff.mkdir()
                (checkoff / 'capture.sh').write_text('touch "$SD/checkoff-ran"\n')
            (card / 'deviceModel').write_text(model)
            guard = card / 'guard'
            guard.touch()
            if off_order:
                (card / '.offOrder').touch()
            hook = shutdown.AFTER_EXIT.replace('/tmp/.offOrder', '$SD/.offOrder')
            hook = hook.replace('/tmp/deviceModel', '$SD/deviceModel')
            hook = hook.replace('/tmp/shutting_down', '$SD/shutting_down')
            hook = 'SD="$1"; LOGS="$SD"; guard="$SD/guard"; status="$2"; export SD\n' + hook
            subprocess.run(['sh', '-e', '-c', hook, 'test', tmp, str(status)], check=True)
            if native:
                self.assertEqual((card / 'native-shutdown').read_text(), 'called\n')
                self.assertTrue((card / 'checkoff-ran').is_file())
                self.assertIn('shutdown unexpectedly returned (7)', (card / 'slot-launch.txt').read_text())
            return guard.exists(), (card / 'released').exists()

    def test_original_mini_waits_for_release_and_clears_clean_shutdown_guard(self):
        self.assertEqual(self.run_handoff(), (False, True))

    def test_plus_clears_guard_without_waiting_for_power(self):
        self.assertEqual(self.run_handoff(model='354'), (False, False))

    def test_crash_preserves_guard_even_when_shutdown_is_requested(self):
        self.assertEqual(self.run_handoff(status=139), (True, True))

    def test_stock_or_unrequested_exit_preserves_existing_guard(self):
        self.assertEqual(self.run_handoff(onion=False), (True, False))
        self.assertEqual(self.run_handoff(off_order=False), (True, False))

    def test_shutdown_survives_order_marker_disappearing_during_release_wait(self):
        self.assertEqual(self.run_handoff(native=True), (False, True))
