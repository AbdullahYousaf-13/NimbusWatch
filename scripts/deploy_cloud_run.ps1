param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $true)]
    [string]$Region,
    [Parameter(Mandatory = $true)]
    [string]$ServiceName,
    [Parameter(Mandatory = $true)]
    [string]$ImageUri,
    [Parameter(Mandatory = $true)]
    [string]$ArtifactBucketUri
)

gcloud run deploy $ServiceName `
  --project $ProjectId `
  --region $Region `
  --image $ImageUri `
  --platform managed `
  --allow-unauthenticated `
  --memory 1Gi `
  --cpu 1 `
  --set-env-vars "ARTIFACT_GCS_URI=$ArtifactBucketUri"
