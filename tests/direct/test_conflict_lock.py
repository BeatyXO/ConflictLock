import json

import pytest


CONTRACT = "contracts/conflict_lock.py"
ZERO = "0x0000000000000000000000000000000000000000"


def deploy(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    direct_vm.check_pickling = True
    return contract


def propose(contract, direct_vm, sender, text, scope="agent.procurement", context=""):
    direct_vm.sender = sender
    return contract.propose_commitment(scope, text, context, ZERO)


def rec(contract, commitment_id):
    return json.loads(contract.get_commitment(commitment_id))


def mock_decision(direct_vm, verdict, conflicts=None, reason="mocked decision"):
    direct_vm.clear_mocks()
    direct_vm.mock_llm(
        r".*GenLayer validator evaluating whether a proposed commitment can coexist.*",
        json.dumps({"verdict": verdict, "reason": reason, "conflicts": conflicts or []}),
    )


def activate_first(contract, direct_vm, sender, text="Provide dataset X to Company B through September 30."):
    cid = propose(contract, direct_vm, sender, text)
    contract.resolve_proposal(cid)
    assert rec(contract, cid)["status"] == "ACTIVE"
    return cid


def test_first_commitment_activates_without_llm(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    cid = propose(contract, direct_vm, direct_alice, "Provide dataset X to Company B through September 30.")
    contract.resolve_proposal(cid)
    result = rec(contract, cid)
    assert result["status"] == "ACTIVE"
    assert result["verdict"] == "COMPATIBLE"


def test_material_conflict_rejects_candidate(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    base = activate_first(contract, direct_vm, direct_alice, "Exclusively provide dataset X to Company B until September 30.")
    candidate = propose(contract, direct_vm, direct_alice, "Provide the same dataset X to Company C on September 12.")
    mock_decision(
        direct_vm,
        "CONFLICTING",
        [{"commitment_id": str(base), "category": "EXCLUSIVITY", "severity": "MATERIAL", "reason": "Cannot both be honored."}],
    )
    contract.resolve_proposal(candidate)
    result = rec(contract, candidate)
    assert result["status"] == "REJECTED"
    assert result["verdict"] == "CONFLICTING"
    edge = json.loads(contract.get_conflict(candidate, 0))
    assert edge["commitment_id"] == str(base)


def test_compatible_candidate_activates(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    activate_first(contract, direct_vm, direct_alice)
    candidate = propose(contract, direct_vm, direct_alice, "Provide unrelated dataset Y to Company C in October.")
    mock_decision(direct_vm, "COMPATIBLE")
    contract.resolve_proposal(candidate)
    assert contract.is_compatible(candidate) is True


def test_potential_edge_cannot_force_rejection(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    base = activate_first(contract, direct_vm, direct_alice)
    candidate = propose(contract, direct_vm, direct_alice, "Perform a possibly overlapping dataset delivery.")
    mock_decision(
        direct_vm,
        "CONFLICTING",
        [{"commitment_id": str(base), "category": "OTHER", "severity": "POTENTIAL", "reason": "Ambiguous overlap."}],
    )
    contract.resolve_proposal(candidate)
    assert rec(contract, candidate)["status"] == "REVIEW_REQUIRED"
    assert rec(contract, candidate)["verdict"] == "INCONCLUSIVE"


def test_invented_conflict_id_cannot_force_rejection(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    activate_first(contract, direct_vm, direct_alice)
    candidate = propose(contract, direct_vm, direct_alice, "Another commitment.")
    mock_decision(
        direct_vm,
        "CONFLICTING",
        [{"commitment_id": "999999", "category": "EXCLUSIVITY", "severity": "MATERIAL", "reason": "Invented."}],
    )
    contract.resolve_proposal(candidate)
    assert rec(contract, candidate)["verdict"] == "INCONCLUSIVE"


def test_stale_snapshot_blocks_double_promise_race(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    activate_first(contract, direct_vm, direct_alice)
    p1 = propose(contract, direct_vm, direct_alice, "Provide dataset Y to Company C.")
    p2 = propose(contract, direct_vm, direct_alice, "Provide dataset Z to Company D.")
    mock_decision(direct_vm, "COMPATIBLE")
    contract.resolve_proposal(p1)
    with direct_vm.expect_revert("stale scope snapshot"):
        contract.resolve_proposal(p2)


def test_refresh_captures_new_revision(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    base = activate_first(contract, direct_vm, direct_alice)
    p1 = propose(contract, direct_vm, direct_alice, "Provide dataset Y to Company C.")
    p2 = propose(contract, direct_vm, direct_alice, "Provide dataset Z to Company D.")
    mock_decision(direct_vm, "COMPATIBLE")
    contract.resolve_proposal(p1)
    direct_vm.sender = direct_alice
    contract.refresh_proposal(p2)
    refreshed = rec(contract, p2)
    assert refreshed["snapshot_revision"] == 2
    assert refreshed["snapshot_ids"] == [str(base), str(p1)]


def test_deactivation_removes_commitment_from_scope(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    cid = activate_first(contract, direct_vm, direct_alice)
    direct_vm.sender = direct_alice
    contract.deactivate_commitment(cid, "Commitment completed.")
    assert rec(contract, cid)["status"] == "DEACTIVATED"
    scope = json.loads(contract.scope_state(direct_alice, "agent.procurement"))
    assert scope["active_ids"] == []
    assert scope["revision"] == 2


def test_exact_active_duplicate_rejected(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    text = "Provide dataset X to Company B through September 30."
    activate_first(contract, direct_vm, direct_alice, text)
    with direct_vm.expect_revert("exact active duplicate"):
        propose(contract, direct_vm, direct_alice, text)


@pytest.mark.parametrize(
    ("raw", "verdict"),
    [
        ("not json", "INCONCLUSIVE"),
        ({}, "INCONCLUSIVE"),
        ({"verdict": "unknown"}, "INCONCLUSIVE"),
        ({"verdict": "CONFLICTING", "conflicts": "bad"}, "INCONCLUSIVE"),
        ({"verdict": "CONFLICTING", "conflicts": []}, "INCONCLUSIVE"),
        ({"verdict": "COMPATIBLE", "conflicts": [{"commitment_id": "1", "severity": "POTENTIAL"}]}, "INCONCLUSIVE"),
        ({"verdict": "COMPATIBLE", "conflicts": [{"commitment_id": "1", "severity": "MATERIAL"}]}, "INCONCLUSIVE"),
        ({"verdict": "INCONCLUSIVE", "conflicts": [{"commitment_id": "1", "severity": "MATERIAL"}]}, "CONFLICTING"),
    ],
)
def test_normalization_fails_closed(direct_vm, direct_deploy, raw, verdict):
    contract = deploy(direct_deploy, direct_vm)
    assert contract._normalize_decision(raw, ["1"])["verdict"] == verdict


def test_normalization_drops_invented_and_duplicate_edges(direct_vm, direct_deploy):
    contract = deploy(direct_deploy, direct_vm)
    decision = contract._normalize_decision({"verdict": "CONFLICTING", "conflicts": [
        {"commitment_id": "99", "category": "EXCLUSIVITY", "severity": "MATERIAL"},
        {"commitment_id": "1", "category": "EXCLUSIVITY", "severity": "MATERIAL"},
        {"commitment_id": "1", "category": "EXCLUSIVITY", "severity": "MATERIAL"},
    ]}, ["1"])
    assert decision["verdict"] == "CONFLICTING"
    assert len(decision["conflicts"]) == 1


def test_material_fingerprint_ignores_reason_but_not_category(direct_vm, direct_deploy):
    contract = deploy(direct_deploy, direct_vm)
    a = {"conflicts": [{"commitment_id": "1", "category": "EXCLUSIVITY", "severity": "MATERIAL", "reason": "A"}]}
    b = {"conflicts": [{"commitment_id": "1", "category": "EXCLUSIVITY", "severity": "MATERIAL", "reason": "B"}]}
    c = {"conflicts": [{"commitment_id": "1", "category": "TIME_COLLISION", "severity": "MATERIAL", "reason": "B"}]}
    assert contract._material_fingerprint(a) == contract._material_fingerprint(b)
    assert contract._material_fingerprint(a) != contract._material_fingerprint(c)


@pytest.mark.parametrize("scope", ["", "bad scope", "UPPER CASE", "x" * 97])
def test_invalid_scope_rejected(direct_vm, direct_deploy, direct_alice, scope):
    contract = deploy(direct_deploy, direct_vm)
    with direct_vm.expect_revert("scope"):
        propose(contract, direct_vm, direct_alice, "Valid commitment.", scope=scope)


def test_scope_normalization_and_isolation(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    cid = propose(contract, direct_vm, direct_alice, "One", scope="Agent.Procurement")
    assert rec(contract, cid)["scope"] == "agent.procurement"
    other = propose(contract, direct_vm, direct_alice, "One", scope="agent.other")
    assert other != cid


def test_cancelled_proposal_cannot_resolve(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    cid = propose(contract, direct_vm, direct_alice, "One")
    contract.cancel_proposal(cid)
    with direct_vm.expect_revert("not resolvable"):
        contract.resolve_proposal(cid)


def test_stale_snapshot_after_deactivation(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    active = activate_first(contract, direct_vm, direct_alice)
    pending = propose(contract, direct_vm, direct_alice, "Later commitment")
    contract.deactivate_commitment(active, "Done")
    with direct_vm.expect_revert("stale scope snapshot"):
        contract.resolve_proposal(pending)


def test_zero_callback_rejected_after_resolution(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_deploy, direct_vm)
    cid = propose(contract, direct_vm, direct_alice, "One")
    contract.resolve_proposal(cid)
    with direct_vm.expect_revert("no callback"):
        contract.send_callback(cid)
