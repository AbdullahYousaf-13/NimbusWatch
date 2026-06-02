param(
    [Parameter(Mandatory = $true)]
    [string]$CsvPaths,
    [string]$OutputDir = "artifacts/generated"
)

python -m src.models.train --csv-paths $CsvPaths --output-dir $OutputDir
