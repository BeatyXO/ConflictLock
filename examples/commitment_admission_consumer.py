# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

import json


class CommitmentAdmissionConsumer(gl.Contract):
    conflict_lock: Address
    admitted: TreeMap[u256, bool]
    last_proposal_id: u256
    last_verdict: str

    def __init__(self, conflict_lock: Address) -> None:
        self.conflict_lock = Address(conflict_lock)
        self.admitted = TreeMap[u256, bool]()
        self.last_proposal_id = u256(0)
        self.last_verdict = ""

    @gl.public.write
    def on_conflict_resolved(
        self,
        proposal_id: u256,
        principal: Address,
        scope: str,
        verdict: str,
        conflict_count: u32,
    ) -> None:
        if Address(gl.message.sender_address) != self.conflict_lock:
            raise gl.vm.UserError("EXPECTED: only ConflictLock callback")
        if proposal_id in self.admitted:
            raise gl.vm.UserError("EXPECTED: duplicate callback")
        self.admitted[proposal_id] = verdict == "COMPATIBLE"
        self.last_proposal_id = proposal_id
        self.last_verdict = verdict

    @gl.public.view
    def is_admitted(self, proposal_id: u256) -> bool:
        if proposal_id not in self.admitted:
            return False
        return self.admitted[proposal_id]

    @gl.public.view
    def summary(self) -> str:
        return json.dumps(
            {
                "conflict_lock": str(self.conflict_lock),
                "last_proposal_id": str(self.last_proposal_id),
                "last_verdict": self.last_verdict,
            }
        )
