# Rollback Module
using module .\Logging.psm1

function Save-RollbackState {
    param(
        [string]$Stage,
        [hashtable]$State
    )
    
    $rollbackFile = Join-Path $PSScriptRoot "../../state/rollback_state.json"
    $rollbackState = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Stage = $Stage
        State = $State
    }
    
    $rollbackState | ConvertTo-Json | Out-File $rollbackFile
    Write-Log -Level Info -Message "Rollback state saved for stage: $Stage"
}

function Get-RollbackState {
    $rollbackFile = Join-Path $PSScriptRoot "../../state/rollback_state.json"
    if (Test-Path $rollbackFile) {
        $rollbackState = Get-Content $rollbackFile | ConvertFrom-Json
        return $rollbackState
    }
    return $null
}

function Remove-DigitalOceanApp {
    param(
        [string]$AppId
    )
    try {
        Write-Log -Level Info -Message "Removing DigitalOcean app: $AppId"
        & doctl apps delete $AppId --force
        return $true
    }
    catch {
        Write-Log -Level Error -Message "Failed to remove DigitalOcean app: $_"
        return $false
    }
}

function Remove-DigitalOceanDatabase {
    param(
        [string]$DbName
    )
    try {
        Write-Log -Level Info -Message "Removing DigitalOcean database: $DbName"
        $dbId = & doctl databases list --format ID,Name --no-header | Where-Object { $_ -match $DbName } | ForEach-Object { ($_ -split '\s+')[0] }
        if ($dbId) {
            & doctl databases delete $dbId --force
            return $true
        }
        return $false
    }
    catch {
        Write-Log -Level Error -Message "Failed to remove DigitalOcean database: $_"
        return $false
    }
}

function Remove-DNSRecords {
    param(
        [string]$Domain
    )
    try {
        Write-Log -Level Info -Message "Removing DNS records for domain: $Domain"
        $records = & doctl compute domain records list $Domain --format ID --no-header
        foreach ($record in $records) {
            & doctl compute domain records delete $Domain $record --force
        }
        return $true
    }
    catch {
        Write-Log -Level Error -Message "Failed to remove DNS records: $_"
        return $false
    }
}

function Invoke-Rollback {
    param(
        [string]$FailedStage,
        [hashtable]$DeploymentState
    )
    
    Write-Log -Level Warning -Message "Starting rollback process due to failure in stage: $FailedStage"
    
    # Save rollback state for debugging
    Save-RollbackState -Stage $FailedStage -State $DeploymentState
    
    switch ($FailedStage) {
        'App Creation' {
            if ($DeploymentState.AppId) {
                Remove-DigitalOceanApp -AppId $DeploymentState.AppId
            }
        }
        'Database Setup' {
            if ($DeploymentState.DbName) {
                Remove-DigitalOceanDatabase -DbName $DeploymentState.DbName
            }
            if ($DeploymentState.AppId) {
                Remove-DigitalOceanApp -AppId $DeploymentState.AppId
            }
        }
        'Domain Configuration' {
            if ($DeploymentState.Domain) {
                Remove-DNSRecords -Domain $DeploymentState.Domain
            }
            if ($DeploymentState.DbName) {
                Remove-DigitalOceanDatabase -DbName $DeploymentState.DbName
            }
            if ($DeploymentState.AppId) {
                Remove-DigitalOceanApp -AppId $DeploymentState.AppId
            }
        }
        default {
            Write-Log -Level Warning -Message "No specific rollback actions for stage: $FailedStage"
        }
    }
    
    # Cleanup local files
    $filesToClean = @(
        "app.yaml",
        "rollback_state.json",
        "deployment_state.json",
        ".env.prod"
    )
    
    foreach ($file in $filesToClean) {
        $filePath = Join-Path $PSScriptRoot "../../$file"
        if (Test-Path $filePath) {
            Remove-Item $filePath -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Log -Level Info -Message "Rollback completed for stage: $FailedStage"
    Write-Log -Level Info -Message "Please check the DigitalOcean console to verify all resources have been properly removed"
}

Export-ModuleMember -Function Save-RollbackState, Get-RollbackState, Remove-DigitalOceanApp, Remove-DigitalOceanDatabase, Remove-DNSRecords, Invoke-Rollback
