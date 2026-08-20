import sys

import pytest


@pytest.fixture(autouse=True)
def reset_known_contract():
    yield
    gl = sys.modules.get("genlayer.gl")
    if gl is not None:
        known = getattr(gl, "genvm_contracts", None)
        if known is not None and hasattr(known, "__known_contract__"):
            known.__known_contract__ = None
