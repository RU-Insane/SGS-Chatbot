import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    # Pinecone API key
    pinecone_api_key: str
    pinecone_index_name: str
    # Voyage API key
    voyage_api_key: str
    # Custom LLM API key
    custom_llm_api_url: str
    custom_llm_max_new_tokens: int
    custom_llm_top_p: float
    custom_llm_temperature: float
    custom_llm_repetition_penalty: float

    def __post_init__(self):
        super().__init__()
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
        self.voyage_api_key = os.getenv("VOYAGE_API_KEY")
        self.custom_llm_api_url = "http://localhost:8080/completion"
        self.custom_llm_max_new_tokens = 1024
        self.custom_llm_top_p = 0.9
        self.custom_llm_temperature = 0
        self.custom_llm_repetition_penalty = 1.5

