param(
    [string]$ArtifactDir = "artifacts/generated",
    [int]$Port = 8000
)

$env:ARTIFACT_DIR = $ArtifactDir
uvicorn src.api.app:app --host 0.0.0.0 --port $Port
