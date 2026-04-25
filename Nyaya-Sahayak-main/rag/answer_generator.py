
import re
import os
from config.settings import settings
from langchain_groq import ChatGroq
from rag.prompts import build_chat_prompt
from rag.retriever import BNSRetriever
from mappings.ipc_bns_mapping import mapper


def _hydrate_env_from_streamlit_secrets() -> None:
    """Best-effort secrets bridge for Streamlit Community Cloud."""
    try:
        import streamlit as st  # type: ignore
    except Exception:
        return

    try:
        for key in ("GROQ_API_KEY", "GROQ_MODEL", "GOOGLE_API_KEY", "GEMINI_MODEL"):
            if key in st.secrets and st.secrets[key] is not None and str(st.secrets[key]).strip():
                os.environ.setdefault(key, str(st.secrets[key]))
    except Exception:
        return

class RAGController:
    def __init__(self):
        self.retriever = BNSRetriever()

        _hydrate_env_from_streamlit_secrets()
        settings.GROQ_API_KEY = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)
        settings.GROQ_MODEL = os.getenv("GROQ_MODEL", settings.GROQ_MODEL)
        settings.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", settings.GOOGLE_API_KEY)
        settings.GEMINI_MODEL = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL)
        
        # LLM Selection Logic
        if settings.GOOGLE_API_KEY:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0,
                convert_system_message_to_human=True # Sometimes needed for older langchain versions
            )
            print(f"Using Google Gemini: {settings.GEMINI_MODEL}")
            
        elif settings.GROQ_API_KEY:
            self.llm = ChatGroq(
                model=settings.GROQ_MODEL,
                groq_api_key=settings.GROQ_API_KEY,
                temperature=0
            )
            print(f"Using Groq: {settings.GROQ_MODEL}")
            
        else:
            raise ValueError("No API Key found! Please set GOOGLE_API_KEY or GROQ_API_KEY in .env")

    def format_context(self, docs):
        context_str = ""
        for i, doc in enumerate(docs):
            sec_num = doc.metadata.get("section_number", "Unknown")
            title = doc.metadata.get("section_title", "")
            page_info = doc.metadata.get("page_range", doc.metadata.get("start_page", "Unknown"))
            text = doc.page_content.replace("\n", " ")
            context_str += f"[{i+1}] Section {sec_num}: {title} (Page: {page_info})\nTEXT: {text}\n\n"
        return context_str

    def answer_question(self, question: str):
        """Unified method for UI and CLI that returns answer + docs."""
        try:
            # 1. Retrieve
            docs = self.retriever.retrieve(question)

            # 2. Guard: No docs found -> retry using IPC->BNS heuristic.
            # Handles inputs like "Section 302 of BNS" where user likely means IPC 302.
            if not docs:
                sec_refs = re.findall(r"(?:section|§)\s*(\d+[A-Z]?)", question, flags=re.IGNORECASE)
                for sec in sec_refs:
                    mapping = mapper.resolve_ipc(sec.upper())
                    if not mapping:
                        continue
                    mapped_bns = str(mapping.get("bns_section", "")).strip()
                    if not mapped_bns:
                        continue
                    retry_query = (
                        f"BNS Section {mapped_bns} {mapping.get('description', '')}. "
                        f"User query: {question}"
                    )
                    docs = self.retriever.retrieve(retry_query)
                    if docs:
                        break

            if not docs:
                return {
                    "answer": "The requested information is not available in the official BNS document or the index is not ready.",
                    "documents": []
                }
            
            # 3. Format context
            context_text = self.format_context(docs)
            
            # 4. Build the full prompt
            from rag.prompts import BASE_SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
            full_prompt = BASE_SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(
                context=context_text,
                question=question
            )
            
            # 5. Generate
            response = self.llm.invoke(full_prompt)
            
            return {
                "answer": response.content,
                "documents": docs
            }
        except Exception as e:
            print(f"CRITICAL ERROR in RAG Pipeline: {e}")
            return {
                "answer": f"An error occurred while processing your request: {str(e)}",
                "documents": []
            }

    def ask_question(self, question: str):
        """Legacy CLI support."""
        res = self.answer_question(question)
        return res["answer"]
