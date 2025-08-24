from sentence_transformers import SentenceTransformer

class Embedder:
    """
    Embedder for generating vector embeddings from text using free models.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> list:
        """
        Embed a single text string.
        Args:
            text (str): Text to embed
        Returns:
            list: Embedding vector
        """
        return self.model.encode(text).tolist()

    def embed_dataset(self, dataset: list) -> list:
        """
        Embed a list of items containing 'content' and 'metadata'.
        Args:
            dataset (list): List of dicts with 'content' and 'metadata'
        Returns:
            list: List of dicts ready for Pinecone upsert
        """
        vectors = []
        for item in dataset:
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            vector = {
                "id": metadata.get("chunk_id"),
                "values": self.embed_text(content),
                "metadata": { 
                    **metadata,
                    "content":content
                }
            }
            vectors.append(vector)
        return vectors

