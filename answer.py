# answer.py

import os
from dotenv import load_dotenv
from groq import Groq

from embed_and_store import retrieve  


load_dotenv()  # loads GROQ_API_KEY from .env in repo root

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set. Add it to .env or your environment.")

client = Groq(api_key=GROQ_API_KEY)

# SYSTEM_PROMPT = """
# You are an internal certification assistant for NJ state certification documents. 
# Answer questions about certification requirements, processes, and rules using ONLY the provided context chunks from the certification corpus. 
# If the context does not contain enough information to answer, say: ‘I don’t have enough information in the provided documents to answer that.’ 
# Do NOT guess or use outside knowledge. 
# Mention which document IDs and chunk IDs you used in your answer (for example, ‘Cert – Criminal History_transcribed, chunk 3’). 
# Note: some documents (e.g., RMC, Renewals, Contact Hours, CERT 2000 Program, Printing Certificates, Revoke–Suspend License – Tenure, Bank Deposits) 
# have not yet been transcribed; if a question clearly requires those, explain that the current corpus may be incomplete.
# """
SYSTEM_PROMPT = """
You are an internal certification assistant for NJ state certification documents. 

=== CONTENT RULES ===
1. Answer questions using ONLY the provided context chunks from the certification corpus. 
2. If the context does not contain enough information to answer, say: 'I don't have enough information in the provided documents to answer that.' 
3. Do NOT guess or use outside knowledge. 
4. MANDATORY: You must explicitly state which document IDs and chunk IDs you used for EVERY piece of information you provide. Append the source right next to the fact or at the bottom of the section (e.g., 'Source: Cert - Criminal History_transcribed, chunk 3').
5. Note: some documents (e.g., RMC, Renewals, Contact Hours, CERT 2000 Program, Printing Certificates, Revoke-Suspend License - Tenure, Bank Deposits) have not yet been transcribed; if a question clearly requires those, explain that the current corpus may be incomplete.

=== GRADIO UI LAYOUT RULES ===
1. NEVER use Markdown tables (e.g., `|---|`). Tables break line breaks in this UI.
2. Use clean, bold headers and standard bulleted lists to structure your information.
3. Add a single empty line between different paragraphs or bullet blocks.
4. Do NOT use HTML tags like '<br>'. Use normal line breaks.
"""



def build_context_string(res):
    """
    Convert Chroma query result into a single context string that
    includes doc/chunk IDs plus the chunk text.
    """
    docs = res["documents"][0]
    metas = res["metadatas"][0]

    ctx_parts = []
    for doc, meta in zip(docs, metas):
        doc_id = meta.get("doc_id", "unknown_doc")
        chunk_id = meta.get("chunk_id", "unknown_chunk")
        ctx_parts.append(
            f"[{doc_id} | chunk {chunk_id}]\n{doc}\n"
        )
    return "\n\n".join(ctx_parts)


def answer_question(question: str, k: int = 5) -> str:
    """
    Retrieve top-k chunks for the question, build a grounded prompt,
    and get an answer from Groq's Llama 3.3 70B.
    """
    retrieval_result = retrieve(question, k=k)
    context = build_context_string(retrieval_result)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Question:\n{question}\n\nContext:\n{context}",
        },
    ]

    completion = client.chat.completions.create(
        # model="llama-3.3-70b-specdec",
        model = "openai/gpt-oss-20b",
        messages=messages,
        temperature=0.1,
    )

    return completion.choices[0].message.content


def main():
    print("Spark RAG CLI. Type 'exit' or 'quit' to stop.")
    while True:
        q = input("\nQ: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        if not q:
            continue

        print("Retrieving and generating answer...")
        try:
            ans = answer_question(q, k=5)
            print("\nA:", ans)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()