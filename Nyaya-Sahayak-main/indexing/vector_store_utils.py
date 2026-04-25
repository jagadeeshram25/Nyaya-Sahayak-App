
from config.settings import settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def get_embedding_model():
    # Use free local embeddings from HuggingFace
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def create_or_load_vector_store():
    settings.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = get_embedding_model()
    
    # Check if FAISS index already exists
    index_path = settings.VECTOR_STORE_DIR / "faiss_index"
    if index_path.exists():
        vector_store = FAISS.load_local(
            str(index_path),
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        # Create empty FAISS index (will be populated later)
        vector_store = None
    
    return vector_store, embeddings


def build_documents_from_chunks(chunks_data):
    documents = []
    for chunk in chunks_data:
        # Convert metadata to match what chroma expects (flat dict usually best)
        # Ensure values are strings, ints, floats, bools.
        metadata = chunk["metadata"].copy()
        metadata["id"] = chunk["id"]
        
        doc = Document(
            page_content=chunk["text"],
            metadata=metadata
        )
        documents.append(doc)
    return documents
