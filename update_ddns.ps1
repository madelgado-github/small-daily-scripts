$token    = "toke.with.update.zone.access.cloudflare"
$zoneId   = "your.zone.id.cloudflare"
$record   = "yoursurdomain.domain.tld"

$ip = Invoke-RestMethod -Uri "https://api.ipify.org/"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

$existing = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/zones/$zoneId/dns_records?type=A&name=$record" -Headers $headers

$body = @{ type = "A"; name = $record; content = $ip; ttl = 60; proxied = $false } | ConvertTo-Json

if ($existing.result.Count -gt 0) {
    $id = $existing.result[0].id
    Invoke-RestMethod -Method PUT -Uri "https://api.cloudflare.com/client/v4/zones/$zoneId/dns_records/$id" -Headers $headers -Body $body | Out-Null
    Write-Host "$(Get-Date) - DNS actualizado: $record -> $ip"
} else {
    Invoke-RestMethod -Method POST -Uri "https://api.cloudflare.com/client/v4/zones/$zoneId/dns_records" -Headers $headers -Body $body | Out-Null
    Write-Host "$(Get-Date) - DNS creado: $record -> $ip"
}
