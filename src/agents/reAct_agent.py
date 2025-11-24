import os
import pandas as pd
from dotenv import load_dotenv
from langchain.agents import Agent_executor, create_react_agent
from langchain.memory import ConversationBufferMemory
from src.utils.cohere_integration import get_cohere_client
from langchain.prompts import PromptTemplate
from src.tools.safe_python_executor import SafePythonExecutorTool
from src.tools.sql_tool import sql_query_tool
load_dotenv()

react_propmt= PromptTemplate.from_template(open("../../prompt/react_system_prompt.txt").read()+"\n\n{tools}\n\n{agent_scratchpad}")


def create_reAct_executor():
    llm= get_cohere_client(temperature=0.2, max_tokens=int(os.getenv("COHERE_MAX_TOKENS", 4096)))
    tools= [SafePythonExecutorTool, sql_query_tool]
    memory= ConversationBufferMemory(memory_key="chat_history")
    agent= create_react_agent(llm, tools, prompt=react_propmt, verbose=True)
    agent_executor= Agent_executor(agent=agent, tools=tools, memory=memory, verbose=True)
    return agent_executor

def process_query_reAct_agent(query: str) -> str:
    agent_executor = create_reAct_executor()
    response = agent_executor.invoke({"input": query})

    return response["output"]


