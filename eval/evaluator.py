import json
import os
import sys
from typing import Dict, Any, List, Optional
from backend.security.auth import create_jwt_token
from backend.agent.planner import AgentPlanner
from backend.agent.synthesizer import Synthesizer

class DomainAgnosticEvaluator:
    def __init__(self, golden_set_path: str):
        self.golden_set_path = golden_set_path
        with open(golden_set_path, "r", encoding="utf-8") as f:
            self.golden_set = json.load(f)

    def evaluate_item(
        self,
        item: Dict[str, Any],
        system_runner_fn
    ) -> Dict[str, Any]:
        """
        Evaluates a single question across 3 layers:
        Layer 1: Structural & Security
        Layer 2: Answer Accuracy
        Layer 3: Governance & Citations
        """
        item_id = item["id"]
        question = item["question"]
        target_id = item.get("supplier_id") or item.get("item_id")
        required_tenant = item.get("required_tenant", "tenant-alpha")
        expected_facts = item.get("expected_facts", [])
        allowed_citations = item.get("allowed_citations", [])

        # Create JWT token for required tenant
        token_payload = {
            "sub": "eval-user",
            "tenant_id": required_tenant,
            "scopes": ["erp:read", "supply:read", "finance:read", "contracts:read"],
            "exp": 9999999999
        }

        # Run system under evaluation
        run_res = system_runner_fn(target_id, question, token_payload)

        layer1_pass = True
        layer1_errors = []
        layer2_pass = True
        layer2_errors = []
        layer3_pass = True
        layer3_errors = []

        # Layer 1: Structural / Security Check
        if "error" in run_res and item.get("expected_classification") != "SECURITY_ISOLATION":
            layer1_pass = False
            layer1_errors.append(f"Unexpected execution error: {run_res['error']}")
        
        if item.get("expected_classification") == "SECURITY_ISOLATION":
            # Expect security block/failure when accessing forbidden tenant
            if not run_res.get("security_blocked"):
                layer1_pass = False
                layer1_errors.append("Security failure: Cross-tenant access was NOT blocked!")

        # Layer 2: Fact Accuracy Check
        full_text = run_res.get("concise_answer", "") + " " + " ".join(run_res.get("key_findings", []))
        for fact in expected_facts:
            if fact.lower() not in full_text.lower():
                layer2_pass = False
                layer2_errors.append(f"Fact missing in answer: '{fact}'")

        # Layer 3: Governance & Citation Check
        citations = [c["document_id"] for c in run_res.get("citations", [])]
        for c in citations:
            if allowed_citations and c not in allowed_citations:
                layer3_pass = False
                layer3_errors.append(f"Disallowed citation present: '{c}'")

        overall_pass = layer1_pass and layer2_pass and layer3_pass

        return {
            "id": item_id,
            "question": question,
            "passed": overall_pass,
            "layer1_security": {"pass": layer1_pass, "errors": layer1_errors},
            "layer2_accuracy": {"pass": layer2_pass, "errors": layer2_errors},
            "layer3_governance": {"pass": layer3_pass, "errors": layer3_errors}
        }

    def run_suite(self, system_runner_fn) -> Dict[str, Any]:
        results = []
        total = len(self.golden_set)
        passed = 0
        l1_failures = 0
        l2_failures = 0
        l3_failures = 0

        for item in self.golden_set:
            res = self.evaluate_item(item, system_runner_fn)
            results.append(res)
            if res["passed"]:
                passed += 1
            if not res["layer1_security"]["pass"]:
                l1_failures += 1
            if not res["layer2_accuracy"]["pass"]:
                l2_failures += 1
            if not res["layer3_governance"]["pass"]:
                l3_failures += 1

        accuracy_rate = round((passed / total) * 100, 1) if total > 0 else 100.0

        return {
            "total_questions": total,
            "passed": passed,
            "failed": total - passed,
            "accuracy_rate_pct": accuracy_rate,
            "layer1_security_failures": l1_failures,
            "layer2_accuracy_failures": l2_failures,
            "layer3_governance_failures": l3_failures,
            "item_results": results
        }

def default_supplier_risk_runner(supplier_id: str, question: str, jwt_payload: Dict[str, Any]) -> Dict[str, Any]:
    planner = AgentPlanner()
    synthesizer = Synthesizer()

    try:
        plan_res = planner.plan_and_execute(
            supplier_id=supplier_id,
            question=question,
            jwt_payload=jwt_payload
        )
        synth_res = synthesizer.synthesize(
            supplier_id=supplier_id,
            question=question,
            tool_results=plan_res["tool_results"],
            execution_trace=plan_res["execution_trace"],
            synthesis_profile="deterministic"
        )
        return synth_res
    except Exception as e:
        if "Tenant mismatch" in str(e) or "cannot access" in str(e) or "SECURITY" in str(e):
            return {"security_blocked": True, "error": str(e), "concise_answer": f"Tenant mismatch: {str(e)}", "key_findings": [str(e)]}
        return {"error": str(e), "concise_answer": str(e), "key_findings": [str(e)]}

if __name__ == "__main__":
    golden_path = os.path.join(os.path.dirname(__file__), "golden_set.json")
    evaluator = DomainAgnosticEvaluator(golden_path)
    report = evaluator.run_suite(default_supplier_risk_runner)
    
    print("\n==================================================")
    print("        EVALUATION REPORT (3-LAYER HARNESS)")
    print("==================================================")
    print(f"Total Questions Evaluated : {report['total_questions']}")
    print(f"Overall Passed            : {report['passed']} / {report['total_questions']} ({report['accuracy_rate_pct']}%)")
    print(f"Layer 1 Security Failures : {report['layer1_security_failures']}")
    print(f"Layer 2 Accuracy Failures : {report['layer2_accuracy_failures']}")
    print(f"Layer 3 Governance Viol.  : {report['layer3_governance_failures']}")
    print("==================================================\n")
