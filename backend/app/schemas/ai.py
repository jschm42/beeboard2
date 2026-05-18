from pydantic import BaseModel
from typing import Dict, Any, List

class AIChatQuery(BaseModel):
    query: str

class AIChatResponse(BaseModel):
    response: str

class AIDraftQuery(BaseModel):
    text: str

class AIDraftResponse(BaseModel):
    draft: Dict[str, Any]
