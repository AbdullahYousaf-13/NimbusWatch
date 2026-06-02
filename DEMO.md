# NimbusWatch Demo Script

## Goal

Demonstrate a zero-cost cloud-hosted anomaly-detection project using `Isolation Forest`, trained locally on a curated `CICIDS2017` subset and deployed as a hosted inference service.

## Demo Sequence

1. Introduce the problem:
   - network traffic can contain malicious behavior
   - manual detection is difficult
   - the project uses anomaly detection with `Isolation Forest`

2. Show local training outputs:
   - open `artifacts/generated/metrics.json`
   - mention test `precision`, `recall`, `f1`, `roc_auc`, and `pr_auc`
   - explain that the model was trained locally to keep the project zero cost

3. Show local inference:
   - run the app locally
   - open the UI
   - enter one sample row
   - show the predicted result and anomaly score

4. Show the hosted cloud component:
   - open the live `Hugging Face Space`
   - show that the same app is accessible remotely
   - mention that the service is Docker-based and hosted on a managed cloud platform

5. Explain the cloud computing angle:
   - inference is cloud-hosted
   - app is containerized
   - model artifacts are separated from training
   - the service is remotely accessible and reproducible

## Short Viva Answers

### Why is this a cloud computing project?

Because the final system is designed and deployed as a remotely accessible hosted service, not just a local script.

### Why didn't you use paid cloud training?

The project had a strict zero-cost constraint, so training was kept local while inference was still deployed in the cloud.

### Why Hugging Face Spaces?

It provides a free cloud hosting path for Dockerized inference apps, which makes it suitable for a student project with no budget.

### What cloud concepts are shown here?

- managed hosting
- containerization
- remote service access
- separation of training and serving
- reproducible deployment

## Fallback Demo

If the hosted Space is unavailable:

1. Run the local app.
2. Show the Docker deployment files.
3. Show `HUGGINGFACE_SPACE.md`.
4. Explain that the hosted deployment uses the same app and bundled artifacts.
