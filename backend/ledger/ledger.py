import sqlite3
import hashlib
import json
import time
import os
from typing import Dict, Any, List, Optional
from backend.config import DB_PATH

class AuditLedger:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_ledger (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    tenant_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    tool TEXT NOT NULL,
                    input_hash TEXT NOT NULL,
                    output_hash TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def _compute_hash(self, payload_str: str, previous_hash: str) -> str:
        data_to_hash = f"{payload_str}:{previous_hash}".encode("utf-8")
        return hashlib.sha256(data_to_hash).hexdigest()

    def _get_last_entry_hash(self, tenant_id: str) -> str:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT entry_hash FROM audit_ledger WHERE tenant_id = ? ORDER BY seq DESC LIMIT 1",
                (tenant_id,)
            ).fetchone()
            if row:
                return row["entry_hash"]
            return "0000000000000000000000000000000000000000000000000000000000000000" # Genesis hash

    def append(
        self,
        tenant_id: str,
        event_type: str,
        actor: str,
        tool: str,
        payload: Dict[str, Any]
    ) -> int:
        timestamp = time.time()
        
        # Format payload canonical JSON
        payload_json = json.dumps(payload, sort_keys=True)
        
        inputs = payload.get("inputs", {})
        outputs = payload.get("result", payload.get("error", {}))
        
        input_hash = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode("utf-8")).hexdigest()
        output_hash = hashlib.sha256(json.dumps(outputs, sort_keys=True).encode("utf-8")).hexdigest()

        previous_hash = self._get_last_entry_hash(tenant_id)
        
        raw_to_hash = f"{timestamp}:{tenant_id}:{event_type}:{actor}:{tool}:{input_hash}:{output_hash}:{payload_json}"
        entry_hash = self._compute_hash(raw_to_hash, previous_hash)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_ledger (
                    timestamp, tenant_id, event_type, actor, tool,
                    input_hash, output_hash, payload, previous_hash, entry_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, tenant_id, event_type, actor, tool,
                input_hash, output_hash, payload_json, previous_hash, entry_hash
            ))
            conn.commit()
            return cursor.lastrowid

    def verify(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        with self._get_connection() as conn:
            if tenant_id:
                rows = conn.execute(
                    "SELECT * FROM audit_ledger WHERE tenant_id = ? ORDER BY seq ASC",
                    (tenant_id,)
                ).fetchall()
            else:
                # Verify grouped per tenant
                tenants = [r["tenant_id"] for r in conn.execute("SELECT DISTINCT tenant_id FROM audit_ledger").fetchall()]
                all_valid = True
                total_checked = 0
                first_bad = None
                invalidated_cnt = 0
                
                for t in tenants:
                    sub_res = self.verify(tenant_id=t)
                    total_checked += sub_res["entries_checked"]
                    if not sub_res["valid"]:
                        all_valid = False
                        if first_bad is None or (sub_res["first_bad_seq"] and sub_res["first_bad_seq"] < first_bad):
                            first_bad = sub_res["first_bad_seq"]
                        invalidated_cnt += sub_res["invalidated_count"]

                return {
                    "valid": all_valid,
                    "entries_checked": total_checked,
                    "first_bad_seq": first_bad,
                    "invalidated_count": invalidated_cnt
                }

            entries_checked = 0
            prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
            first_bad_seq = None
            invalidated_count = 0

            for row in rows:
                entries_checked += 1
                seq = row["seq"]
                stored_prev = row["previous_hash"]
                stored_entry_hash = row["entry_hash"]

                # 1. Check previous hash link
                if stored_prev != prev_hash and first_bad_seq is None:
                    first_bad_seq = seq

                # 2. Recompute current entry hash
                raw_to_hash = f"{row['timestamp']}:{row['tenant_id']}:{row['event_type']}:{row['actor']}:{row['tool']}:{row['input_hash']}:{row['output_hash']}:{row['payload']}"
                expected_entry_hash = self._compute_hash(raw_to_hash, stored_prev)

                if expected_entry_hash != stored_entry_hash and first_bad_seq is None:
                    first_bad_seq = seq

                if first_bad_seq is not None:
                    invalidated_count += 1
                else:
                    prev_hash = stored_entry_hash

            if first_bad_seq is not None:
                return {
                    "valid": False,
                    "entries_checked": entries_checked,
                    "first_bad_seq": first_bad_seq,
                    "invalidated_count": invalidated_count
                }

            return {
                "valid": True,
                "entries_checked": entries_checked,
                "first_bad_seq": None,
                "invalidated_count": 0
            }

    def get_entries(self, tenant_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if tenant_id:
                rows = conn.execute(
                    "SELECT * FROM audit_ledger WHERE tenant_id = ? ORDER BY seq DESC LIMIT ?",
                    (tenant_id, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM audit_ledger ORDER BY seq DESC LIMIT ?",
                    (limit,)
                ).fetchall()

            res = []
            for r in rows:
                res.append({
                    "seq": r["seq"],
                    "timestamp": r["timestamp"],
                    "tenant_id": r["tenant_id"],
                    "event_type": r["event_type"],
                    "actor": r["actor"],
                    "tool": r["tool"],
                    "input_hash": r["input_hash"],
                    "output_hash": r["output_hash"],
                    "payload": json.loads(r["payload"]),
                    "previous_hash": r["previous_hash"],
                    "entry_hash": r["entry_hash"]
                })
            return res

_global_ledger: Optional[AuditLedger] = None

def get_ledger() -> AuditLedger:
    global _global_ledger
    if _global_ledger is None:
        _global_ledger = AuditLedger()
    return _global_ledger
