#!/usr/bin/env python3
"""Check the bundled demo for personal data and exercise it in a temporary game."""
import argparse
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', type=Path)
    executable = parser.parse_args().executable.resolve(strict=True)
    root = Path(__file__).resolve().parents[1]
    fixture = root / 'examples' / 'azure-demo.mdb'
    seed = fixture.read_bytes()

    # Inspect the decoded database, since its attributes use compression.
    with tempfile.TemporaryDirectory(prefix='mare-demo-audit-') as directory:
        result = subprocess.run([str(executable), '-t', str(fixture)], cwd=directory,
                                capture_output=True, timeout=20)
        assert result.returncode == 0, result.stderr.decode('latin1')
        audit = result.stdout.decode('latin1')
        assert re.findall(r'^Rlname:(.*)$', audit, re.M) == ['Demo Account']
        assert re.findall(r'^Email:(.*)$', audit, re.M) == ['None']
        assert not re.search(r'^(Lastfrom|Created|Modified):', audit, re.M)
        assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', audit)
        assert audit.count('Type:  Player') == 1
        assert 'DemoAdmin(#1P)' in audit

    with tempfile.TemporaryDirectory(prefix='mare-demo-') as directory:
        runtime = Path(directory)
        for name in ('msgs', 'help', 'etc', 'maps'):
            shutil.copytree(root / 'run' / name, runtime / name)
        for name in ('db', 'logs', 'mail'):
            (runtime / name).mkdir()
        shutil.copyfile(fixture, runtime / 'db' / 'mdb')
        for name in ('welcome.txt', 'prologue.txt', 'motd.txt'):
            (runtime / 'msgs' / name).write_text('')
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0))
            port = reservation.getsockname()[1]
        process = None
        connection = None

        def expect(expected):
            output = ''
            deadline = time.monotonic() + 12
            while time.monotonic() < deadline:
                try:
                    data = connection.recv(65536)
                except socket.timeout:
                    continue
                if not data:
                    break
                output += data.decode('latin1')
                plain = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', output)
                if expected in plain:
                    return plain
            raise AssertionError(f'Expected {expected!r}, received {output!r}')

        def command(value, expected):
            connection.sendall(value.encode() + b'\r\n')
            return expect(expected)

        def start(room):
            nonlocal process, connection
            with (runtime / 'process.log').open('ab') as diagnostics:
                process = subprocess.Popen([str(executable), str(port)], cwd=runtime,
                                           env=dict(os.environ, WATCHDOG='1'),
                                           stdout=diagnostics, stderr=diagnostics)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                assert process.poll() is None, 'Server exited during startup'
                try:
                    connection = socket.create_connection(('127.0.0.1', port), timeout=.5)
                    break
                except OSError:
                    time.sleep(.1)
            else:
                raise AssertionError('Server did not accept a connection')
            connection.settimeout(.2)
            expect('type new:')
            command('DemoAdmin', 'Password:')
            command('demo-local-only', room)

        def shutdown():
            command('@shutdown', 'Going Down')
            process.wait(timeout=10)
            assert process.returncode == 0, process.returncode
            connection.close()

        try:
            start('Azure(#2R)')
            command('@search type=Room', '10 objects found.')
            command('@search type=Thing', '22 objects found.')
            command('@teleport #0', 'Limbo(#0R)')
            command('Learn', 'Azure(#2R)')
            command('VM', 'VM(#5R)')
            command('look', 'IAAS where you maintain the OS')
            command('Azure', 'Azure(#2R)')
            command('@teleport #0', 'Limbo(#0R)')
            command('@create DemoKeepsake', 'created')
            command('@dump', 'Dumping...')
            # This seed has no log channel subscription; observe the actual save.
            deadline = time.monotonic() + 10
            while (runtime / 'db' / 'mdb').read_bytes() == seed:
                assert time.monotonic() < deadline, 'Database save did not finish'
                time.sleep(.1)
            shutdown()
            start('Limbo(#0R)')
            command('inventory', 'DemoKeepsake')
            command('@search type=Room', '10 objects found.')
            shutdown()
            assert 'Runtime Malfunction' not in (runtime / 'logs' / 'main').read_text()
            assert fixture.read_bytes() == seed, 'Bundled seed changed'
            print('PASS: demo profile, login, rooms, exits, descriptions, object creation, '
                  'save/reload, and shutdown')
        except Exception:
            for path in [runtime / 'process.log', *sorted((runtime / 'logs').iterdir())]:
                if path.is_file():
                    print(f'--- {path.relative_to(runtime)} ---', file=sys.stderr)
                    print(path.read_text(errors='replace'), file=sys.stderr)
            raise
        finally:
            if connection:
                connection.close()
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == '__main__':
    main()
