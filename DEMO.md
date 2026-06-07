# NimbusWatch Demo Script

## Goal

Demonstrate NimbusWatch as a hybrid-cloud anomaly-detection system with:

- improved `IsolationForest` prediction quality
- primary deployment on `Google Cloud`
- secondary deployment on `Hugging Face Spaces`

## Demo Sequence

1. Introduce the problem
   - network traffic contains benign and malicious behavior
   - manual inspection is slow and inconsistent
   - NimbusWatch detects anomalous traffic with `IsolationForest`

2. Show the architecture
   - explain that `Vertex AI` is used for training
   - explain that `Cloud Storage` stores versioned artifacts
   - explain that `Cloud Run` serves the stateless API
   - explain that `Hugging Face` is the secondary hosted deployment

3. Show the improved training outputs
   - open `artifacts/generated/metrics.json`
   - mention validation/test `precision`, `recall`, `f1`, `roc_auc`, `pr_auc`
   - mention `operational` metrics such as latency and artifact size
   - open `artifacts/generated/training_summary.json`
   - mention feature selection, preprocessor choice, and top experiments

4. Show local inference
   - run `.\scripts\serve_local.ps1`
   - open the UI
   - submit one sample row
   - explain anomaly score and threshold

5. Show the primary cloud path
   - show `scripts\submit_vertex_job.ps1`
   - show `scripts\deploy_cloud_run.ps1`
   - if deployed, open the live `Cloud Run` URL and check `/health`

6. Show the secondary cloud path
   - show `scripts\sync_huggingface_bundle.ps1`
   - open the `Hugging Face Space`
   - explain that the same artifacts and API contract are reused there

7. Explain the advanced-cloud concepts
   - elasticity through `Cloud Run`
   - cost control through serverless and scheduled retraining
   - support services through logging and monitoring
   - hybrid-cloud integration through shared artifacts across two platforms

## Short Viva Answers

### Why is this a cloud computing project?

Because NimbusWatch is deployed as a remotely accessible managed service, not only as a local ML script.

### Why use Google Cloud as the primary architecture?

Because it supports managed training, object storage, serverless inference, and operational support services in one workflow.

### Why keep Hugging Face Spaces?

It provides a second cloud deployment path for demo continuity and cross-cloud integration.

### How did you improve prediction quality?

By adding feature selection, outlier-aware preprocessing, broader hyperparameter tuning, and balanced-threshold selection while keeping `IsolationForest` as the deployed model.

### Why not deploy on raw VMs?

Serverless inference reduces idle cost, simplifies scaling, and avoids manual VM operations for a student project.

## Fallback Demo

If live cloud access is unavailable:

1. run the app locally
2. show `metrics.json` and `training_summary.json`
3. show the GCP deployment scripts
4. show the `Hugging Face` packaging script
5. explain that multi-cloud failover is manual or semi-manual in the current version
