# Nyaya-Sahayak: A Retrieval-Augmented Legal Assistant for Bharatiya Nyaya Sanhita (BNS)
## Project Technical Report

### 1. Abstract
The transition from the Indian Penal Code (IPC) to the **Bharatiya Nyaya Sanhita (BNS)** presents a significant challenge for legal practitioners, students, and citizens. **Nyaya-Sahayak** is an advanced AI-powered legal assistant designed to bridge this gap. Unlike generic Large Language Models (LLMs) that often "hallucinate" or invent legal sections, Nyaya-Sahayak utilizes a **Retrieval-Augmented Generation (RAG)** architecture. This ensures that every answer is grounded in a verifiable, authoritative source text—specifically, the official BNS document. This report outlines the system architecture, data pipeline, and hallucination control mechanisms implemented in the project.

---

### 2. Problem Statement
Generic AI models (like GPT-4 or Gemini) are trained on vast, uncurated datasets. When asked about specific legal statutes, they often:
1.  **Hallucinate**: Invent non-existent laws or mix up IPC and BNS sections.
2.  **Lack Citations**: Cannot provide the exact source text required for legal verification.
3.  **Outdated Knowledge**: May rely on training data that predates the official enforcement of BNS.

**Objective**: To build a system that answers legal queries *only* if the answer exists in the provided legal text, failing gracefully otherwise, while also supporting the legacy IPC section references that users are accustomed to.

---

### 3. System Architecture

The project follows a modular **RAG Pipeline** consisting of four distinct layers:

#### A. Data Layer (The Source of Truth)
*   **Input**: The raw PDF of the Bharatiya Nyaya Sanhita.
*   **Processing**: We do not simply feed the PDF to the LLM. Instead, we perform a deterministic extraction of text.
*   **Key Component**: `data_ingestion/chunk_bns.py`
    *   This script uses intelligent **Section-Aware Chunking**. Instead of arbitrarily splitting text every 500 characters, it uses Regular Expressions (`Regex`) to identify Section headers (e.g., "103. Punishment for murder").
    *   This ensures that a legal section is never split in the middle, preserving the semantic integrity of the statute.

#### B. Indexing Layer (Vector Database)
*   **Embeddings**: We use high-performance open-source embeddings (e.g., `sentence-transformers`) to convert text chunks into numerical vectors.
*   **Storage**: These vectors are stored in a **FAISS (Facebook AI Similarity Search)** index. This allows for millisecond-latency retrieval of relevant legal sections based on semantic meaning, not just keyword matching.

#### C. Retrieval Layer (The "Brain")
*   **Hybrid Search Strategy**:
    *   **Semantic Search**: Finds relevant sections even if the user doesn't use exact legal terminology (e.g., "killing someone" maps to "murder").
    *   **Rule-Based Mapping**: A specialized component maps old IPC sections to new BNS sections (e.g., `IPC 302` -> `BNS 103`). If a user mentions an IPC section, the system mathematically "boosts" the score of the corresponding BNS section to ensure it is retrieved.
*   **Strict Filtering**: The system discards retrieved information if the similarity score is too low, preventing irrelevant context from confusing the AI.

#### D. Generation Layer (The Interface)
*   **LLM Integration**: We utilize **Google Gemini 1.5** via the API.
*   **Prompt Engineering**: The core of the hallucination control lies in the System Prompt.
    *   *Constraint 1*: "Answer ONLY using the text provided in the CONTEXT."
    *   *Constraint 2*: "If the answer is not contained... reply 'The requested information is not available'."
    *   *Constraint 3*: "Always cite BNS section numbers."

---

### 4. Technical Implementation Workflow

1.  **Ingestion**: 
    `PDF -> Clean Text -> Regex Segmentation -> JSON Chunks`
2.  **Embedding**:
    `JSON Chunks -> Vector Model -> FAISS Index`
3.  **Inference (User Query)**:
    *   *User*: "What is the punishment for mob lynching?"
    *   *Retriever*: Scans FAISS index -> Finds Section 103(2).
    *   *LLM*: Receives Section 103(2) text + User Question.
    *   *Output*: "According to Section 103(2) of the BNS..."

---

### 5. Key Features for Legal Accuracy

*   **Zero-Shot Fallback**: If the retrieval layer finds nothing relevant, the LLM is forcibly instructed to say "I don't know" rather than inventing a law.
*   **IPC Bridge**: Recognizes that users still think in terms of IPC (e.g., "420") and automatically redirects them to the new BNS equivalents.
*   **Source Citations**: Every answer includes the specific Section Number, allowing for manual verification by the user.

### 6. Conclusion
Nyaya-Sahayak represents a "White-Box" approach to Legal AI. By constraining the AI to a specific, immutable document and using rigorous retrieval logic, we significantly reduce the risk of misinformation. This tool serves as a reliable co-pilot for navigating the new Bharatiya Nyaya Sanhita.
