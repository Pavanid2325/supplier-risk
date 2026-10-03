from typing import Dict, Any, List

# Synthetic / Mock ERP & Supplier Dataset
# Clearly marked as Synthetic Demo Data

SEED_SUPPLIERS: Dict[str, Dict[str, Any]] = {
    "SUP-40217": {
        "supplier_id": "SUP-40217",
        "name": "Apex Microelectronics GmbH",
        "tenant_id": "tenant-alpha",
        "balance": {
            "supplier_id": "SUP-40217",
            "owed_to_supplier": 184300.0,
            "owed_by_supplier": 0.0,
            "currency": "EUR"
        },
        "alternate_sources": [
            {
                "supplier_id": "SUP-62001",
                "name": "Nordic SemiTech AB",
                "region": "EU-North",
                "capacity": "85%",
                "lead_time_days": 14,
                "availability": "High"
            },
            {
                "supplier_id": "SUP-73012",
                "name": "Vanguard Micro-Components",
                "region": "EU-West",
                "capacity": "90%",
                "lead_time_days": 10,
                "availability": "Medium"
            }
        ],
        "payment_history": [
            {"month": "2025-10", "on_time": True, "delay_days": 0, "amount": 45000.0},
            {"month": "2025-11", "on_time": True, "delay_days": 0, "amount": 52000.0},
            {"month": "2025-12", "on_time": False, "delay_days": 12, "amount": 38000.0},
            {"month": "2026-01", "on_time": True, "delay_days": 0, "amount": 60000.0},
            {"month": "2026-02", "on_time": False, "delay_days": 5, "amount": 41000.0},
            {"month": "2026-03", "on_time": True, "delay_days": 0, "amount": 48300.0}
        ]
    },
    "SUP-51190": {
        "supplier_id": "SUP-51190",
        "name": "Beta ChemSolutions NV",
        "tenant_id": "tenant-beta",  # Isolated tenant
        "balance": {
            "supplier_id": "SUP-51190",
            "owed_to_supplier": 42000.0,
            "owed_by_supplier": 5000.0,
            "currency": "EUR"
        },
        "alternate_sources": [
            {
                "supplier_id": "SUP-73012",
                "name": "Vanguard Micro-Components",
                "region": "EU-West",
                "capacity": "60%",
                "lead_time_days": 21,
                "availability": "Low"
            }
        ],
        "payment_history": [
            {"month": "2025-11", "on_time": True, "delay_days": 0, "amount": 15000.0},
            {"month": "2025-12", "on_time": True, "delay_days": 0, "amount": 12000.0},
            {"month": "2026-01", "on_time": True, "delay_days": 0, "amount": 15000.0}
        ]
    },
    "SUP-62001": {
        "supplier_id": "SUP-62001",
        "name": "Nordic SemiTech AB",
        "tenant_id": "tenant-alpha",
        "balance": {
            "supplier_id": "SUP-62001",
            "owed_to_supplier": 12500.0,
            "owed_by_supplier": 0.0,
            "currency": "EUR"
        },
        "alternate_sources": [
            {
                "supplier_id": "SUP-40217",
                "name": "Apex Microelectronics GmbH",
                "region": "EU-Central",
                "capacity": "75%",
                "lead_time_days": 7,
                "availability": "High"
            }
        ],
        "payment_history": [
            {"month": "2026-01", "on_time": True, "delay_days": 0, "amount": 12500.0}
        ]
    },
    "SUP-73012": {
        "supplier_id": "SUP-73012",
        "name": "Vanguard Micro-Components",
        "tenant_id": "tenant-alpha",
        "balance": {
            "supplier_id": "SUP-73012",
            "owed_to_supplier": 98000.0,
            "owed_by_supplier": 1200.0,
            "currency": "EUR"
        },
        "alternate_sources": [],
        "payment_history": [
            {"month": "2026-01", "on_time": True, "delay_days": 0, "amount": 50000.0},
            {"month": "2026-02", "on_time": True, "delay_days": 0, "amount": 48000.0}
        ]
    }
}
