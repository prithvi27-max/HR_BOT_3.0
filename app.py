import streamlit as st
from plotly.graph_objs import Figure

from modules.analytics_router import process_query
from config import APP_NAME, DEFAULT_LANGUAGE


# ==========================
# Page Config
# ==========================
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="🤖"
)

# ==========================
# Language Map
# ==========================
LANG_MAP = {
    "English": "en",
    "German": "de",
    "French": "fr",
    "Spanish": "es",
    "Italian": "it"
}

# ==========================
# Sidebar
# ==========================
with st.sidebar:
    st.title("HR-GPT 3.0")
    st.caption("Multilingual HR Analytics Assistant")

    selected_lang = st.selectbox(
        "🌍 Language",
        list(LANG_MAP.keys())
    )
    lang_code = LANG_MAP[selected_lang]

    st.markdown("---")

    # 🆕 New Chat Button
    if st.button("🆕 New Chat"):
        st.session_state.messages = []

    st.markdown("---")
    st.markdown("### 🧾 Chat History")

    # Show compact history
    if "messages" in st.session_state:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.markdown(f"• {msg['content'][:40]}")

    st.markdown("---")
    st.info("🔒 This assistant answers HR-related questions only.")


# ==========================
# Multilingual Title
# ==========================
TITLE_MAP = {
    "en": "HR-GPT 3.0: Multilingual AI-Powered HR Analytics Assistant",
    "de": "HR-GPT 3.0: Mehrsprachiger KI-HR-Analyseassistent",
    "fr": "HR-GPT 3.0 : Assistant RH multilingue alimenté par l’IA",
    "es": "HR-GPT 3.0: Asistente multilingüe de análisis de RRHH con IA",
    "it": "HR-GPT 3.0: Assistente multilingue di analisi HR basato sull’IA"
}

st.title(TITLE_MAP.get(lang_code, TITLE_MAP["en"]))


# ==========================
# Chat State
# ==========================
if "messages" not in st.session_state:
    st.session_state.messages = []


def add_message(role, content):
    st.session_state.messages.append({
        "role": role,
        "content": content
    })


# ==========================
# Display Chat Messages
# ==========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ==========================
# Chat Input
# ==========================
user_query = st.chat_input(
    "Ask about headcount, attrition trends, charts, or HR concepts..."
)

if user_query:
    # User message
    add_message("user", user_query)
    with st.chat_message("user"):
        st.markdown(user_query)

    # Assistant response
    response = process_query(user_query, lang_code)

    # Chart or Text
    if isinstance(response, Figure):
        with st.chat_message("assistant"):
            st.markdown("📊 **Here’s the chart you requested**")
            st.plotly_chart(response, use_container_width=True)

        add_message("assistant", "[Chart generated]")

    else:
        add_message("assistant", response)
        with st.chat_message("assistant"):
            st.markdown(response)
