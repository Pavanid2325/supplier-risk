from typing import Dict, Any, List
from backend.data.seed_data import SEED_SUPPLIERS
from backend.security.validation import validate_supplier_id, ValidationError

def handle_get_alternate_sources(inputs: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    supplier_id = inputs.get("supplier_id")
    validate_supplier_id(supplier_id)

    supplier_data = SEED_SUPPLIERS.get(supplier_id)
    if not supplier_data:
        raise ValidationError(f"Supplier ID '{supplier_id}' not found in registry.")

    return supplier_data.get("alternate_sources", [])
