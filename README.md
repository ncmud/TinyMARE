# TinyMARE on macOS, Linux, and BSD

[![CMake CI](https://github.com/ncmud/TinyMARE/actions/workflows/cmake.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/cmake.yml)
[![FreeBSD CI](https://github.com/ncmud/TinyMARE/actions/workflows/freebsd.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/freebsd.yml)
[![NetBSD CI](https://github.com/ncmud/TinyMARE/actions/workflows/netbsd.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/netbsd.yml)
[![OpenBSD CI](https://github.com/ncmud/TinyMARE/actions/workflows/openbsd.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/openbsd.yml)
[![Zig CI](https://github.com/ncmud/TinyMARE/actions/workflows/zig.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/zig.yml)

TinyMARE is Byron Stanoszek's (Gandalf's) code from WindsMARE. We host this
repository for archival purposes, preserving his work and making it easier for
people to jump in, build the server, and explore the game on modern systems.
The original code belongs to its authors; our additions provide build tooling,
portability fixes, and instructions for getting started.

This archive is based on TinyMARE 1.0.10340. The original releases are available
in the [WindsMARE TinyMARE release archive](https://www.winds.org/pub/tinymare/).
See [LICENSE](LICENSE) for the original copyright notice and terms.

![WindsMARE's colorful ASCII welcome screen and character login prompt](docs/images/windsmare-login.png)

Both CMake and Zig compile the existing C game. Neither requires converting it
to another language. Builds generate their own configuration header and leave
`src/hdrs/main.h` and the source version unchanged.

## CMake

Requires CMake 3.18+ and GCC or Clang. On macOS, install the Xcode Command Line
Tools; on Linux, install your distribution's C compiler, CMake, and libc headers.
FreeBSD, NetBSD, and OpenBSD use the same CMake commands. Install CMake and
Python 3 with the system package manager; their base systems provide a C compiler.
BSD CI builds the server and runs the smoke tests in native FreeBSD 14.3,
NetBSD 10.1, and OpenBSD 7.8 virtual machines.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
cmake --build build --target run
```

The executable is `build/netmare`. To use a different port for one launch:

```sh
./tools/run build/netmare 7349
```

Optional defaults are `-DMARE_NAME=MyMARE`, `-DMARE_PORT=7348`, and
`-DMARE_EMAIL=admin@example.com`, passed to the first command.

### Xcode

Install the full Xcode app and CMake, then generate a separate Xcode project
from the repository root:

```sh
mkdir -p run/db run/logs run/mail
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  cmake -S . -B build-xcode -G Xcode
open build-xcode/TinyMARE.xcodeproj
```

Choose the `netmare` scheme and **My Mac**, then press **Run** (Cmd-R). CMake
configures the scheme to use `run/` as its working directory and sets
`WATCHDOG=1` so the server stays attached to Xcode's debugger. Connect a MUD
client to `localhost:7348`; the Xcode console displays server output. Stop it
with `@shutdown` to save the database before ending the debugging session.

To change the port, open **Product → Scheme → Edit Scheme → Run → Arguments**
and add a port such as `7349` under **Arguments Passed On Launch**. Stop any
server already listening on that port before running the scheme. The Xcode
scheme uses your main `run/db/mdb` database; to debug the example world, prepare
its runtime as described below and change the scheme's working directory to
`examples/azure-demo/` under **Run → Options**.

## Zig

Tested with Zig 0.15.2. Zig supplies the C compiler and build runner.

```sh
zig build -Doptimize=ReleaseFast
zig build run -Doptimize=ReleaseFast
```

The executable is `zig-out/bin/netmare`. Optional defaults are `-Dname=MyMARE`,
`-Dport=7348`, and `-Demail=admin@example.com`. Pass a launch port after `--`:

```sh
zig build run -Doptimize=ReleaseFast -- 7349
```

On this Mac, Zig 0.15.2 cannot link its build runner against the Xcode 27 SDK's
ARM library stubs. The installed Command Line Tools SDK works. Prefix Zig
commands with this environment setting (no global Xcode change is needed):

```sh
DEVELOPER_DIR=/Library/Developer/CommandLineTools zig build -Doptimize=ReleaseFast
DEVELOPER_DIR=/Library/Developer/CommandLineTools zig build run -Doptimize=ReleaseFast
```

Zig can also build a Linux executable from this Mac:

```sh
DEVELOPER_DIR=/Library/Developer/CommandLineTools zig build \
  -Dtarget=x86_64-linux-musl -Doptimize=ReleaseFast --prefix zig-out-linux
```

The resulting `zig-out-linux/bin/netmare` runs on x86-64 Linux; copy the `run`
assets along with it.

The original interactive `src/configure` and Makefiles remain available; see
`INSTALL` for that workflow.

## Running and stopping

Run steps create `run/db` and `run/logs`, then start the server on TCP port 7348
by default. The server detaches into the background. Logs are in `run/logs/main`
and `run/logs/io`; game data is in `run/db/mdb`. Ctrl-C in the launching terminal
does not stop a detached server.

Connect with `telnet localhost 7348` or a MUD client using host `localhost` and
port `7348`. Type `New` to create a character. The first character becomes the
administrator and must be created from localhost. The bundled welcome text still
uses the original WindsMARE branding; the default game name is TinyMARE.

Use `@dump` in the game to save, and `@shutdown` as administrator to save and
stop. If no administrator exists yet, find the listener with
`lsof -nP -iTCP:7348 -sTCP:LISTEN` and send `kill -TERM <PID>` for a graceful stop.
Stop the existing server before launching another build on the same port.

## Example world

The bundled [Azure demo database](examples/azure-demo.mdb) is adapted from
[Eric Angell's MareMac example](https://github.com/erangell/kfest2024/blob/ba77ec2fb88e29f01d71256f2f34be5a29ad31a2/MareMac/run/db/mdb)
in his KansasFest 2024 project. Credit for the educational world content belongs
to its upstream author. It contains 10 rooms, 18 exits, and 22 informational
objects about Azure. It demonstrates world building rather than combat or quests.

The bundled copy replaces the upstream player with a generic `DemoAdmin`
account, resets its password and activity history, replaces its profile with synthetic placeholders,
clears object timestamps, and uses the server's default configuration. It contains
no data from your local game. TinyMARE requires an administrator account when
loading an existing database.

After building, run these commands from the repository root to prepare a separate
example game. Its runtime directory and local saves are ignored by Git:

```sh
mkdir -p examples/azure-demo/db examples/azure-demo/logs examples/azure-demo/mail
cp -R run/msgs run/help run/etc run/maps examples/azure-demo/
cp examples/azure-demo.mdb examples/azure-demo/db/mdb
(cd examples/azure-demo && ../../build/netmare 7349)
```

For Zig, substitute `../../zig-out/bin/netmare` in the last command. Connect to
`localhost:7349` and log in as `DemoAdmin` with password `demo-local-only`.
This is a public demo password; run `@passwd` and follow its prompts before
making the example accessible to others. You start in Azure; type `exits` to see
the available destinations and `VM` to visit the virtual-machine room. Use `@search` to list all objects.

Use `@dump` to save and `@shutdown` to save and stop the example. Copying the
bundled database into the runtime directory again resets the example and
replaces its local saves. The checked-in database is a seed; run the copied
runtime database so your own account changes and game activity stay out of Git.

For an online world to explore, the
[MicroMARE connection instructions](https://github.com/erangell/kfest2024/blob/main/readme.md)
list `mare.hoardersheaven.net:4201` with guest access. That is a separate hosted
world; the Azure database above is the locally runnable example.
