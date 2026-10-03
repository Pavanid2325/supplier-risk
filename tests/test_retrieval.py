import pytest
from backend.retrieval.hybrid_search import get_hybrid_retriever

def test_hybrid_retrieval_and_tenant_filtering():
    retriever = get_hybrid_retriever()
    
    # Query for tenant-alpha
    res_alpha = retriever.search(query="insolvency liability", tenant_id="tenant-alpha", k=3)
    assert len(res_alpha) > 0
    for doc in res_alpha:
        assert doc["tenant_id"] == "tenant-alpha"

    # Query for tenant-beta
    res_beta = retriever.search(query="Confidentiality and Scope", tenant_id="tenant-beta", k=3)
    assert len(res_beta) > 0
    for doc in res_beta:
        assert doc["tenant_id"] == "tenant-beta"
