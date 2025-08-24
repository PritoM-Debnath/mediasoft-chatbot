from typing import Any, Dict, List, Optional

from app.embedder import Embedder
from app.pinecone_client import PineconeClient


class Retriever:
    """
    Embeds a user query with the SAME model used for ingestion and searches Pinecone.
    """
    def __init__(self, top_k: int = 4):
        self.top_k = top_k
        self.embedder = Embedder()      # must match ingestion model
        self.pc = PineconeClient()      # uses env to connect to index

    def embed_query(self, query: str) -> List[float]:
        vec = self.embedder.embed_text(query)
        if not isinstance(vec, list) or not vec:
            raise ValueError("Embedder.embed_text() must return a non-empty list of floats.")
        return vec

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns normalized matches: [{id, score, content, metadata}, ...]
        Assumes content was stored in metadata at ingestion time.
        """
        qvec = self.embed_query(query)
        res = self.pc.index.query(
            vector=qvec,
            top_k=top_k or self.top_k,
            include_metadata=True,
            filter=filters or {},
        )

        hits: List[Dict[str, Any]] = []
        for m in res.get("matches", []) or []:
            md = m.get("metadata") or {}
            hits.append({
                "id": m.get("id"),
                "score": m.get("score"),
                "content": md.get("content", ""),  
                "metadata": md,
            })
        return hits


def build_filter(
    taxonomy_id: Optional[str] = None,
    product_id: Optional[str] = None,
    section_title: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Build a Pinecone v3 JSON filter (exact matches).
    Example returned shape:
      {"$and": [{"taxonomy_id":{"$eq":"cat-pharmacy"}}, {"section_title":{"$eq":"Features"}}]}
    """
    clauses = []
    if taxonomy_id:
        clauses.append({"taxonomy_id": {"$eq": taxonomy_id}})
    if product_id:
        clauses.append({"product_id": {"$eq": product_id}})
    if section_title:
        clauses.append({"section_title": {"$eq": section_title}})
    return {"$and": clauses} if clauses else None
