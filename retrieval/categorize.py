import re
from typing import Optional, Tuple, Dict, List 

# Keywords for categorization (can be expanded/tuned)
SECTION_KEYWORDS = {
    "benefits": [
        "benefit", "advantage", "pro", "gain", "value",
        "positive", "merit", "strength", "edge", "usefulness",
        "good point", "plus", "worth", "perk", "reason to choose",
        "added value", "profit", "helpfulness", "improvement"
    ],
    "features": [
        "feature", "functionality", "capability", "option",
        "characteristic", "trait", "element", "attribute", "component",
        "specification", "module", "property", "highlight", "tool",
        "technical detail", "function", "aspect", "ability", "part"
    ],
    "overview": [
        "overview", "description", "about", "summary", "info",
        "introduction", "background", "explanation", "insight", "outline",
        "details", "introduction", "snapshot", "presentation", "context",
        "general info", "profile", "introductory section"
    ]
}

TAXONOMY_KEYWORDS = {
    "cat-pharmacy": [
        "pharmacy ", "retailpharma", "drugstore", "medicine "
    ],
    "cat-chemist": [
        "chemist ", "apothecary"
    ],
    "cat-ayurvedic": [
        "ayurvedic ", "herbal", "natural"
    ],
    "cat-surgical": [
        "surgical", "clinic", "surgery"
    ],
    "cat-superstore": [
        "superstore", "supershop", "departmental", "mega mart"
    ],
    "cat-groceries": [
        "grocery", "daily need"
    ],
    "cat-convenience-store": [
        "convenience", "mini mart", "corner shop", "small retail"
    ],
    "cat-department-stores": [
        "departmental", "multi category"
    ],
    "cat-hypermarket": [
        "hypermarket", "big retail", "mega retail", "large supermarket"
    ],
    "cat-fruits-vegetables": [
        "fruits ", "vegetables", "fresh produce"
    ],
    "cat-meat-butcher": [
        "butcher ", "meat", "poultry"
    ],
    "cat-apparel-clothing": [
        "clothing ", "apparel", "fashion"
    ],
    "cat-boutiques-handicrafts": [
        "boutique ", "handicraft", "artisan", "fashion boutique"
    ],
    "cat-readymade-garment": [
        "garment ", "readymade clothing", "garment showroom", "cloth retail"
    ],
    "cat-tailoring-fabrics": [
        "tailor", "fabric", "dressmaking", "tailoring"
    ],
    "cat-fancy-costume": [
        "costume", "fancy", "party"
    ],
    "cat-home-decore": [
        "home decore", "furniture", "interior", "furnishing"
    ],
    "cat-luggage-bags": [
        "luggage", "bag", "travel accessories", "backpack"
    ],
    "cat-fashion-watches": [
        "watch", "timepiece", "time", "watches"
    ],
    "cat-glass-crockeries": [
        "crockery", "glassware", "utensils", "kitchenware"
    ],
    "cat-baby-kids-store": [
        "baby", "kids", "toy", "infant"
    ],
    "cat-books-shop": [
        "bookshop", "stationery", "library", "bookstore"
    ],
    "cat-cosmetics-perfumes": [
        "cosmetic", "perfume", "beauty", "makeup"
    ],
    "cat-jewellery": [
        "jewellery", "gold", "diamond", "ornaments"
    ],
    "cat-salon-spa": [
        "salon", "parlor ", "spa"
    ],
    "cat-beauty-parlor": [
        "parlor", "beauty", "makeup"
    ],
    "cat-footwear": [
        "footwear", "shoe", "sandal", "sneaker"
    ],
    "cat-electronics-shop-pos": [
        "electronics", "electrical", "appliance", "gadget"
    ],
    "cat-mobile-phone-accessories": [
        "mobile", "phone accessories", "smartphone", "cell phone"
    ],
    "cat-computer-hardware-shop-pos": [
        "computer", "hardware", "pc", "laptop" "electronics accessories"
    ],
    "cat-camera-accessories-software": [
        "camera", "dslr shop ", "photography"
    ],
    "cat-restaurant": [
        "restaurant", "dining", "food order"
    ],
    "cat-quick-service-restaurant": [
        "quick service", "fast food", "takeaway", "quick dine"
    ],
    "cat-fine-dine": [
        "fine dining", "luxury", "dine-in"
    ],
    "cat-food-court": [
        "food court", "canteen", "multi-outlet restaurant"
    ],
    "cat-burger-sandwich": [
        "burger", "sandwich", "fast food", "snack"
    ],
    "cat-bakery": [
        "bakery", "erp", "confectionery", "cake", "bread"
    ],
    "cat-franchise": [
        "franchise", "multi-branch", "chain store"
    ],
    "cat-ecommerce-dev": [
        "ecommerce development", "online store building", "webshop design"
    ],
    "cat-ecommerce-om": [
        "order management", "oms", "order tracking software", "ecommerce operations"
    ],
}

def _score_matches(text: str, keywords: List[str]) -> int:
    """Count keyword hits with word-boundary matching (case-insensitive)."""
    hits = 0
    for kw in keywords:
        # exact word/phrase match, escaped, case-insensitive
        if re.search(rf"\b{re.escape(kw)}\b", text, flags=re.IGNORECASE):
            hits += 1
    return hits

def _select_unique_best(text: str, table: Dict[str, List[str]]) -> Optional[str]:
    """
    Return the single key with the highest score if:
    - score > 0, and
    - it is a unique maximum (no tie).
    Otherwise return None 
    """
    scored = []
    for key, kws in table.items():
        scored.append((key, _score_matches(text, kws)))

    if not scored:
        return None

    # Find best score
    best_key, best_score = max(scored, key=lambda x: x[1])

    # If no hits at all or there’s a tie for best score, return None
    if best_score == 0:
        return None
    if sum(1 for _, s in scored if s == best_score) > 1:
        return None

    return best_key


def categorize_keywords(question: str) -> Tuple[Optional[str], Optional[str]]:
    
    """
    Returns (taxonomy_id, section_title) based on the question text.

    Rule: if keyword matching does not go well (no clear unique best match),
    return None for that field.
    """
    q = (question or "").strip()
    if not q:
        return None, None

    # Decide section_title (benefits/features/overview) with unique-best criterion
    section_title = _select_unique_best(q, SECTION_KEYWORDS)

    # Decide taxonomy_id with the same unique-best criterion
    taxonomy_id = _select_unique_best(q, TAXONOMY_KEYWORDS)

    return taxonomy_id, section_title


def main():
    question = "what are the key features of groceries ?"
    taxonomy_id, section_title = categorize_keywords(question)
    print(f"Taxonomy ID: {taxonomy_id}")
    print(f"Section Title: {section_title}")


if __name__ == "__main__":
    main()