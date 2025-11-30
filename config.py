import os
from dotenv import load_dotenv

# Charge d'abord le .env
load_dotenv()

# Désactiver explicitement LangSmith si aucune clé n'est fournie pour éviter les 401
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGSMITH_API_KEY"] = ""
os.environ.setdefault("LANGCHAIN_ENDPOINT", "")
os.environ.setdefault("LANGSMITH_ENDPOINT", "")

# Répertoires de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROMPT_DIR = os.path.join(BASE_DIR, 'prompt')

# Chemins data
RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw', 'bareshemotorenwerke.csv')
CLEANED_DATA_PATH = os.path.join(DATA_DIR, 'processed', 'bmw_cleaned.csv')
DB_PATH = os.path.join(DATA_DIR, 'processed', 'bmw_sales.db')

# Cohere config
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
# Modèle Cohere : on utilise par défaut "command-r" (command-r-plus est retiré)
COHERE_MODEL = os.getenv('COHERE_MODEL', 'command-a-03-2025')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 4096))
TEMPERATURE = 0.3  # Pour deterministic code generation
LLM_READY = bool(COHERE_API_KEY)

# Sécurité params
EXEC_TIMEOUT = int(os.getenv('TIMEOUT_EXEC', 10))  # 10s max
MAX_AGENT_ITERATIONS = 5  # Limite boucles ReAct

# Langues supportées
SUPPORTED_LANGUAGES = ['Français', 'Anglais']

# Prompts paths
SYSTEM_PROMPT_PATH = os.path.join(PROMPT_DIR, 'system_prompt.txt')
REACT_PROMPT_PATH = os.path.join(PROMPT_DIR, 'reAct_prompt.txt')
FEW_SHOT_PATH = os.path.join(PROMPT_DIR, 'few_shot.json')
