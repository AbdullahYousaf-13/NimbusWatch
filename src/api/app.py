from __future__ import annotations

import json
from contextlib import asynccontextmanager
from io import StringIO

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from src.api.inference import InferenceService
from src.api.ui_metadata import build_field_groups


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


@app.get("/demo-scenarios")
def demo_scenarios() -> dict:
    return get_service().demo_scenarios()


@app.get("/template.csv", response_class=PlainTextResponse)
def template_csv() -> str:
    return get_service().csv_template()


@app.post("/predict")
async def predict(request: Request) -> dict:
    payload = await request.json()
    try:
        numeric_payload = get_service().normalize_payload(payload)
        return get_service().predict(numeric_payload)
    except ValueError as exc:
        detail = str(exc)
        try:
            detail = json.loads(detail)
        except json.JSONDecodeError:
            pass
        raise HTTPException(status_code=422, detail=detail) from exc


@app.post("/predict-csv")
async def predict_csv(file: UploadFile = File(...)) -> dict:
    try:
        content = await file.read()
        frame = pd.read_csv(StringIO(content.decode("utf-8-sig")), low_memory=False, skipinitialspace=True)
        numeric_payload = get_service().validate_csv_frame(frame)
        return get_service().predict(numeric_payload)
    except ValueError as exc:
        detail = str(exc)
        try:
            detail = json.loads(detail)
        except json.JSONDecodeError:
            pass
        raise HTTPException(status_code=422, detail=detail) from exc
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=422, detail={"message": "CSV upload must be UTF-8 encoded."}) from exc
    except pd.errors.EmptyDataError as exc:
        raise HTTPException(status_code=422, detail={"message": "CSV upload is empty."}) from exc


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    active = get_service()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "feature_names": active.feature_names,
            "demo_scenarios": active.demo_scenarios()["scenarios"],
            "field_groups": build_field_groups(active.feature_names),
            "model_info": active.model_info(),
        },
    )
