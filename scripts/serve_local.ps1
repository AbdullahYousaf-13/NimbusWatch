param(
    [string]$ArtifactDir = "artifacts/generated",
    [string]$ArtifactGcsUri = "",
    [int]$Port = 8000
)

$env:ARTIFACT_DIR = $ArtifactDir
if ($ArtifactGcsUri) {
    $env:ARTIFACT_GCS_URI = $ArtifactGcsUri
}
uvicorn src.api.app:app --host 0.0.0.0 --port $Port
