from cohere import Client, CohereAPIError 

from langchain_cohere import ChatCohere
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import os 
from dotenv import load_dotenv

load_dotenv() 
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
model = "command-a-2025-03"
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(CohereAPIError))
def get_cohere_client() -> Client:
    return Client(api_key=COHERE_API_KEY)

