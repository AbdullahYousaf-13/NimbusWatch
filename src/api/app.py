from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.api.inference import InferenceService


templates = Jinja2Templates(directory="src/ui")
service: InferenceService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = InferenceService()
    try:
        yield
    finally:
        if service is not None:
            service.close()


app = FastAPI(title="NimbusWatch", version="1.0.0", lifespan=lifespan)


def get_service() -> InferenceService:
    if service is None:
        raise RuntimeError("Inference service is not initialized.")
    return service


@app.get("/health")
def health() -> dict:
    active = get_service()
    return {"status": "ok", "model_name": active.model_info()["model_name"]}


@app.get("/model-info")
def model_info() -> dict:
    return get_service().model_info()


@app.post("/predict")
async def predict(request: Request) -> dict:
    payload = await request.json()
    try:
        numeric_payload = {key: float(value) for key, value in payload.items()}
        return get_service().predict(numeric_payload)
    except ValueError as exc:
        detail = str(exc)
        try:
            detail = json.loads(detail)
        except json.JSONDecodeError:
            pass
        raise HTTPException(status_code=422, detail=detail) from exc


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    active = get_service()
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "feature_names": active.feature_names,
            "model_info": active.model_info(),
        },
    )
