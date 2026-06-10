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

NimbusWatch is the secondary `Hugging Face Spaces` deployment for the NimbusWatch malicious-traffic detection project.

## Role of This Space

This Space is not the primary production architecture. It is the:

- public demo endpoint
- secondary cloud deployment
- backup hosting path for the same inference contract

Primary training and artifact management are designed around `Google Cloud`.

## What This Space Hosts

- the same `FastAPI` inference app used in the main repo
- the same trained classifier artifacts exported from the primary workflow
- the same HTTP interface used locally and on `Cloud Run`

## Endpoints

- `GET /health`
- `GET /model-info`
- `POST /predict`
- `GET /`

## Deployment Workflow

Deploy this Space from a dedicated `Hugging Face` repo, separate from the main source repository.

Use the main repo script:

```powershell
.\scripts\sync_huggingface_bundle.ps1 -SpaceRepoPath "D:\repos\nimbuswatch-space"
```

That script copies:

- `Dockerfile.serve` as `Dockerfile`
- `requirements.txt`
- `src/`
- `artifacts/generated/`
- this file as the Space `README.md`

## Notes

- this Space uses bundled local artifacts instead of pulling directly from `GCS`
- the backup flow is manual or semi-manual
- it is intended for demo continuity and cross-cloud portability, not automatic failover
