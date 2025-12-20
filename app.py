import streamlit as st
from plotly.graph_objs import Figure

from modules.analytics_router import process_query
from config import APP_NAME, DEFAULT_LANGUAGE

# ==========================
# Streamlit Page Config
# ==========================
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="🤖"
)

# ==========================
# Sidebar Language Selector
# ==========================
language_map = {
    "English": "en",
    "German": "de",
    "French": "fr",
    "Spanish": "es",
    "Italian": "it"
}

with st.sidebar:
    st.header("🌍 Language")
    selected_lang = st.selectbox("Select language:", list(language_map.keys()))
    lang_code = language_map[selected_lang]

# ==========================
# Title
# ==========================
title_text = {
    "en": "HR-GPT 3.0: Multilingual AI-Powered HR Analytics Assistant",
    "de": "HR-GPT 3.0: Mehrsprachiger KI-gestützter HR-Analyseassistent",
    "fr": "HR-GPT 3.0 : Assistant multilingue d'analyse RH alimenté par l'IA",
    "es": "HR-GPT 3.0: Asistente multilingüe de análisis de RRHH impulsado por IA",
    "it": "HR-GPT 3.0: Assistente multilingue di analisi HR basato sull'IA"
}

st.title(title_text.get(lang_code, title_text["en"]))

# ==========================
# Chat History
# ==========================
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def add_message(role, content):
    st.session_state["messages"].append({"role": role, "content": content})

# Display history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================
# Chat Input
# ==========================
user_query = st.chat_input("Ask something about HR analytics, workforce, charts, or HR concepts...")

if user_query:
    # Log user's message
    add_message("user", user_query)
    with st.chat_message("user"):
        st.markdown(user_query)

    # Process with analytics + LLM
    response = process_query(user_query, lang_code)

    # Render chart or text
    if isinstance(response, Figure):
        with st.chat_message("assistant"):
            st.markdown("📊 Here's the chart you requested:")
        st.plotly_chart(response, use_container_width=True)
        add_message("assistant", "[CHART DISPLAYED]")
    else:
        add_message("assistant", response)
        with st.chat_message("assistant"):
            st.markdown(response)
