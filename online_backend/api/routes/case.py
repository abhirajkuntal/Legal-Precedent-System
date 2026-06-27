from fastapi import APIRouter

router = APIRouter()


@router.get("/{case_id}")
def get_case(case_id: str):

    # later: fetch from metadata store / parquet / sqlite
    return {
        "case_id": case_id,
        "message": "Case endpoint placeholder"
    }
