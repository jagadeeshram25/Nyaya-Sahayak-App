<img width="1919" height="1020" alt="Screenshot 2026-04-25 183652" src="https://github.com/user-attachments/assets/2756fba0-b9cb-491b-8278-602eb2e827c3" />
<img width="1919" height="1011" alt="Screenshot 2026-04-25 183645" src="https://github.com/user-attachments/assets/94477f70-3c76-4dae-b41e-a22b2fcfca5b" />
<img width="1919" height="1024" alt="Screenshot 2026-04-25 183633" src="https://github.com/user-attachments/assets/5f62fc2e-b0a5-4c47-8ef1-1b1be4209e9c" />
<img width="1919" height="1014" alt="Screenshot 2026-04-25 183618" src="https://github.com/user-attachments/assets/8b2a44b9-8f66-494c-b1b1-27fd2b2d1ad5" />
<img width="1919" height="1016" alt="Screenshot 2026-04-25 183615" src="https://github.com/user-attachments/assets/db5ded03-18d5-492b-ad91-6d8f038090d0" />
<img width="1918" height="1000" alt="Screenshot 2026-04-25 183707" src="https://github.com/user-attachments/assets/1b761c65-713f-4350-914f-703e6cf3e7df" />

# ⚖️ Nyaya-Sahayak BNS Legal Assistant v2.0

Nyaya-Sahayak is an AI-driven legal assistant designed to help citizens and legal professionals navigate India's new criminal laws (BNS, BNSS, BSA) while maintaining context with the legacy IPC/CrPC systems.

## ✨ Features
- **Intelligent RAG Chatbot**: Uses FAISS indexing to provide answers directly grounded in the 2023 legal reforms.
- **Bi-directional Mapping**: Instantly find which BNS section replaces a specific IPC section.
- **Multilingual Support**: Interface accessible in English and regional languages.
- **Document Knowledge Base**: Direct access to verified legal texts for deep research.

## 🏗️ Architecture
The system uses **Retrieval-Augmented Generation (RAG)**:
1. **PDF/Text Processing**: Legal codes are parsed and broken into chunks.
2. **Embedding**: Chunks are converted to vectors and stored in **FAISS**.
3. **Querying**: The **LLaMA 3.3-70b** model retrieves relevant law sections before generating a response to ensure legal accuracy.

## 🛠️ Installation & Setup
1. **Clone the repo:**
   ```bash
   git clone [https://github.com/your-username/nyaya-sahayak.git](https://github.com/your-username/nyaya-sahayak.git)
Install dependencies:

Bash
pip install -r requirements.txt
Set up Environment Variables:
Create a .env file and add your LLM API keys:

Code snippet
GROQ_API_KEY=your_key_here
Run the App:

Bash
streamlit run app.py
