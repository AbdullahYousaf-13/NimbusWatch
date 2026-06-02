# NimbusWatch

NimbusWatch is a cloud-hosted binary anomaly-detection project built on `Isolation Forest` and a curated `CICIDS2017` subset. It keeps the machine-learning model aligned with the approved proposal while shifting deployment to `Google Cloud` for a stronger cloud-computing demonstration.

## Architecture

- `Vertex AI Custom Job` runs containerized training in the cloud.
- `Google Cloud Storage` stores dataset copies and exported artifacts.
- `Artifact Registry` stores the training and serving images.
- `Cloud Run` serves a `FastAPI` inference API and a minimal HTML demo page.

Artifacts exported after training:

- `model.joblib`
- `feature_schema.json`
- `metrics.json`
- `training_summary.json`

## Local Setup

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Train Locally

First build a curated subset from one or more CICIDS2017 CSVs.

```powershell
python -m src.data.build_subset --csv-paths "D:\data\Tuesday-WorkingHours.pcap_ISCX.csv,D:\data\Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv,D:\data\Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" --output-path "data\processed\cicids2017_curated.csv"
```

Then train on the curated file:

```powershell
.\scripts\train_local.ps1 -CsvPaths "data\processed\cicids2017_curated.csv"
```

This writes artifacts to `artifacts/generated`.

## Run Locally

```powershell
.\scripts\serve_local.ps1 -ArtifactDir "artifacts/generated" -Port 8000
```

Open `http://localhost:8000`.

## GCP Deployment Flow

### 1. Create buckets and Artifact Registry

- Create a GCS bucket for raw dataset copies and training artifacts.
- Create an Artifact Registry Docker repository, for example `nimbuswatch`.

### 2. Build images

```powershell
.\scripts\build_images.ps1 -ProjectId "<gcp-project>" -Region "us-central1" -Repository "nimbuswatch"
```

### 3. Upload curated dataset to GCS

Example target:

- `gs://<bucket>/datasets/cicids2017/subset1.csv`
- `gs://<bucket>/datasets/cicids2017/subset2.csv`

### 4. Submit Vertex AI training

```powershell
.\scripts\submit_vertex_job.ps1 `
  -ProjectId "<gcp-project>" `
  -Region "us-central1" `
  -StagingBucket "gs://<bucket>/staging" `
  -ArtifactBucketUri "gs://<bucket>/artifacts/latest" `
  -TrainingImageUri "us-central1-docker.pkg.dev/<gcp-project>/nimbuswatch/nimbuswatch-train:latest" `
  -CsvGcsPaths "gs://<bucket>/datasets/cicids2017/subset1.csv,gs://<bucket>/datasets/cicids2017/subset2.csv"
```

### 5. Deploy Cloud Run

```powershell
.\scripts\deploy_cloud_run.ps1 `
  -ProjectId "<gcp-project>" `
  -Region "us-central1" `
  -ServiceName "nimbuswatch-api" `
  -ImageUri "us-central1-docker.pkg.dev/<gcp-project>/nimbuswatch/nimbuswatch-serve:latest" `
  -ArtifactBucketUri "gs://<bucket>/artifacts/latest"
```

The service loads `model.joblib`, `feature_schema.json`, `metrics.json`, and `training_summary.json` from GCS on startup.

## API

- `GET /health`
- `GET /model-info`
- `POST /predict`
- `GET /`

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

## Cloud Computing Justification

This qualifies as a cloud computing project because:

- training runs on a managed cloud service instead of only on a local laptop
- inference is deployed as a stateless cloud service
- model artifacts are stored in cloud object storage
- compute and storage are separated
- containers make training and serving reproducible
- Cloud Run provides low-cost managed scaling for the deployed service
