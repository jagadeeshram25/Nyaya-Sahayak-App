
import os
import re
from typing import List, Dict
from langchain_core.documents import Document
from config.settings import settings
from indexing.vector_store_utils import create_or_load_vector_store
from mappings.ipc_bns_mapping import mapper

class BNSRetriever:
    def __init__(self):
        # Validate FAISS index path before load.
        relative_index_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "vector_store", "faiss_index")
        )
        configured_index_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", str("data/vector_store/faiss_index"))
        )
        candidate_paths = [relative_index_path, configured_index_path]
        if not any(os.path.exists(path) for path in candidate_paths):
            # Deployment fallback: build processed files + FAISS index on first boot.
            try:
                import data_ingestion
                import indexing

                if not settings.BNS_TEXT_JSON.exists():
                    data_ingestion.run_extraction()
                if not settings.BNS_CHUNKS_JSON.exists():
                    data_ingestion.run_chunking()
                indexing.run_indexing()
            except Exception as build_error:
                index_path = relative_index_path
                raise FileNotFoundError(
                    f"FAISS index not found at {index_path}. "
                    f"Auto-build failed: {build_error}. Run: python -m indexing.build_index"
                ) from build_error

            if not any(os.path.exists(path) for path in candidate_paths):
                index_path = relative_index_path
                raise FileNotFoundError(
                    f"FAISS index not found at {index_path}. Run: python -m indexing.build_index"
                )
        self.vector_store, self.embeddings = create_or_load_vector_store()

    def _extract_ipc_sections(self, query: str) -> List[str]:
        # Regex to find "IPC" followed by number
        matches = re.findall(r"IPC\s*(\d+[A-Z]?)", query, re.IGNORECASE)
        return matches

    def _extract_section_refs(self, query: str) -> Dict[str, List[str]]:
        """
        Extract explicit section refs like:
        - Section 64
        - BNS 101 / BNS Section 101
        - IPC 302
        - §64
        """
        refs = {"bns": [], "ipc": []}
        patterns = [
            (r"\bBNS\s*(?:section)?\s*(\d+[A-Z]?)\b", "bns"),
            (r"\bIPC\s*(?:section)?\s*(\d+[A-Z]?)\b", "ipc"),
            (r"\bsection\s*(\d+[A-Z]?)\b", "bns"),
            (r"§\s*(\d+[A-Z]?)\b", "bns"),
        ]
        for pattern, key in patterns:
            for match in re.findall(pattern, query, flags=re.IGNORECASE):
                token = str(match).upper().strip()
                if token not in refs[key]:
                    refs[key].append(token)
        return refs

    def _extract_keywords(self, query: str) -> List[str]:
        stop_words = {
            "what", "is", "the", "of", "for", "under", "and", "or", "in", "to",
            "a", "an", "please", "explain", "tell", "me", "about", "bns", "ipc",
            "section", "punishment", "law", "legal"
        }
        terms = re.findall(r"[A-Za-z0-9]+", query.lower())
        keywords = [t for t in terms if len(t) >= 3 and t not in stop_words]
        # Preserve order while deduplicating.
        return list(dict.fromkeys(keywords))

    def _keyword_score(self, text: str, keywords: List[str]) -> float:
        if not keywords:
            return 0.0
        lower_text = text.lower()
        matches = sum(1 for kw in keywords if kw in lower_text)
        return matches / len(keywords)

    def retrieve(self, query: str, k: int = 5, score_threshold: float = 0.3) -> List[Document]:
        # Compatibility fallback for alternate internal attribute naming.
        if not getattr(self, "vector_store", None):
            if hasattr(self, "vectorstore") and self.vectorstore:
                return self.vectorstore.similarity_search(query, k=k)
            if hasattr(self, "index") and self.index:
                return self.index.similarity_search(query, k=k)
            raise AttributeError("No vectorstore or index found on BNSRetriever")

        # 0. Normalize Query: Strip whitespace and common trailing punctuation
        # This addresses the user requirement: "Treat user queries the same regardless of punctuation"
        query = query.strip().rstrip(".,;!?")

        # 1. Check for explicit section references and IPC mappings.
        refs = self._extract_section_refs(query)
        ipc_refs = self._extract_ipc_sections(query)
        for ipc_sec in refs["ipc"]:
            if ipc_sec not in ipc_refs:
                ipc_refs.append(ipc_sec)

        explicit_bns_sections = set(refs["bns"])
        mapped_bns_sections = set()
        for ipc_sec in ipc_refs:
            mapping = mapper.resolve_ipc(ipc_sec)
            if mapping:
                bns_sec = str(mapping["bns_section"])
                mapped_bns_sections.add(bns_sec)
                print(f"DEBUG: Found IPC {ipc_sec} -> Mapping to BNS {bns_sec}")

        prioritized_sections = set(explicit_bns_sections) | set(mapped_bns_sections)

        if not self.vector_store:
            print("ERROR: Vector store not initialized.")
            return []

        # 2. Get broader candidate pool, then re-rank.
        candidate_k = 6
        results = self.vector_store.similarity_search_with_score(query, k=candidate_k)
        if not results:
            return []

        keywords = self._extract_keywords(query)
        prioritized_docs = []
        ranked_docs = []
        seen_ids = set()

        # 3. Priority 1: explicit section match override.
        for doc, distance in results:
            doc_id = doc.metadata.get("id", str(hash(doc.page_content)))
            if doc_id in seen_ids:
                continue

            sec_num = str(doc.metadata.get("section_number", "")).upper().strip()
            vector_score = 1 / (1 + float(distance))  # normalize from distance
            keyword_score = self._keyword_score(doc.page_content, keywords)
            combined_score = (0.6 * vector_score) + (0.4 * keyword_score)

            doc.metadata["vector_score"] = round(vector_score, 4)
            doc.metadata["keyword_score"] = round(keyword_score, 4)
            doc.metadata["score"] = round(combined_score, 4)
            doc.metadata["is_mapped"] = sec_num in mapped_bns_sections
            doc.metadata["is_section_priority"] = sec_num in prioritized_sections

            if sec_num in prioritized_sections:
                prioritized_docs.append(doc)
            else:
                ranked_docs.append(doc)
            seen_ids.add(doc_id)

        prioritized_docs.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
        ranked_docs.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
        final_docs = (prioritized_docs + ranked_docs)[:max(1, k)]

        # 4. Fallback if everything filtered out.
        if not final_docs:
            for doc, distance in results[:3]:
                doc.metadata["score"] = round(1 / (1 + float(distance)), 4)
                final_docs.append(doc)

        return final_docs

    def search(self, query: str, k: int = 5) -> List[Document]:
        """Alias — calls the main retrieval method."""
        return self.retrieve(query=query, k=k)
