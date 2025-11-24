from langchain.tools import tool 
import sqlite3
import os

db_path = "../data/bmw_sales.db"
@tool
def sql_query_tool(query: str) -> str:
    if not query.lower().startswith("select"):
        return "Only SELECT queries are allowed."
    dangerous_statements = ["insert", "update", "delete", "drop", "alter", "create"]
    if any(stmt in query.lower() for stmt in dangerous_statements):
        return "Only SELECT queries are allowed."
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        if  not results:
            return "Query executed successfully, but no results to display."
        return str(results)
    except Exception as e:
        return f"An error occurred: {str(e)}"
    