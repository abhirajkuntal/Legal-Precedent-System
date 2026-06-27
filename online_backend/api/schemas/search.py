from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):

    query: str
    top_k: int = 5

    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    judge: Optional[str] = None
    category: Optional[str] = None
