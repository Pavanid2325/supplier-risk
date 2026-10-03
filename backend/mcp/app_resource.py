from typing import Dict, Any
from backend.mcp.dispatcher import dispatch_tool_call
from backend.security.validation import validate_supplier_id

RESOURCE_URI = "ui://srp/supplier-exposure-view"

def get_mcp_ui_resource(supplier_id: str, jwt_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Renders structured MCP UI Resource representation for ui://srp/supplier-exposure-view.
    Uses the exact same tool dispatcher and schema validation.
    """
    validate_supplier_id(supplier_id)

    balance_res = dispatch_tool_call(
        tool_name="get_supplier_balance",
        inputs={"supplier_id": supplier_id},
        jwt_payload=jwt_payload,
        actor="mcp-ui-resource"
    )

    alternate_res = dispatch_tool_call(
        tool_name="get_alternate_sources",
        inputs={"supplier_id": supplier_id},
        jwt_payload=jwt_payload,
        actor="mcp-ui-resource"
    )

    payment_res = dispatch_tool_call(
        tool_name="get_payment_history",
        inputs={"supplier_id": supplier_id},
        jwt_payload=jwt_payload,
        actor="mcp-ui-resource"
    )

    contract_res = dispatch_tool_call(
        tool_name="search_contract_corpus",
        inputs={"query": f"insolvency SUP-{supplier_id[-5:]}", "supplier_id": supplier_id},
        jwt_payload=jwt_payload,
        actor="mcp-ui-resource"
    )

    return {
        "resource_uri": RESOURCE_URI,
        "title": "Supplier Exposure View",
        "supplier_id": supplier_id,
        "data": {
            "balance": balance_res["result"],
            "alternate_sources": alternate_res["result"],
            "payment_history": payment_res["result"],
            "contract_findings": contract_res["result"]
        }
    }
