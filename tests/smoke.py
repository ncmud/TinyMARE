#!/usr/bin/env python3
"""Exercise a real server in a temporary game directory, then reload its database."""
import argparse
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', type=Path)
    args = parser.parse_args()
    executable = args.executable.resolve(strict=True)
    assets = Path(__file__).resolve().parents[1] / 'run'
    with tempfile.TemporaryDirectory(prefix='mare-smoke-') as directory:
        runtime = Path(directory)
        for name in ('msgs', 'help'):
            shutil.copytree(assets / name, runtime / name)
        for name in ('logs', 'db', 'mail'):
            (runtime / name).mkdir()
        # Skip optional introductory pages so this check tests the game itself.
        for name in ('welcome.txt', 'prologue.txt', 'motd.txt'):
            (runtime / 'msgs' / name).write_text('')
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0))
            port = reservation.getsockname()[1]
        env = dict(os.environ, WATCHDOG='1')  # Keep the server as a child process.
        process = None
        connection = None

        def start():
            nonlocal process, connection
            process = subprocess.Popen([str(executable), str(port)], cwd=runtime, env=env,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise AssertionError('Server exited during startup')
                try:
                    connection = socket.create_connection(('127.0.0.1', port), timeout=.5)
                    connection.settimeout(.2)
                    return
                except OSError:
                    time.sleep(.1)
            raise AssertionError('Server did not accept a connection')

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

        def command(text, expected):
            connection.sendall(text.encode() + b'\r\n')
            return expect(expected)

        def shutdown():
            command('@shutdown', 'Going Down')
            process.wait(timeout=10)
            assert process.returncode == 0, process.returncode
            connection.close()

        try:
            start()
            expect('type new:')
            command('New', 'choose a name')
            command('Portability', 'Enter new password:')
            command('Temporary-test-7348', 'Retype for verification:')
            command('Temporary-test-7348', 'First and Last name?')
            command('Test Operator', 'Email Address?')
            command('None', 'available to other players?')
            command('n', "character's gender?")
            command('m', 'ANSI Terminal Emulation?')
            command('n', 'registered.')
            command('', 'Press Enter to Continue')
            command('', 'Limbo(#0R)')
            command('@pemit me=Result-[add(2,3)]', 'Result-5')
            command('@create Keepsake', 'created')
            command('@dump', 'Checkpoint Done')
            shutdown()
            assert (runtime / 'db' / 'mdb').stat().st_size > 0
            start()
            expect('type new:')
            command('Portability', 'Password:')
            command('Temporary-test-7348', 'Limbo(#0R)')
            command('inventory', 'Keepsake')
            command('@pemit me=Reload-[add(2,3)]', 'Reload-5')
            shutdown()
            logs = (runtime / 'logs' / 'main').read_text()
            assert 'Runtime Malfunction' not in logs, logs
            print('PASS: character creation, login, expression evaluation, object creation, '
                  'database save/reload, and clean shutdown')
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
