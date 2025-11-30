# src/agents/pandas_agent.py
"""
Agent Pandas fallback pour analyses directes sur DataFrame.
Utilisé si ReAct échoue ou pour queries simples.
Conforme au cahier : Analyses sur Pandas DF, génération code Python.
"""

from dotenv import load_dotenv
import pandas as pd
import os
import io
import re
from contextlib import redirect_stdout
from typing import Optional, Dict, Any

try:
    from langchain_experimental.agents import create_pandas_dataframe_agent
except ImportError:
    create_pandas_dataframe_agent = None

from config import CLEANED_DATA_PATH, SYSTEM_PROMPT_PATH, MAX_TOKENS, LLM_READY
from src.utils.cohere_integration import get_cohere_client

load_dotenv()


def _region_from_query(query: str) -> Optional[str]:
    """Mappe quelques pays/termes courants vers les régions dispo dans le dataset."""
    q = query.lower()
    mapping = {
        "china": "Asia",
        "chinese": "Asia",
        "asie": "Asia",
        "asia": "Asia",
        "europe": "Europe",
        "europa": "Europe",
        "france": "Europe",
        "germany": "Europe",
        "allemagne": "Europe",
        "uk": "Europe",
        "united kingdom": "Europe",
        "usa": "North America",
        "united states": "North America",
        "america": "North America",
        "north america": "North America",
        "middle east": "Middle East",
        "moyen-orient": "Middle East",
        "africa": "Africa",
        "afrique": "Africa",
        "south america": "South America",
        "amerique du sud": "South America",
        "latam": "South America",
    }
    for key, region in mapping.items():
        if key in q:
            return region
    return None


def _fallback_region_chart(df: pd.DataFrame, query: str) -> Optional[Dict[str, Any]]:
    """Construit un graphique par région quand la granularité pays n'existe pas."""
    region = _region_from_query(query)
    if region is None:
        return None

    df_power = df[(df["powertrain"].isin(["BEV", "PHEV"])) & (df["year"] >= 2018) & (df["region"] == region)]
    if df_power.empty:
        return None

    try:
        import plotly.express as px
    except Exception:
        return {"explanation": "Plotly est requis pour afficher le graphique (pip install plotly)."}

    grouped = df_power.groupby("year")["sales"].sum().reset_index()
    fig = px.line(
        grouped,
        x="year",
        y="sales",
        title=f"Ventes électriques en {region} (granularité région seulement)",
        markers=True,
    )
    return {
        "graph": fig,
        "explanation": f"Le dataset n'a pas le détail par pays. Affichage par région ({region}) pour BEV/PHEV depuis 2018.",
    }

def create_pandas_agent():
    if create_pandas_dataframe_agent is None:
        raise ImportError("Package manquant : installez 'langchain-experimental' pour activer l'agent Pandas.")

    if not LLM_READY:
        raise RuntimeError("Cohere n'est pas configuré. Ajoutez COHERE_API_KEY dans .env.")

    if not os.path.exists(CLEANED_DATA_PATH):
        raise FileNotFoundError(f"Je ne trouve pas le fichier nettoyé {CLEANED_DATA_PATH}. Lancez data_Preparation.py pour le générer.")

    # Chargement DF
    df = pd.read_csv(CLEANED_DATA_PATH)
    
    # LLM Cohere
    llm = get_cohere_client(temperature=0.2, max_tokens=MAX_TOKENS)
    
    # Agent Pandas
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_type="tool-calling",
        allow_dangerous_code=True,  # Opt-in requis par LangChain pour le python repl
        prefix=open(SYSTEM_PROMPT_PATH, encoding="utf-8").read(),  # Intégrer system prompt
    )
    
    return agent

# Fonction pour process query avec Pandas agent (fallback)
def process_query_with_pandas(query: str):
    agent = create_pandas_agent()
    result = agent.invoke(query)
    output_text = result.get("output") if isinstance(result, dict) else str(result)

    # Tente d'exécuter le code Python généré pour récupérer une figure réelle
    code_match = re.search(r"```python\s*(.*?)```", output_text, re.DOTALL | re.IGNORECASE)
    code_to_run = code_match.group(1) if code_match else output_text

    df = pd.read_csv(CLEANED_DATA_PATH)
    exec_env = {"pd": pd, "df": df}
    try:
        import plotly.express as px  # import local pour éviter dépendance si manquante
        exec_env["px"] = px
    except Exception:
        return "Plotly est requis pour afficher le graphique (pip install plotly)."

    captured = io.StringIO()
    fig_obj = None
    try:
        with redirect_stdout(captured):
            exec(code_to_run, exec_env, exec_env)
        # Cherche une figure explicite ou toute figure Plotly présente dans l'environnement
        fig_obj = exec_env.get("fig")
        if fig_obj is None:
            for value in exec_env.values():
                if hasattr(value, "to_plotly_json") and hasattr(value, "write_image"):
                    fig_obj = value
                    break
    except Exception as exec_err:
        fallback = _fallback_region_chart(df, query)
        return fallback if fallback else f"Echec exécution du code généré : {exec_err}"

    response = {"explanation": captured.getvalue().strip()}
    if fig_obj is not None:
        # Si la figure est vide, on tente un fallback par région
        is_empty = False
        try:
            is_empty = not fig_obj.data or all(
                (not getattr(trace, "x", None) or len(trace.x) == 0) for trace in fig_obj.data
            )
        except Exception:
            is_empty = False

        if is_empty:
            fallback = _fallback_region_chart(df, query)
            if fallback:
                return fallback
        response["graph"] = fig_obj

    return response if response else output_text
