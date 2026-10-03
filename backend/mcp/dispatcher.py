import time
from typing import Dict, Any, Optional
from backend.mcp.registry import registry
from backend.ledger.ledger import get_ledger, AuditLedger
from backend.security.validation import ValidationError
from backend.security.auth import AuthError

def dispatch_tool_call(
    tool_name: str,
    inputs: Dict[str, Any],
    jwt_payload: Dict[str, Any],
    version: Optional[str] = None,
    actor: str = "agent",
    resource_tenant_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Unified Dispatch Path for Agent and UI tool calls.
    Performs logging, SHA-256 ledger recording, input validation, and scope verification.
    """
    start_time = time.time()
    tenant_id = jwt_payload.get("tenant_id", "tenant-alpha")
    
    context = {
        "jwt_payload": jwt_payload,
        "tenant_id": tenant_id,
        "resource_tenant_id": resource_tenant_id or tenant_id
    }

    tool_info = registry.get_tool(tool_name, version)
    actual_version = tool_info["version"]

    try:
        # Call tool via registry (which runs pre-validation & scope checks)
        result = registry.call_tool(tool_name, inputs, context, version=actual_version)
        exec_ms = round((time.time() - start_time) * 1000, 2)

        # Audit ledger record
        ledger = get_ledger()
        seq = ledger.append(
            tenant_id=tenant_id,
            event_type="TOOL_CALL_SUCCESS",
            actor=actor,
            tool=f"{tool_name}:{actual_version}",
            payload={
                "inputs": inputs,
                "result": result,
                "execution_ms": exec_ms
            }
        )

        return {
            "success": True,
            "tool": tool_name,
            "version": actual_version,
            "result": result,
            "execution_ms": exec_ms,
            "audit_seq": seq
        }

    except (ValidationError, AuthError) as e:
        exec_ms = round((time.time() - start_time) * 1000, 2)
        ledger = get_ledger()
        seq = ledger.append(
            tenant_id=tenant_id,
            event_type="TOOL_CALL_REJECTED",
            actor=actor,
            tool=f"{tool_name}:{version or 'latest'}",
            payload={
                "inputs": inputs,
                "error": str(e),
                "code": getattr(e, "code", "VALIDATION_ERROR"),
                "execution_ms": exec_ms
            }
        )
        raise e
    except Exception as e:
        exec_ms = round((time.time() - start_time) * 1000, 2)
        ledger = get_ledger()
        ledger.append(
            tenant_id=tenant_id,
            event_type="TOOL_CALL_ERROR",
            actor=actor,
            tool=f"{tool_name}:{version or 'latest'}",
            payload={
                "inputs": inputs,
                "error": str(e),
                "execution_ms": exec_ms
            }
        )
        raise e
