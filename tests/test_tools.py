import pytest
from backend.mcp.registry import registry
from backend.security.auth import create_jwt_token
from backend.mcp.dispatcher import dispatch_tool_call

def test_tool_registry_list():
    tools = registry.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "get_supplier_balance" in tool_names
    assert "get_alternate_sources" in tool_names
    assert "get_payment_history" in tool_names
    assert "search_contract_corpus" in tool_names

def test_versioning_backward_compatibility():
    token = create_jwt_token("v-user", "tenant-alpha", ["finance:read"])
    payload = {"tenant_id": "tenant-alpha", "scopes": ["finance:read"]}

    # Call v1 payment history
    v1_res = dispatch_tool_call("get_payment_history", {"supplier_id": "SUP-40217"}, payload, version="v1")
    assert v1_res["version"] == "v1"
    assert isinstance(v1_res["result"], list)

    # Call v2 payment history
    v2_res = dispatch_tool_call("get_payment_history", {"supplier_id": "SUP-40217", "include_projections": True}, payload, version="v2")
    assert v2_res["version"] == "v2"
    assert isinstance(v2_res["result"], dict)
    assert "projections" in v2_res["result"]
    assert "summary" in v2_res["result"]
