import re
from typing import Dict, Any, Callable, List, Optional
from pydantic import BaseModel
from backend.security.validation import validate_supplier_id, ValidationError
from backend.security.auth import check_scope, AuthError
from backend.mcp.tools.balance import handle_get_supplier_balance
from backend.mcp.tools.alternate import handle_get_alternate_sources
from backend.mcp.tools.payment import handle_get_payment_history_v1, handle_get_payment_history_v2
from backend.mcp.tools.contract import handle_search_contract_corpus

class MCPTool(BaseModel):
    name: str
    version: str
    description: str
    required_scopes: List[str]
    input_schema: Dict[str, Any]
    
    class Config:
        arbitrary_types_allowed = True

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Dict[str, Any]]] = {} # name -> { version -> tool_dict }

    def register_tool(
        self,
        name: str,
        version: str,
        description: str,
        required_scopes: List[str],
        input_schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any], Dict[str, Any]], Any]
    ):
        if name not in self._tools:
            self._tools[name] = {}
        
        self._tools[name][version] = {
            "name": name,
            "version": version,
            "description": description,
            "required_scopes": required_scopes,
            "input_schema": input_schema,
            "handler": handler
        }

    def get_tool(self, name: str, version: Optional[str] = None) -> Dict[str, Any]:
        if name not in self._tools:
            raise ValidationError(f"Tool '{name}' not found in registry.")
        
        versions = self._tools[name]
        if version:
            if version not in versions:
                raise ValidationError(f"Version '{version}' of tool '{name}' not found.")
            return versions[version]
        
        # Return default latest version if not specified
        latest_version = sorted(versions.keys())[-1]
        return versions[latest_version]

    def list_tools(self) -> List[Dict[str, Any]]:
        tool_list = []
        for name, versions in self._tools.items():
            for version, tool_info in versions.items():
                tool_list.append({
                    "name": tool_info["name"],
                    "version": tool_info["version"],
                    "description": tool_info["description"],
                    "required_scopes": tool_info["required_scopes"],
                    "input_schema": tool_info["input_schema"]
                })
        return tool_list

    def validate_inputs(self, name: str, version: str, inputs: Dict[str, Any]):
        tool = self.get_tool(name, version)
        schema = tool["input_schema"]
        
        # Validate required properties
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in inputs or inputs[field] is None:
                raise ValidationError(f"Missing required field '{field}' for tool '{name}'", field=field)

        # Validate supplier_id regex pattern if present or required
        if "supplier_id" in inputs:
            supplier_id = inputs["supplier_id"]
            if not isinstance(supplier_id, str) or not re.match(r"^SUP-[0-9]{5}$", supplier_id):
                raise ValidationError(
                    f"Malformed supplier_id '{supplier_id}'. Must match pattern ^SUP-[0-9]{{5}}$",
                    field="supplier_id"
                )

        # Validate search_contract_corpus query and k parameters
        if "query" in inputs:
            if not isinstance(inputs["query"], str):
                raise ValidationError("Field 'query' must be a string", field="query")
        if "k" in inputs:
            k_val = inputs["k"]
            if not isinstance(k_val, int) or isinstance(k_val, bool) or k_val <= 0 or k_val > 100:
                raise ValidationError("Field 'k' must be a positive integer between 1 and 100", field="k")

    def call_tool(
        self,
        name: str,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
        version: Optional[str] = None
    ) -> Any:
        """
        Unified tool invocation entry point.
        Enforces schema validation and JWT scope verification BEFORE calling handler.
        """
        tool = self.get_tool(name, version)
        actual_version = tool["version"]

        # 1. Pre-handler Input Validation
        self.validate_inputs(name, actual_version, inputs)

        # 2. Scope & Tenant Authorization Check
        required_scopes = tool["required_scopes"]
        token_payload = context.get("jwt_payload", {})
        resource_tenant = context.get("resource_tenant_id")

        for scope in required_scopes:
            check_scope(token_payload, scope, resource_tenant)

        # 3. Handler Execution
        handler = tool["handler"]
        return handler(inputs, context)

# Singleton Registry Instance
registry = ToolRegistry()

# Register standard MCP tools
registry.register_tool(
    name="get_supplier_balance",
    version="v1",
    description="Retrieve ERP outstanding financial balance for a supplier",
    required_scopes=["erp:read"],
    input_schema={
        "type": "object",
        "properties": {
            "supplier_id": {
                "type": "string",
                "pattern": "^SUP-[0-9]{5}$",
                "description": "Unique Supplier ID (e.g. SUP-40217)"
            }
        },
        "required": ["supplier_id"]
    },
    handler=handle_get_supplier_balance
)

registry.register_tool(
    name="get_alternate_sources",
    version="v1",
    description="Find qualified alternative suppliers and capacity",
    required_scopes=["supply:read"],
    input_schema={
        "type": "object",
        "properties": {
            "supplier_id": {
                "type": "string",
                "pattern": "^SUP-[0-9]{5}$",
                "description": "Unique Supplier ID"
            }
        },
        "required": ["supplier_id"]
    },
    handler=handle_get_alternate_sources
)

registry.register_tool(
    name="get_payment_history",
    version="v1",
    description="Retrieve historical payment performance and delays (v1)",
    required_scopes=["finance:read"],
    input_schema={
        "type": "object",
        "properties": {
            "supplier_id": {
                "type": "string",
                "pattern": "^SUP-[0-9]{5}$",
                "description": "Unique Supplier ID"
            }
        },
        "required": ["supplier_id"]
    },
    handler=handle_get_payment_history_v1
)

registry.register_tool(
    name="get_payment_history",
    version="v2",
    description="Retrieve payment performance with risk summary and projections (v2)",
    required_scopes=["finance:read"],
    input_schema={
        "type": "object",
        "properties": {
            "supplier_id": {
                "type": "string",
                "pattern": "^SUP-[0-9]{5}$",
                "description": "Unique Supplier ID"
            },
            "include_projections": {
                "type": "boolean",
                "default": False
            }
        },
        "required": ["supplier_id"]
    },
    handler=handle_get_payment_history_v2
)

registry.register_tool(
    name="search_contract_corpus",
    version="v1",
    description="Search contract documents using hybrid TF-IDF and RRF retrieval",
    required_scopes=["contracts:read"],
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "k": {"type": "integer", "default": 3},
            "supplier_id": {"type": "string", "pattern": "^SUP-[0-9]{5}$"}
        },
        "required": ["query"]
    },
    handler=handle_search_contract_corpus
)
