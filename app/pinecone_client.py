import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

class PineconeClient:
    def __init__(self, index_name: str = "default", dim: int = 384, metric: str = "cosine"):
        self.api_key = os.environ.get("PINECONE_API_KEY")
        self.index_name = os.environ.get("PINECONE_INDEX", index_name)
        self.dim = int(os.environ.get("PINECONE_DIM", dim))
        self.metric = os.environ.get("PINECONE_METRIC", metric)
        self.cloud = os.environ.get("PINECONE_CLOUD", "aws")
        self.region = os.environ.get("PINECONE_REGION", "us-east-1")

        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables.")

        # v3 client: no pinecone.init
        self.pc = Pinecone(api_key=self.api_key)

        # Create index if needed
        existing_names = self.pc.list_indexes().names()
        if self.index_name not in existing_names:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dim,
                metric=self.metric,
                spec=ServerlessSpec(cloud=self.cloud, region=self.region),
            )
            print(f"Created Pinecone index '{self.index_name}' "
                  f"(dim={self.dim}, metric={self.metric}, {self.cloud}/{self.region})")

        # Connect to index
        self.index = self.pc.Index(self.index_name)

    def upsert_vectors(self, vectors: list, batch_size: int = 100):
        """
        vectors: list of dicts like:
          {"id": "<chunk_id>", "values": [float, ...], "metadata": {...}}
        """
        total = len(vectors)
        for i in range(0, total, batch_size):
            batch = vectors[i:i + batch_size]
            # v3 expects: index.upsert(vectors=[{"id","values","metadata"}, ...])
            self.index.upsert(vectors=batch)
            print(f"Upserted batch {i // batch_size + 1} ({len(batch)} / {total})")
