import os
import math
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.retrieval.corpus import ContractChunk, load_and_chunk_corpus

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "corpus_docs")

class HybridRetriever:
    def __init__(self, corpus_dir: str = CORPUS_DIR):
        self.corpus_dir = corpus_dir
        self.chunks: List[ContractChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.reload_corpus()

    def reload_corpus(self):
        self.chunks = load_and_chunk_corpus(self.corpus_dir)
        if self.chunks:
            texts = [c.text for c in self.chunks]
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        else:
            self.vectorizer = None
            self.tfidf_matrix = None

    def search(
        self,
        query: str,
        tenant_id: str,
        k: int = 3,
        supplier_id_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval combining TF-IDF + Keyword Overlap + Reciprocal Rank Fusion (RRF)
        with tenant entitlement filtering.
        """
        if not self.chunks or not self.vectorizer or self.tfidf_matrix is None:
            return []

        # 1. Tenant Entitlement Filtering
        eligible_indices = []
        for idx, chunk in enumerate(self.chunks):
            # Tenant isolation strict check
            if chunk.tenant_id != tenant_id and tenant_id != "admin":
                continue
            
            # Optional supplier filter if chunk has supplier_id metadata
            chunk_supp = chunk.metadata.get("supplier_id")
            if supplier_id_filter and chunk_supp and chunk_supp != supplier_id_filter:
                continue

            eligible_indices.append(idx)

        if not eligible_indices:
            return []

        # 2. TF-IDF Scoring
        query_vec = self.vectorizer.transform([query])
        tfidf_sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Rank by TF-IDF among eligible
        tfidf_ranked = sorted(eligible_indices, key=lambda i: tfidf_sims[i], reverse=True)
        tfidf_ranks = {idx: rank + 1 for rank, idx in enumerate(tfidf_ranked)}

        # 3. Keyword Overlap Scoring
        query_tokens = set(query.lower().split())
        keyword_scores = {}
        for idx in eligible_indices:
            text_tokens = set(self.chunks[idx].text.lower().split())
            overlap = len(query_tokens.intersection(text_tokens))
            keyword_scores[idx] = overlap

        keyword_ranked = sorted(eligible_indices, key=lambda i: keyword_scores[i], reverse=True)
        keyword_ranks = {idx: rank + 1 for rank, idx in enumerate(keyword_ranked)}

        # 4. Reciprocal Rank Fusion (RRF)
        # RRF score = 1 / (60 + r_tfidf) + 1 / (60 + r_kw)
        rrf_scores = {}
        for idx in eligible_indices:
            r1 = tfidf_ranks[idx]
            r2 = keyword_ranks[idx]
            rrf_scores[idx] = (1.0 / (60.0 + r1)) + (1.0 / (60.0 + r2))

        # Sort by RRF score descending
        final_ranked = sorted(eligible_indices, key=lambda i: rrf_scores[i], reverse=True)[:k]

        results = []
        for idx in final_ranked:
            chunk = self.chunks[idx]
            results.append({
                "document_id": chunk.document_id,
                "section": chunk.section,
                "text": chunk.text,
                "score": round(rrf_scores[idx], 4),
                "tenant_id": chunk.tenant_id,
                "source": chunk.metadata.get("source", "Contract Store"),
                "metadata": chunk.metadata
            })

        return results

_global_retriever: Optional[HybridRetriever] = None

def get_hybrid_retriever() -> HybridRetriever:
    global _global_retriever
    if _global_retriever is None:
        _global_retriever = HybridRetriever()
    return _global_retriever
