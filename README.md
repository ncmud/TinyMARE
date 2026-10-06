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

## Connect and save

Connect with `telnet localhost 7348` or a MUD client. A new database starts
with only Limbo. Type `New` to create a character; the first character must
connect from localhost and becomes the administrator.

Use `@dump` to save and `@shutdown` as administrator to save and stop.
Outside Xcode, the server runs in the background; Ctrl-C does not stop it.
The database is `run/db/mdb`, and logs are in `run/logs/`.
