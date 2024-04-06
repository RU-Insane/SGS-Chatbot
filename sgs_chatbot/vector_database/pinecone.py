# Description: This module contains the PineconeVectorDatabase class which is used to interact with the Pinecone API.
import hashlib
import random
import itertools
from pinecone import Pinecone
from .record import Record

def chunks(iterable, batch_size=100):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))


class PineconeVectorDatabase:
    def __init__(self, api_key: str, index_name: str):
        self.pinecone = Pinecone(api_key, pool_threads=30)
        self.index_name = index_name
        self.index = self.pinecone.Index(self.index_name)
    
    def delete_index(self):
        self.pinecone.delete_index(self.index_name)
    
    def search(self, vector: list[float], top_k: int = 8, include_metadata: bool = True):
        return self.index.query(vector=vector, top_k=top_k, include_metadata=include_metadata)['matches']
    
    def upsert(self, records: Record, batch_size: int = 100):
        # Transform records into instances of Record model
        record_instances = [Record(**record) for record in records]
        
        # Prepare records for upsert in the required format
        upsert_records = [
            {
                "id": record_instance.id,
                "values": record_instance.values,
                "metadata": record_instance.metadata
            }
            for record_instance in record_instances
        ]

        # Send requests in parallel using chunks of transformed records
        async_results = [
            self.index.upsert(vectors=records_chunk, async_req=True)
                for records_chunk in chunks(upsert_records, batch_size=batch_size)
        ]

        # Wait for and retrieve responses
        [async_result.get() for async_result in async_results]
        print('Upserted: ', len(records), ' records with batch size: ', batch_size)
