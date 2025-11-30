import streamlit as st
import time
import json
import os
from langchain.memory import ConversationBufferMemory

from src.agents.react_agent import process_query_with_react
from src.agents.pandas_agent import process_query_with_pandas
from src.utils.visualisation import export_fig
from config import EXEC_TIMEOUT, SUPPORTED_LANGUAGES

# CSS custom pour styling BMW-inspired (bleu #003478, gris #f0f0f0, blanc)
st.markdown("""
<style>
    :root {
        --bmw-blue: #003478;
        --bmw-dark: #0f1f3a;
        --bmw-grey: #f0f0f0;
        --bmw-light: #ffffff;
        --bmw-muted: #6b778c;
    }
    .stApp, body, .main, .block-container {
        background-color: var(--bmw-grey);
        color: var(--bmw-dark);
    }
    .main-header, h1, h2, h3, h4, h5, h6, label, p, span, div, .stMarkdown {
        color: var(--bmw-dark);
    }
    .stTabs [data-baseweb="tab"] p {
        color: var(--bmw-dark);
    }
    .stButton > button {
        background-color: var(--bmw-blue);
        color: var(--bmw-light);
        border-radius: 8px;
    }
    .stMetric {
        background-color: var(--bmw-light);
        border: 1px solid var(--bmw-blue);
        border-radius: 8px;
        padding: 10px;
        color: var(--bmw-dark);
    }
    .stRadio label, .stSelectbox label, .stFileUploader label {
        color: var(--bmw-dark);
    }
    .stRadio div[role="radiogroup"] label p {
        color: var(--bmw-dark);
    }
    /* Text inputs */
    .stTextInput input, .stChatInput textarea {
        color: var(--bmw-light);
        background-color: var(--bmw-dark);
    }
    .stTextInput input::placeholder, .stChatInput textarea::placeholder {
        color: var(--bmw-muted);
    }
    /* Sidebar tweaks for contrast */
    section[data-testid="stSidebar"] {
        background-color: #101522;
    }
    section[data-testid="stSidebar"] * {
        color: #e8edf5 !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo BMW (URL publique, ou remplace par local si besoin)
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/512px-BMW.svg.png", width=100)

# Titre principal
st.markdown('<div class="main-header">Self-BI BMW (Bayerische Motoren Werke) : Analyses Ventes Mondiales (2010-2024)</div>', unsafe_allow_html=True)
st.markdown("Posez une question en langage naturel pour des insights instantanés ! (FR/EN)")

# Sidebar enrichie
with st.sidebar:
    st.header("Configuration")
    language = st.selectbox("Langue", SUPPORTED_LANGUAGES, help="Choisissez la langue pour les labels et explications.")
    st.info(f"Timeout max : {EXEC_TIMEOUT}s | Taux succès cible : >92%")
    st.markdown("---")
    st.subheader("À propos du dataset")
    st.write("Source : Kaggle BMW Sales (~150k lignes)")
    st.write("Colonnes : Year, Region, Model, Powertrain, Sales, etc.")

# Tabs pour organisation
tab1, tab2 = st.tabs(["Analyse Principale", "Historique"])

with tab1:
    # Input chat-like
    query = st.chat_input(placeholder="Ex: Évolution des ventes électriques en Asie/Europe depuis 2018 ?")

    if query:
        # Timer pour UX
        start_time = time.time()
        with st.spinner("Analyse en cours... (cible <12s)"):
            try:
                result = process_query_with_react(query)
            except Exception:
                try:
                    result = process_query_with_pandas(query)
                except Exception as pandas_error:
                    error_msg = f"Analyse impossible : {pandas_error}"
                    st.error(error_msg)
                    result = error_msg
            
            elapsed = time.time() - start_time
            st.success(f"Analyse terminée en {elapsed:.2f}s !")

        # Affichage résultat (assume result est dict avec 'graph', 'key_figures' (dict), 'explanation')
        if isinstance(result, dict):
            if 'graph' in result:
                st.plotly_chart(result['graph'], use_container_width=True)
                st.session_state.last_graph = result['graph']
            
            if 'key_figures' in result:
                st.subheader("Chiffres Clés" if language == 'Français' else "Key Figures")
                cols = st.columns(len(result['key_figures']))
                for i, (label, value) in enumerate(result['key_figures'].items()):
                    cols[i].metric(label, value)
            
            if 'explanation' in result:
                with st.expander("Explication Détaillée" if language == 'Français' else "Detailed Explanation"):
                    st.write(result['explanation'])
        else:
            st.write(result)  # Fallback textuel
        
        # Ajout à historique et mémoire
        st.session_state.history.append({"question": query, "response": result, "time": elapsed})
        st.session_state.memory.save_context({"input": query}, {"output": str(result)})

# Export section (reste accessible après exécution)
with tab1:
    st.subheader("Exporter")
    export_format = st.radio("Format", ['PNG', 'PDF'], horizontal=True, key="export_format")
    graph = st.session_state.get("last_graph")
    if graph is None:
        st.info("Exécutez une analyse pour activer l'export.")
    else:
        try:
            file_ext = export_format.lower()
            data_bytes = graph.to_image(format=file_ext, engine="kaleido")
            download_name = f"bmw_analysis.{file_ext}"
            st.download_button("Télécharger", data=data_bytes, file_name=download_name, mime=f"image/{file_ext}")
        except Exception as export_error:
            st.error(f"Export impossible : {export_error}")

with tab2:
    st.header("Historique des Analyses")
    if 'history' not in st.session_state or not st.session_state.history:
        st.info("Aucune analyse pour l'instant. Posez une question pour commencer !")
    else:
        for item in reversed(st.session_state.history):  # Plus récent en haut
            with st.chat_message("user"):
                st.write(f"**Q:** {item['question']}")
            with st.chat_message("assistant"):
                st.write(f"**R:** {item['response']}")
                st.caption(f"Temps : {item['time']:.2f}s")
            st.divider()

# Initialisation session si besoin
if 'history' not in st.session_state:
    st.session_state.history = []
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()
if 'last_graph' not in st.session_state:
    st.session_state.last_graph = None