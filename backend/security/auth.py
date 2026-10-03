import time
import jwt
from typing import List, Dict, Any, Optional
from backend.config import SRP_JWT_SIGNING_KEY

ALGORITHM = "HS256"

class AuthError(Exception):
    def __init__(self, message: str, code: str = "UNAUTHORIZED"):
        super().__init__(message)
        self.message = message
        self.code = code

def create_jwt_token(
    subject: str,
    tenant_id: str,
    scopes: List[str],
    expires_in_seconds: int = 3600
) -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "scopes": scopes,
        "iat": now,
        "exp": now + expires_in_seconds
    }
    return jwt.encode(payload, SRP_JWT_SIGNING_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SRP_JWT_SIGNING_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("JWT token has expired", code="EXPIRED_TOKEN")
    except jwt.InvalidTokenError as e:
        raise AuthError(f"Invalid JWT token: {str(e)}", code="INVALID_TOKEN")

def check_scope(
    token_or_payload: Any,
    required_scope: str,
    resource_tenant_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validates token, verifies expiry, checks required scope, and enforces tenant isolation.
    Rejects:
    1. invalid token
    2. expired token
    3. tenant mismatch (if resource_tenant_id is provided)
    4. missing scope
    """
    if isinstance(token_or_payload, str):
        payload = decode_jwt_token(token_or_payload)
    elif isinstance(token_or_payload, dict):
        payload = token_or_payload
    else:
        raise AuthError("Invalid authorization format", code="INVALID_TOKEN")

    # Check expiry explicitly if token payload passed directly as dict
    exp = payload.get("exp")
    if exp and int(time.time()) > exp:
        raise AuthError("JWT token has expired", code="EXPIRED_TOKEN")

    # 1. Tenant mismatch check
    token_tenant = payload.get("tenant_id")
    if resource_tenant_id and token_tenant != resource_tenant_id:
        raise AuthError(
            f"Tenant mismatch: token tenant '{token_tenant}' cannot access resource tenant '{resource_tenant_id}'",
            code="TENANT_MISMATCH"
        )

    # 2. Scope check
    scopes = payload.get("scopes", [])
    if required_scope not in scopes and "*" not in scopes:
        raise AuthError(
            f"Missing required scope: '{required_scope}'",
            code="MISSING_SCOPE"
        )

    return payload
