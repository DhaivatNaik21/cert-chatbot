from embed_and_store import retrieve
from evaluation.queries import TEST_QUERIES


def main():
    for question in TEST_QUERIES:
        print(f"\n{'=' * 80}")
        print(f"QUESTION: {question}")

        # override for experimentation with different k values .e.g. [result = retrieve(question, k = 10)]
        result = retrieve(question)

        for rank, (text, metadata, distance) in enumerate(
            zip(
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0],
            ),
            start=1,
        ):
            print(
                f"\n#{rank} | {metadata['doc_id']} "
                f"| chunk {metadata['chunk_id']} "
                f"| distance={distance:.4f}"
            )
            print(text)


if __name__ == "__main__":
    main()