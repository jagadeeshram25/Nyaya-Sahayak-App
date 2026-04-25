# Nyaya-Sahayak: Legal Assistant (RAG Pipeline)

Nyaya-Sahayak is a **Retrieval-Augmented Generation (RAG)** application designed to provide accurate answers regarding the **Bharatiya Nyaya Sanhita (BNS)**. It uses vector search to retrieve relevant legal sections and an LLM to generate precise, cited answers.

## 🚀 Features
*   **Hallucination Free**: Answers are strictly grounded in the provided BNS text.
*   **IPC-to-BNS Mapping**: Automatically understands legacy IPC section references.
*   **Section-Aware Chunking**: Preserves the context of legal statutes.
*   **Hybrid Search**: Combines semantic similarity with rule-based filtering.

## 🛠️ Prerequisites
*   Python 3.10+
*   Groq API Key

## 📦 Installation

1.  **Clone the repository** (if applicable) or navigate to the project folder:
    ```bash
    cd c:\project\Nyaya-Sahayak
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Setup**:
    *   Copy the example environment file:
        ```bash
        copy .env.example .env
        ```
    *   Open `.env` and paste your API key:
        ```ini
        GROQ_API_KEY=your_actual_api_key_here
        ```

## ⚙️ Data Pipeline / Setup
Before running the app, you must process the data and build the search index. Run these commands in order:

1.  **Ingest & Chunk Data**:
    *   Extracts text from the PDF and splits it into logical legal sections.
    ```bash
    python -m data_ingestion.load_bns_pdf
    python -m data_ingestion.chunk_bns
    ```

2.  **Build Vector Index**:
    *   Creates the FAISS vector store for similarity search.
    ```bash
    python -m indexing.build_index
    ```

## 🖥️ Running the Application

### Option 1: Web Interface (Streamlit)
The most user-friendly way to use the assistant.
```bash
streamlit run ui/streamlit_app.py
```

### Option 2: Command Line Interface (CLI)
For quick testing without a UI.
```bash
python main.py
```

## 📂 Project Structure
*   `data_ingestion/`: Scripts to clean PDF text and create JSON chunks.
*   `indexing/`: Handles vector embedding creation (FAISS).
*   `rag/`: Core logic for Retrieval (finding docs) and Generation (answering).
*   `ui/`: The Streamlit frontend.
*   `data/`: Stores the raw PDF, processed chunks, and vector store files.
