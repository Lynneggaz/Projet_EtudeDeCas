# src/agents/react_agent.py

"""
Agent LangChain ReAct avec Cohere pour génération de code Python/SQL.
Conforme au cahier des charges : Utilise ReAct pour raisonner étape par étape,
génère code sécurisé, exécute via tools sandboxés.
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

from config import MAX_TOKENS, REACT_PROMPT_PATH, LLM_READY
from src.tools.safe_python_executor import safe_python_tool
from src.tools.sql_tool import sql_query_tool
from src.utils.cohere_integration import get_cohere_client

load_dotenv()

# Prompt ReAct personnalisé (chargé depuis prompt/reAct_prompt.txt + system)
with open(REACT_PROMPT_PATH, encoding="utf-8") as prompt_file:
    base_prompt = prompt_file.read()

# Template ReAct : ne pas exiger la variable {tool} (non fournie par create_react_agent)
react_prompt_template = PromptTemplate.from_template(
    base_prompt
    + "\n\nOutils disponibles:\n{tools}\n\nChoisis un outil parmi: {tool_names}\n\n"
    + "Format attendu:\nQuestion: {input}\nThought: ...\nAction: <nom de l'outil choisi>\nAction Input: ...\nObservation: ...\n"
    + "(répéter Thought/Action/Observation si besoin)\nFinal Answer: ...\n\n"
    + "Question: {input}\n{agent_scratchpad}"
)

def create_react_agent_executor():
    if not LLM_READY:
        raise RuntimeError("Cohere n'est pas configuré. Ajoutez COHERE_API_KEY dans .env.")

    # LLM Cohere Command R+
    llm = get_cohere_client(temperature=0.3, max_tokens=MAX_TOKENS)
    
    # Tools disponibles pour l'agent
    tools = [safe_python_tool, sql_query_tool]
    
    # Création agent ReAct
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=react_prompt_template,
    )
    
    # Mémoire pour contexte (historique questions)
    memory = ConversationBufferMemory(memory_key="chat_history")
    
    # Executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        memory=memory,
        handle_parsing_errors="Le format de sortie a été corrigé. Réessaie brièvement.",
        max_iterations=4,           # Quelques boucles pour converger
        max_execution_time=20,      # Coupe court pour éviter les attentes longues
    )
    
    return executor

# Fonction principale pour traiter une question
def process_query_with_react(query: str):
    executor = create_react_agent_executor()
    result = executor.invoke({"input": query})

    output = result.get("output", "")
    # Si l'agent s'est arrêté par limite, on force le fallback
    if isinstance(output, str) and "Agent stopped due to iteration limit or time limit" in output:
        raise RuntimeError(output)

    return output  # Contient code généré + résultat exécution + explication
