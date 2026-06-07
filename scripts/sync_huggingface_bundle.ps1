param(
    [Parameter(Mandatory = $true)]
    [string]$SpaceRepoPath,
    [string]$ArtifactDir = "artifacts/generated"
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptRoot "..")).Path
$resolvedSpaceRepo = (Resolve-Path $SpaceRepoPath).Path
$resolvedArtifactDir = (Resolve-Path (Join-Path $repoRoot $ArtifactDir)).Path

if (-not (Test-Path $resolvedSpaceRepo)) {
    throw "Space repo path not found: $SpaceRepoPath"
}

if ($resolvedSpaceRepo -eq $repoRoot) {
    throw "Space repo path cannot be the main NimbusWatch repo. Point this to a separate cloned Hugging Face Space repository."
}

New-Item -ItemType Directory -Force -Path (Join-Path $resolvedSpaceRepo "artifacts") | Out-Null

Copy-Item -Path (Join-Path $repoRoot "Dockerfile.serve") -Destination (Join-Path $resolvedSpaceRepo "Dockerfile") -Force
Copy-Item -Path (Join-Path $repoRoot "requirements.txt") -Destination $resolvedSpaceRepo -Force

if (Test-Path (Join-Path $resolvedSpaceRepo "src")) {
    Remove-Item -Recurse -Force (Join-Path $resolvedSpaceRepo "src")
}
Copy-Item -Recurse -Force -Path (Join-Path $repoRoot "src") -Destination $resolvedSpaceRepo

if (Test-Path (Join-Path $resolvedSpaceRepo "artifacts\\generated")) {
    Remove-Item -Recurse -Force (Join-Path $resolvedSpaceRepo "artifacts\\generated")
}
Copy-Item -Recurse -Force -Path $resolvedArtifactDir -Destination (Join-Path $resolvedSpaceRepo "artifacts\\generated")

Copy-Item -Path (Join-Path $repoRoot "HUGGINGFACE_SPACE.md") -Destination (Join-Path $resolvedSpaceRepo "README.md") -Force

Write-Host "Hugging Face bundle synced to $resolvedSpaceRepo"
