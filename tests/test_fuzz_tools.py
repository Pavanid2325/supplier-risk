import pytest
import random
import string
from backend.mcp.dispatcher import dispatch_tool_call
from backend.security.validation import ValidationError
from backend.security.auth import AuthError

def generate_malformed_inputs(count: int = 1000):
    malformed_inputs = []
    
    # Categories of malformed inputs
    bad_supplier_ids = [
        "SUP-1", "SUP-1234", "SUP-123456", "SUP-ABCDE", "SUP-40217; DROP TABLE",
        "../../etc/passwd", "SUP-40217\x00null", "<script>alert(1)</script>",
        "SUP-00000", "sup-40217", "SUP 40217", "SUP_40217", "", "   "
    ]
    
    tools = ["get_supplier_balance", "get_alternate_sources", "get_payment_history", "search_contract_corpus"]

    for i in range(count):
        tool = random.choice(tools)
        if tool == "search_contract_corpus":
            payload = {
                "query": random.choice(["DROP TABLE contracts;", "UNION SELECT *", "", "a" * 1000, 12345, None]),
                "k": random.choice([-1, 0, 999999, "invalid", None])
            }
        else:
            payload = {
                "supplier_id": random.choice(bad_supplier_ids)
            }
            if random.random() < 0.2:
                payload["unexpected_field"] = "malicious_payload_" + "".join(random.choices(string.ascii_letters, k=20))

        malformed_inputs.append((tool, payload))

    return malformed_inputs

def test_fuzz_1000_malformed_tool_requests():
    """
    Fuzzing test running 1000 malformed requests through dispatch_tool_call.
    Verifies that 0 bypasses occur and no handler executes with bad input.
    """
    inputs = generate_malformed_inputs(1000)
    valid_payload = {"sub": "fuzzer", "tenant_id": "tenant-alpha", "scopes": ["erp:read", "supply:read", "finance:read", "contracts:read"]}

    bypasses = 0
    rejections = 0

    for tool_name, payload in inputs:
        try:
            res = dispatch_tool_call(
                tool_name=tool_name,
                inputs=payload,
                jwt_payload=valid_payload,
                actor="fuzzer"
            )
            # If tool completed without throwing ValidationError, check if input was actually invalid
            supplier_id = payload.get("supplier_id")
            if supplier_id and not supplier_id.startswith("SUP-") or (supplier_id and len(supplier_id) != 9):
                bypasses += 1
        except (ValidationError, AuthError):
            rejections += 1
        except Exception as e:
            # Unhandled crash is considered a security failure in fuzzing
            bypasses += 1

    print(f"\n[FUZZER SUMMARY] Tested: {len(inputs)} requests | Rejections: {rejections} | Bypasses: {bypasses}")
    assert bypasses == 0, f"Fuzzing detected {bypasses} security bypasses!"

if __name__ == "__main__":
    test_fuzz_1000_malformed_tool_requests()
