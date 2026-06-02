param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $true)]
    [string]$Region,
    [string]$Repository = "nimbuswatch"
)

$trainImage = "$Region-docker.pkg.dev/$ProjectId/$Repository/nimbuswatch-train:latest"
$serveImage = "$Region-docker.pkg.dev/$ProjectId/$Repository/nimbuswatch-serve:latest"

gcloud builds submit --project $ProjectId --tag $trainImage --file Dockerfile.train .
gcloud builds submit --project $ProjectId --tag $serveImage --file Dockerfile.serve .

Write-Host "Training image: $trainImage"
Write-Host "Serving image:  $serveImage"
