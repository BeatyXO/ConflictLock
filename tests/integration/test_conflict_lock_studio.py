import os

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get("GENLAYER_RUN_INTEGRATION"),
    reason="Set GENLAYER_RUN_INTEGRATION=1 with a configured Studio/StudioNet signer to run live integration tests.",
)


def test_contract_factory_can_load_and_deploy():
    from gltest import get_contract_factory
    from gltest.assertions import tx_execution_succeeded

    factory = get_contract_factory("ConflictLock")
    contract = factory.deploy()
    tx = contract.propose_commitment(
        args=[
            "agent.procurement",
            "Exclusively provide Dataset X to Company B until September 30.",
            "",
            "0x0000000000000000000000000000000000000000",
        ]
    ).transact()
    assert tx_execution_succeeded(tx)
