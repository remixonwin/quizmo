# PowerShell script for automating DigitalOcean App Platform deployment

# Configuration
$DOMAIN_NAME = "quizmo.me"
$APP_NAME = "mn-dmv-quiz"
$REGION = "nyc"
$DOCTL_VERSION = "1.101.0"

# Import required modules
$modulesPath = Join-Path $PSScriptRoot "scripts\modules"
Import-Module "$modulesPath\Config.psm1" -Force
Import-Module "$modulesPath\Installation.psm1" -Force
Import-Module "$modulesPath\DeploymentValidation.psm1" -Force
Import-Module "$modulesPath\DigitalOcean.psm1" -Force
Import-Module "$modulesPath\Logging.psm1" -Force
Import-Module "$modulesPath\Rollback.psm1" -Force

# Function to validate environment
function Test-Environment {
    Write-Host "Validating environment..." -ForegroundColor Yellow
    
    # Check if doctl is installed
    $doctlPath = Get-Command doctl -ErrorAction SilentlyContinue
    if (-not $doctlPath) {
        Write-Host "doctl not found. Installing..." -ForegroundColor Yellow
        Install-Doctl
    }
}

# Function to install doctl
function Install-Doctl {
    Write-Host "Installing doctl..." -ForegroundColor Yellow
    
    $output = "doctl.zip"
    $url = "https://github.com/digitalocean/doctl/releases/download/v$DOCTL_VERSION/doctl-$DOCTL_VERSION-windows-amd64.zip"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $output
        Expand-Archive -Path $output -DestinationPath . -Force
        if (Test-Path $output) {
            Remove-Item $output -Force
        }
    }
    catch {
        Write-Error "Failed to install doctl: $_"
        exit 1
    }
    
    # Configure doctl with API token
    Write-Host "Configuring doctl with API token..."
    & doctl auth init -t $env:DO_PAT
}

# Function to create and configure app
function New-DigitalOceanApp {
    Write-Host "Creating/updating DigitalOcean App..." -ForegroundColor Yellow
    
    try {
        # Check if app exists
        $app = & doctl apps list --format ID,Spec.Name --no-header | Where-Object { $_ -match $APP_NAME }
        
        if ($app) {
            Write-Host "Updating existing app..."
            & doctl apps update $app.Split()[0] --spec app.yaml
        }
        else {
            Write-Host "Creating new app..."
            & doctl apps create --spec app.yaml
        }
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create/update app"
        }
    }
    catch {
        Write-Error "Failed to create/update DigitalOcean App: $_"
        exit 1
    }
}

# Function to configure domain
function Set-AppDomain {
    Write-Host "Configuring domain..." -ForegroundColor Yellow
    
    try {
        $app = & doctl apps list --format ID,Spec.Name --no-header | Where-Object { $_ -match $APP_NAME }
        if (-not $app) {
            throw "App not found"
        }
        
        $appId = $app.Split()[0]
        & doctl apps create-deployment $appId
        
        Write-Host "Waiting for deployment to complete..."
        Start-Sleep -Seconds 30
        
        # Add domain
        & doctl apps update $appId --spec app.yaml
    }
    catch {
        Write-Error "Failed to configure domain: $_"
        exit 1
    }
}

# Main deployment process
try {
    Write-Host "Starting deployment process..." -ForegroundColor Green
    
    # Validate environment
    Test-Environment
    
    # Create and configure app
    New-DigitalOceanApp
    Set-AppDomain
    
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Your app should be available at: https://$DOMAIN_NAME" -ForegroundColor Green
}
catch {
    Write-Error "Deployment failed: $_"
    exit 1
}
