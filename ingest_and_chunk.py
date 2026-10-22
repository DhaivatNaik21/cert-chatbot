from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader

from config import CHUNK_SIZE, CHUNK_OVERLAP, CHUNK_SEPARATORS, DOC_DIR

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = CHUNK_SIZE,
    chunk_overlap = CHUNK_OVERLAP,
    separators = CHUNK_SEPARATORS,
)

# def load_documents(doc_dir: Path):
#     docs = []
#     for path in doc_dir.glob("*.docx"):
#         try:
#             loader = Docx2txtLoader(str(path))
#             loaded_docs = loader.load()

#             text = "\n".join([doc.page_content for doc in loaded_docs])

#             docs.append({"id": path.name, "path": str(path), "text": text})

#             print(f"Loaded document: {path.name}")
#         except Exception as e:
#             print(f"Error loading document {path.name}: {e}")

#     return docs

def load_documents(doc_dir: Path):
    if not doc_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {doc_dir}")

    paths = sorted(
        path
        for path in doc_dir.glob("*.docx")
        if not path.name.startswith("~$")
    )

    if not paths:
        raise RuntimeError(f"No DOCX files found in: {doc_dir}")

    docs = []

    for path in paths:
        try:
            loaded_docs = Docx2txtLoader(str(path)).load()
            text = "\n".join(
                doc.page_content for doc in loaded_docs
            ).strip()
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load document: {path.name}"
            ) from exc

        if not text:
            raise RuntimeError(
                f"No text extracted from document: {path.name}"
            )

        docs.append({
            "id": path.name,
            "path": str(path),
            "text": text,
        })

        print(f"Loaded document: {path.name}")

    return docs

def chunk_document(doc):
    chunks = text_splitter.split_text(doc["text"])
    return [
        {
            "doc_id": doc["id"],
            "chunk_id": i,
            "text": chunk,
        }
        for i, chunk in enumerate(chunks)
    ]

def main():
    docs = load_documents(DOC_DIR)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))

    # Preview extracted chunks for ingestion verification
    for c in all_chunks[:5]:
        print("-" * 40)
        print(c["doc_id"], "chunk", c["chunk_id"])
        print(c["text"][:300])

if __name__ == "__main__":
    main()