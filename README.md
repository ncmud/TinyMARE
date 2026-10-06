# TinyMARE

[![CMake CI](https://github.com/ncmud/TinyMARE/actions/workflows/cmake.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/cmake.yml)
[![FreeBSD CI](https://github.com/ncmud/TinyMARE/actions/workflows/freebsd.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/freebsd.yml)
[![NetBSD CI](https://github.com/ncmud/TinyMARE/actions/workflows/netbsd.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/netbsd.yml)
[![OpenBSD CI](https://github.com/ncmud/TinyMARE/actions/workflows/openbsd.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/openbsd.yml)
[![Zig CI](https://github.com/ncmud/TinyMARE/actions/workflows/zig.yml/badge.svg?branch=trunk)](https://github.com/ncmud/TinyMARE/actions/workflows/zig.yml)

TinyMARE 1.0.10340 is Byron Stanoszek's (Gandalf's) C server from WindsMARE,
with build support for macOS, Linux, FreeBSD, NetBSD, and OpenBSD.
See the [original releases](https://www.winds.org/pub/tinymare/) and
[LICENSE](LICENSE) for the original copyright and terms.

![WindsMARE login screen](docs/images/windsmare-login.png)

## Build and run

Run these commands from the repository root. Choose CMake or Zig.

### CMake

Requires CMake 3.18+ and GCC or Clang. On macOS, install the Xcode Command Line
Tools. On Linux and BSD, install CMake and any missing compiler or libc headers.
Python 3 is optional for running tests.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
cmake --build build --target run
```

The executable is `build/netmare`. To launch on another port:

```sh
./tools/run build/netmare 7349
```

### Zig

Requires Zig 0.15.2, which includes the C compiler.

```sh
zig build -Doptimize=ReleaseFast
zig build run -Doptimize=ReleaseFast
```

The executable is `zig-out/bin/netmare`. For another port, use
`zig build run -Doptimize=ReleaseFast -- 7349`.
The original Makefile workflow is described in [INSTALL](INSTALL).

### Xcode

Requires the full Xcode app and CMake:

```sh
mkdir -p run/db run/logs run/mail
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  cmake -S . -B build-xcode -G Xcode
open build-xcode/TinyMARE.xcodeproj
```

Choose the `netmare` scheme and **My Mac**, then press **Run** (Cmd-R).
The scheme uses `run/` as its working directory and keeps the server attached
to the debugger. Set a different port in **Edit Scheme → Run → Arguments**.
To debug the example below, prepare its runtime and set the working directory
to `examples/azure-demo/` under **Run → Options**.

## Connect and save

Connect with `telnet localhost 7348` or a MUD client. A new database starts
with only Limbo. Type `New` to create a character; the first character must
connect from localhost and becomes the administrator.

Use `@dump` to save and `@shutdown` as administrator to save and stop.
Outside Xcode, the server runs in the background; Ctrl-C does not stop it.
The database is `run/db/mdb`, and logs are in `run/logs/`.

## Example world

The bundled [Azure teaching world](examples/azure-demo.mdb) comes from
[Eric Angell's KansasFest 2024 MareMac project](https://github.com/erangell/kfest2024/blob/ba77ec2fb88e29f01d71256f2f34be5a29ad31a2/MareMac/run/db/mdb).
It has 10 rooms, 18 exits, and 22 informational objects about Azure.
The original account's profile, credentials, and activity history have been
replaced with a generic demo account. This example has no combat or quests.

After building, copy the seed into a separate runtime directory:

```sh
mkdir -p examples/azure-demo/db examples/azure-demo/logs examples/azure-demo/mail
cp -R run/msgs run/help run/etc run/maps examples/azure-demo/
cp examples/azure-demo.mdb examples/azure-demo/db/mdb
(cd examples/azure-demo && ../../build/netmare 7349)
```

For Zig, substitute `../../zig-out/bin/netmare` in the last command.
Connect to `localhost:7349` as **DemoAdmin**, password **demo-local-only**.
Run `@passwd` to change this public password before allowing remote access.
Try `exits`, `VM`, and `@search`. Ordinary players' `@search` results are limited
to objects they own; from Limbo, use `Learn` to enter the teaching world.

The runtime and its saves are ignored by Git. Copying the seed again overwrites
local progress. Use `@dump` to save and `@shutdown` to stop.
