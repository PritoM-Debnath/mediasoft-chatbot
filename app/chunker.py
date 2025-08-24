# It will:
# - read products.json (+ taxonomy.json for validation)
# - create chunks per product field (overview, benefits, features)
# - split long fields to ~150–200 words per chunk
# - write JSONL to --out

import os, json, re, argparse
from datetime import datetime, timezone 
from typing import List, Dict, Any

# ----------- helpers -----------
WORD_MIN, WORD_MAX = 100, 200  # target chunk size
SENTENCE_OVERLAP = 1           # 1 sentence overlap when splitting long fields

def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text or ""))

def sent_split(text: str) -> List[str]:
    # simple sentence splitter (good enough for product text)
    text = (text or "").strip()
    if not text:
        return []
    # split on ., !, ? followed by space/newline
    parts = re.split(r'(?<=[.!?])\s+', text)
    # normalize whitespace
    return [re.sub(r'\s+', ' ', p).strip() for p in parts if p.strip()]

def combine_to_windows(sents: List[str], min_w=WORD_MIN, max_w=WORD_MAX, overlap=SENTENCE_OVERLAP) -> List[str]:
    """Greedy pack sentences into ~min..max word windows; add 1-sentence overlap between windows."""
    chunks, cur, cur_wc = [], [], 0
    for s in sents:
        w = word_count(s)
        if cur and cur_wc + w > max_w:
            chunks.append(" ".join(cur).strip())
            # prepare next window with overlap
            cur = cur[-overlap:] if overlap > 0 else []
            cur_wc = sum(word_count(x) for x in cur)
        cur.append(s)
        cur_wc += w
    if cur:
        chunks.append(" ".join(cur).strip())

    # If a chunk is too short (<min_w) and there is a next chunk, merge them
    fixed = []
    i = 0
    while i < len(chunks):
        if i < len(chunks) - 1 and word_count(chunks[i]) < min_w:
            merged = (chunks[i] + " " + chunks[i+1]).strip()
            fixed.append(merged)
            i += 2
        else:
            fixed.append(chunks[i])
            i += 1
    return fixed

def list_to_paragraph(items: Any, label: str) -> str:
    """
    Normalize list fields to a readable paragraph.
    If items is already a string, return as-is.
    """
    if isinstance(items, list):
        vals = [str(x).strip() for x in items if str(x).strip()]
        if not vals:
            return ""
        return f"{label}: " + "; ".join(vals) + "."
    if isinstance(items, str):
        return items.strip()
    return ""

def make_chunk_obj(product: Dict[str, Any], section_title: str, idx: int, content: str) -> Dict[str, Any]:
    pid = product["id"]
    return {
        "content": content,
        "metadata": {
            "chunk_id": f"ch:{pid}:{section_title.lower().replace(' ','-')}:{idx:03d}",
            "product_id": pid,
            "taxonomy_id": product.get("taxonomy_id"),
            "section_title": section_title,
            "language": product.get("language", "en"),
            "visibility": "public",
            "source_type": "product_record",
            "source_url": product.get("website"),
            "price_range": product.get("price_range"),
            "version": product.get("version", "v1"),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    }

# ----------- main -----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-dir", required=True, help="Folder containing products.json (and taxonomy.json for validation).")
    ap.add_argument("--out", required=True, help="Output JSONL file path, e.g. ./dataset/chunks.jsonl")
    args = ap.parse_args()

    products_path = os.path.join(args.dataset_dir, "products.json")
    taxonomy_path = os.path.join(args.dataset_dir, "taxonomy.json")

    with open(products_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    # Optional: validate taxonomy ids
    if os.path.exists(taxonomy_path):
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            taxonomy = json.load(f)
        tax_ids = {n["id"] for n in taxonomy if isinstance(n, dict) and "id" in n}
    else:
        taxonomy, tax_ids = [], set()

    # Build chunks
    out_lines = []
    for p in products:
        # sanity: product must have taxonomy_id, and ideally it exists in taxonomy.json
        tid = p.get("taxonomy_id")
        if not tid:
            print(f"[WARN] {p.get('id')} missing taxonomy_id; skipping.")
            continue
        if tax_ids and tid not in tax_ids:
            print(f"[WARN] {p.get('id')} taxonomy_id {tid} not found in taxonomy.json; continuing anyway.")

        # 1) Overview (kept separate)
        overview = (p.get("overview") or p.get("overview_text") or "").strip()
        if overview:
            sents = sent_split(overview)
            parts = combine_to_windows(sents)
            for i, text in enumerate(parts, 1):
                out_lines.append(make_chunk_obj(p, "Overview", i, text))

        # 2) Benefits (kept separate)
        # benefits may be a string OR a list of strings OR list of {title, description}
        benefits_raw = p.get("benefits")
        if isinstance(benefits_raw, list):
            # flatten list to sentences/short phrases
            flat = []
            for b in benefits_raw:
                if isinstance(b, dict):
                    t, d = b.get("title"), b.get("description")
                    if t and d: flat.append(f"{t}: {d}")
                    elif d: flat.append(d)
                    elif t: flat.append(t)
                else:
                    flat.append(str(b))
            benefits_text = "Benefits: " + "; ".join(x.strip().rstrip(".") for x in flat if x.strip()) + "."
        else:
            benefits_text = (benefits_raw or p.get("benefits_text") or "").strip()

        if benefits_text:
            sents = sent_split(benefits_text)
            parts = combine_to_windows(sents)
            for i, text in enumerate(parts, 1):
                out_lines.append(make_chunk_obj(p, "Benefits", i, text))

        # 3) Features (kept separate)
        features_text = list_to_paragraph(p.get("features"), "Features") or (p.get("features_text") or "")
        features_text = features_text.strip()
        if features_text:
            sents = sent_split(features_text)
            parts = combine_to_windows(sents)
            for i, text in enumerate(parts, 1):
                out_lines.append(make_chunk_obj(p, "Features", i, text))

    # write JSONL
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for obj in out_lines:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"Wrote {len(out_lines)} chunks to {args.out}")

if __name__ == "__main__":
    main()



