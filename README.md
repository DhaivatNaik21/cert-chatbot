# DLGS Certifications Assistant

An internal certification reference assistant being developed by the Digital Transformation Unit (DTU) for the Division of Local Government Services (DLGS), New Jersey Department of Community Affairs.

The application uses retrieval-augmented generation (RAG) to help staff locate and understand information from certification reference documents and statutes. Relevant document passages are retrieved from a local vector database and supplied to a language model to generate plain-language answers with source references.

## Development Status

This project is a local development prototype intended for development and testing. It is not a production service. Document coverage, retrieval quality, answer accuracy, and the user interface remain under development. Generated answers should be checked against the cited materials before being used in certification work.

## Purpose and Scope

The assistant is intended to support staff researching certification requirements, application materials, exam qualifications, exemptions, appointments, renewals, and related questions covered by the available documents.

The intended certification scope includes:

- CMFO
- CPWM
- CTC
- QPA
- RMC
- CCFO

Exemption pathways include CMFO/RMA, CPWM/PE, and QPA/SBA where addressed by the available source material. Intended scope does not establish complete document coverage. The assistant can answer only from the passages retrieved from the indexed corpus. The application is a reference aid. It does not make final eligibility, appointment, enforcement, or legal determinations.

## How It Works

The application separates document indexing from question answering.

### Document indexing

1. Load DOCX files from `documents/cert data/`.
2. Extract their text.
3. Split the text into overlapping chunks.
4. Generate embeddings for each chunk.
5. Store the text, embeddings, and source identifiers in a persistent ChromaDB collection.

### Question answering

1. Generate an embedding for the user's question.
2. Retrieve the five nearest document chunks by default.
3. Assemble the retrieved text and document/chunk identifiers into a context block.
4. Send the question and context to the Groq-hosted generation model.
5. Display the generated answer in the Gradio interface or CLI.

The application does not perform live web searches.

## Technology Stack

- Language: Python
- Interface: Gradio
- Document loading: LangChain Community `Docx2txtLoader`
- Text splitting: LangChain `RecursiveCharacterTextSplitter`
- Embeddings: Sentence Transformers `all-MiniLM-L6-v2`
- Vector storage: Persistent ChromaDB
- Generation provider: Groq
- Generation model: `openai/gpt-oss-20b`
- Environment configuration: `python-dotenv`

## Repository Structure

```text
CERT-CHATBOT/
├── documents/
│   └── cert data/             # Certification reference DOCX files
├── chroma_db/                 # Generated local vector database
├── evaluation/
│   ├── __init__.py
│   ├── queries.py             # Reference questions for retrieval testing
│   └── evaluate_retrieval.py  # Inspect retrieved passages and distances
├── config.py                  # Shared paths and pipeline settings
├── ingest_and_chunk.py        # Document loading and chunking
├── embed_and_store.py         # Index construction and retrieval
├── answer.py                  # Context assembly, generation, and CLI
├── gradio_app.py              # Local web interface
├── requirements.txt           # Python dependencies
├── planning.md                # Development planning material
├── README.md
└── .gitignore
```

Local configuration files such as `.env` and the virtual environment are not source documents and should not be committed.

## Local Setup

Run the following commands from the repository root.

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

Replace the placeholders with the private repository URL and the local directory created by cloning.

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create a `.env` file in the repository root:

```dotenv
GROQ_API_KEY=your_api_key_here
```

An environment variable named `GROQ_API_KEY` may also be used.

Do not commit API keys or other credentials. A network connection is required to call the Groq API. Initial embedding model setup may also require downloading model files.

## Configuration

Shared application settings are defined in `config.py`, including:

- Source-document and vector-database paths.
- ChromaDB collection name.
- Embedding and generation models.
- Chunk size, overlap, and split boundaries.
- Default retrieval count.
- Generation temperature.

Paths are resolved relative to the project directory.

Current baseline settings:

- Chunk size: 512 characters.
- Chunk overlap: 100 characters.
- Embedding model: `all-MiniLM-L6-v2`.
- Default retrieval count: 5 chunks.
- Generation model: `openai/gpt-oss-20b`.
- Generation temperature: 0.1.

Keep credentials in `.env` or environment variables, not in `config.py`.

Restart the application after changing configuration settings. Changes to chunking or the embedding model require rebuilding the index. Changes to the retrieval count, generation model, or temperature do not
require rebuilding the index.

## Source Documents

Place supported source documents in:

```text
documents/cert data/
```

The current loader reads `.docx` files directly inside this directory.

It does not currently load PDF or plain-text files, and it does not recursively scan subdirectories. Source filenames are used as document identifiers in the index and answer context. Use descriptive filenames and check extracted text when adding or updating documents. Adding a document to the directory does not automatically make it available to the chatbot. The document must be indexed.

## Indexing Documents

### Optional: inspect ingestion and chunking

```bash
python ingest_and_chunk.py
```

This command loads the documents, reports document and chunk counts, and prints sample chunks for inspection. It does not persist an index or save chunks to an intermediate file.

### Build the vector index

```bash
python embed_and_store.py
```

This command loads and chunks the source documents, generates embeddings, and stores records in the local ChromaDB collection.

Running `ingest_and_chunk.py` separately is not required: the indexing script imports and runs the document-loading and chunking functions.

Current index configuration:

- Source directory: `documents/cert data/`
- Database directory: `chroma_db/`
- Collection: `cert_docs`
- Chunk size: 512 characters
- Chunk overlap: 100 characters
- Split boundaries: paragraphs, line breaks, spaces, then character fallback
- Similarity metric: cosine distance
- Chunk metadata: document filename and zero-based chunk identifier

Document and chunk counts depend on the current corpus and are not fixed. The indexing script loads and chunks source documents, generates embeddings, stores records in ChromaDB, and reports the collection's chunk count. Retrieval questions are run separately through the evaluation script.

## Updating the Corpus

The current indexing implementation uses `collection.add()`. It is not a complete document-synchronization mechanism.

For a clean rebuild after editing, removing, or renaming source documents:

1. Stop the running application.
2. Confirm the source directory contains the intended documents.
3. Delete the generated `cert_docs` collection.
4. Run the indexing script again.
5. Restart the application and verify representative answers.

The following command deletes the local `cert_docs` collection. It does not delete source documents. Run it only when intentionally rebuilding this project's index.

```bash
python -c "import chromadb; chromadb.PersistentClient(path='chroma_db').delete_collection(name='cert_docs')"
```

Then rebuild:

```bash
python embed_and_store.py
```

If the collection does not exist, skip the deletion step and build the index directly.

## Running the Assistant/Testing

Reference questions are maintained in `evaluation/queries.py`.

To inspect the passages retrieved from the existing index, run the following command from the repository root:

```bash
python -m evaluation.evaluate_retrieval
```

The script prints each question, retrieved passages, document and chunk identifiers, and cosine distances.

It does not rebuild the index or call the generation API. Build the index before running it.

This is a manual retrieval-inspection tool, not an automated accuracy evaluation. Review whether the retrieved passages contain the evidence, conditions, and exceptions needed to answer each question.

### Web interface

```bash
python gradio_app.py
```

Open the local URL printed in the terminal.

Starting the interface does not ingest documents or rebuild embeddings.

### Command-line interface

```bash
python answer.py
```

Enter a question at the prompt. Enter `exit` or `quit` to stop.

## Answer Behavior and References

The generation prompt instructs the model to:

- Use only the supplied certification context for factual answers.
- Explain supported information in plain language.
- Distinguish requirements from interpretations and suggested next steps.
- Identify insufficient information rather than invent missing details.
- Describe apparent source conflicts and explain applicability only when supported by the supplied material.
- Include numbered references identifying supporting documents and chunks.

These are model instructions, not guarantees of correctness. The application does not independently validate generated claims or citations.

The context includes document filenames and chunk identifiers. Statute sections can be referenced when present in the retrieved text; they are not currently stored as separate metadata fields.

## Example Questions

- What documents are required for an initial CMFO exam application?
- What information must a repeat CPWM exam applicant submit?
- What qualifications are required for the CTC exam?
- How does the CMFO exam pathway differ from the CMFO/RMA exemption?
- When can a county appoint or reappoint a chief financial officer?
- What do the available documents say about QPA conflicts of interest?

An example question does not imply that the current corpus contains all information needed to answer it.

## Current Limitations

- Retrieval uses vector similarity without keyword search or reranking.
- Five chunks are retrieved by default.
- No relevance threshold is applied before generation.
- Character-based chunks may separate requirements from conditions or exceptions.
- Only directly contained DOCX files are ingested.
- Coverage depends on the available documents and their extracted text.
- The application does not automatically check document currencor resolve legal authority.
- Citations and factual claims are not programmatically verified.
- Each question is processed independently; conversation history is not passed to the generation model.
- The Gradio interface displays answers in a text box.
- Authentication and role-based access controls are not implemented in the application code.
- Index synchronization and automated evaluation remain future work.

## Data Flow

Source files, extracted chunks, and embeddings are processed locally and stored in the local vector database.

When answering a question, the application sends the user's question and retrieved document passages to the Groq API.

The prototype is intended for certification reference material. Do not enter credentials, applicant records, or sensitive information during testing.

## Maintenance

Maintaining unit: Digital Transformation Unit (DTU).

Development activities include:

- Maintaining source document coverage.
- Verifying ingestion and index updates.
- Reviewing retrieved evidence and generated answers.
- Improving chunking and retrieval where testing identifies gaps.
- Keeping dependencies and setup instructions aligned with the code.

Production hosting, access controls, service arrangements, licensing review, and operational support are outside the current prototype scope.


