from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os

from backend.config import DEFAULT_TENANT
from backend.security.auth import create_jwt_token, check_scope, decode_jwt_token, AuthError
from backend.security.validation import validate_supplier_id, ValidationError
from backend.mcp.registry import registry
from backend.mcp.dispatcher import dispatch_tool_call
from backend.mcp.app_resource import get_mcp_ui_resource
from backend.agent.planner import AgentPlanner
from backend.agent.synthesizer import Synthesizer
from backend.ledger.ledger import get_ledger
from backend.data.seed_data import SEED_SUPPLIERS
from eval.evaluator import DomainAgnosticEvaluator, default_supplier_risk_runner

app = FastAPI(
    title="SUPPLIER RISK PLATFORM - Secure MCP-Based Agentic Risk System",
    version="1.0.0",
    description="Security-focused academic & enterprise supplier risk analysis system."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class AnalysisRequest(BaseModel):
    supplier_id: str = Field(..., example="SUP-40217")
    question: str = Field(..., example="Are we exposed if SUP-40217 fails?")
    token: Optional[str] = None

class ToolCallRequest(BaseModel):
    name: str = Field(..., example="get_supplier_balance")
    version: Optional[str] = "v1"
    inputs: Dict[str, Any] = Field(..., example={"supplier_id": "SUP-40217"})
    token: Optional[str] = None

class TokenRequest(BaseModel):
    subject: str = "demo-analyst"
    tenant_id: str = "tenant-alpha"
    scopes: List[str] = ["erp:read", "supply:read", "finance:read", "contracts:read"]

# Auth helper
def get_current_payload(authorization: Optional[str] = Header(None), token_param: Optional[str] = None) -> Dict[str, Any]:
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif token_param:
        token = token_param
    
    if not token:
        # Default demo token for convenience in development
        return {
            "sub": "demo-analyst",
            "tenant_id": "tenant-alpha",
            "scopes": ["erp:read", "supply:read", "finance:read", "contracts:read"],
            "exp": 9999999999
        }
    
    try:
        return decode_jwt_token(token)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "supplier-risk-platform",
        "mcp_registry_tools": len(registry.list_tools())
    }

@app.post("/api/auth/token")
def generate_token(req: TokenRequest):
    token = create_jwt_token(
        subject=req.subject,
        tenant_id=req.tenant_id,
        scopes=req.scopes
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "tenant_id": req.tenant_id,
        "scopes": req.scopes
    }

@app.post("/api/analyze")
def analyze_supplier_risk(req: AnalysisRequest, authorization: Optional[str] = Header(None)):
    payload = get_current_payload(authorization, req.token)
    
    try:
        validate_supplier_id(req.supplier_id)
        planner = AgentPlanner()
        synthesizer = Synthesizer()

        plan_res = planner.plan_and_execute(
            supplier_id=req.supplier_id,
            question=req.question,
            jwt_payload=payload
        )

        synth_res = synthesizer.synthesize(
            supplier_id=req.supplier_id,
            question=req.question,
            tool_results=plan_res["tool_results"],
            execution_trace=plan_res["execution_trace"]
        )

        return synth_res
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suppliers/{supplier_id}")
def get_supplier_details(supplier_id: str, authorization: Optional[str] = Header(None)):
    payload = get_current_payload(authorization)
    try:
        validate_supplier_id(supplier_id)
        if supplier_id not in SEED_SUPPLIERS:
            raise HTTPException(status_code=404, detail=f"Supplier '{supplier_id}' not found.")
        
        supp = SEED_SUPPLIERS[supplier_id]
        if payload.get("tenant_id") != supp.get("tenant_id") and payload.get("tenant_id") != "admin":
            raise HTTPException(status_code=403, detail="Tenant mismatch access denied.")
            
        return supp
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/audit")
def get_audit_ledger(tenant_id: Optional[str] = None, limit: int = 100):
    ledger = get_ledger()
    entries = ledger.get_entries(tenant_id=tenant_id, limit=limit)
    return {"entries": entries, "count": len(entries)}

@app.post("/api/audit/verify")
def verify_audit_ledger(tenant_id: Optional[str] = None):
    ledger = get_ledger()
    res = ledger.verify(tenant_id=tenant_id)
    return res

@app.get("/api/evaluation")
def run_system_evaluation():
    golden_path = os.path.join(os.path.dirname(__file__), "..", "eval", "golden_set.json")
    evaluator = DomainAgnosticEvaluator(golden_path)
    report = evaluator.run_suite(default_supplier_risk_runner)
    return report

@app.get("/api/tools")
def list_mcp_tools():
    return {"tools": registry.list_tools()}

@app.post("/api/tools/call")
def call_mcp_tool(req: ToolCallRequest, authorization: Optional[str] = Header(None)):
    payload = get_current_payload(authorization, req.token)
    try:
        res = dispatch_tool_call(
            tool_name=req.name,
            inputs=req.inputs,
            jwt_payload=payload,
            version=req.version,
            actor="ui-user"
        )
        return res
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp/resource")
def get_ui_resource(supplier_id: str = Query("SUP-40217"), authorization: Optional[str] = Header(None)):
    payload = get_current_payload(authorization)
    try:
        return get_mcp_ui_resource(supplier_id, payload)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthError as e:
        raise HTTPException(status_code=403, detail=str(e))
