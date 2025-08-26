from __future__ import annotations
import os
from typing import Dict, Any, List, Optional

from .retriever import Retriever, build_filter  
from .categorize import categorize_keywords

def build_context_for_llm(contexts: List[Dict[str, Any]]) -> str:
    lines = []
    for i, c in enumerate(contexts, 1):
        md = c["metadata"]
        hdr = (
            f"[{i}] chunk_id={md.get('chunk_id')} | product_id={md.get('product_id')} | price_range={md.get('price_range')} "
            f"| taxonomy_id={md.get('taxonomy_id')} | section={md.get('section_title')} | url={md.get("source_url")}"
        )
        lines.append(hdr + "\n" + (md.get("content") or ""))             #c.get("content") ==> md.get("content")
    return "\n\n".join(lines)

def answer_with_groq(question: str, contexts: List[Dict[str, Any]]) -> str:
    """RAG answer with Groq (free tier available). Falls back to showing contexts if no key."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        joined = "\n\n".join(c.get("content") or "" for c in contexts)
        return f"(No GROQ_API_KEY set)\n\nTop contexts:\n{joined[:2000]}"

    
    from groq import Groq
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = Groq(api_key=api_key)

    system_prompt = (
        "You are a precise human like assistant for a company catalog.\n"
        "- Answer ONLY using the provided context. Do not hallucinate\n"
        "- Response should be in a human conversational tone.\n"
        "- If the answer is not present, say you don't know.\n"
        "- Cite chunk's url from the context in the next line like, 'For more info, go to : {url}' \n"
        "- Keep answers concise and factual. However, give a brief version only if needed.\n"
        "- If there are multiple questions, provide separate complete answers in different paragraphs."
    )
    ctx = build_context_for_llm(contexts)
    print(ctx)
    user_msg = f"Question: {question}\n\nContext:\n{ctx}\n\nAnswer:"

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()

    # taxonomy_id: Optional[str] = None,
    # product_id: Optional[str] = None,
    # section_title: Optional[str] = None,
def run_query(
    question: str,
    top_k: int = 4,
) -> Dict[str, Any]:
    
    taxonomy_id, section_title = categorize_keywords(question)
    retriever = Retriever(top_k=top_k)
    flt = build_filter(taxonomy_id, section_title)
    hits = retriever.search(question, top_k=top_k, filters=flt)
    answer = answer_with_groq(question, hits)
    return {"matches": hits, "answer": answer}

 