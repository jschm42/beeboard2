from pydantic import BaseModel
from typing import Dict, Any, List

class AIChatQuery(BaseModel):
    query: str
    lang: str = "de"

class AIChatResponse(BaseModel):
    response: str

class AIDraftQuery(BaseModel):
    text: str
    lang: str = "de"

class AIDraftResponse(BaseModel):
    draft: Dict[str, Any]
