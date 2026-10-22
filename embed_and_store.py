from sentence_transformers import SentenceTransformer
import chromadb
from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    DOC_DIR,
    EMBEDDING_MODEL,
    TOP_K,
)
from ingest_and_chunk import load_documents, chunk_document

# Load the local embedding model
model = SentenceTransformer(EMBEDDING_MODEL)

# Open the persistent certification document collection
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

# def retrieve(query: str, k: int = 5):
#     q_emb = model.encode([query])
#     result = collection.query(
#         query_embeddings=q_emb,
#         n_results=k,
#     )
#     return result  # includes ids, documents, metadatas, distances

def retrieve(query: str, k: int = TOP_K):
    query = query.strip()

    if not query:
        raise ValueError("Question cannot be empty.")

    if k < 1:
        raise ValueError("k must be at least 1.")

    count = collection.count()

    if count == 0:
        raise RuntimeError(
            "The certification index is empty. "
            "Run python embed_and_store.py before asking questions."
        )

    query_embedding = model.encode([query])

    return collection.query(
        query_embeddings=query_embedding,
        n_results=min(k, count),
        include=["documents", "metadatas", "distances"],
    )

if __name__ == "__main__":
    build_index()
    print(
        f"Indexing complete. Collection '{COLLECTION_NAME}' "
        f"contains {collection.count()} chunks."
    )

# if __name__ == "__main__":
#     build_index()
#     # quick retrieval sanity check
#     res = retrieve("Whom can I contact for questions related to purchasing?")
#     for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
#         print("----")
#         print(meta["doc_id"], meta["chunk_id"], "distance:", dist)
#         print(doc[:300])

#     print("__________________________Additional retrieval tests__________________________")

#     # test_queries = [
#     # "What are the requirements to obtain the CMFO certification?",
#     # "How to renew a CCFO certification?",
#     # "What information needs to be completed for a repeat participantfor CPWM certification?",
#     # "What qualifications are required for a CTC exam?",
#     # "When can a person be appointed or reappointed as a chief financial officer by a county?",
#     # ]
    
#     test_queries = [
#     "What documents are required for an initial CMFO exam application?",

#     "How do the requirements for a CMFO exam application differ "
#     "from the CMFO/RMA exemption pathway?",

#     "What information must a repeat CPWM exam applicant submit, "
#     "and what differs from a first-time applicant?",

#     "What qualifications are required for the CTC exam? "
#     "Separate mandatory qualifications from any exceptions.",

#     "When can a county appoint or reappoint a chief financial officer? "
#     "Identify any conditions or exceptions in the sources.",

#     "How do I renew a CCFO certification? If the available documents "
#     "do not cover renewal, tell me exactly what you can establish.",

#     "Can someone qualify for the QPA/SBA exemption? "
#     "What facts about the applicant would you need to check?",

#     "What do the documents say about conflicts of interest "
#     "for a QPA? Distinguish explicit restrictions from interpretation.",

#     "If an internal reference document and a statute appear "
#     "to disagree about an appointment requirement, explain both "
#     "and whether the supplied sources resolve the difference.",

#     "Does the absence of a listed requirement mean "
#     "the applicant does not need to satisfy it?",

#     "What are the RMC exam requirements? Identify any "
#     "limitations in the available source coverage.",
# ]

#     for q in test_queries:
#         print("\n=== QUERY:", q)
#         res = retrieve(q, k=5) # top 5 chunks
#         for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
#             print("----")
#             print(meta["doc_id"], "chunk", meta["chunk_id"], "distance:", dist)
#             print(doc[:300].replace("\n", " "))