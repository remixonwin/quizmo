# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Requesting administrator privileges..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Get the directory of this script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$deployScript = Join-Path $scriptPath "deploy_to_do.ps1"

# Run the main deployment script
Write-Host "Running deployment script with administrator privileges..."
& $deployScript

# Main Deployment Script
using module .\scripts\modules\Config.psm1
using module .\scripts\modules\Logging.psm1
using module .\scripts\modules\Installation.psm1
using module .\scripts\modules\DigitalOcean.psm1
using module .\scripts\modules\Rollback.psm1

# Create necessary directories
$stateDir = Join-Path $PSScriptRoot "state"
if (-not (Test-Path $stateDir)) {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
}

# Main deployment script
try {
    Write-Log -Level Info -Message "Starting Minnesota DMV Quiz App deployment"
    Write-Log -Level Info -Message "================================================="

    # Step 1: Install required tools
    try {
        Write-Log -Level Info -Message "Step 1: Installing required tools..."
        Install-Chocolatey
        Install-RequiredTools
        Install-DOCTL
    }
    catch {
        Handle-Error -Stage 'Tool Installation' -ErrorRecord $_
        Invoke-Rollback -FailedStage 'Tool Installation' -DeploymentState @{}
        exit 1
    }

    # Step 2: Generate production environment variables
    try {
        Write-Log -Level Info -Message "Step 2: Setting up production environment..."
        $config = Get-DeploymentConfig
        $dbName = "mnquiz_prod_db"
        $dbUser = "mnquiz_user"
        $dbPassword = Get-SecureRandomString 32
        $allowedHosts = "$($config.DOMAIN_NAME),.digitalocean.app"
        
        # Create production environment file
        $envContent = @"
DEBUG=False
SECRET_KEY=$dbPassword
ALLOWED_HOSTS=$allowedHosts
DB_NAME=$dbName
DB_USER=$dbUser
DB_PASSWORD=$dbPassword
"@
        $envContent | Out-File -FilePath ".env.prod" -Encoding UTF8
        
        Write-Log -Level Info -Message "Production environment configured"
    }
    catch {
        Handle-Error -Stage 'Environment Setup' -ErrorRecord $_
        Invoke-Rollback -FailedStage 'Environment Setup' -DeploymentState @{}
        exit 1
    }

    # Step 3: Create and deploy the app
    try {
        Write-Log -Level Info -Message "Step 3: Creating and deploying the application..."
        $config = Get-DeploymentConfig
        $appCreation = & doctl apps create --spec app.yaml --format ID --no-header
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create DigitalOcean app"
        }
        $appId = $appCreation.Trim()
        Write-Log -Level Info -Message "App ID: $appId"
    }
    catch {
        Handle-Error -Stage 'App Creation' -ErrorRecord $_
        Invoke-Rollback -FailedStage 'App Creation' -DeploymentState @{
            AppId = $appId
        }
        exit 1
    }

    # Step 4: Configure domain and SSL
    try {
        Write-Log -Level Info -Message "Step 4: Configuring domain and SSL..."
        Configure-Domain -AppId $appId -DomainName $config.DOMAIN_NAME
    }
    catch {
        Handle-Error -Stage 'Domain Configuration' -ErrorRecord $_
        Invoke-Rollback -FailedStage 'Domain Configuration' -DeploymentState @{
            AppId = $appId
            Domain = $config.DOMAIN_NAME
            DbName = $dbName
        }
        exit 1
    }

    # Step 5: Set up monitoring and alerts
    try {
        Write-Log -Level Info -Message "Step 5: Setting up monitoring and alerts..."
        Configure-Monitoring -AppId $appId
    }
    catch {
        Handle-Error -Stage 'Monitoring Setup' -ErrorRecord $_
        Write-Log -Level Warning -Message "Monitoring setup incomplete, continuing deployment..."
    }

    # Step 6: Configure backups
    try {
        Write-Log -Level Info -Message "Step 6: Setting up automated backups..."
        Configure-Backups -AppId $appId -DbName $dbName
    }
    catch {
        Handle-Error -Stage 'Backup Configuration' -ErrorRecord $_
        Write-Log -Level Warning -Message "Backup configuration incomplete, continuing deployment..."
    }

    # Step 7: Set up error tracking
    try {
        Write-Log -Level Info -Message "Step 7: Setting up error tracking..."
        Configure-ErrorTracking -AppId $appId
    }
    catch {
        Handle-Error -Stage 'Error Tracking Setup' -ErrorRecord $_
        Write-Log -Level Warning -Message "Error tracking setup incomplete, continuing deployment..."
    }

    # Step 8: Test deployment
    try {
        Write-Log -Level Info -Message "Step 8: Testing deployment..."
        $appUrl = & doctl apps get $appId --format DefaultIngress --no-header
        $testResult = Test-Deployment -AppUrl $appUrl
        
        if ($testResult) {
            Write-Log -Level Info -Message "Deployment test successful!"
        }
        else {
            Write-Log -Level Warning -Message "Deployment test failed, but deployment may still be in progress"
        }
    }
    catch {
        Handle-Error -Stage 'Deployment Testing' -ErrorRecord $_
        Write-Log -Level Warning -Message "Could not test deployment, manual verification required"
    }

    Write-Log -Level Info -Message "`nDeployment Complete!"
    Write-Log -Level Info -Message "================================"
    Write-Log -Level Info -Message "Your application is being deployed to: https://$($config.DOMAIN_NAME)"
    Write-Log -Level Info -Message "`nPlease note the following:"
    Write-Log -Level Info -Message "1. Initial build and deployment may take 5-10 minutes"
    Write-Log -Level Info -Message "2. Database migrations will run automatically"
    Write-Log -Level Info -Message "3. DNS configuration may take up to 48 hours to propagate"
    Write-Log -Level Info -Message "`nMonitoring and Maintenance:"
    Write-Log -Level Info -Message "1. View app metrics: https://cloud.digitalocean.com/apps/$appId/metrics"
    Write-Log -Level Info -Message "2. Check alerts: https://cloud.digitalocean.com/apps/$appId/alerts"
    Write-Log -Level Info -Message "3. View logs: https://cloud.digitalocean.com/apps/$appId/logs"
    Write-Log -Level Info -Message "4. Database backups: https://cloud.digitalocean.com/databases"
    Write-Log -Level Info -Message "5. Deployment logs: $(Get-LogPath)"

    Write-Log -Level Info -Message "`nPost-Deployment Steps:"
    Write-Log -Level Info -Message "1. Create a superuser: doctl apps console $($config.APP_NAME)"
    Write-Log -Level Info -Message "2. Run: python manage.py createsuperuser"
    Write-Log -Level Info -Message "3. Run: python manage.py create_full_dmv_quiz"
    Write-Log -Level Info -Message "4. Verify DNS configuration for $($config.DOMAIN_NAME)"
}
catch {
    Handle-Error -Stage 'Main Script' -ErrorRecord $_
    Write-Log -Level Error -Message "Deployment failed. Check $(Get-ErrorLogPath) for details."
    exit 1
}
