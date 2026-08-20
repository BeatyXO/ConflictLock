import os
import json

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get("GENLAYER_RUN_INTEGRATION"),
    reason="Set GENLAYER_RUN_INTEGRATION=1 with a configured Studio/StudioNet signer to run live integration tests.",
)


def _write(contract, name, args):
    from gltest.assertions import tx_execution_succeeded
    receipt = getattr(contract, name)(args=args).transact(wait_retries=100)
    assert tx_execution_succeeded(receipt)
    print("CONFLICTLOCK_TX " + name + "=" + str(receipt.get("hash", receipt.get("tx_id", ""))))
    return receipt


CANONICAL_ADDRESS = "0x27e417bbeD7B79eeC89276924fDaB1060e4CeC53"


def test_live_semantic_admission_flow():
    from gltest import get_contract_factory
    from gltest.assertions import tx_execution_succeeded

    from gltest.utils import extract_contract_address

    factory = get_contract_factory("ConflictLock")
    deployment = factory.deploy_contract_tx(wait_retries=100)
    assert tx_execution_succeeded(deployment)
    address = extract_contract_address(deployment)
    print("CONFLICTLOCK_DEPLOYMENT_TX=" + str(deployment.get("hash", deployment.get("tx_id", ""))))
    print("CONFLICTLOCK_ADDRESS=" + str(address))
    contract = factory.build_contract(address)
    zero = "0x0000000000000000000000000000000000000000"
    _write(contract, "propose_commitment", ["agent.procurement", "Exclusively provide Dataset X to Company B until September 30.", "", zero])
    _write(contract, "resolve_proposal", [1])
    assert contract.status_of(args=[1]).call() == "ACTIVE"
    assert contract.verdict_of(args=[1]).call() == "COMPATIBLE"

    conflicting = _write(contract, "propose_commitment", ["agent.procurement", "Provide Dataset X to Company C on September 12.", "", zero])
    conflict_id = int(json.loads(contract.stats(args=[]).call())["next_commitment_id"]) - 1
    conflict_resolve = _write(contract, "resolve_proposal", [conflict_id])
    conflict_status = contract.status_of(args=[conflict_id]).call()
    assert conflict_status in ("ACTIVE", "REJECTED", "REVIEW_REQUIRED")

    compatible = _write(contract, "propose_commitment", ["agent.procurement", "Provide unrelated Dataset Y to Company C in October.", "", zero])
    compatible_id = int(json.loads(contract.stats(args=[]).call())["next_commitment_id"]) - 1
    compatible_resolve = _write(contract, "resolve_proposal", [compatible_id])
    assert contract.status_of(args=[compatible_id]).call() in ("ACTIVE", "REVIEW_REQUIRED")

    print("CONFLICTLOCK_CONFLICT_STATUS=" + conflict_status)
    print("CONFLICTLOCK_CONFLICT_VERDICT=" + contract.verdict_of(args=[conflict_id]).call())
    print("CONFLICTLOCK_CONFLICT_RESOLUTION=" + contract.get_resolution(args=[conflict_id]).call())
    if conflict_status == "REJECTED":
        print("CONFLICTLOCK_CONFLICT_EDGE=" + contract.get_conflict(args=[conflict_id, 0]).call())
    print("CONFLICTLOCK_COMPATIBLE_STATUS=" + contract.status_of(args=[compatible_id]).call())
    print("CONFLICTLOCK_COMPATIBLE_VERDICT=" + contract.verdict_of(args=[compatible_id]).call())

    # Keep receipts referenced so pytest displays them in assertion failures and
    # downstream evidence scripts can be extended without changing the flow.
    assert all((conflicting, conflict_resolve, compatible, compatible_resolve))
