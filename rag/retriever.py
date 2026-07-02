import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DataFrameLoader

INDEX_PATH = "embeddings/faiss_index"


def get_faiss_retriever(df=None, k=3):
    """Initializes or loads a local persistent FAISS vector store index."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Check if vector index is already built and stored locally
    if os.path.exists(INDEX_PATH) and os.path.isdir(INDEX_PATH):

        print("-> Found existing FAISS index on disk. Loading...")
        vector_store = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        if df is None:
            raise ValueError("FAISS local index not found. You must pass a preprocessed DataFrame to initialize it.")

        print("-> Creating new FAISS index from 47k+ rows. This might take a couple of minutes on first run...")
        loader = DataFrameLoader(df, page_content_column="page_content")
        documents = loader.load()
        vector_store = FAISS.from_documents(documents, embeddings)

        print(f"-> Saving built FAISS index to disk at: {INDEX_PATH}")
        os.makedirs("embeddings", exist_ok=True)
        vector_store.save_local(INDEX_PATH)

    return vector_store.as_retriever(search_kwargs={"k": k})