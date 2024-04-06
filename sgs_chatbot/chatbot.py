from dotenv import load_dotenv
from sgs_chatbot.embedder.voyage import VoyageEmbedder
from sgs_chatbot.vector_database.pinecone import PineconeVectorDatabase
from sgs_chatbot.llm.custom_llm import CustomLLM
from sgs_chatbot.config import Config


class Chatbot:
    def __init__(self, embedder: VoyageEmbedder, vector_database: PineconeVectorDatabase, llm: CustomLLM, config: Config):
        self.embedder = embedder(api_key=config.voyage_api_key)
        self.vector_database = vector_database(api_key=config.pinecone_api_key, index_name=config.pinecone_index_name)
        self.llm = llm(
            api_url=config.custom_llm_api_url,
            max_new_tokens=config.custom_llm_max_new_tokens,
            top_p=config.custom_llm_top_p,
            temperature=config.custom_llm_temperature,
            repetition_penalty=config.custom_llm_repetition_penalty
        )
        self.config = config
    
    def get_records(self, text: str, top_k: int = 8):
        vector = self.embedder.embed(text)
        records = self.vector_database.search(vector=vector, top_k=top_k)
        return records

    def truncate_context(self, context: str, max_tokens: int = 1000):
        return context[:max_tokens]
    
    async def generate_answer(self, prompt: str):
        return await self.llm._acall(prompt=prompt)
        
    
