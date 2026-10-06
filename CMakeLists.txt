cmake_minimum_required(VERSION 3.18)
project(TinyMARE VERSION 1.0.10340 LANGUAGES C)

# The server uses GNU C extensions and pre-C23 function declarations.
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)
if(NOT CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
  message(FATAL_ERROR "TinyMARE requires GCC or Clang")
endif()

set(MARE_NAME "TinyMARE" CACHE STRING "Default game name")
set(MARE_PORT 7348 CACHE STRING "Default TCP port")
set(MARE_EMAIL "admin@localhost" CACHE STRING "Default administrator email")
if(NOT MARE_PORT MATCHES "^[0-9]+$" OR MARE_PORT LESS 1 OR MARE_PORT GREATER 65535)
  message(FATAL_ERROR "MARE_PORT must be between 1 and 65535")
endif()
foreach(setting MARE_NAME MARE_EMAIL)
  string(REPLACE "\\" "\\\\" ${setting}_C "${${setting}}")
  string(REPLACE "\"" "\\\"" ${setting}_C "${${setting}_C}")
  string(REPLACE "\n" "\\n" ${setting}_C "${${setting}_C}")
  string(REPLACE "\r" "\\r" ${setting}_C "${${setting}_C}")
endforeach()

include(CheckTypeSize)
check_type_size("long" SIZEOF_LONG LANGUAGE C)
if(SIZEOF_LONG EQUAL 8)
  set(ARCH_64BIT 1)
endif()
include(CheckCSourceRuns)
check_c_source_runs("int main(void) {
  void *a=__builtin_alloca(1), *b=__builtin_alloca(1);
  return b < a ? 0 : 1;
}" STACK_GROWS_DOWN)
configure_file(cmake/main.h.in generated/main.h @ONLY)

add_executable(netmare
  src/comm/admin.c src/comm/com.c src/comm/create.c src/comm/give.c
  src/comm/look.c src/comm/move.c src/comm/set.c src/comm/speech.c
  src/db/attrib.c src/db/compress.c src/db/convert.c src/db/destroy.c
  src/db/inherit.c src/db/load.c src/db/runtime.c src/db/save.c
  src/game/command.c src/game/help.c src/game/match.c src/game/player.c
  src/game/powers.c src/game/predicates.c src/game/queue.c src/game/unparse.c
  src/io/console.c src/io/dns.c src/io/file.c src/io/html.c src/io/ident.c
  src/io/mail.c src/io/net.c src/io/server.c src/io/user.c
  src/prog/boolexp.c src/prog/ctrl.c src/prog/eval.c src/prog/hash.c
  src/mare/config.c src/mare/crypt.c src/mare/rand.c src/mare/stats.c
  src/mare/timer.c src/mare/utils.c src/mare/version.c)
target_include_directories(netmare PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/generated" src/hdrs)
target_compile_options(netmare PRIVATE -Wall -Wno-pointer-sign)
include(CheckCCompilerFlag)
check_c_compiler_flag(-Wformat-truncation HAVE_FORMAT_TRUNCATION)
if(HAVE_FORMAT_TRUNCATION)
  target_compile_options(netmare PRIVATE -Wno-format-truncation)
endif()
find_library(RESOLV_LIBRARY resolv REQUIRED)
target_link_libraries(netmare PRIVATE "${RESOLV_LIBRARY}" m)
install(TARGETS netmare RUNTIME DESTINATION bin)

add_custom_target(run
  COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/tools/run" $<TARGET_FILE:netmare>
  DEPENDS netmare USES_TERMINAL)

include(CTest)
if(BUILD_TESTING)
  find_package(Python3 COMPONENTS Interpreter)
  if(Python3_Interpreter_FOUND)
    add_test(NAME server-smoke COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/smoke.py" $<TARGET_FILE:netmare>)
    set_tests_properties(server-smoke PROPERTIES TIMEOUT 120)
  endif()
endif()
