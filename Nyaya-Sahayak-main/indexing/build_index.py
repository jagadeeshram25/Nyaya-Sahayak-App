
import json
from indexing.vector_store_utils import get_embedding_model, build_documents_from_chunks
from langchain_community.vectorstores import FAISS
from config.settings import settings

def run_indexing():
    if not settings.BNS_CHUNKS_JSON.exists():
        print(f"Chunks file not found at {settings.BNS_CHUNKS_JSON}. Run chunk_bns.py first.")
        return

    print("Loading chunks...")
    with open(settings.BNS_CHUNKS_JSON, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)
    
    print(f"Loaded {len(chunks_data)} chunks.")
    
    docs = build_documents_from_chunks(chunks_data)
    embeddings = get_embedding_model()
    
    print("Initializing Vector Store (this may take time as it generates embeddings)...")
    settings.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create FAISS index from documents
    vector_store = FAISS.from_documents(docs, embeddings)
    
    # Save the index
    index_path = settings.VECTOR_STORE_DIR / "faiss_index"
    vector_store.save_local(str(index_path))
    
    print(f"Successfully indexed {len(docs)} documents into {index_path}")

if __name__ == "__main__":
    run_indexing()
