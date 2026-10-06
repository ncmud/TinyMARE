const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const os = target.result.os.tag;
    if (os != .macos and os != .linux) @panic("Supported targets are macOS and Linux");
    const name = b.option([]const u8, "name", "Default game name") orelse "TinyMARE";
    const port = b.option(u16, "port", "Default TCP port") orelse 7348;
    const email = b.option([]const u8, "email", "Default administrator email") orelse "admin@localhost";
    if (port == 0) @panic("port must be between 1 and 65535");
    const stack_down = b.option(bool, "stack-grows-down", "Target stack direction") orelse true;
    const config = b.addConfigHeader(.{ .include_path = "main.h" }, .{
        .DEFAULT_MUDNAME = name,
        .DEFAULT_PORT = port,
        .DEFAULT_EMAIL = email,
        .STACK_GROWS_DOWN = if (stack_down) @as(?bool, true) else null,
        .ARCH_64BIT = if (target.result.ptrBitWidth() == 64) @as(?bool, true) else null,
    });
    const mod = b.createModule(.{
        .target = target,
        .optimize = optimize,
        .link_libc = true,
    });
    mod.addConfigHeader(config);
    mod.addIncludePath(b.path("src/hdrs"));
    mod.addCSourceFiles(.{
        .files = &.{
            "src/comm/admin.c",   "src/comm/com.c",        "src/comm/create.c", "src/comm/give.c",
            "src/comm/look.c",    "src/comm/move.c",       "src/comm/set.c",    "src/comm/speech.c",
            "src/db/attrib.c",    "src/db/compress.c",     "src/db/convert.c",  "src/db/destroy.c",
            "src/db/inherit.c",   "src/db/load.c",         "src/db/runtime.c",  "src/db/save.c",
            "src/game/command.c", "src/game/help.c",       "src/game/match.c",  "src/game/player.c",
            "src/game/powers.c",  "src/game/predicates.c", "src/game/queue.c",  "src/game/unparse.c",
            "src/io/console.c",   "src/io/dns.c",          "src/io/file.c",     "src/io/html.c",
            "src/io/ident.c",     "src/io/mail.c",         "src/io/net.c",      "src/io/server.c",
            "src/io/user.c",      "src/prog/boolexp.c",    "src/prog/ctrl.c",   "src/prog/eval.c",
            "src/prog/hash.c",    "src/mare/config.c",     "src/mare/crypt.c",  "src/mare/rand.c",
            "src/mare/stats.c",   "src/mare/timer.c",      "src/mare/utils.c",  "src/mare/version.c",
        },
        .flags = &.{ "-std=gnu11", "-Wall", "-Wno-pointer-sign" },
    });
    mod.linkSystemLibrary("resolv", .{});
    mod.linkSystemLibrary("m", .{});
    const exe = b.addExecutable(.{ .name = "netmare", .root_module = mod });
    b.installArtifact(exe);

    const run = b.addSystemCommand(&.{"sh"});
    run.addFileArg(b.path("tools/run"));
    run.addArtifactArg(exe);
    if (b.args) |args| run.addArgs(args);
    b.step("run", "Start the game using the run directory").dependOn(&run.step);

    const smoke = b.addSystemCommand(&.{"python3"});
    smoke.addFileArg(b.path("tests/smoke.py"));
    smoke.addArtifactArg(exe);
    b.step("test", "Test a real server with a temporary database (requires Python 3)").dependOn(&smoke.step);
}
