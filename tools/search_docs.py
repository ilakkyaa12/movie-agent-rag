import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 🔹 Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔹 Global storage
documents = []
doc_ids = []
chunks = []
metadata = []
index = None


# 🔹 Step 1: Load documents
def load_documents(folder_path="data/docs"):
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                text = f.read()
                documents.append(text)
                doc_ids.append(filename.replace(".txt", ""))


# 🔹 Step 2: Simple chunking (no LangChain)
def simple_split(text, chunk_size=500, overlap=50):
    split_chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        split_chunks.append(chunk)
        start += chunk_size - overlap

    return split_chunks


def split_documents():
    global chunks, metadata

    for i, doc in enumerate(documents):
        split_texts = simple_split(doc)

        for chunk in split_texts:
            chunks.append(chunk)
            metadata.append(doc_ids[i])


# 🔹 Step 3: Create vector store (FAISS)
def create_vector_store():
    global index

    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings))


# 🔹 Step 4: Search function
def search_docs(query, top_k=3):
    query_embedding = model.encode([query])

    distances, indices = index.search(np.array(query_embedding), top_k)

    results = []

    for idx in indices[0]:
        results.append({
            "content": chunks[idx],
            "source": metadata[idx]
        })

    return results


# 🔹 Initialize everything (runs once when imported)
load_documents()
split_documents()
create_vector_store()