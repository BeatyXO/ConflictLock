"""Deterministic local submission checks; never claims live network proof."""
from __future__ import annotations
import ast, hashlib, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "conflict_lock.py"
REQUIRED = [CONTRACT, ROOT/"README.md", ROOT/"DEPLOYMENT.md", ROOT/"requirements.txt", ROOT/"gltest.config.yaml", ROOT/"examples"/"commitment_admission_consumer.py"]
METHODS = {"propose_commitment","refresh_proposal","resolve_proposal","cancel_proposal","deactivate_commitment","send_callback","get_commitment","get_resolution","get_conflict","is_compatible"}
CONSTANTS = {"VERDICT_COMPATIBLE","VERDICT_CONFLICTING","VERDICT_INCONCLUSIVE"}
STATUSES = {"STATUS_PENDING", "STATUS_ACTIVE", "STATUS_REJECTED", "STATUS_REVIEW_REQUIRED", "STATUS_CANCELLED", "STATUS_DEACTIVATED"}
def check(label, ok):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}"); return ok
def main():
    print("LOCAL PREFLIGHT")
    results=[check("required files exist", all(p.is_file() for p in REQUIRED))]
    try:
        tree=ast.parse(CONTRACT.read_text(encoding="utf-8")); results.append(check("contract parses", True))
    except (OSError,SyntaxError) as exc:
        print(exc); tree=ast.Module(body=[]); results.append(check("contract parses", False))
    classes={n.name for n in tree.body if isinstance(n,ast.ClassDef)}
    functions={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    names={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
    source = CONTRACT.read_text(encoding="utf-8")
    results += [check("ConflictLock class exists","ConflictLock" in classes), check("public API surface exists",METHODS <= functions), check("verdict constants exist",CONSTANTS <= names), check("status constants exist", STATUSES <= names)]
    results += [check("active scope limit is bounded", "MAX_ACTIVE_PER_SCOPE = 8" in source), check("stale revision guard exists", "stale scope snapshot; refresh proposal" in source), check("nondeterministic consensus exists", "run_nondet_unsafe" in source), check("material fingerprint exists", "def _material_fingerprint" in source), check("unknown conflict IDs are filtered", "if cid not in allowed" in source), check("callback replay guard exists", "callback already sent" in source), check("scope normalization exists", "def _normalize_scope" in source)]
    results.append(check("contract-only layout", not any((ROOT/x).exists() for x in ("frontend","app","dashboard"))))
    print(f"CONTRACT_SOURCE_SHA256={hashlib.sha256(CONTRACT.read_bytes()).hexdigest()}")
    print("LIVE NETWORK PROOF"); print("NOT RUN: this script intentionally does not claim StudioNet deployment or consensus.")
    print(f"LOCAL_PREFLIGHT_RESULT={sum(results)}/{len(results)}")
    return 0 if all(results) else 1
if __name__=="__main__": sys.exit(main())
