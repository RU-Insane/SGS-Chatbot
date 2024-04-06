from pinecone import Pinecone

class PineconeVectorDatabase:
    def __init__(self, api_key: str, index_name: str):
        self.pinecone = Pinecone(api_key)
        self.index = self.pinecone.Index(index_name)
    
    def search(self, vector: list[float], top_k: int = 8, include_metadata: bool = True):
        return self.index.query(vector = vector, top_k=top_k, include_metadata=include_metadata)
    
    def upsert(self, id: str, vectors: list, metadata: dict = None):
        self.index.upsert(id, vectors, metadata)