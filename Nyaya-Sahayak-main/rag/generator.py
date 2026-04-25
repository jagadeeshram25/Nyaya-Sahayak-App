import os

from config.settings import settings
from langchain_groq import ChatGroq

SYSTEM_PROMPT = """You are Nyaya Sahayak, an expert AI legal assistant
specializing in Indian criminal law. You have deep knowledge of:
- Bharatiya Nyaya Sanhita (BNS) 2023
- Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023
- Bharatiya Sakshya Adhiniyam (BSA) 2023
- Indian Penal Code (IPC) 1860
- Code of Criminal Procedure (CrPC)

RULES:
1. Answer based on the retrieved legal text provided below.
2. If the user asks about an IPC section, ALWAYS map it to the
   corresponding BNS section and explain the equivalent.
3. Always mention the exact BNS section number in your answer.
4. If retrieved text is insufficient, use your knowledge of BNS 2023
   to provide the correct answer — do NOT say "not available".
5. Structure your answer with: definition, punishment, key points.
6. End with: "Source: Bharatiya Nyaya Sanhita, 2023 (Official Gazette)"

CRITICAL RULE — SECTION NUMBER ACCURACY:
When an IPC-to-BNS mapping is provided to you in the context,
you MUST use ONLY that mapped BNS section number in your answer.
NEVER replace or override the provided BNS section number with
any other number found in retrieved chunks.

The mapping provided is ground truth. Example:
  If told "IPC 498A → BNS 85", your answer must say
  "BNS Section 85" throughout — never "BNS Section 230"
  or any other number.

Retrieved legal sections:
{context}
"""


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


_cached_llm = None

def _build_llm():
    # Ensure Streamlit secrets are visible even if Settings was imported early.
    _hydrate_env_from_streamlit_secrets()
    settings.GROQ_API_KEY = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)
    settings.GROQ_MODEL = os.getenv("GROQ_MODEL", settings.GROQ_MODEL)
    settings.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", settings.GOOGLE_API_KEY)
    settings.GEMINI_MODEL = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL)

    if settings.GOOGLE_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
            convert_system_message_to_human=True,
        )

    if settings.GROQ_API_KEY:
        return ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0,
        )

    raise ValueError("No API Key found! Please set GOOGLE_API_KEY or GROQ_API_KEY in .env")


def _get_llm():
    global _cached_llm
    if _cached_llm is None:
        _cached_llm = _build_llm()
    return _cached_llm


def generate_answer(query: str, context: str) -> str:
    llm = _get_llm()
    prompt = f"{SYSTEM_PROMPT.format(context=context)}\n\nUser Question:\n{query}\n\nAnswer:"
    response = llm.invoke(prompt)
    return response.content
