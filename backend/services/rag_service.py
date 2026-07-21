import chromadb

from services.vector_service import create_embedding

client = chromadb.PersistentClient(
    path="vector_db"
)

collection = client.get_or_create_collection(
    name="spreadsheet_data"
)


CHUNK_SIZE = 25


def add_dataframe(filename, dataframe):
    """Kept for backwards compatibility -- indexes a whole dataframe under
    a filename. Prefer add_table() for new code so chunks are traceable
    back to a specific subtable."""
    add_table(table_id=filename, filename=filename, table_name=filename, dataframe=dataframe)


def add_table(table_id, filename, table_name, dataframe):
    """Index one detected subtable, chunked by row, tagged with the
    table_id so search results can be traced back to the exact subtable
    (and dataframe) they came from."""

    texts = []
    metadatas = []
    ids = []
    embeddings = []

    total_rows = len(dataframe)

    if total_rows == 0:
        return

    for start in range(0, total_rows, CHUNK_SIZE):

        chunk = dataframe.iloc[start:start + CHUNK_SIZE]
        text = f"Table: {table_name}\n{chunk.to_string(index=False)}"

        embedding = create_embedding(text)

        ids.append(f"{table_id}_{start}")
        texts.append(text)
        embeddings.append(embedding)

        metadatas.append({
            "file": filename,
            "table_id": table_id,
            "table_name": table_name,
            "start_row": start,
            "end_row": min(start + CHUNK_SIZE - 1, total_rows - 1)
        })

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    print(f"Indexed {len(ids)} chunks from table '{table_name}' ({filename})")


def add_text(doc_id, filename, text, extra_meta=None):
    """Index raw text (e.g. a PDF page) that isn't tabular."""

    if not text or not text.strip():
        return

    embedding = create_embedding(text)

    metadata = {"file": filename, "table_id": None, "table_name": None}
    if extra_meta:
        metadata.update(extra_meta)

    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )


def search(question, n_results=10):

    embedding = create_embedding(question)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )

    if not results["documents"]:
        return []

    return results["documents"][0]


def clear_database():

    global collection

    client.delete_collection("spreadsheet_data")

    collection = client.get_or_create_collection(
        name="spreadsheet_data"
    )
