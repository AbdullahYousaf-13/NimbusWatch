# NimbusWatch

NimbusWatch is a binary anomaly-detection project built on `Isolation Forest` and a curated `CICIDS2017` subset. The project is designed for **zero-cost delivery**: model training runs locally, while the inference web app is intended to be deployed for free on `Hugging Face Spaces` as a managed cloud-hosted service.

## Primary Architecture

- Local pipeline builds a curated `CICIDS2017` subset.
- Local training produces the final `Isolation Forest` model and evaluation artifacts.
- The deployed component is the stateless `FastAPI` inference app.
- The live cloud target is `Hugging Face Spaces` using a Docker-based deployment.

Artifacts exported after training:

- `model.joblib`
- `feature_schema.json`
- `metrics.json`
- `training_summary.json`

Generated datasets and artifacts are **not source-controlled inputs**. They are recreated locally when needed and copied into the deployment repo only for live hosting.

## Local Setup

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Build the Curated Dataset

```powershell
python -m src.data.build_subset --csv-paths "D:\data\Tuesday-WorkingHours.pcap_ISCX.csv,D:\data\Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv,D:\data\Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" --output-path "data\processed\cicids2017_curated.csv"
```

This creates a smaller working dataset suitable for local training and zero-cost demo preparation.

## Train the Model Locally

```powershell
.\scripts\train_local.ps1 -CsvPaths "data\processed\cicids2017_curated.csv"
```

This writes the trained model and metadata to `artifacts/generated`.

Expected generated outputs:

- `artifacts/generated/model.joblib`
- `artifacts/generated/feature_schema.json`
- `artifacts/generated/metrics.json`
- `artifacts/generated/training_summary.json`

## Run the App Locally

```powershell
.\scripts\serve_local.ps1 -ArtifactDir "artifacts/generated" -Port 8000
```

Open `http://localhost:8000`.

## Planned Free Cloud Deployment

The live deployment target is `Hugging Face Spaces`:

- free managed hosting for the inference web app
- Docker-based app deployment
- public URL for the demo
- no paid cloud training requirement

The deployed app keeps the current interface:

- `GET /health`
- `GET /model-info`
- `POST /predict`
- `GET /`

## Hugging Face Spaces Deployment

Deploy the existing `FastAPI` app through a separate Hugging Face Space repo rather than directly from the GitHub source repo.

### Space repo contents

Copy these items into the Hugging Face Space repository:

- `Dockerfile.serve` renamed to `Dockerfile`
- `requirements.txt`
- `src/`
- `artifacts/generated/`
- the Space README template from `HUGGINGFACE_SPACE.md`, saved as the Space repo `README.md`

### Space repo steps

1. Create a new `Docker` Space on Hugging Face.
2. Keep the Space separate from the main GitHub source repository.
3. Rename `Dockerfile.serve` to `Dockerfile` inside the Space repo.
4. Retrain locally if needed, then copy the latest generated artifacts from `artifacts/generated`.
5. Copy the template from `HUGGINGFACE_SPACE.md` into the Space repo `README.md`.
6. Push the Space repo to Hugging Face.

### Deployment notes

- The app listens on the runtime `PORT` environment variable.
- The API contract stays unchanged.
- The deployed app loads local bundled artifacts from `artifacts/generated`.
- Retrain locally before redeploying if you want updated metrics or a newer model.

## API Example

Example `POST /predict` body:

```json
{
  "Flow Duration": 1200.0,
  "Total Fwd Packets": 25.0,
  "Total Backward Packets": 20.0,
  "Flow Bytes/s": 410.0,
  "SYN Flag Count": 1.0,
  "ACK Flag Count": 12.0,
  "Average Packet Size": 148.0,
  "Idle Mean": 190.0
}
```

The service requires the exact saved feature names from `feature_schema.json`. Missing or extra fields return a `422` validation error.

## Test

```powershell
pytest
```

## Why This Counts as Cloud Computing

This project still fits a cloud computing course because the final system is designed as a cloud-hosted service:

- inference is exposed as a remotely accessible managed web app
- the app is containerized for reproducible deployment
- training and serving are separated into distinct stages
- model artifacts are produced once and consumed by a stateless service
- the same service can be hosted on a managed cloud platform without changing the prediction contract

## Demo Flow

For the final demo, present the project in this order:

1. Show the problem statement and explain that the project detects anomalous network traffic using `Isolation Forest`.
2. Show the trained evaluation results from `artifacts/generated/metrics.json`.
3. Run the local app and make at least one prediction through the UI.
4. Open the live `Hugging Face Space` URL and show the same hosted app.
5. Explain that training is local for zero cost, while inference is deployed as a managed cloud service.

## Viva Notes

Use this explanation in the viva:

- `Why cloud computing?`
  The final system is deployed as a remotely accessible hosted service instead of remaining only a desktop script.
- `Why train locally?`
  The project was constrained to zero cost, so managed cloud training was avoided while keeping deployment cloud-based.
- `Why is this still cloud-native enough?`
  The inference app is stateless, containerized, and deployable without changing the API contract.
- `Why Hugging Face Spaces?`
  It provides a free managed hosting path for the deployed inference service, which satisfies the live cloud component requirement.

## Fallback Plan

If the live `Hugging Face Space` is not ready in time:

1. Run the local app and complete the prediction demo locally.
2. Show the Docker deployment files and Space README template.
3. Explain that the hosted deployment target is prepared and uses the same app and artifacts.
4. If available, show the Space repository or build logs as evidence of the cloud deployment path.

## Future Extension

If credits or institutional resources become available later, the same architecture can be extended to larger managed cloud platforms. That is optional and not required for the zero-cost version.
