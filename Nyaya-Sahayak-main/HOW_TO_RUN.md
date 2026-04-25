# How to Run Nyaya-Sahayak

## Option 1: The Easy Way (Windows Batch Script)
We have created a convenient script that handles everything for you (activating the environment and starting the app).

1.  Locate the file **`run.bat`** in the main project folder.
2.  **Double-click** it.
3.  The application will open in your default web browser.

## Option 2: Manual Data Setup (First Run Only)
If this is your first time running the project, you need to process the data first. Run these commands in your terminal:

```bash
# 1. Parsing the PDF
python -m data_ingestion.load_bns_pdf

# 2. Chunking the text
python -m data_ingestion.chunk_bns

# 3. Building the Search Index
python -m indexing.build_index
```

## Option 3: Manual Startup (Command Line)
If you prefer to run commands manually:

1.  **Activate the Virtual Environment**:
    ```powershell
    .venv\Scripts\activate
    ```

2.  **Start the Web UI**:
    ```powershell
    streamlit run ui/streamlit_app.py
    ```

3.  **OR Start the CLI (Text-based mode)**:
    ```powershell
    python main.py
    ```

## Troubleshooting
*   **"Command not found"**: Make sure you have activated the virtual environment first (`.venv\Scripts\activate`).
*   **API Key Error**: Ensure your `.env` file exists and has a valid `GROQ_API_KEY`.
