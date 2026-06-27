from fastapi import APIRouter

from online_backend.api.dependencies import service
from online_backend.api.schemas.analyze import (
    AnalyzeRequest,
    AnalyzeResponse
)

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)


@router.post(
    "",
    response_model=AnalyzeResponse
)
def analyze(request: AnalyzeRequest):

    return service.analyze_text(
        request.text
    )
