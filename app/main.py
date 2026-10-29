
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.analysis import router as analysis_router

app = FastAPI(
    title="Cross-Language Package Interoperability Agent",
    version="0.1.0",
    description="Analyzes packages and recommends interoperability strategies.",
)

app.include_router(analysis_router)

frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount(
    "/assets",
    StaticFiles(directory=frontend_dir),
    name="frontend-assets",
)


@app.get("/health", tags=["service"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


app.mount(
    "/",
    StaticFiles(directory=frontend_dir),
    name="frontend-root-assets",
)
