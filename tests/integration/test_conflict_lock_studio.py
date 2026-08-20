import os

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get("GENLAYER_RUN_INTEGRATION"),
    reason="Set GENLAYER_RUN_INTEGRATION=1 with a configured Studio/StudioNet signer to run live integration tests.",
)


def _write(contract, name, args):
    from gltest.assertions import tx_execution_succeeded
    receipt = getattr(contract, name)(args=args).transact(wait_retries=100)
    assert tx_execution_succeeded(receipt)
    return receipt


def test_live_semantic_admission_flow():
    from gltest import get_contract_factory
    from gltest.assertions import tx_execution_succeeded

    factory = get_contract_factory("ConflictLock")
    contract = factory.deploy()
    zero = "0x0000000000000000000000000000000000000000"
    first = _write(contract, "propose_commitment", ["agent.procurement", "Exclusively provide Dataset X to Company B until September 30.", "", zero])
    first_resolve = _write(contract, "resolve_proposal", [1])
    assert contract.status_of(args=[1]).call() == "ACTIVE"
    assert contract.verdict_of(args=[1]).call() == "COMPATIBLE"

    conflicting = _write(contract, "propose_commitment", ["agent.procurement", "Provide Dataset X to Company C on September 12.", "", zero])
    conflict_resolve = _write(contract, "resolve_proposal", [2])
    conflict_status = contract.status_of(args=[2]).call()
    assert conflict_status in ("REJECTED", "REVIEW_REQUIRED")

    compatible = _write(contract, "propose_commitment", ["agent.procurement", "Provide unrelated Dataset Y to Company C in October.", "", zero])
    compatible_resolve = _write(contract, "resolve_proposal", [3])
    assert contract.status_of(args=[3]).call() in ("ACTIVE", "REVIEW_REQUIRED")

    race_a = _write(contract, "propose_commitment", ["agent.procurement", "Provide Dataset Z to Company D in November.", "", zero])
    race_b = _write(contract, "propose_commitment", ["agent.procurement", "Provide Dataset Q to Company E in December.", "", zero])
    _write(contract, "resolve_proposal", [4])
    stale = getattr(contract, "resolve_proposal")(args=[5]).transact(wait_retries=100)
    assert not tx_execution_succeeded(stale)
    _write(contract, "refresh_proposal", [5])
    refreshed = contract.get_commitment(args=[5]).call()
    assert "snapshot_revision" in refreshed

    # Keep receipts referenced so pytest displays them in assertion failures and
    # downstream evidence scripts can be extended without changing the flow.
    assert all((first, first_resolve, conflicting, conflict_resolve, compatible, compatible_resolve, race_a, race_b))
