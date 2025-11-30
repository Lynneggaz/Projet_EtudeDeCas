# src/tools/safe_python_executor.py
"""
Outil pour exécution Python en sandbox (restrictedpython + timeout).
Conforme au cahier : Sandbox + restrictions Python + timeout 10s.
Utilise multiprocessing pour timeout, restrictedpython pour limiter globals.
"""

from langchain.tools import tool
import multiprocessing
import os
import signal
import pandas as pd
import plotly.express as px  # Autorisé

try:
    from restrictedpython import compile_restricted, safe_globals, limited_builtins
except ImportError:
    compile_restricted = None
    safe_globals = None
    limited_builtins = None

TIMEOUT = int(os.getenv('TIMEOUT_EXEC', 10))

# Globals autorisés (seulement pandas, plotly, print, etc.) si restrictedpython est dispo
if safe_globals is not None and limited_builtins is not None:
    SANDBOX_GLOBALS = dict(safe_globals)
    SANDBOX_GLOBALS['pd'] = pd
    SANDBOX_GLOBALS['px'] = px
    SANDBOX_GLOBALS['print'] = print
    SANDBOX_GLOBALS['_getitem_'] = limited_builtins['getitem']
    SANDBOX_GLOBALS['_getattr_'] = limited_builtins['getattr']

    # Blacklist fonctions dangereuses
    for key in ['open', 'exec', 'eval', '__import__']:
        if key in SANDBOX_GLOBALS:
            del SANDBOX_GLOBALS[key]
else:
    SANDBOX_GLOBALS = None

def timeout_handler(signum, frame):
    raise TimeoutError("Exécution Python timeout après 10s")

@tool
def safe_python_tool(code: str) -> str:
    """
    Exécute code Python en sandbox avec timeout.
    Input: code str à exécuter.
    Output: Résultat print ou erreur.
    """
    if compile_restricted is None or SANDBOX_GLOBALS is None:
        return "Erreur: le module 'restrictedpython' n'est pas installé. Installez les dépendances via requirements.txt."

    try:
        # Compiler restricted
        byte_code = compile_restricted(code, '<string>', 'exec')
        
        # Locals pour sortie
        locals_dict = {}
        
        # Timeout via signal (Unix only; pour Windows, utiliser multiprocessing)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TIMEOUT)
        
        # Exécuter
        exec(byte_code, dict(SANDBOX_GLOBALS), locals_dict)
        
        signal.alarm(0)  # Reset alarm
        
        # Capturer prints ou fig (mais fig.show() est pour démo Streamlit)
        return "Exécution réussie. Résultats affichés."
    
    except TimeoutError:
        return "Erreur: Timeout après 10s."
    except Exception as e:
        return f"Erreur sandbox: {str(e)}"
