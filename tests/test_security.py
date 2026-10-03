import pytest
import time
from backend.security.auth import create_jwt_token, check_scope, AuthError
from backend.security.validation import validate_supplier_id, sanitize_search_query, ValidationError
from backend.mcp.dispatcher import dispatch_tool_call

def test_jwt_valid_and_scope_check():
    token = create_jwt_token("user1", "tenant-alpha", ["erp:read", "supply:read"])
    payload = check_scope(token, "erp:read", "tenant-alpha")
    assert payload["sub"] == "user1"
    assert payload["tenant_id"] == "tenant-alpha"

def test_jwt_expired_token():
    token = create_jwt_token("user1", "tenant-alpha", ["erp:read"], expires_in_seconds=-10)
    with pytest.raises(AuthError) as exc_info:
        check_scope(token, "erp:read", "tenant-alpha")
    assert exc_info.value.code == "EXPIRED_TOKEN"

def test_tenant_mismatch_rejection():
    token = create_jwt_token("user1", "tenant-alpha", ["erp:read"])
    with pytest.raises(AuthError) as exc_info:
        check_scope(token, "erp:read", "tenant-beta") # Resource is tenant-beta!
    assert exc_info.value.code == "TENANT_MISMATCH"

def test_missing_scope_rejection():
    token = create_jwt_token("user1", "tenant-alpha", ["erp:read"])
    with pytest.raises(AuthError) as exc_info:
        check_scope(token, "admin:delete", "tenant-alpha") # Missing admin:delete scope
    assert exc_info.value.code == "MISSING_SCOPE"

def test_malformed_supplier_id_regex():
    invalid_ids = ["SUP-123", "SUP-ABCDE", "INVALID-40217", "SUP-40217; DROP TABLE", "SUP-4021712"]
    for bad_id in invalid_ids:
        with pytest.raises(ValidationError):
            validate_supplier_id(bad_id)

def test_sql_injection_attempt_sanitization():
    sql_attacks = [
        "SUP-40217'; DROP TABLE suppliers;--",
        "UNION SELECT * FROM user_tokens",
        "procurement -- SQL comment"
    ]
    for attack in sql_attacks:
        with pytest.raises(ValidationError):
            sanitize_search_query(attack)

def test_unauthorized_cross_tenant_tool_call():
    # tenant-alpha token attempting to access tenant-beta document via contract search
    token_alpha = create_jwt_token("alpha-user", "tenant-alpha", ["contracts:read"])
    payload = check_scope(token_alpha, "contracts:read")

    res = dispatch_tool_call(
        tool_name="search_contract_corpus",
        inputs={"query": "ChemSolutions SUP-51190"},
        jwt_payload=payload,
        actor="test"
    )

    # Must NOT contain tenant-beta documents
    retrieved_docs = res["result"]
    for doc in retrieved_docs:
        assert doc["tenant_id"] == "tenant-alpha"
        assert doc["document_id"] != "DOC-SUP-51190-MA"
