param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $true)]
    [string]$Location,
    [Parameter(Mandatory = $true)]
    [string]$JobName,
    [Parameter(Mandatory = $true)]
    [string]$ServiceUrl,
    [string]$Schedule = "*/15 * * * *"
)

$healthUrl = $ServiceUrl.TrimEnd("/") + "/health"

gcloud scheduler jobs create http $JobName `
  --project $ProjectId `
  --location $Location `
  --schedule $Schedule `
  --http-method GET `
  --uri $healthUrl
