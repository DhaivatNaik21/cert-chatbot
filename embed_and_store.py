from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from pathlib import Path

from ingest_and_chunk import load_documents, chunk_document

DOC_DIR = Path("documents/cert data")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "cert_docs"

# 1. Set up embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Set up Chroma client + collection
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)

def build_index():
    docs = load_documents(DOC_DIR)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))

    texts = [c["text"] for c in all_chunks]
    ids = [f'{c["doc_id"]}-{c["chunk_id"]}' for c in all_chunks]
    metadatas = [
        {
            "doc_id": c["doc_id"],
            "chunk_id": c["chunk_id"],
        }
        for c in all_chunks
    ]

    embeddings = model.encode(texts, show_progress_bar=True)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

def retrieve(query: str, k: int = 5):
    q_emb = model.encode([query])
    result = collection.query(
        query_embeddings=q_emb,
        n_results=k,
    )
    return result  # includes ids, documents, metadatas, distances

if __name__ == "__main__":
    build_index()
    # quick retrieval sanity check
    res = retrieve("Whom can I contact for questions related to purchasing?")
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        print("----")
        print(meta["doc_id"], meta["chunk_id"], "distance:", dist)
        print(doc[:300])

    print("__________________________Additional retrieval tests__________________________")

    test_queries = [
    "What are the requirements to obtain the CMFO certification?",
    "How to renew a CCFO certification?",
    "What information needs to be completed for a repeat participantfor CPWM certification?",
    "What qualifications are required for a CTC exam?",
    "When can a person be appointed or reappointed as a chief financial officer by a county?",
    ]

    for q in test_queries:
        print("\n=== QUERY:", q)
        res = retrieve(q, k=5) # top 5 chunks
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            print("----")
            print(meta["doc_id"], "chunk", meta["chunk_id"], "distance:", dist)
            print(doc[:300].replace("\n", " "))