import platform
from pathlib import Path

from .autd3capi_emulator import NativeMethods as Emulator

_PLATFORM = platform.system()
_PREFIX = ""
_BIN_EXT = ""
if _PLATFORM == "Windows":
    _BIN_EXT = ".dll"
elif _PLATFORM == "Darwin":
    _PREFIX = "lib"
    _BIN_EXT = ".dylib"
elif _PLATFORM == "Linux":
    _PREFIX = "lib"
    _BIN_EXT = ".so"
else:
    err = "Not supported OS"
    raise ImportError(err)

_LIB_PATH = Path(__file__).parent.parent / "bin"

Emulator().init_dll(_LIB_PATH, _PREFIX, _BIN_EXT)
