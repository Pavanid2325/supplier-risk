# SUPPLIER RISK PLATFORM — Secure MCP-Based Agentic Supplier Risk Analysis System

> **A Security-Focused Enterprise Architecture for Controlled MCP Tool Execution, Tenant Isolation, Hybrid Retrieval, Concurrent Planning, Deterministic Reduction, 3-Layer Evaluation, Adversarial Defense, and Tamper-Evident Audit Logging.**

---

## 1. Project Overview
The **Supplier Risk Platform (SRP)** is a production-grade, security-focused academic and enterprise system designed to evaluate supply chain exposure when key suppliers experience financial failure or operational default.

Rather than relying on unconstrained RAG chatbots or raw LLM output, SRP coordinates four controlled Model Context Protocol (MCP) tools through a schema-validated tool registry, multi-threaded agent planner, thread-safe reducer, hybrid TF-IDF + Reciprocal Rank Fusion (RRF) search engine, and SHA-256 tamper-evident audit ledger.

All supplier data is 100% synthetic mock data to ensure complete privacy and repeatability.

---

## 2. Problem Statement
Modern enterprises face severe supply chain vulnerabilities when key Tier-1 suppliers default. Generic AI chatbots fail in enterprise governance because they:
1. Blindly trust retrieved contract summaries over live ERP financial ledgers.
2. Lack tenant isolation and JWT scope authorization, risking cross-tenant data leaks.
3. Fail to log executions in a tamper-evident audit ledger.
4. Suffer from race conditions when aggregating parallel tool responses.

The Supplier Risk Platform addresses these vulnerabilities by establishing **Factual Precedence** (authoritative ERP ledger data overrides unverified document text) and enforcing unified security validation for both agent and UI requests.

---

## 3. Architecture

```
React Dashboard (Vite + Tailwind CSS)
        |
        v
FastAPI Application (/api/analyze, /api/tools, /api/audit, /api/mcp/resource)
        |
        v
Agent Planner (Concurrent Multi-Tool Scheduler via ThreadPoolExecutor)
        |
        v
MCP Tool Registry (Input Regex Schema Validation & JWT Scope Check)
        |
   +----+----+----+----------------+
   |         |         |            |
   v         v         v            v
get_supplier get_alternate get_payment search_contract
  _balance    _sources     _history      _corpus
   |         |         |            |
   +---------+---------+------------+
                     |
                     v
  Safe Deterministic Reducer (Aggregates 4/4 tool results)
                     |
                     v
 Grounded Synthesizer (Factual Precedence & Grounding Warnings)
                     |
          +----------+----------+
          |                     |
          v                     v
      Final Answer          Audit Ledger (SHA-256 Chained SQLite)
```

---

## 4. Technologies
- **Backend**: Python 3.12+, FastAPI, Uvicorn, Pydantic v2, PyJWT, scikit-learn, SQLite.
- **Frontend**: React 18, Vite 5, Tailwind CSS, Lucide Icons.
- **Protocol**: Model Context Protocol (MCP Python SDK v1.2+).
- **Retrieval Engine**: TF-IDF, Keyword Token Overlap, Reciprocal Rank Fusion (RRF).
- **Testing & Fuzzing**: Pytest, Custom 1000-request Schema Fuzzer.

---

## 5. Folder Structure

```
supplier-risk/
├── .env.example
├── README.md
├── requirements.txt
├── package.json
├── pytest.ini
├── run_demo.py
├── run_demo.ps1
├── backend/
│   ├── app.py                     # FastAPI server & REST API
│   ├── config.py                  # Configuration settings
│   ├── security/
│   │   ├── auth.py                # JWT creation, scope checking, tenant isolation
│   │   └── validation.py          # Input regex (^SUP-[0-9]{5}$) & SQLi defense
│   ├── mcp/
│   │   ├── registry.py            # Central MCP Tool Registry (v1 & v2 versioning)
│   │   ├── dispatcher.py          # Unified tool dispatch path & audit logger
│   │   ├── app_resource.py        # MCP UI resource (ui://srp/supplier-exposure-view)
│   │   └── tools/                 # Tool handlers
│   │       ├── balance.py         # get_supplier_balance
│   │       ├── alternate.py       # get_alternate_sources
│   │       ├── payment.py         # get_payment_history (v1 & v2)
│   │       └── contract.py        # search_contract_corpus
│   ├── retrieval/
│   │   ├── corpus.py              # Clause/heading chunker
│   │   └── hybrid_search.py       # Hybrid TF-IDF + Keyword + RRF retriever
│   ├── agent/
│   │   ├── planner.py             # Concurrent multi-tool scheduler
│   │   ├── reducer.py             # Safe thread-locked reducer & naive race fixture
│   │   └── synthesizer.py         # Grounded synthesizer with factual precedence
│   ├── ledger/
│   │   └── ledger.py              # SQLite SHA-256 chained audit log
│   └── data/
│       ├── seed_data.py           # Synthetic supplier database
│       └── corpus_docs/           # Contract markdown files & adversarial fake doc
├── eval/
│   ├── evaluator.py               # Domain-agnostic 3-layer evaluator
│   ├── golden_set.json            # 12 benchmark evaluation questions
│   ├── adversarial_tests.py       # Defense against fake document injection attacks
│   └── domains/
│       └── office_supplies/       # Second domain proving evaluator domain-independence
└── tests/
    ├── test_security.py           # JWT, scope, tenant isolation, SQLi, malformed regex
    ├── test_tools.py              # Tool registry & versioning backward compatibility
    ├── test_retrieval.py          # Hybrid RRF search & tenant entitlement filter
    ├── test_adversarial.py        # Factual precedence over fake contract figures
    ├── test_reducer.py            # Safe reducer vs Naive race condition
    ├── test_ledger.py             # SHA-256 tamper detection verification
    └── test_fuzz_tools.py         # 1000 malformed requests fuzz testing (0 bypasses)
└── frontend/                      # React + Vite + Tailwind CSS Dashboard
```

---

## 6. Installation

### Prerequisites
- Python 3.12+
- Node.js v18+ and npm

### Step 1: Install Backend Dependencies
```bash
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
# if want to check api working open: http://localhost:8000/docs
```

### Step 2: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 7. Environment Setup
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default content:
```env
SRP_JWT_SIGNING_KEY=srp-super-secret-jwt-signing-key-2026-secure
LLM_PROVIDER=mock
LLM_API_KEY=
```

---

## 8. Backend Run Commands
Start the FastAPI server on port 8000:

```bash
uvicorn backend.app:app --reload --port 8000
```

FastAPI Documentation (Swagger UI): `http://localhost:8000/docs`

---

## 9. Frontend Run Commands
Start the React + Vite dashboard on port 3000:

```bash
cd frontend
npm run dev
```

Dashboard URL: `http://localhost:3000`

---

## 10. How to Seed Data
Synthetic seed data is loaded automatically from `backend/data/seed_data.py` and markdown contract files in `backend/data/corpus_docs/`. No extra seeding commands required.

Suppliers available in seed data:
- `SUP-40217`: Apex Microelectronics GmbH (High Exposure >100k EUR)
- `SUP-51190`: Beta ChemSolutions NV (Isolated `tenant-beta`)
- `SUP-62001`: Nordic SemiTech AB
- `SUP-73012`: Vanguard Micro-Components

---

## 11. How to Run Tests
Run the entire Pytest test suite (17 tests covering security, retrieval, reducer, versioning, ledger tamper detection, adversarial defense, and fuzzing):

```bash
python -m pytest -v
```

### Run Fuzz Test (1000 Malformed Requests):
```bash
python -m tests.test_fuzz_tools
```

---

## 12. How to Run Evaluation
Run the domain-agnostic 3-layer evaluation suite against the 12 golden set questions:

```bash
python -m eval.evaluator
```

---

## 13. How to Run Adversarial Tests
Run specific defense tests verifying immunity against fake balance document injection attacks:

```bash
python -m eval.adversarial_tests
```

---

## 14. How to Verify Ledger
Run SHA-256 audit ledger cryptographic verification:

```bash
python -c "from backend.ledger.ledger import get_ledger; print(get_ledger().verify())"
```

---

## 15. How to Test MCP Tools via API

### List Registered Tools:
```bash
curl http://localhost:8000/api/tools
```

### Call Tool `get_supplier_balance`:
```bash
curl -X POST http://localhost:8000/api/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_supplier_balance", "version": "v1", "inputs": {"supplier_id": "SUP-40217"}}'
```

---

## 16. How to Test the UI
1. Open `http://localhost:3000` in browser.
2. Navigate to **Supplier Risk Analysis**.
3. Select `SUP-40217` and click **Analyze Risk**.
4. Inspect the concurrent tool timeline, citations, and evidence warnings.
5. Navigate to **Audit Ledger** and click **[Verify Ledger]** to test SHA-256 chain integrity.

---

## 17. Troubleshooting
- **Port 8000 or 3000 in use**: Ensure no existing processes occupy port 8000 or 3000.
- **Permission Error on SQLite DB**: SQLite locks database files while opened. Run `pytest` or `run_demo.py` directly.

---

## 18. Example Queries
- `"Are we exposed if SUP-40217 fails?"`
- `"What is the open balance for SUP-40217?"`
- `"What alternative suppliers can replace SUP-40217?"`

---

## 19. Expected Outputs
For `SUP-40217`:
- **Concise Answer**: YES, we are significantly exposed if SUP-40217 fails. Direct financial exposure totals 184,300.00 EUR in open accounts payable. However, operational risk is mitigated by 2 qualified alternate suppliers.
- **Financial Exposure**: 184,300.00 EUR.
- **Alternates**: Nordic SemiTech AB (EU-North, 14 days lead time), Vanguard Micro-Components (EU-West, 10 days lead time).

---

## 20. Security Design
- **Strict Input Regex**: Tool inputs matching `^SUP-[0-9]{5}$` are validated prior to tool handler execution.
- **JWT Authorization**: Token payload claims (`tenant_id`, `scopes`) are checked at the tool dispatcher level.
- **Cross-Tenant Isolation**: Tenant A credentials can never retrieve Tenant B contract documents or ERP records.
- **Factual Precedence**: Authoritative ERP ledger records take strict precedence over untrusted document text.

---

## 21. Limitations
- All dataset supplier records and agreement documents are synthetic demo figures.

---

## 22. Future Improvements
- Multi-region replication for SQLite ledger chains.
- Production OAuth2 server integration.

---

## HOW TO RUN (Quick Commands)

### Option 1: One-Command Python Runner
```bash
python run_demo.py
```

### Option 2: Windows PowerShell
```powershell
.\run_demo.ps1
```

### Option 3: Manual Execution
```bash
# Terminal 1 (Backend)
uvicorn backend.app:app --reload --port 8000

# Terminal 2 (Frontend)
cd frontend
npm run dev

# Run Tests
pytest -v
```
