import json
from embedder import Embedder
from pinecone_client import PineconeClient  
import pinecone 


def load_jsonl(file_path: str) -> list:
    """
    Load a JSONL file containing 'content' and 'metadata'
    """
    dataset = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            dataset.append(item)
    return dataset

if __name__ == "__main__":
    # Path to your JSONL file
    jsonl_file = "C:\\Users\\debna\\OneDrive\\Desktop\\MediaSoft\\dataset\\chunks.jsonl"  

    # Load dataset
    data = load_jsonl(jsonl_file)
    print(f"Loaded {len(data)} items.")

    # Initialize Embedder
    embedder = Embedder()

    # Generate embeddings
    vectors = embedder.embed_dataset(data)
    print(vectors)
    print(f"Generated embeddings for {len(vectors)} items.")

    pc = PineconeClient()
    # Upsert vectors to Pinecone
    pc.upsert_vectors(vectors)