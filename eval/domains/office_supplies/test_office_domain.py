import os
from eval.evaluator import DomainAgnosticEvaluator

def mock_office_domain_runner(item_id: str, question: str, token_payload: dict) -> dict:
    # Simulated domain runner for Office Supplies domain
    office_db = {
        "ITEM-101": {"concise_answer": "Ergonomic Chairs stock level is 150 units.", "key_findings": ["150 units in stock"], "citations": [{"document_id": "OFF-DOC-101"}]},
        "ITEM-102": {"concise_answer": "Primary vendor for Standing Desks is Workspace Dynamics.", "key_findings": ["Vendor: Workspace Dynamics"], "citations": [{"document_id": "OFF-DOC-102"}]},
        "ITEM-103": {"concise_answer": "Low exposure for ITEM-103 recycled paper.", "key_findings": ["recycled paper backup active"], "citations": [{"document_id": "OFF-DOC-103"}]}
    }
    return office_db.get(item_id, {"concise_answer": "Item not found", "key_findings": [], "citations": []})

def test_domain_agnostic_evaluator_on_office_supplies():
    golden_path = os.path.join(os.path.dirname(__file__), "golden_set.json")
    evaluator = DomainAgnosticEvaluator(golden_path)
    report = evaluator.run_suite(mock_office_domain_runner)
    
    assert report["total_questions"] == 3
    assert report["passed"] == 3
    assert report["accuracy_rate_pct"] == 100.0
