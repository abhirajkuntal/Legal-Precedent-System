from fastapi import FastAPI
from api.routes import search, case, health

app = FastAPI(
    title="Legal Precedent Search Engine",
    version="1.0"
)

app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(case.router, prefix="/case", tags=["Case"])
app.include_router(health.router, prefix="/health", tags=["Health"])
