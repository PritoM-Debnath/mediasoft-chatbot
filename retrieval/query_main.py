from .query import run_query

def run():
    #Test Questions: "What is the price of pharmacy POS ?", "What are the key features of the pharmacy POS?", 
    res = run_query(
        question="what are the key features of groceries-pos ?",  
        top_k=4,
        section_title="Features",
        taxonomy_id="cat-groceries",
    )
    print("\n=== ANSWER ===\n")
    print(res["answer"])

    print("\n=== MATCHED CHUNKS ===\n")
    for i, m in enumerate(res["matches"], 1): 
        md = m["metadata"]
        print(f"[{i}] {m['id']}  score={m['score']:.4f}")
        print(f"    product={md.get('product_id')}  taxonomy={md.get('taxonomy_id')}  section={md.get('section_title')}")
        print(f"    url={md.get('source_url')}; price_range={md.get('price_range')}")
        print(f"    Content:{m['content'][:500]}...\n")

if __name__ == "__main__":
    run()
