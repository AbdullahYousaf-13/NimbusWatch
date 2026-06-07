param(
    [Parameter(Mandatory = $true)]
    [string]$SpaceRepoPath,
    [string]$ArtifactDir = "artifacts/generated"
)

$resolvedSpaceRepo = (Resolve-Path $SpaceRepoPath).Path
$resolvedArtifactDir = (Resolve-Path $ArtifactDir).Path

if (-not (Test-Path $resolvedSpaceRepo)) {
    throw "Space repo path not found: $SpaceRepoPath"
}

New-Item -ItemType Directory -Force -Path (Join-Path $resolvedSpaceRepo "artifacts") | Out-Null

Copy-Item -Path "Dockerfile.serve" -Destination (Join-Path $resolvedSpaceRepo "Dockerfile") -Force
Copy-Item -Path "requirements.txt" -Destination $resolvedSpaceRepo -Force

if (Test-Path (Join-Path $resolvedSpaceRepo "src")) {
    Remove-Item -Recurse -Force (Join-Path $resolvedSpaceRepo "src")
}
Copy-Item -Recurse -Force -Path "src" -Destination $resolvedSpaceRepo

if (Test-Path (Join-Path $resolvedSpaceRepo "artifacts\\generated")) {
    Remove-Item -Recurse -Force (Join-Path $resolvedSpaceRepo "artifacts\\generated")
}
Copy-Item -Recurse -Force -Path $resolvedArtifactDir -Destination (Join-Path $resolvedSpaceRepo "artifacts\\generated")

Copy-Item -Path "HUGGINGFACE_SPACE.md" -Destination (Join-Path $resolvedSpaceRepo "README.md") -Force

Write-Host "Hugging Face bundle synced to $resolvedSpaceRepo"
