
from cohere import Client
from langchain_cohere import ChatCohere
from tenacity import retry, stop_after_attempt, wait_exponential

from config import COHERE_API_KEY, COHERE_MODEL


def _resolve_model(model: str) -> str:
    # Le modèle "command-r-plus" est retiré; on bascule vers "command-r" par défaut
    if model.strip().lower() in {"command-r-plus", "command-r-plus-08-2024"}:
        return "command-r"
    return model

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_cohere_client(temperature=0.5, max_tokens=4096, stream=False):
    if not COHERE_API_KEY:
        raise RuntimeError("COHERE_API_KEY manquante. Ajoutez-la dans le fichier .env pour activer les agents.")

    model_to_use = _resolve_model(COHERE_MODEL)

    client = Client(api_key=COHERE_API_KEY)
    
    # Pour LangChain integration
    chat = ChatCohere(
        cohere_api_key=COHERE_API_KEY,
        model=model_to_use,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    if stream:
        # Exemple streaming (pour app Streamlit)
        def stream_response(prompt):
            try:
                response = client.chat_stream(message=prompt, model=model_to_use, temperature=temperature)
                for event in response:
                    if event.event_type == "text-generation":
                        yield event.text
            except Exception as e:
                yield f"Erreur Cohere: {str(e)}"
        
        return stream_response
    
    return chat
