import re
from typing import Any, Dict
from pydantic import BaseModel, Field, field_validator

SUPPLIER_ID_REGEX = r"^SUP-[0-9]{5}$"

class ValidationError(Exception):
    def __init__(self, message: str, field: str = ""):
        super().__init__(message)
        self.message = message
        self.field = field

def validate_supplier_id(supplier_id: str) -> str:
    if not isinstance(supplier_id, str):
        raise ValidationError("Supplier ID must be a string", field="supplier_id")
    
    # Check regex strictly
    if not re.match(SUPPLIER_ID_REGEX, supplier_id):
        raise ValidationError(
            f"Invalid Supplier ID format: '{supplier_id}'. Must match pattern ^SUP-[0-9]{{5}}$ (e.g. SUP-40217)",
            field="supplier_id"
        )
    return supplier_id

def sanitize_search_query(query: str) -> str:
    if not isinstance(query, str):
        raise ValidationError("Query must be a string", field="query")
    
    # Prevent arbitrary SQL injection patterns or command injections if any
    sql_forbidden = ["DROP TABLE", "SELECT * FROM", "UNION SELECT", "INSERT INTO", "DELETE FROM", "--", ";--"]
    upper_query = query.upper()
    for forbidden in sql_forbidden:
        if forbidden in upper_query:
            raise ValidationError(f"Potentially malicious query string detected: '{forbidden}'", field="query")
    
    return query.strip()
