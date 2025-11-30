# src/tools/sql_tool.py
"""
Outil SQL sur SQLite avec validation queries.
Conforme au cahier : Requêtes SQL ultra-rapides, validation pour sécurité (no DROP, no UPDATE).
"""

from langchain.tools import tool
import sqlite3
import os

from config import DB_PATH

@tool
def sql_query_tool(query: str) -> str:
    """
    Exécute SQL query sur SQLite DB.
    Input: SQL query str (SELECT only).
    Output: Résultats en str.
    """
    if not query.lower().startswith('select'):
        return "Erreur: Seules les queries SELECT sont autorisées."
    
    # Validation basique (no dangerous keywords)
    dangerous = ['drop', 'delete', 'update', 'insert', 'alter']
    if any(word in query.lower() for word in dangerous):
        return "Erreur: Query non autorisée (modifications interdites)."

    if not os.path.exists(DB_PATH):
        return f"Erreur: base SQLite introuvable ({DB_PATH}). Exécutez data_Preparation.py pour la créer."
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "Aucun résultat."
        
        return str(results)
    
    except Exception as e:
        return f"Erreur SQL: {str(e)}"
