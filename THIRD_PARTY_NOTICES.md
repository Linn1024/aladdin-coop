# Source and notices

The `engine/` directory contains modified Genesis Plus GX sources. Original
project: https://github.com/ekeeke/Genesis-Plus-GX . The exact upstream revision
of the imported source snapshot was not recorded.

Retain [engine/LICENSE.txt](engine/LICENSE.txt), the original copyright headers,
and the component-specific license files throughout the source tree. The engine
license includes noncommercial redistribution conditions and a requirement to
provide complete source for modified builds; this repository retains the engine
source and its bundled dependencies. Individual components have their own terms.
No blanket MIT/GPL license is asserted for the combined project.

Co-op behavior is implemented in `engine/core/m68k/aladdin_coop.h`, with engine
integration and probe exports. The frontends are `launcher.cpp` and
`bizhawk/aladdin_libretro.cpp`, sharing `debug_menu.h`.

The Aladdin game ROM is not included. Players must supply the supported ROM.
Local game saves, disassemblies, emulator profiles, and debug captures are excluded.
