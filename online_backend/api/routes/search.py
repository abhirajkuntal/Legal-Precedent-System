from fastapi import APIRouter
from online_backend.api.schemas.search import SearchRequest
from online_backend.api.dependencies import service

router = APIRouter(prefix="/search")



@router.post("")
def search_cases(request: SearchRequest):

    results = service.search(
        query=request.query,
        #top_k=request.top_k,
        court=request.court,
        jurisdiction=request.jurisdiction,
        judge=request.judge,
        category=request.category
    )

    return results
