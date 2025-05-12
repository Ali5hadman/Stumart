import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
import os

# --- Configuration ---
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "pdf_chunks")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# --- Initialize Qdrant client and embedding model ---
qdrant = QdrantClient(url=QDRANT_URL)
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": DEVICE})

# --- Create or recreate the vector collection ---
def create_vector_collection(collection_name: str, vector_size: int):
    """
    (Re)creates a Qdrant collection with cosine distance.
    """
    # if not qdrant.collection_exists(collection_name):
    #     qdrant.create_collection(
    #         collection_name=collection_name,
    #         vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE),
    #     )
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(
            size=vector_size,
            distance=rest.Distance.COSINE,
        ),
    )
    st.success(f"Collection '{collection_name}' created with vector size {vector_size}.")

# --- Load file, split into chunks, and embed ---
def load_and_embed(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    Loads a PDF, splits into text chunks, computes embeddings, and returns texts and vectors.
    """
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    long_text = " ".join([page.page_content for page in pages])

    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = splitter.create_documents([long_text])

    texts = [doc.page_content for doc in docs]
    print(type(texts), texts[3:])
    vectors = embeddings.embed_documents(texts)

    return texts, vectors

# --- Upload texts and vectors to collection ---
def upload_to_qdrant(collection_name: str, texts: list[str], vectors: list[list[float]]):
    """
    Uploads points to the specified Qdrant collection.
    """
    points = [
        rest.PointStruct(id=i, vector=vectors[i], payload={"text": texts[i]})
        for i in range(len(vectors))
    ]
    qdrant.upsert(collection_name=collection_name, points=points)
    st.success(f"Uploaded {len(points)} chunks to collection '{collection_name}'.")


# --- Streamlit UI ---
def main():
    # texts, vectors = load_and_embed("book.pdf")
    # create_vector_collection(COLLECTION_NAME, len(vectors[0]))
    # upload_to_qdrant(COLLECTION_NAME, texts, vectors)

    st.title("📄 PDF to Vector DB Uploader")
    st.write("Upload a PDF file to chunk, embed, and store in Qdrant.")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.info("File uploaded, processing...")

        texts, vectors = load_and_embed("temp.pdf")
        create_vector_collection(COLLECTION_NAME, len(vectors[0]))
        upload_to_qdrant(COLLECTION_NAME, texts, vectors)

        os.remove("temp.pdf")

if __name__ == "__main__":
    main()