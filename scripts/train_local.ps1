param(
    [Parameter(Mandatory = $true)]
    [string]$CsvPaths,
    [string]$OutputDir = "artifacts/generated",
    [string]$ArtifactGcsUri = "",
    [int]$MaxBenignTrainRows = 120000
)

python -m src.models.train --csv-paths $CsvPaths --output-dir $OutputDir --artifact-gcs-uri $ArtifactGcsUri --max-benign-train-rows $MaxBenignTrainRows
