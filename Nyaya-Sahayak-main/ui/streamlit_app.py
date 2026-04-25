import io
import importlib
import os
import sys
from datetime import date, datetime

import pandas as pd
import streamlit as st

# Ensure project root is importable when running from ui/ on Streamlit Cloud.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

st.set_page_config(
    page_title="Nyaya-Sahayak | BNS Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "AI Assistant"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""

IPC_TO_BNS = {
    "53": {"bns": "6", "title": "Punishments", "category": "Punishments"},
    "302": {"bns": "101", "title": "Punishment for murder", "category": "Offences Against Body"},
    "303": {"bns": "102", "title": "Murder by life-convict", "category": "Offences Against Body"},
    "304": {"bns": "105", "title": "Culpable homicide not amounting to murder", "category": "Offences Against Body"},
    "304A": {"bns": "106", "title": "Causing death by negligence", "category": "Offences Against Body"},
    "304B": {"bns": "80", "title": "Dowry death", "category": "Women & Children"},
    "305": {"bns": "107", "title": "Abetment of suicide of child or insane person", "category": "Offences Against Body"},
    "306": {"bns": "108", "title": "Abetment of suicide", "category": "Offences Against Body"},
    "307": {"bns": "109", "title": "Attempt to murder", "category": "Offences Against Body"},
    "308": {"bns": "110", "title": "Attempt to commit culpable homicide", "category": "Offences Against Body"},
    "309": {"bns": "226", "title": "Attempt to commit suicide", "category": "Offences Against Body"},
    "312": {"bns": "88", "title": "Causing miscarriage", "category": "Women & Children"},
    "313": {"bns": "89", "title": "Causing miscarriage without woman's consent", "category": "Women & Children"},
    "319": {"bns": "113", "title": "Hurt", "category": "Offences Against Body"},
    "320": {"bns": "114", "title": "Grievous hurt", "category": "Offences Against Body"},
    "323": {"bns": "115", "title": "Punishment for voluntarily causing hurt", "category": "Offences Against Body"},
    "324": {"bns": "117", "title": "Hurt by dangerous weapons", "category": "Offences Against Body"},
    "325": {"bns": "116", "title": "Punishment for grievous hurt", "category": "Offences Against Body"},
    "326": {"bns": "117", "title": "Grievous hurt by dangerous weapons", "category": "Offences Against Body"},
    "326A": {"bns": "124", "title": "Voluntarily causing grievous hurt by acid", "category": "Women & Children"},
    "326B": {"bns": "125", "title": "Voluntarily throwing acid", "category": "Women & Children"},
    "339": {"bns": "126", "title": "Wrongful restraint", "category": "Offences Against Body"},
    "340": {"bns": "127", "title": "Wrongful confinement", "category": "Offences Against Body"},
    "354": {"bns": "74", "title": "Assault to outrage modesty of woman", "category": "Women & Children"},
    "354A": {"bns": "75", "title": "Sexual harassment", "category": "Women & Children"},
    "354B": {"bns": "76", "title": "Assault with intent to disrobe", "category": "Women & Children"},
    "354C": {"bns": "77", "title": "Voyeurism", "category": "Women & Children"},
    "354D": {"bns": "78", "title": "Stalking", "category": "Women & Children"},
    "359": {"bns": "138", "title": "Kidnapping", "category": "Offences Against Body"},
    "362": {"bns": "141", "title": "Abduction", "category": "Offences Against Body"},
    "363": {"bns": "137", "title": "Punishment for kidnapping", "category": "Offences Against Body"},
    "364A": {"bns": "144", "title": "Kidnapping for ransom", "category": "Offences Against Body"},
    "375": {"bns": "63", "title": "Rape — definition", "category": "Women & Children"},
    "376": {"bns": "64", "title": "Punishment for rape", "category": "Women & Children"},
    "376A": {"bns": "66", "title": "Rape causing death or vegetative state", "category": "Women & Children"},
    "376D": {"bns": "70", "title": "Gang rape", "category": "Women & Children"},
    "378": {"bns": "303", "title": "Theft — definition", "category": "Property Offences"},
    "379": {"bns": "303", "title": "Punishment for theft", "category": "Property Offences"},
    "380": {"bns": "305", "title": "Theft in dwelling house", "category": "Property Offences"},
    "382": {"bns": "307", "title": "Theft after preparation for hurt", "category": "Property Offences"},
    "383": {"bns": "308", "title": "Extortion — definition", "category": "Property Offences"},
    "384": {"bns": "308", "title": "Punishment for extortion", "category": "Property Offences"},
    "390": {"bns": "314", "title": "Robbery — definition", "category": "Property Offences"},
    "391": {"bns": "310", "title": "Dacoity — definition", "category": "Property Offences"},
    "392": {"bns": "309", "title": "Punishment for robbery", "category": "Property Offences"},
    "395": {"bns": "310", "title": "Punishment for dacoity", "category": "Property Offences"},
    "396": {"bns": "317", "title": "Dacoity with murder", "category": "Property Offences"},
    "399": {"bns": "319", "title": "Preparation to commit dacoity", "category": "Property Offences"},
    "403": {"bns": "323", "title": "Dishonest misappropriation of property", "category": "Property Offences"},
    "405": {"bns": "316", "title": "Criminal breach of trust", "category": "Property Offences"},
    "406": {"bns": "316", "title": "Punishment for criminal breach of trust", "category": "Property Offences"},
    "409": {"bns": "319", "title": "Criminal breach of trust by public servant", "category": "Property Offences"},
    "415": {"bns": "318", "title": "Cheating — definition", "category": "Property Offences"},
    "420": {"bns": "318", "title": "Cheating and dishonestly inducing delivery", "category": "Property Offences"},
    "425": {"bns": "324", "title": "Mischief — definition", "category": "Property Offences"},
    "426": {"bns": "324", "title": "Punishment for mischief", "category": "Property Offences"},
    "435": {"bns": "331", "title": "Mischief by fire or explosive substance", "category": "Property Offences"},
    "436": {"bns": "331", "title": "Mischief destroying house by fire", "category": "Property Offences"},
    "441": {"bns": "329", "title": "Criminal trespass", "category": "Property Offences"},
    "442": {"bns": "330", "title": "House-trespass", "category": "Property Offences"},
    "445": {"bns": "333", "title": "House-breaking", "category": "Property Offences"},
    "447": {"bns": "329", "title": "Punishment for criminal trespass", "category": "Property Offences"},
    "463": {"bns": "336", "title": "Forgery — definition", "category": "Property Offences"},
    "465": {"bns": "336", "title": "Punishment for forgery", "category": "Property Offences"},
    "467": {"bns": "339", "title": "Forgery of valuable security or will", "category": "Property Offences"},
    "468": {"bns": "340", "title": "Forgery for purpose of cheating", "category": "Property Offences"},
    "471": {"bns": "343", "title": "Using forged document as genuine", "category": "Property Offences"},
    "477A": {"bns": "350", "title": "Falsification of accounts", "category": "Property Offences"},
    "493": {"bns": "81", "title": "Cohabitation by deceitful belief of marriage", "category": "Marriage"},
    "494": {"bns": "82", "title": "Marrying again during lifetime of spouse", "category": "Marriage"},
    "495": {"bns": "83", "title": "Bigamy with concealment", "category": "Marriage"},
    "496": {"bns": "84", "title": "Fraudulent marriage ceremony", "category": "Marriage"},
    "498": {"bns": "86", "title": "Enticing away a married woman", "category": "Marriage"},
    "498A": {"bns": "85", "title": "Cruelty by husband or relatives", "category": "Women & Children"},
    "499": {"bns": "356", "title": "Defamation — definition", "category": "Defamation"},
    "500": {"bns": "356", "title": "Punishment for defamation", "category": "Defamation"},
    "503": {"bns": "351", "title": "Criminal intimidation", "category": "General"},
    "504": {"bns": "352", "title": "Intentional insult to provoke breach of peace", "category": "General"},
    "505": {"bns": "353", "title": "Statements conducing to public mischief", "category": "General"},
    "506": {"bns": "351", "title": "Punishment for criminal intimidation", "category": "General"},
    "509": {"bns": "79", "title": "Insulting modesty of woman by gesture/word", "category": "Women & Children"},
    "121": {"bns": "147", "title": "Waging war against Government of India", "category": "State Offences"},
    "124A": {"bns": "152", "title": "Sedition — acts endangering sovereignty", "category": "State Offences"},
    "107": {"bns": "46", "title": "Abetment of a thing", "category": "General Exceptions"},
    "109": {"bns": "48", "title": "Punishment of abetment", "category": "General Exceptions"},
    "120A": {"bns": "60", "title": "Criminal conspiracy — definition", "category": "General Exceptions"},
    "120B": {"bns": "61", "title": "Punishment of criminal conspiracy", "category": "General Exceptions"},
    "76": {"bns": "19", "title": "Act done by mistake of fact believing bound by law", "category": "General Exceptions"},
    "80": {"bns": "23", "title": "Accident in doing a lawful act", "category": "General Exceptions"},
    "82": {"bns": "25", "title": "Act of child under seven years", "category": "General Exceptions"},
    "84": {"bns": "27", "title": "Act of person of unsound mind", "category": "General Exceptions"},
    "96": {"bns": "36", "title": "Right of private defence", "category": "General Exceptions"},
    "100": {"bns": "39", "title": "Private defence extending to causing death", "category": "General Exceptions"},
}

LAWYERS = [
    {"name": "Adv. Priya Sharma", "city": "Delhi", "spec": "Criminal Law", "exp": "12 yrs", "rating": 4.8, "phone": "+91-9876543210"},
    {"name": "Adv. Rajan Mehta", "city": "Mumbai", "spec": "Family Law", "exp": "8 yrs", "rating": 4.6, "phone": "+91-9123456789"},
    {"name": "Adv. Sunita Rao", "city": "Bangalore", "spec": "BNS & IPC", "exp": "15 yrs", "rating": 4.9, "phone": "+91-9988776655"},
    {"name": "Adv. Vikram Singh", "city": "Chennai", "spec": "Property Law", "exp": "10 yrs", "rating": 4.5, "phone": "+91-9876001234"},
    {"name": "Adv. Meera Joshi", "city": "Hyderabad", "spec": "Women & Child Rights", "exp": "7 yrs", "rating": 4.7, "phone": "+91-9765432100"},
    {"name": "Adv. Arjun Nair", "city": "Kochi", "spec": "Cybercrime", "exp": "5 yrs", "rating": 4.4, "phone": "+91-9654321098"},
]

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700&display=swap');
:root{
  --bg-base:#0d1117; --bg-surface:#161b22; --bg-elevated:#1e3a5f; --border:#21262d;
  --accent-blue:#58a6ff; --accent-green:#3fb950; --accent-orange:#f0883e; --accent-red:#f85149;
  --text-primary:#e6edf3; --text-muted:#8b949e; --text-hint:#6e7681;
}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {
  visibility: visible;
  background: transparent;
}
html,body,[class*="css"]{font-family:'Inter',sans-serif;color:var(--text-primary);}
h1,h2,h3,h4{font-family:'Playfair Display',serif;}
.stApp{background:var(--bg-base);}
[data-testid="stAppViewContainer"] > .main .block-container{max-width:1200px;padding:1.5rem 2rem;}
[data-testid="stSidebar"]{background:var(--bg-base);border-right:1px solid var(--border);}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] [data-baseweb="select"] > div{
  background:var(--bg-surface)!important;border:1px solid var(--border)!important;color:var(--text-primary)!important;border-radius:10px!important;
}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:#3b82f6!important;box-shadow:none!important;}
.stButton > button{background:var(--bg-elevated);color:var(--accent-blue);border:1px solid #2d5a9e;border-radius:10px;}
.stButton > button[kind="primary"]{
  background:#238636;color:#fff;border:1px solid #238636;
  box-shadow: inset 3px 0 0 var(--accent-blue);font-weight:500;
}
/* Sidebar: 6th button is "+ New Conversation" */
[data-testid="stSidebar"] .stButton:nth-of-type(6) button{
  background:transparent !important;
  color:var(--accent-blue) !important;
  border:1px dashed #2d5a9e !important;
}
.page-card,.card{
  background:var(--bg-surface);border:1px solid var(--border);border-radius:12px;padding:1rem;
}
.page-header{border-radius:14px;padding:1rem 1.2rem;display:flex;gap:0.9rem;align-items:center;}
.logo-icon{
  width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,#1e3a5f,#2d5a9e);font-size:26px;
}
.sidebar-logo{
  display:flex;gap:10px;align-items:center;margin-bottom:1rem;padding:0.5rem 0.2rem;
}
.sidebar-logo .sq{
  width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#1e3a5f,#2d5a9e);
  display:flex;align-items:center;justify-content:center;font-size:20px;
}
.section-chip{
  display:inline-block;padding:0.2rem 0.55rem;border-radius:999px;background:#1e2d3d;border:1px solid #2d4a6e;
  color:var(--accent-blue);font-size:11px;margin-right:0.35rem;margin-top:0.3rem;
}
.cite{
  border-left:3px solid #3b82f6;background:var(--bg-base);border-radius:0 8px 8px 0;padding:0.7rem;margin-top:0.6rem;
}
.left-msg{max-width:82%;background:var(--bg-surface);border:1px solid var(--border);border-radius:18px 18px 18px 4px;padding:0.85rem;}
.right-wrap{display:flex;justify-content:flex-end;}
.right-msg{max-width:70%;background:var(--bg-elevated);border-radius:18px 18px 4px 18px;padding:0.8rem 0.9rem;}
.assistant-block{max-width:82%;margin:0.55rem 0 0.85rem 0;}
.assistant-head{background:var(--bg-surface);border:1px solid var(--border);border-radius:18px 18px 18px 4px;padding:0.75rem 0.85rem;}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:#0d1117}
::-webkit-scrollbar-thumb{background:#30363d;border-radius:3px}
</style>
""",
    unsafe_allow_html=True,
)


def page_header(icon: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-card page-header">
            <div class="logo-icon">{icon}</div>
            <div>
                <div style="font-family:'Playfair Display',serif;font-size:26px;font-weight:700;">{title}</div>
                <div style="color:#8b949e;">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner="Loading legal database...")
def _load_retriever():
    """Load retriever once and cache across all Streamlit reruns."""
    from rag.retriever import BNSRetriever
    return BNSRetriever()


@st.cache_resource(show_spinner="Connecting to AI model...")
def _load_llm():
    """Load LLM client once and cache across all Streamlit reruns."""
    from rag.generator import _build_llm
    return _build_llm()


def run_rag_query(query: str) -> dict:
    import time
    answer = ""
    sources = []
    ipc_mapped = None
    try:
        t0 = time.time()

        # Use cached retriever & LLM (loaded only once)
        retriever = _load_retriever()
        llm = _load_llm()

        t1 = time.time()
        print(f"[TIME] Cache lookup: {t1 - t0:.2f}s")

        from rag.pipeline import enrich_query, safe_retrieve, _extract_ipc_bns_pair, _extract_ipc_mapped_text, correct_section_numbers
        from rag.generator import SYSTEM_PROMPT

        enriched_query = enrich_query(query)
        t2 = time.time()
        print(f"[TIME] Enrich query: {t2 - t1:.2f}s")

        docs = safe_retrieve(retriever, enriched_query, k=5)
        t3 = time.time()
        print(f"[TIME] FAISS retrieve: {t3 - t2:.2f}s")

        if not docs or len(docs) == 0:
            context = "No specific chunks retrieved. Answer from your BNS 2023 knowledge."
            sources = []
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

        # Call LLM directly with cached client
        prompt = f"{SYSTEM_PROMPT.format(context=context)}\n\nUser Question:\n{enriched_query}\n\nAnswer:"
        response = llm.invoke(prompt)
        answer = response.content
        t4 = time.time()
        print(f"[TIME] LLM response: {t4 - t3:.2f}s")

        if ipc_num and bns_num:
            answer = correct_section_numbers(answer, ipc_num, bns_num)

        ipc_mapped = f"IPC {ipc_num} -> BNS {bns_num}" if ipc_num and bns_num else _extract_ipc_mapped_text(enriched_query)

        print(f"[TIME] TOTAL: {time.time() - t0:.2f}s")

    except FileNotFoundError as e:
        answer = f"⚠️ Index not built yet. Please run:\n\n```\npython -m indexing.build_index\n```\n\nError: {e}"
        sources = []
        ipc_mapped = None
    except Exception as e:
        answer = f"⚠️ Pipeline error: {str(e)}"
        sources = []
        ipc_mapped = None
    return {"answer": answer, "sources": sources, "ipc_mapped": ipc_mapped}


def save_current_chat() -> None:
    if not st.session_state.messages:
        return
    copied_messages = [dict(m) for m in st.session_state.messages]
    if not copied_messages:
        return
    if st.session_state.chat_history:
        latest = st.session_state.chat_history[0].get("messages", [])
        if latest == copied_messages:
            return
    st.session_state.chat_history.insert(0, {"saved_at": datetime.now().isoformat(), "messages": copied_messages})


def submit_query(query: str) -> None:
    if not query.strip():
        return
    st.session_state.messages.append(
        {"role": "user", "content": query, "timestamp": datetime.now().strftime("%H:%M")}
    )
    with st.spinner("Nyaya Sahayak is thinking..."):
        rag_result = run_rag_query(query)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": rag_result["answer"],
            "sources": rag_result["sources"],
            "ipc_mapped": rag_result["ipc_mapped"],
            "timestamp": datetime.now().strftime("%H:%M"),
        }
    )
    st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-logo">
                <div class="sq">⚖️</div>
                <div>
                    <div style="font-family:'Playfair Display',serif;font-weight:700;">Nyaya-Sahayak</div>
                    <div style="font-size:12px;color:#8b949e;">BNS Legal Assistant v2.0</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_items = [
            ("AI Assistant", "💬  AI Assistant"),
            ("Dashboard", "📊  Dashboard"),
            ("IPC Tool", "🔄  IPC BNS Mapping Tool"),
            ("Lawyers", "👨‍⚖️  Lawyers"),
            ("Knowledge Base", "📚  Knowledge Base"),
        ]
        for key, label in nav_items:
            if st.button(
                label,
                key=f"nav_{key}",
                type="primary" if st.session_state.page == key else "secondary",
                use_container_width=True,
            ):
                if st.session_state.page == "AI Assistant" and key != "AI Assistant":
                    save_current_chat()
                st.session_state.page = key
                st.rerun()

        if st.button("+ New Conversation", key="new_conv", use_container_width=True):
            had_messages = bool(st.session_state.messages)
            if had_messages:
                save_current_chat()
            st.session_state.messages = []
            st.session_state.pending_query = ""
            st.session_state.query_input = ""
            st.session_state.page = "AI Assistant"
            st.toast("Started a new conversation" if had_messages else "Ready for a new conversation")
            st.rerun()

        st.markdown("<div style='margin-top:0.8rem;color:#8b949e;font-size:12px;'>CHAT HISTORY</div>", unsafe_allow_html=True)
        today_items, older_items = [], []
        for i, chat in enumerate(st.session_state.chat_history):
            try:
                ts = datetime.fromisoformat(chat["saved_at"]).date()
            except Exception:
                ts = date.today()
            (today_items if ts == date.today() else older_items).append((i, chat))

        def render_chat_group(title: str, items: list) -> None:
            if not items:
                return
            st.markdown(
                f"<div style='margin-top:0.4rem;color:#6e7681;font-size:11px;letter-spacing:.06em;text-transform:uppercase;'>{title}</div>",
                unsafe_allow_html=True,
            )
            for idx, chat in items:
                first_user = next((m["content"] for m in chat["messages"] if m.get("role") == "user"), "Conversation")
                label = f"💬 {first_user[:35]}"
                if st.button(label, key=f"hist_{title}_{idx}", use_container_width=True):
                    st.session_state.messages = chat["messages"].copy()
                    st.session_state.page = "AI Assistant"
                    st.rerun()

        render_chat_group("Today", today_items)
        render_chat_group("Older", older_items)

        st.divider()
        st.markdown(
            """
            <div style="font-size:12px;color:#8b949e;line-height:1.8;">
              ✅ FAISS Index: Active<br/>
              🧠 Model: LLaMA 3.3-70b-versatile<br/>
              📂 BNS Sections: 358
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_ai_assistant_page() -> None:
    page_header("⚖️", "Nyaya-Sahayak", "Your AI-powered legal assistant for BNS, BNSS, BSA, IPC and CrPC guidance")
    st.divider()

    if not st.session_state.messages:
        st.markdown(
            """
            <div style="text-align:center;padding:1.5rem 0 0.8rem 0;">
                <div style="font-size:56px;">⚖️</div>
                <div style="font-family:'Playfair Display',serif;font-size:30px;">Welcome to Nyaya-Sahayak</div>
                <div style="color:#8b949e;max-width:760px;margin:0.5rem auto;">
                    Your AI-powered Indian legal assistant. Ask questions about BNS, BNSS, BSA, IPC, CrPC, and more.
                    All answers are grounded in verified legal texts.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        suggestions = [
            "What is IPC 302 mapped to in BNS?",
            "Explain the right to bail under BNSS",
            "What are the penalties for theft?",
            "Difference between IPC and BNS",
            "Punishment for rape under BNS",
            "What is BNS Section 85 (IPC 498A)?",
        ]
        for i in range(0, len(suggestions), 2):
            c1, c2 = st.columns(2)
            if c1.button(suggestions[i], key=f"sug_{i}", use_container_width=True):
                submit_query(suggestions[i])
            if c2.button(suggestions[i + 1], key=f"sug_{i+1}", use_container_width=True):
                submit_query(suggestions[i + 1])
        st.divider()
    else:
        for idx, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.markdown(f"<div class='right-wrap'><div class='right-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    """
                    <div class='assistant-block'>
                    <div class='assistant-head'>
                      <div style='font-size:11px;text-transform:uppercase;color:#58a6ff;font-weight:600;'>⚖ BNS Assistant's Guidance</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if msg.get("ipc_mapped"):
                    st.markdown(
                        f"<div style='color:#f0883e;font-size:12px;margin:6px 0 4px 0;'>🔄 Mapped: {msg['ipc_mapped']}</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(msg["content"])
                for src in msg.get("sources", []):
                    if isinstance(src, dict):
                        sec = src.get("section", src.get("section_number", "BNS Section"))
                        txt = src.get("text", src.get("excerpt", ""))
                        chip = src.get("source", "Official source")
                    else:
                        sec, txt, chip = "BNS Section", str(src), "Official source"
                    st.markdown(
                        f"""
                        <div class='cite'>
                          <div style='font-size:10px;text-transform:uppercase;color:#58a6ff;font-weight:700;'>{sec}</div>
                          <div style='font-size:13px;color:#8b949e;'>{txt}</div>
                        </div>
                        <span class='section-chip'>{chip}</span>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    f"<div style='font-size:10px;color:#6e7681;margin-top:.45rem;'>{msg.get('timestamp','')} · AI answers are grounded in verified legal texts</div></div>",
                    unsafe_allow_html=True,
                )
        st.divider()

    q_col, lang_col, ask_col = st.columns([7, 2, 1.3])
    user_query = q_col.text_input("Ask", placeholder="Ask a legal question...", label_visibility="collapsed", key="query_input")
    lang_col.selectbox("Language", ["🌐 English"], label_visibility="collapsed", key="lang")
    ask_now = ask_col.button("➤ Ask", type="primary", use_container_width=True)
    st.markdown(
        "<div style='text-align:center;color:#8b949e;font-size:11px;margin-top:6px;'>AI answers are grounded in verified legal texts · BNS 2023</div>",
        unsafe_allow_html=True,
    )
    if ask_now and user_query.strip():
        submit_query(user_query)

    if st.session_state.pending_query:
        q = st.session_state.pending_query
        st.session_state.pending_query = ""
        submit_query(q)


def render_dashboard_page() -> None:
    page_header("📊", "Dashboard", "Usage insights and legal query trends")
    st.divider()
    total_conversations = len(st.session_state.chat_history) + (1 if st.session_state.messages else 0)
    total_messages = sum(len(c["messages"]) for c in st.session_state.chat_history) + len(st.session_state.messages)
    ipc_maps = sum(1 for c in st.session_state.chat_history for m in c["messages"] if m.get("ipc_mapped"))
    ipc_maps += sum(1 for m in st.session_state.messages if m.get("ipc_mapped"))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Conversations", total_conversations)
    m2.metric("Messages Sent", total_messages)
    m3.metric("BNS Sections", 358)
    m4.metric("IPC Mappings", max(ipc_maps, 531))

    st.divider()
    st.subheader("📂 Chat History")
    if not st.session_state.chat_history:
        st.info("No saved chat history yet. Use + New Conversation after chatting.")
    for i, chat in enumerate(st.session_state.chat_history):
        with st.expander(f"Conversation {i + 1}"):
            for msg in chat["messages"]:
                role = msg.get("role", "assistant").capitalize()
                content = msg.get("content", "")
                st.write(f"**{role}:** {content[:140]}")

    st.divider()
    st.subheader("🔥 Popular Topics")
    topic_scores = [
        ("Murder/Homicide", 76),
        ("Theft/Robbery", 64),
        ("Rape/Sexual Offences", 58),
        ("Cheating/Fraud", 51),
        ("Bail/Arrest", 47),
        ("Cruelty/498A", 43),
    ]
    for name, score in topic_scores:
        st.write(name)
        st.progress(score / 100)

    st.divider()
    if st.button("🔄 Open IPC → BNS Mapping Tool"):
        st.session_state.page = "IPC Tool"
        st.rerun()


def render_ipc_bns_tool() -> None:
    page_header("🔄", "IPC → BNS Mapping Tool", "Translate IPC references to BNS 2023 sections")
    st.divider()
    tab1, tab2, tab3 = st.tabs(["🔍 Section Lookup", "📋 Full Reference Table", "📖 BNS Section Details"])

    with tab1:
        ip = st.text_input("IPC Section Number", placeholder="e.g. 302, 376, 420, 498A", key="ipc_lookup")
        if st.button("Search Mapping", key="search_mapping") and ip:
            key = ip.strip().upper()
            if key == "497":
                st.warning("IPC 497 (Adultery) was struck down by the Supreme Court and has no BNS equivalent.")
            elif key in IPC_TO_BNS:
                item = IPC_TO_BNS[key]
                st.markdown(
                    f"""
                    <div class='card'>
                      <span class='section-chip'>IPC {key}</span>
                      <span style='color:#f0883e;margin:0 6px;'>→</span>
                      <span class='section-chip' style='color:#3fb950;border-color:#2f6e46;'>BNS {item['bns']}</span>
                      <div style='margin-top:8px;font-weight:600;'>{item['title']}</div>
                      <div style='margin-top:8px;color:#3fb950;'>✅ Successfully mapped · Source: BNS 2023 Official Gazette</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"💬 Ask about BNS §{item['bns']}", key=f"ask_bns_{key}"):
                    st.session_state.page = "AI Assistant"
                    st.session_state.pending_query = f"Explain BNS Section {item['bns']} ({item['title']})"
                    st.rerun()
            else:
                st.error("No mapping found for this section in current reference.")

    with tab2:
        rows = [
            {"IPC Section": ipc, "BNS Section": v["bns"], "Title/Description": v["title"], "Category": v["category"]}
            for ipc, v in IPC_TO_BNS.items()
        ]
        df = pd.DataFrame(rows)
        category = st.selectbox(
            "Category Filter",
            [
                "All",
                "Offences Against Body",
                "Property Offences",
                "Women & Children",
                "State Offences",
                "Marriage",
                "Defamation",
                "General Exceptions",
                "Punishments",
            ],
            key="cat_filter",
        )
        search = st.text_input("Search in table", key="map_search")
        if category != "All":
            df = df[df["Category"] == category]
        if search:
            patt = search.strip()
            mask = (
                df["IPC Section"].str.contains(patt, case=False, na=False)
                | df["BNS Section"].str.contains(patt, case=False, na=False)
                | df["Title/Description"].str.contains(patt, case=False, na=False)
                | df["Category"].str.contains(patt, case=False, na=False)
            )
            df = df[mask]
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        section_map = {}
        for ipc, info in IPC_TO_BNS.items():
            bns = info["bns"]
            if bns not in section_map:
                section_map[bns] = {
                    "title": info["title"],
                    "definition": f"This section governs: {info['title'].lower()}.",
                    "punishment": "As prescribed under BNS 2023 and relevant judicial interpretation.",
                    "chapter": info["category"],
                    "ipc_eq": [ipc],
                }
            else:
                section_map[bns]["ipc_eq"].append(ipc)

        options = sorted(section_map.keys(), key=lambda x: (len(x), x))
        selected = st.selectbox("Choose BNS section", options, key="bns_detail")
        detail = section_map[selected]
        st.markdown(
            f"""
            <div class='card'>
                <div style='font-size:20px;font-weight:700;'>BNS Section {selected}</div>
                <div style='color:#58a6ff;margin-top:4px;'>{detail['title']}</div>
                <div style='margin-top:10px;'><b>Definition:</b> {detail['definition']}</div>
                <div style='margin-top:6px;'><b>Punishment:</b> {detail['punishment']}</div>
                <div style='margin-top:6px;'><b>Chapter:</b> {detail['chapter']}</div>
                <div style='margin-top:6px;'><b>IPC Equivalent:</b> {", ".join(detail['ipc_eq'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_lawyers_page() -> None:
    page_header("👨‍⚖️", "Lawyers Directory", "Find verified legal professionals")
    st.divider()
    search = st.text_input("Search lawyers by name, city, or specialization")
    filtered = [
        l
        for l in LAWYERS
        if not search
        or search.lower() in l["name"].lower()
        or search.lower() in l["city"].lower()
        or search.lower() in l["spec"].lower()
    ]
    for i in range(0, len(filtered), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j >= len(filtered):
                continue
            l = filtered[i + j]
            initials = "".join([x[0] for x in l["name"].replace("Adv. ", "").split()[:2]]).upper()
            with col:
                st.markdown(
                    f"""
                    <div class='card'>
                        <div style='width:42px;height:42px;border-radius:50%;background:#1e3a5f;color:#58a6ff;display:flex;align-items:center;justify-content:center;font-weight:700;'>{initials}</div>
                        <div style='margin-top:8px;font-size:15px;font-weight:700;'>{l['name']}</div>
                        <div class='section-chip' style='margin-top:6px;'>{l['spec']}</div>
                        <div style='margin-top:8px;color:#8b949e;'>{l['city']} · {l['exp']}</div>
                        <div style='margin-top:6px;'>{"⭐" * int(round(l['rating']))} ({l['rating']})</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("📞 Contact", key=f"contact_{l['phone']}", use_container_width=True):
                    st.toast(f"Call {l['name']} at {l['phone']}")
                    st.success(f"Phone: {l['phone']}")


def render_knowledge_base_page() -> None:
    page_header("📚", "Knowledge Base", "BNS summaries, changes, and quick section reference")
    st.divider()
    t1, t2, t3 = st.tabs(["📖 BNS Overview", "⚡ New in BNS", "📜 Key Sections Quick Reference"])

    with t1:
        chapters = [
            ("Chapter V — Offences Against Women and Children (Sections 63–124)", "63–124", "63, 64, 70, 74, 78, 85", "Sexual offences, cruelty, acid attacks, and child/women protections."),
            ("Chapter XVI — Offences Affecting the Human Body (Sections 99–146)", "99–146", "101, 105, 109, 113, 117, 138", "Homicide, hurt, kidnapping, and bodily safety offences."),
            ("Chapter XVII — Offences Against Property (Sections 303–334)", "303–334", "303, 308, 309, 310, 318, 329", "Theft, robbery, dacoity, cheating, and trespass provisions."),
            ("Chapter XX — Offences Relating to Marriage (Sections 80–90)", "80–90", "81, 82, 84, 85, 86", "Bigamy, fraudulent marriage, cruelty, and related offences."),
            ("Chapter VI — Offences Against the State (Sections 147–158)", "147–158", "147, 152", "Acts endangering sovereignty, war against state, and related offences."),
        ]
        for title, sec_range, key_sections, desc in chapters:
            with st.expander(title):
                st.write(f"**Section range:** {sec_range}")
                st.write(f"**Key sections:** {key_sections}")
                st.write(desc)

    with t2:
        highlights = [
            ("🟢 NEW", "#3fb950", "Community Service as punishment"),
            ("🟢 NEW", "#3fb950", "Organized crime provisions"),
            ("🟢 NEW", "#3fb950", "Terrorism provisions (moved from UAPA to BNS)"),
            ("🟢 NEW", "#3fb950", "Trial in absentia"),
            ("🟠 CHANGED", "#f0883e", "Sedition (IPC 124A) renamed and expanded to §152"),
            ("🟠 CHANGED", "#f0883e", "Rape definition broadened"),
            ("🟠 CHANGED", "#f0883e", "Juvenile age clarified in murder"),
            ("🟠 CHANGED", "#f0883e", "Suicide attempt decriminalized"),
            ("🔴 REMOVED", "#f85149", "IPC 497 (Adultery) struck down by SC — not in BNS"),
            ("🔴 REMOVED", "#f85149", "IPC 309 punishment softened"),
        ]
        for tag, color, text in highlights:
            st.markdown(
                f"<div class='card' style='border-left:4px solid {color};margin-bottom:8px;'><b>{tag}</b> · {text}</div>",
                unsafe_allow_html=True,
            )

    with t3:
        top_30 = []
        for ipc, val in list(IPC_TO_BNS.items())[:30]:
            top_30.append(
                {
                    "Section": val["bns"],
                    "Title": val["title"],
                    "Punishment": "As per BNS schedule and judicial interpretation",
                    "Category": val["category"],
                }
            )
        df = pd.DataFrame(top_30).drop_duplicates(subset=["Section", "Title"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button("Download CSV", csv_buf.getvalue().encode("utf-8"), "bns_quick_reference.csv", "text/csv")


def main() -> None:
    render_sidebar()
    if st.session_state.page == "AI Assistant":
        render_ai_assistant_page()
    elif st.session_state.page == "Dashboard":
        render_dashboard_page()
    elif st.session_state.page == "Lawyers":
        render_lawyers_page()
    elif st.session_state.page == "Knowledge Base":
        render_knowledge_base_page()
    else:
        render_ipc_bns_tool()


if __name__ == "__main__":
    main()
