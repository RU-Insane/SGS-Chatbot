from pydantic import BaseModel, validator
from typing import List, Dict, Any
import hashlib

class Record(BaseModel):
    id: str
    values: List[float]
    metadata: Dict[str, Any]

    # Using a validator to generate the id based on metadata['content']
    @validator('id', pre=True, always=True)
    def set_id_from_metadata(cls, v, values):
        # If 'id' is explicitly given, use it
        if v is not None:
            return v
        # Generate the id based on metadata['content']
        content = values.get('metadata', {}).get('content', '')
        # Here, we're using SHA-256 for hashing. Adjust as necessary.
        hashed_content = hashlib.sha256(content.encode()).hexdigest()
        return hashed_content

    class Config:
        # Allow setting of fields via constructor even if they are computed by validators
        allow_mutation = True
