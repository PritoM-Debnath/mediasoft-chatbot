# 💬 AI Chatbot Prototype with RAG (Mediasoft Project)

This project is a **Retrieval-Augmented Generation (RAG) chatbot backend** for a company catalog.  
It ingests product and taxonomy data, chunks the content, embeds it into a vector database (**Pinecone**), and allows **semantic search + LLM-powered responses**.

---

## 📂 Project Structure

```
.
├── app/                     # Core pipeline modules
│   ├── chunker.py           # Splits product content into chunks
│   ├── embedder.py          # Embeds text using SentenceTransformers
│   ├── pinecone_client.py   # Handles Pinecone index and upserts
│   ├── main.py              # Ingests chunks → embeddings → Pinecone
│   └── __init__.py
│
├── retrieval/               # Retrieval + Query system
│   ├── retriever.py         # Retrieves nearest neighbors from Pinecone
│   ├── query.py             # Query helper (RAG pipeline)
│   ├── query_main.py        # Entry point for running retrieval
│   └── __init__.py
│
├── dataset/                 # Project data
│   ├── products.json        # Product definitions
│   ├── taxonomy.json        # Taxonomy (categories, hierarchy)
│   └── chunks.jsonl         # Generated chunks (after running chunker)
│
├── .env                     # Environment variables
├── LICENSE                  # Apache License 2.0
└── README.md                # Project documentation
```

---

## ⚙️ Setup

### 1. Clone the project
```bash
git clone https://github.com/PritoM-Debnath/mediasoft-chatbot.git
cd mediasoft-chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

Minimal dependencies include:
```txt
python-dotenv
pinecone
sentence-transformers
groq  ```

### 3. Configure environment
Modify the `.env.example` to `.env` file in the root directory:

```env
# Pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX=mediasoft-index
PINECONE_DIM=384   # or 1536 depending on embedding model
PINECONE_ENV=us-east-1-gcp

# Groq (optional, for answering with LLM)
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.1-70b-versatile
```

---

## 🚀 Usage

### Step 1: Chunk dataset
```bash
python app/chunker.py --dataset-dir ./dataset --out ./dataset/chunks.jsonl
```

### Step 2: Ingest into Pinecone
```bash
python app/main.py
```

This:
- Loads `chunks.jsonl`
- Generates embeddings
- Upserts into Pinecone index

### Step 3: Run Retrieval
```bash
python -m retrieval.query_main
```

Modify `query_main.py` to test your questions directly:
```python
question = "What are the key features of the Pharmacy POS?"
```

---

## 🧩 Features

- **Taxonomy-driven product structure** (`taxonomy.json`)
- **Product catalog ingestion** (`products.json`)
- **Chunking pipeline** (JSONL format for embeddings)
- **Semantic Search** using Pinecone vector DB
- **Retrieval-Augmented Generation** (via Groq LLM)
- **Modularized codebase** (easy to extend)

---

## 📌 Roadmap

- [ ] Add **chat session memory**
- [ ] Multi-language support (Bangla + English)
- [ ] Add **API layer** (FastAPI/Flask) to serve chatbot
- [ ] Build **frontend integration** (handed to frontend team)

---

## 📄 License

This project is licensed under the **Apache License 2.0** – see the [LICENSE](./LICENSE) file for details.
