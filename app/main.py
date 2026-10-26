
from fastapi import FastAPI

from app.api.routes.analysis import router as analysis_router

app = FastAPI(
    title="Cross-Language Package Interoperability Agent",
    version="0.1.0",
    description="Analyzes packages and recommends interoperability strategies.",
)

app.include_router(analysis_router)
