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
    
    # Check for DO_PAT environment variable
    if (-not $env:DO_PAT) {
        Write-Error "DO_PAT environment variable not set. Please set your DigitalOcean Personal Access Token."
        exit 1
    }
    
    # Check if doctl is installed and in PATH
    $doctlPath = Get-Command doctl -ErrorAction SilentlyContinue
    if (-not $doctlPath) {
        Write-Host "doctl not found. Installing..." -ForegroundColor Yellow
        Install-Doctl
        
        # Add doctl to PATH for current session
        $env:PATH = "$PSScriptRoot;$env:PATH"
        
        # Verify installation
        $doctlPath = Get-Command doctl -ErrorAction SilentlyContinue
        if (-not $doctlPath) {
            Write-Error "Failed to install doctl or add it to PATH"
            exit 1
        }
    }
    
    # Verify doctl auth
    $authStatus = & doctl auth list 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Authenticating with DigitalOcean..."
        & doctl auth init -t $env:DO_PAT
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to authenticate with DigitalOcean"
            exit 1
        }
    }
}

# Function to install doctl
function Install-Doctl {
    Write-Host "Installing doctl..." -ForegroundColor Yellow
    
    $output = "doctl.zip"
    $url = "https://github.com/digitalocean/doctl/releases/download/v$DOCTL_VERSION/doctl-$DOCTL_VERSION-windows-amd64.zip"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $output
        Expand-Archive -Path $output -DestinationPath $PSScriptRoot -Force
        if (Test-Path $output) {
            Remove-Item $output -Force
        }
    }
    catch {
        Write-Error "Failed to install doctl: $_"
        exit 1
    }
}

# Function to create and configure app
function New-DigitalOceanApp {
    Write-Host "Creating/updating DigitalOcean App..." -ForegroundColor Yellow
    
    try {
        # Check if app exists
        $apps = & doctl apps list --format ID,Spec.Name --no-header
        $app = $apps | Where-Object { $_ -match $APP_NAME }
        
        if ($app) {
            $appId = ($app -split '\s+')[0]
            Write-Host "Updating existing app..."
            & doctl apps update $appId --spec app.yaml --wait
        }
        else {
            Write-Host "Creating new app..."
            & doctl apps create --spec app.yaml --wait
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

# Function to configure domain and wait for deployment
function Set-AppDomain {
    Write-Host "Configuring domain..." -ForegroundColor Yellow
    
    try {
        $apps = & doctl apps list --format ID,Spec.Name --no-header
        $app = $apps | Where-Object { $_ -match $APP_NAME }
        if (-not $app) {
            throw "App not found"
        }
        
        $appId = ($app -split '\s+')[0]
        $deployment = & doctl apps create-deployment $appId --wait
        
        if ($LASTEXITCODE -ne 0) {
            throw "Deployment failed"
        }
        
        Write-Host "Waiting for deployment to complete..."
        do {
            Start-Sleep -Seconds 10
            $status = & doctl apps get-deployment $appId $deployment.ID --format Progress,Phase --no-header
            Write-Host "Deployment status: $status"
        } while ($status -notmatch "100/100")
        
        # Update app spec with domain
        & doctl apps update $appId --spec app.yaml --wait
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
