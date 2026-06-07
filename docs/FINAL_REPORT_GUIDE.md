# NimbusWatch Final Report Guide

## Summary

NimbusWatch is a hybrid-cloud anomaly-detection system for suspicious network traffic. It uses `IsolationForest` on a curated `CICIDS2017` subset and exposes predictions through a stateless `FastAPI` service.

Recommended report framing:

- **Primary cloud:** Google Cloud
- **Secondary cloud:** Hugging Face Spaces
- **Objective:** improve anomaly detection while keeping deployment simple, elastic, and cost-aware

## Designing Phase, Options, and Tradeoffs

Use these three options in the report:

1. Local training + Hugging Face inference
2. Google Cloud only
3. Hybrid Google Cloud + Hugging Face

State that option 3 was selected because it gives:

- managed training and artifact storage
- serverless inference
- cross-cloud portability
- better coverage of cloud-architecture concepts

## Economic Structure

Break cost analysis into these components:

- `Vertex AI` training job cost per run
- `Cloud Storage` cost for artifacts and curated data
- `Cloud Run` cost based on requests, CPU, and memory use
- `Cloud Logging/Monitoring` operational overhead
- `Hugging Face Space` free or low-cost backup hosting

Use three scenarios:

1. demo usage
2. class presentation usage
3. moderate production usage

Cost-saving decisions:

- do not retrain continuously
- store artifacts instead of keeping a training VM active
- use serverless inference instead of always-on compute
- reduce data volume through curation and feature selection

## Data Handling, Scheduling, and Technical Flow

### Data handling

- ingest selected `CICIDS2017` CSV files
- remove leakage columns
- clean invalid numeric values
- split into train, validation, and test
- export reusable model artifacts

### Optimization

- feature selection removes weak and redundant features
- preprocessing uses clipping, log transforms, and scaler comparison
- threshold selection optimizes balanced `F1`

### Scheduling

- use `Cloud Scheduler` for health probes
- describe retraining as weekly or data-triggered
- keep the API stable while refreshing artifacts

### Virtual machines

- explain that direct VMs were not chosen as the primary solution
- justify serverless and managed services for lower idle cost and easier scaling

## Support Services, Elasticity, and Scalability

- `Cloud Run` handles traffic scaling
- `Cloud Storage` scales independently of inference
- `Cloud Monitoring` and `Cloud Logging` support health and debugging
- training and inference are decoupled, so user traffic does not block model updates

## System Integration

Describe the cross-cloud integration like this:

1. train and store artifacts in Google Cloud
2. serve the main API from `Cloud Run`
3. copy the same artifacts and app bundle into the `Hugging Face` Space
4. expose the same API behavior on both platforms

Do not claim automatic failover unless it is actually built and tested.

## Technical, Implementation, and Deployment Phases

### Technical phase

- choose `IsolationForest`
- define features and thresholding strategy
- define artifact storage and deployment topology

### Implementation phase

- dataset curation
- preprocessing
- model training and tuning
- artifact loading from local storage or `GCS`
- API and UI
- tests

### Deployment phase

- build container images
- deploy inference to `Cloud Run`
- configure artifact bucket
- package secondary deployment for `Hugging Face`
- verify `/health` and `/predict`

## Research Component

Use this research question:

`How can NimbusWatch improve anomaly-detection quality while preserving low deployment complexity and cloud efficiency?`

Experiment dimensions already implemented in the repo:

- scaler choice
- clipping configuration
- threshold optimization
- feature reduction
- broader `IsolationForest` tuning

Compare experiments using:

- `precision`
- `recall`
- `F1`
- `ROC-AUC`
- `PR-AUC`
- training cost/time
- single-row inference latency
- artifact size

## Files to Cite

- [README.md](/d:/Abd/Programming/NimbusWatch/README.md)
- [docs/ARCHITECTURE.md](/d:/Abd/Programming/NimbusWatch/docs/ARCHITECTURE.md)
- [src/models/train.py](/d:/Abd/Programming/NimbusWatch/src/models/train.py)
- [scripts/deploy_cloud_run.ps1](/d:/Abd/Programming/NimbusWatch/scripts/deploy_cloud_run.ps1)
- [scripts/submit_vertex_job.ps1](/d:/Abd/Programming/NimbusWatch/scripts/submit_vertex_job.ps1)
