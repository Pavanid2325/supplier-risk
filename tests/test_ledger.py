import pytest
import sqlite3
import os
import tempfile
import gc
from backend.ledger.ledger import AuditLedger

def safe_remove(path):
    gc.collect()
    try:
        if os.path.exists(path):
            os.remove(path)
    except PermissionError:
        pass

def test_ledger_append_and_verify_valid():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name

    try:
        ledger = AuditLedger(db_path=db_path)
        ledger.append("tenant-alpha", "TOOL_CALL", "agent", "get_supplier_balance", {"inputs": {"supplier_id": "SUP-40217"}})
        ledger.append("tenant-alpha", "TOOL_CALL", "agent", "get_alternate_sources", {"inputs": {"supplier_id": "SUP-40217"}})
        ledger.append("tenant-alpha", "TOOL_CALL", "agent", "get_payment_history", {"inputs": {"supplier_id": "SUP-40217"}})

        res = ledger.verify(tenant_id="tenant-alpha")
        assert res["valid"] is True
        assert res["entries_checked"] == 3
        assert res["first_bad_seq"] is None
    finally:
        safe_remove(db_path)

def test_ledger_tamper_detection():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name

    try:
        ledger = AuditLedger(db_path=db_path)
        seq1 = ledger.append("tenant-alpha", "TOOL_CALL", "agent", "tool1", {"inputs": {"x": 1}})
        seq2 = ledger.append("tenant-alpha", "TOOL_CALL", "agent", "tool2", {"inputs": {"x": 2}})
        seq3 = ledger.append("tenant-alpha", "TOOL_CALL", "agent", "tool3", {"inputs": {"x": 3}})

        # Verify initial valid state
        assert ledger.verify("tenant-alpha")["valid"] is True

        # Directly tamper with seq 2 payload in database directly (simulating adversary attack)
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE audit_ledger SET payload = '{\"tampered\": true}' WHERE seq = ?", (seq2,))
        conn.commit()
        conn.close()

        # Run verification after tampering
        verify_res = ledger.verify("tenant-alpha")
        assert verify_res["valid"] is False
        assert verify_res["first_bad_seq"] == seq2
        assert verify_res["invalidated_count"] == 2 # seq 2 and seq 3 downstream invalidated!
    finally:
        safe_remove(db_path)
