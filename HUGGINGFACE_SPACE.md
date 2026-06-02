---
title: NimbusWatch
emoji: "🚨"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8080
pinned: false
license: mit
---

# NimbusWatch

NimbusWatch is a binary anomaly-detection web app built on `Isolation Forest` and a curated `CICIDS2017` subset.

## What this Space does

- hosts the trained inference app publicly
- loads the bundled `model.joblib` and metadata files
- predicts whether a traffic row is `benign` or `attack`
- exposes the same `FastAPI` endpoints used locally

## Included endpoints

- `GET /health`
- `GET /model-info`
- `POST /predict`
- `GET /`

## Deployment source

This Space is deployed from a dedicated Hugging Face repository, separate from the main GitHub source repo. The app is trained locally and the generated artifacts are copied into the Space before deployment.
