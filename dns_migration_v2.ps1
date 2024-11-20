# DNS Migration and Monitoring Script
$ErrorActionPreference = "Continue"  # Changed to Continue to prevent script termination

$config = @{
    Domain = "quizmo.me"
    DigitalOceanApp = "mn-dmv-quiz-ci43y.ondigitalocean.app"
    CheckInterval = 300  # 5 minutes
    MaxAttempts = 288   # 24 hours worth of 5-minute checks
    ExpectedCNAME = "mn-dmv-quiz-ci43y.ondigitalocean.app"
    LogFile = "dns_migration_v2.log"
}

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $config.LogFile -Value $logMessage
}

function Test-DNSPropagation {
    Write-Log "Checking DNS records for $($config.Domain)..."
    
    try {
        $dnsRecords = Resolve-DnsName -Name $config.Domain -ErrorAction Stop
        
        # Log all records with more detail
        $dnsRecords | ForEach-Object {
            $recordInfo = "Type=$($_.RecordType), TTL=$($_.TimeToLive)"
            if ($_.RecordType -eq 'A') {
                $recordInfo += ", IP=$($_.IPAddress)"
            }
            elseif ($_.RecordType -eq 'CNAME') {
                $recordInfo += ", Target=$($_.NameHost)"
            }
            Write-Log "Found DNS record: $recordInfo"
        }
        
        # Check for CNAME record
        $cname = $dnsRecords | Where-Object { $_.RecordType -eq 'CNAME' }
        if ($cname) {
            Write-Log "CNAME record found pointing to: $($cname.NameHost)"
            return $cname.NameHost -eq $config.ExpectedCNAME
        }
        
        # Check for A records
        $aRecords = $dnsRecords | Where-Object { $_.RecordType -eq 'A' }
        if ($aRecords) {
            Write-Log "Found A records: $($aRecords.IPAddress -join ', ')"
        }
        
        Write-Log "No CNAME record found - DNS migration not complete"
        return $false
    }
    catch {
        Write-Log "Error checking DNS: $_"
        return $false
    }
}

function Test-SiteAccessibility {
    param($Url)
    
    Write-Log "Testing accessibility of https://$Url"
    
    try {
        $response = Invoke-WebRequest -Uri "https://$Url" -UseBasicParsing -TimeoutSec 30
        Write-Log "Site returned status code: $($response.StatusCode)"
        Write-Log "Response headers: $($response.Headers | ConvertTo-Json)"
        return $response.StatusCode -eq 200
    }
    catch {
        $errorDetails = if ($_.Exception.Response) {
            "Status: $($_.Exception.Response.StatusCode.value__), StatusDescription: $($_.Exception.Response.StatusDescription)"
        } else {
            $_.Exception.Message
        }
        Write-Log "Error accessing site: $errorDetails"
        return $false
    }
}

# Main monitoring loop
Write-Log "Starting DNS migration monitoring (v2)..."
Write-Log "Will check every $($config.CheckInterval/60) minutes for up to 24 hours"

for ($attempt = 1; $attempt -le $config.MaxAttempts; $attempt++) {
    Write-Log "`n=== Check Attempt $attempt of $($config.MaxAttempts) ==="
    Write-Log "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    
    # Check DNS propagation
    $dnsPropagated = Test-DNSPropagation
    
    # Check site accessibility
    $doAppAccessible = Test-SiteAccessibility -Url $config.DigitalOceanApp
    $customDomainAccessible = Test-SiteAccessibility -Url $config.Domain
    
    # Status summary
    Write-Log "`nStatus Summary:"
    Write-Log "- DNS Propagation: $(if ($dnsPropagated) { 'SUCCESS' } else { 'PENDING' })"
    Write-Log "- DigitalOcean App: $(if ($doAppAccessible) { 'ACCESSIBLE' } else { 'NOT ACCESSIBLE' })"
    Write-Log "- Custom Domain: $(if ($customDomainAccessible) { 'ACCESSIBLE' } else { 'NOT ACCESSIBLE' })"
    
    if ($dnsPropagated -and $doAppAccessible -and $customDomainAccessible) {
        Write-Log "`nSUCCESS: Migration completed successfully!"
        exit 0
    }
    
    if ($attempt -lt $config.MaxAttempts) {
        Write-Log "Waiting $($config.CheckInterval/60) minutes before next check..."
        Start-Sleep -Seconds $config.CheckInterval
    }
}

Write-Log "`nWARNING: Migration not completed after 24 hours"
exit 1
