$domains = @(
    "mn-dmv-quiz-ci43y.ondigitalocean.app",
    "quizmo.me"
)

$maxAttempts = 24  # Check for 24 hours
$intervalMinutes = 30  # Check every 30 minutes

function Test-Domain {
    param (
        [string]$domain
    )
    
    Write-Host "`nChecking $domain..."
    
    # Check DNS resolution
    try {
        $dnsResult = Resolve-DnsName -Name $domain -ErrorAction Stop
        Write-Host "DNS Resolution: SUCCESS"
        Write-Host "IP Address(es):"
        $dnsResult | Where-Object { $_.Type -eq 'A' -or $_.Type -eq 'CNAME' } | ForEach-Object {
            Write-Host "  $($_.Type): $($_.NameHost)"
        }
    }
    catch {
        Write-Host "DNS Resolution: FAILED"
        Write-Host "Error: $_"
        return $false
    }
    
    # Check HTTP accessibility
    try {
        $response = Invoke-WebRequest -Uri "https://$domain" -UseBasicParsing
        Write-Host "HTTP Status: $($response.StatusCode)"
        if ($response.StatusCode -eq 200) {
            Write-Host "Site Accessibility: SUCCESS"
            return $true
        }
    }
    catch {
        Write-Host "Site Accessibility: FAILED"
        Write-Host "Error: $_"
        return $false
    }
    
    return $false
}

Write-Host "Starting DNS and site accessibility monitoring..."
Write-Host "Will check every $intervalMinutes minutes for up to $(($maxAttempts * $intervalMinutes) / 60) hours"

for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    Write-Host "`n=== Check Attempt $attempt of $maxAttempts ==="
    Write-Host "Time: $(Get-Date)"
    
    $allSuccess = $true
    foreach ($domain in $domains) {
        $success = Test-Domain -domain $domain
        if (-not $success) {
            $allSuccess = $false
        }
    }
    
    if ($allSuccess) {
        Write-Host "`nSUCCESS: All domains are properly configured and accessible!"
        exit 0
    }
    
    if ($attempt -lt $maxAttempts) {
        Write-Host "`nWaiting $intervalMinutes minutes before next check..."
        Start-Sleep -Seconds ($intervalMinutes * 60)
    }
}

Write-Host "`nWARNING: Not all domains are properly configured after $(($maxAttempts * $intervalMinutes) / 60) hours"
exit 1
