import re
from typing import Dict, List

from mappings.ipc_bns_mapping import mapper
from rag.generator import generate_answer
from rag.retriever import BNSRetriever

# Cache retriever at module level — avoids reloading FAISS index + embeddings on every query.
_cached_retriever = None

def _get_retriever():
    global _cached_retriever
    if _cached_retriever is None:
        _cached_retriever = BNSRetriever()
    return _cached_retriever

IPC_TO_BNS_QUICK = {
    "302": "101", "304": "105", "304A": "106", "304B": "80",
    "306": "108", "307": "109", "323": "115", "325": "116",
    "326": "117", "326A": "124", "354": "74", "354A": "75",
    "354B": "76", "354C": "77", "354D": "78", "375": "63",
    "376": "64", "376D": "70", "379": "303", "380": "305",
    "384": "308", "392": "309", "395": "310", "405": "316",
    "406": "316", "420": "318", "447": "329", "465": "336",
    "467": "339", "471": "343", "494": "82", "498A": "85",
    "499": "356", "503": "351", "506": "351", "509": "79",
    "120A": "60", "120B": "61",
}


def enrich_query(query: str) -> str:
    # Match patterns: IPC 302 / IPC302 / Section 302 / 302 IPC
    pattern = r"(?:IPC\s*|[Ss]ection\s*)(\d{2,3}[A-Za-z]?)|(\d{2,3}[A-Za-z]?)\s*IPC"
    matches = re.findall(pattern, query)
    enriched = query
    for g1, g2 in matches:
        ipc_num = (g1 or g2).upper().strip()
        if ipc_num in IPC_TO_BNS_QUICK:
            bns = IPC_TO_BNS_QUICK[ipc_num]
            snippet = f"BNS section {bns} equivalent of IPC {ipc_num}"
            if snippet.lower() not in enriched.lower():
                enriched += f" {snippet}"
    return enriched


def safe_retrieve(retriever, query: str, k: int = 5):
    """Try all common retriever method names."""
    for method_name in ["retrieve", "search", "query", "get_relevant_documents", "similarity_search"]:
        if hasattr(retriever, method_name):
            method = getattr(retriever, method_name)
            try:
                result = method(query, k=k)
            except TypeError:
                result = method(query)
            return result if result else []
    raise AttributeError(
        f"Could not find a retrieval method on {type(retriever).__name__}. "
        f"Available methods: {[m for m in dir(retriever) if not m.startswith('_')]}"
    )


def _extract_ipc_mapped_text(query: str) -> str | None:
    ipc_matches = re.findall(r"\bIPC\s*(\d+[A-Z]?)\b", query, flags=re.IGNORECASE)
    for ipc in ipc_matches:
        mapping = mapper.resolve_ipc(ipc.upper())
        if mapping:
            return f"IPC {ipc.upper()} -> BNS {mapping.get('bns_section')}"
    return None


def _extract_ipc_bns_pair(query: str) -> tuple[str | None, str | None]:
    ipc_matches = re.findall(r"\bIPC\s*(\d+[A-Z]?)\b", query, flags=re.IGNORECASE)
    for ipc in ipc_matches:
        mapping = mapper.resolve_ipc(ipc.upper())
        if mapping and mapping.get("bns_section"):
            return ipc.upper(), str(mapping.get("bns_section")).upper()
    return None, None


def correct_section_numbers(answer: str, ipc_num: str, bns_num: str) -> str:
    """
    If LLM hallucinated a wrong BNS section number,
    replace it with the correct one from our mapping.
    """
    wrong_sections = re.findall(r"BNS\s+[Ss]ection\s+(\d+[A-Za-z]?)", answer)
    corrected = answer
    for wrong in wrong_sections:
        if wrong.upper() != bns_num.upper():
            corrected = re.sub(
                rf"BNS\s+[Ss]ection\s+{re.escape(wrong)}\b",
                f"BNS Section {bns_num}",
                corrected,
            )
    return corrected


def get_answer(query: str) -> Dict:
    retriever = _get_retriever()
    enriched_query = enrich_query(query)
    docs = safe_retrieve(retriever, enriched_query, k=5)

    if not docs or len(docs) == 0:
        context = "No specific chunks retrieved. Answer from your BNS 2023 knowledge."
        sources: List[Dict] = []
    else:
        context = "\n\n".join([d.page_content for d in docs])
        sources = []
        for d in docs:
            md = d.metadata or {}
            sources.append(
                {
                    "section": f"BNS Section {md.get('section_number', 'Unknown')}",
                    "text": d.page_content[:450],
                    "source": md.get("section_title", "Official Gazette"),
                }
            )

    ipc_num, bns_num = _extract_ipc_bns_pair(enriched_query)
    answer = generate_answer(query=enriched_query, context=context)
    if ipc_num and bns_num:
        answer = correct_section_numbers(answer, ipc_num, bns_num)

    ipc_mapped = f"IPC {ipc_num} -> BNS {bns_num}" if ipc_num and bns_num else _extract_ipc_mapped_text(enriched_query)
    return {
        "answer": answer,
        "sources": sources,
        "ipc_mapped": ipc_mapped,
    }
