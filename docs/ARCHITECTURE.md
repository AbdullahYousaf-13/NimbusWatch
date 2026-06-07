# NimbusWatch Architecture

## Summary

NimbusWatch uses a hybrid-cloud design:

- **Primary cloud:** Google Cloud
- **Secondary cloud:** Hugging Face Spaces
- **Workload split:** managed training, artifact storage, stateless inference, and backup/public demo hosting

This architecture was chosen to satisfy advanced cloud-computing requirements without changing the public prediction API.

## Design Options and Tradeoffs

### Option A: Local training + Hugging Face inference

- lowest cost
- easiest to demo
- weak coverage for managed training, elasticity, and support services

### Option B: Google Cloud only

- strongest production-style design
- clean managed-service story
- no cross-cloud integration example

### Option C: Hybrid Google Cloud + Hugging Face

- recommended architecture
- Google Cloud is the training and artifact source of truth
- Hugging Face acts as a secondary hosted deployment
- stronger for viva questions on system integration, portability, and cloud tradeoffs

## Final System Flow

1. Curate the `CICIDS2017` dataset locally or from cloud-staged data.
2. Train `IsolationForest` with tuning on `Vertex AI` or locally.
3. Store artifacts in `Cloud Storage`.
4. Deploy the inference container to `Cloud Run`.
5. Configure the service to fetch artifacts through `ARTIFACT_GCS_URI`.
6. Package the same application and artifacts for `Hugging Face Spaces`.
7. Use `Cloud Scheduler` to probe `/health`.

## Data Handling and Optimization

- identifier and leakage columns are dropped before training
- invalid `inf` values are converted to `NaN`
- missing values are imputed using medians
- extreme values are clipped using percentile bounds
- skewed non-negative features are log-transformed
- low-variance and highly correlated features are removed using training-only statistics
- model artifacts are stored separately from runtime compute

## Elasticity, Support Services, and VMs

- `Cloud Run` provides request-driven scaling
- `Cloud Storage` provides durable artifact storage
- `Cloud Logging` and `Cloud Monitoring` provide observability
- `IAM` secures access between services and storage
- raw VMs are not the preferred deployment path
- managed services still run on cloud-managed compute, but VM operations are abstracted away

## Multi-Cloud Integration

- Google Cloud is the primary environment for training and artifact management
- Hugging Face uses the same trained artifacts and the same API interface
- failover is manual or semi-manual, not automatic
- this keeps claims technically accurate while still demonstrating one cloud connecting to another
