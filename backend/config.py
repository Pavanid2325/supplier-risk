import os
from dotenv import load_dotenv

load_dotenv()

SRP_JWT_SIGNING_KEY = os.getenv("SRP_JWT_SIGNING_KEY", "srp-super-secret-jwt-signing-key-2026-secure")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
DB_PATH = os.getenv("SRP_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "srp_ledger.db"))

# fetches .env takes these values if not set in .env, defaults to these values
DEFAULT_TENANT = "tenant-alpha"
