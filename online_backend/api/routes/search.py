from fastapi import APIRouter
from api.schemas.search import SearchRequest
from online_backend.services.legal_search_service import LegalSearchService

router = APIRouter()

service = LegalSearchService()


@router.post("/")
def search_cases(request: SearchRequest):

    results = service.search(
        query=request.query,
        top_k=request.top_k,
        court=request.court,
        jurisdiction=request.jurisdiction,
        judge=request.judge,
        category=request.category
    )

    return results
