param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $true)]
    [string]$Region,
    [Parameter(Mandatory = $true)]
    [string]$StagingBucket,
    [Parameter(Mandatory = $true)]
    [string]$ArtifactBucketUri,
    [Parameter(Mandatory = $true)]
    [string]$TrainingImageUri,
    [Parameter(Mandatory = $true)]
    [string]$CsvGcsPaths
)

$displayName = "nimbuswatch-train-" + (Get-Date -Format "yyyyMMdd-HHmmss")

gcloud ai custom-jobs create `
  --project $ProjectId `
  --region $Region `
  --display-name $displayName `
  --staging-bucket $StagingBucket `
  --worker-pool-spec "machine-type=e2-standard-4,replica-count=1,container-image-uri=$TrainingImageUri" `
  --args="--csv-paths=$CsvGcsPaths,--artifact-gcs-uri=$ArtifactBucketUri"
