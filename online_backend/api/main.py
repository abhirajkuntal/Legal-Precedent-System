from fastapi import FastAPI
from online_backend.api.routes import search, case, health, analyze

app = FastAPI(
    title="Legal Precedent Search Engine",
    version="1.0"
)

app.include_router(search.router)
app.include_router(case.router)
app.include_router(health.router)
app.include_router(analyze.router)
