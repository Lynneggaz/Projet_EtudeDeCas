from dotenv import load_dotenv
from langchain.agents import create_pandas_dataframe_agent
import os
import pandas as pd
from src.utils.cohere_integration import get_cohere_client


load_dotenv()
cleanPath= "../../data/processed/bmw_data_clean.csv"

def created_pandas_agent():
    df = pd.read_csv(cleanPath)
    llm= get_cohere_client(temperature=0.2, max_tokens=int(os.getenv("COHERE_MAX_TOKENS", 4096)))
    agent= create_pandas_dataframe_agent(llm, df, verbose=True,agent_type="tool-calling",allow_dangerous_code=False,prefix=open("../../prompt/system_prompt.txt").read())
    return agent


def process_query_pandas_agent(query: str) -> str:
    agent = created_pandas_agent()
    response = agent.invoke(query)

    return response["output"]







    

    