import streamlit as st
import pandas as pd
from plotly.graph_objs import Figure

from config import APP_NAME
from modules.analytics_router import process_query


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="🤖"
)

# ==================================================
# LANGUAGE MAP
# ==================================================
LANG_MAP = {
    "English": "en",
    "German": "de",
    "French": "fr",
    "Spanish": "es",
    "Italian": "it"
}

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.title("HR-GPT 3.0")
    st.caption("Multilingual HR Analytics Assistant")

    selected_lang = st.selectbox("🌍 Language", list(LANG_MAP.keys()))
    lang_code = LANG_MAP[selected_lang]

    st.markdown("---")

    if st.button("🆕 New Chat"):
        st.session_state.messages = []

    st.markdown("---")
    st.info("🔒 This assistant answers HR-related questions only.")

# ==================================================
# TITLE
# ==================================================
st.title("HR-GPT 3.0: Multilingual AI-Powered HR Analytics Assistant")

# ==================================================
# CHAT STATE
# ==================================================
if "messages" not in st.session_state:
    st.session_state.messages = []


def add_message(role, content):
    st.session_state.messages.append({
        "role": role,
        "content": content
    })


# ==================================================
# DISPLAY CHAT HISTORY
# ==================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str):
            st.markdown(msg["content"])
        else:
            st.write(msg["content"])


# ==================================================
# USER INPUT
# ==================================================
user_query = st.chat_input(
    "Ask about headcount, attrition, salary, engagement, or HR concepts..."
)

if user_query:
    # USER MESSAGE
    add_message("user", user_query)
    with st.chat_message("user"):
        st.markdown(user_query)

    # ASSISTANT RESPONSE
    response = process_query(user_query, lang_code)

    with st.chat_message("assistant"):

        # ---------------------------
        # CASE 1: CHART
        # ---------------------------
        if isinstance(response, Figure):
            st.markdown("📊 **Here’s the chart you requested**")
            st.plotly_chart(response, use_container_width=True)
            add_message("assistant", "[Chart generated]")

        # ---------------------------
        # CASE 2: TABLE (DataFrame)
        # ---------------------------
        elif isinstance(response, pd.DataFrame):
            st.dataframe(response, use_container_width=True)
            add_message("assistant", "[Table displayed]")

        # ---------------------------
        # CASE 3: KPI (int / float)
        # ---------------------------
        elif isinstance(response, (int, float)):
            st.metric(label="Result", value=response)
            add_message("assistant", f"Result: {response}")

        # ---------------------------
        # CASE 4: TEXT (LLM / fallback)
        # ---------------------------
        elif isinstance(response, str):
            st.markdown(response)
            add_message("assistant", response)

        # ---------------------------
        # CASE 5: NOTHING / ERROR
        # ---------------------------
        else:
            st.warning("⚠️ Unable to process this request with available data.")
            add_message("assistant", "⚠️ Unable to process this request.")
