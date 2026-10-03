from typing import Dict, Any, List
from backend.retrieval.hybrid_search import get_hybrid_retriever
from backend.security.validation import sanitize_search_query, ValidationError

def handle_search_contract_corpus(inputs: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    query = inputs.get("query", "")
    k = inputs.get("k", 3)
    supplier_id = inputs.get("supplier_id")

    if not query:
        raise ValidationError("Search query cannot be empty", field="query")

    sanitized_query = sanitize_search_query(query)
    tenant_id = context.get("tenant_id", "tenant-alpha")

    retriever = get_hybrid_retriever()
    results = retriever.search(
        query=sanitized_query,
        tenant_id=tenant_id,
        k=k,
        supplier_id_filter=supplier_id
    )
    return results
