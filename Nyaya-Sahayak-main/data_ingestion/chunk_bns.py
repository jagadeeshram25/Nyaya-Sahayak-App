
import json
import re
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings

def load_processed_text():
    if not settings.BNS_TEXT_JSON.exists():
        raise FileNotFoundError(f"{settings.BNS_TEXT_JSON} not found. Run load_bns_pdf.py first.")
    
    with open(settings.BNS_TEXT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def run_chunking():
    pages = load_processed_text()
    
    print("Processing pages and identifying sections...")
    
    all_sections = []
    
    # Combined text approach but keeping track of page boundaries
    full_text = ""
    page_markers = [] # (index in full_text, page_num)
    
    current_idx = 0
    for page in pages:
        txt = page["text"] + "\n"
        full_text += txt
        page_markers.append((current_idx, page["page_number"]))
        current_idx += len(txt)

    def get_page_for_idx(idx):
        # Find which page this index belongs to
        for i in range(len(page_markers)-1):
            if page_markers[i][0] <= idx < page_markers[i+1][0]:
                return page_markers[i][1]
        return page_markers[-1][1]

    # Regex for BNS Section headers: Starts with a number followed by a dot.
    # We look for \d+\. followed by a capital letter or "Except" or "Punishment" etc.
    # To avoid years (like 2023), we ensure it's not preceded by a long word or is near a newline.
    # In our cleaned text, we have some newlines preserved from the page join.
    
    # Regex for BNS Section headers: Starts with a number followed by a dot at the beginning of a line.
    # We use a capturing group to keep the delimiter (the section number line)
    parts = re.split(r"(\n\d+\.)", "\n" + full_text)
    
    current_section = {
        "number": "0",
        "title": "Preliminary",
        "text": "",
        "start_page": 1,
        "end_page": 1
    }
    
    section_offset = 0
    # First part is text before any section
    for i, part in enumerate(parts):
        if i == 0:
            current_section["text"] += part
            section_offset += len(part)
            continue

        if i % 2 == 1:
            # Capture group: the digits + dot (e.g. "\n103.")
            # We strictly check if it ends with a dot to confirm it is a header
            if not part.strip().endswith("."):
                 current_section["text"] += part
                 section_offset += len(part)
                 continue

            sec_num_match = re.search(r"(\d+)", part)
            if not sec_num_match:
                current_section["text"] += part
                section_offset += len(part)
                continue
                
            sec_num = sec_num_match.group(1)
            
            # Validation: BNS has ~358 sections.
            if int(sec_num) > 400:
                current_section["text"] += part
                section_offset += len(part)
            else:
                # Save previous
                if current_section["text"].strip():
                    all_sections.append(current_section)
                
                # Start new
                current_section = {
                    "number": sec_num,
                    "title": f"Section {sec_num}",
                    "text": part, # Start with the "103."
                    "start_page": get_page_for_idx(section_offset),
                    "end_page": get_page_for_idx(section_offset)
                }
        else:
            current_section["text"] += part
            current_section["end_page"] = get_page_for_idx(section_offset + len(part))
        
        section_offset += len(part)
                
    if current_section["text"].strip():
        all_sections.append(current_section)

    print(f"Found {len(all_sections)} potential sections.")
    
    # Optional: Debug print first few section numbers
    debug_nums = [s["number"] for s in all_sections[:15]]
    print(f"Sample section numbers found: {debug_nums}")

    # Sub-chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=250,
        separators=["\n\n", "\n", "Explanation", "Illustration", ". ", " ", ""]
    )
    
    final_chunks = []
    for sec in all_sections:
        chunks = text_splitter.split_text(sec["text"])
        for i, chunk_text in enumerate(chunks):
            # Refine title: look for the first line or first sentence
            title = sec["title"]
            first_line = chunk_text.split("\n")[0].strip()
            # If the first line looks like a title (short, following the number)
            if i == 0 and len(first_line) < 150:
                # Remove the number prefix
                title = re.sub(r"^\d+\.\s*", "", first_line)
                if not title: title = f"Section {sec['number']}"

            final_chunks.append({
                "id": f"sec_{sec['number']}_chunk_{i}",
                "text": chunk_text,
                "metadata": {
                    "section_number": sec["number"],
                    "section_title": title,
                    "page_range": f"{sec['start_page']}-{sec['end_page']}",
                    "start_page": sec["start_page"],
                    "full_section_text": sec["text"]
                }
            })
            
    print(f"Created {len(final_chunks)} chunks.")
    
    with open(settings.BNS_CHUNKS_JSON, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=2, ensure_ascii=False)
        
    print(f"Saved chunks to {settings.BNS_CHUNKS_JSON}")

if __name__ == "__main__":
    run_chunking()
