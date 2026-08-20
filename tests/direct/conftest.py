import os
import sys

import pytest


# gltest injects its message context by duplicating a temporary file onto fd 0
# and then unlinking it. Windows does not allow unlinking that still-open file.
# Keep this strictly test-local workaround narrow: only suppress that WinError.
if sys.platform == "win32":
    _unlink = os.unlink

    def _windows_safe_unlink(path, *args, **kwargs):
        try:
            _unlink(path, *args, **kwargs)
        except PermissionError:
            if str(path).lower().startswith(os.getenv("TEMP", "").lower()):
                return
            raise

    os.unlink = _windows_safe_unlink


@pytest.fixture(autouse=True)
def reset_known_contract():
    yield
    gl = sys.modules.get("genlayer.gl")
    if gl is not None:
        known = getattr(gl, "genvm_contracts", None)
        if known is not None and hasattr(known, "__known_contract__"):
            known.__known_contract__ = None
