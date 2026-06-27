from fastapi import APIRouter, HTTPException

from online_backend.api.dependencies import service

router = APIRouter(
    prefix="/case",
    tags=["Case"]
)



@router.get("/{case_id}")
def get_case(case_id: int):

    case = service.get_case(case_id)

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    return case
