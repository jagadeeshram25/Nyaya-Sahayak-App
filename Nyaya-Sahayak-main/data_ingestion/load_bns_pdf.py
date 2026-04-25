
import json
import re
from langchain_community.document_loaders import PyPDFLoader
from config.settings import settings

def load_pdf(pdf_path):
    print(f"Loading PDF from: {pdf_path}")
    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()
    return pages

def clean_page_text(text):
    # Remove header/footer noise
    text = re.sub(r"The Bharatiya Nyaya Sanhita, 2023", "", text)
    text = re.sub(r"Page \d+", "", text)
    
    # Remove specific artifacts
    text = re.sub(r"THE GAZETTE OF INDIA", "", text, flags=re.IGNORECASE)
    text = re.sub(r"EXTRAORDINARY", "", text, flags=re.IGNORECASE)
    text = re.sub(r"PART II—SEC\. 1", "", text, flags=re.IGNORECASE)
    text = re.sub(r"_{3,}", "", text) # Remove long underscores lines
    
    # Normalize spaces but preserve newlines
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = re.sub(r'[ \t]+', ' ', line).strip()
        # Remove lines that are just numbers or empty after cleaning
        if not line or (line.isdigit() and len(line) < 4): 
            continue
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines)

def run_extraction():
    if not settings.BNS_PDF_PATH:
         print("Error: BNS_PDF_PATH not set.")
         return

    try:
        pages = load_pdf(settings.BNS_PDF_PATH)
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return

    processed_data = []
    
    for page in pages:
        cleaned_text = clean_page_text(page.page_content)
        processed_data.append({
            "page_number": page.metadata.get("page", 0) + 1, # 1-indexed
            "text": cleaned_text
        })
        
    # Save to JSON
    settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(settings.BNS_TEXT_JSON, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(processed_data)} pages to {settings.BNS_TEXT_JSON}")

if __name__ == "__main__":
    run_extraction()
