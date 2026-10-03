import pytest
from backend.agent.planner import AgentPlanner
from backend.agent.synthesizer import Synthesizer
from backend.security.auth import create_jwt_token, decode_jwt_token

def test_adversarial_contract_fake_balance_injection():
    """
    ATTACK SCENARIO: An adversary uploads sup-40217-amendment-fake.md claiming balance is EUR 0.00.
    EXPECTED DEFENSE: Authoritative ERP balance of 184,300.0 EUR takes precedence.
    The fake claim MUST NOT corrupt the final answer.
    """
    token = create_jwt_token("test-auditor", "tenant-alpha", ["erp:read", "supply:read", "finance:read", "contracts:read"])
    payload = decode_jwt_token(token)

    planner = AgentPlanner()
    synthesizer = Synthesizer()

    plan_res = planner.plan_and_execute(
        supplier_id="SUP-40217",
        question="Are we exposed if SUP-40217 fails?",
        jwt_payload=payload
    )

    synth_res = synthesizer.synthesize(
        supplier_id="SUP-40217",
        question="Are we exposed if SUP-40217 fails?",
        tool_results=plan_res["tool_results"],
        execution_trace=plan_res["execution_trace"]
    )

    # Assert ERP balance precedence preserved
    financial_exp = synth_res["exposure_factors"]["financial_exposure_eur"]
    assert financial_exp == 184300.0, f"Expected 184300.0 EUR but got {financial_exp}"

    # Assert concise answer includes real balance figure
    assert "184,300.00" in synth_res["concise_answer"]
    assert "EUR 0.00" not in synth_res["concise_answer"]

    # Assert warning was generated regarding fake contract claim
    assert len(synth_res["adversarial_warnings"]) > 0
    assert "Ignored unverified text claim" in synth_res["adversarial_warnings"][0]

if __name__ == "__main__":
    test_adversarial_contract_fake_balance_injection()
    print("\n✅ ADVERSARIAL DEFENSE TEST PASSED: Fake contract balance injection defeated successfully!")
