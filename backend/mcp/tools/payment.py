from typing import Dict, Any, List, Union
from backend.data.seed_data import SEED_SUPPLIERS
from backend.security.validation import validate_supplier_id, ValidationError

def handle_get_payment_history_v1(inputs: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    supplier_id = inputs.get("supplier_id")
    validate_supplier_id(supplier_id)

    supplier_data = SEED_SUPPLIERS.get(supplier_id)
    if not supplier_data:
        raise ValidationError(f"Supplier ID '{supplier_id}' not found.")

    return supplier_data.get("payment_history", [])

def handle_get_payment_history_v2(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    supplier_id = inputs.get("supplier_id")
    include_projections = inputs.get("include_projections", False)
    validate_supplier_id(supplier_id)

    supplier_data = SEED_SUPPLIERS.get(supplier_id)
    if not supplier_data:
        raise ValidationError(f"Supplier ID '{supplier_id}' not found.")

    records = supplier_data.get("payment_history", [])
    delayed_count = sum(1 for r in records if not r["on_time"])
    risk_level = "High" if delayed_count >= 2 else ("Medium" if delayed_count == 1 else "Low")

    res = {
        "supplier_id": supplier_id,
        "version": "v2",
        "records": records,
        "summary": {
            "total_records": len(records),
            "delayed_records": delayed_count,
            "delay_risk": risk_level
        }
    }
    if include_projections:
        res["projections"] = {
            "expected_next_month_delay_days": 2 if risk_level != "Low" else 0
        }
    return res
