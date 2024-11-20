# DigitalOcean Module
using module .\Logging.psm1
using module .\Config.psm1

function Configure-Domain {
    param(
        [string]$AppId,
        [string]$DomainName
    )
    
    Write-Log -Level Info -Message "Configuring domain: $DomainName"
    
    # Add domain to DigitalOcean
    & doctl compute domain create $DomainName
    
    # Get app URL
    $appUrl = & doctl apps get $AppId --format DefaultIngress --no-header
    
    # Create DNS records
    $records = @(
        @{type = "A"; name = "@"; data = $appUrl},
        @{type = "CNAME"; name = "www"; data = "$DomainName."}
    )
    
    foreach ($record in $records) {
        & doctl compute domain records create $DomainName `
            --record-type $record.type `
            --record-name $record.name `
            --record-data $record.data
    }
}

function Configure-Monitoring {
    param(
        [string]$AppId
    )
    
    Write-Log -Level Info -Message "Setting up monitoring for app: $AppId"
    
    $alerts = @(
        @{
            name = "High CPU Usage"
            type = "cpu"
            threshold = 80
        },
        @{
            name = "High Memory Usage"
            type = "memory"
            threshold = 80
        },
        @{
            name = "High Disk Usage"
            type = "disk"
            threshold = 80
        }
    )
    
    foreach ($alert in $alerts) {
        & doctl apps alert create $AppId `
            --name $alert.name `
            --type $alert.type `
            --threshold $alert.threshold
    }
}

function Configure-Backups {
    param(
        [string]$AppId,
        [string]$DbName
    )
    
    Write-Log -Level Info -Message "Configuring backups for database: $DbName"
    
    $backupConfig = @{
        schedule_hour = 1
        schedule_minute = 0
        retention_period_days = 7
    }
    
    & doctl databases backup-schedule update $DbName `
        --hour $backupConfig.schedule_hour `
        --minute $backupConfig.schedule_minute `
        --retention-period $backupConfig.retention_period_days
}

function Configure-ErrorTracking {
    param(
        [string]$AppId
    )
    
    Write-Log -Level Info -Message "Setting up error tracking for app: $AppId"
    
    # Configure Sentry integration
    $sentryConfig = @{
        dsn = "https://sentry.io/api/v1/projects/$AppId"
        environment = "production"
        traces_sample_rate = 1.0
    }
    
    # Update app spec with Sentry configuration
    & doctl apps update $AppId --spec app.yaml
}

function Test-Deployment {
    param(
        [string]$AppUrl
    )
    
    Write-Log -Level Info -Message "Testing deployment at: $AppUrl"
    
    try {
        $response = Invoke-WebRequest -Uri $AppUrl -UseBasicParsing
        return $response.StatusCode -eq 200
    }
    catch {
        Write-Log -Level Error -Message "Deployment test failed: $_"
        return $false
    }
}

Export-ModuleMember -Function Configure-Domain, Configure-Monitoring, Configure-Backups, Configure-ErrorTracking, Test-Deployment
