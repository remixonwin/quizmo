# Deployment Validation Module
using module .\Logging.psm1
using module .\Config.psm1

# Pre-deployment validation checks
$script:PreDeploymentChecks = @{
    RequiredTools = @(
        @{
            Name = "doctl"
            MinVersion = "1.101.0"
            ValidationCmd = "doctl version"
            VersionRegex = "doctl version (\d+\.\d+\.\d+)"
        }
        @{
            Name = "git"
            MinVersion = "2.30.0"
            ValidationCmd = "git --version"
            VersionRegex = "git version (\d+\.\d+\.\d+)"
        }
        @{
            Name = "python"
            MinVersion = "3.8.0"
            ValidationCmd = "python --version"
            VersionRegex = "Python (\d+\.\d+\.\d+)"
        }
    )
    RequiredFiles = @(
        "app.py"
        "requirements.txt"
        "static/css/main.css"
        "templates/index.html"
    )
    RequiredEnvVars = @(
        "DEBUG"
        "SECRET_KEY"
        "ALLOWED_HOSTS"
        "DB_NAME"
        "DB_USER"
        "DB_PASSWORD"
    )
}

# Post-deployment verification checks
$script:PostDeploymentChecks = @{
    Endpoints = @(
        @{
            Path = "/"
            Method = "GET"
            ExpectedStatus = 200
            ContentCheck = { param($content) $content -match "Minnesota DMV Practice Quiz" }
        }
        @{
            Path = "/health/"
            Method = "GET"
            ExpectedStatus = 200
            ContentCheck = { param($content) $content -match '"status":"healthy"' }
        }
    )
    DatabaseChecks = @(
        "SELECT 1 FROM questions LIMIT 1"
        "SELECT 1 FROM quiz_attempts LIMIT 1"
    )
    MetricThresholds = @{
        CPUUsage = 80
        MemoryUsage = 80
        DiskUsage = 80
        ResponseTime = 2000  # milliseconds
    }
}

function Test-PreDeploymentRequirements {
    param(
        [switch]$StopOnFailure
    )
    
    Write-Log -Level Info -Message "Starting pre-deployment validation checks..."
    $timer = Start-TimedOperation "PreDeploymentValidation"
    $failures = @()
    
    # Check required tools and versions
    foreach ($tool in $script:PreDeploymentChecks.RequiredTools) {
        Write-Log -Level Info -Message "Checking $($tool.Name) installation..."
        try {
            $version = Invoke-Expression $tool.ValidationCmd 2>&1
            if ($version -match $tool.VersionRegex) {
                $installedVersion = $matches[1]
                if (-not (Test-VersionRequirement $installedVersion $tool.MinVersion)) {
                    $failures += "Tool $($tool.Name) version $installedVersion is below minimum required version $($tool.MinVersion)"
                }
            } else {
                $failures += "Unable to determine version for tool $($tool.Name)"
            }
        } catch {
            $failures += "Tool $($tool.Name) is not installed or not accessible"
        }
    }
    
    # Check required files
    foreach ($file in $script:PreDeploymentChecks.RequiredFiles) {
        Write-Log -Level Info -Message "Checking required file: $file..."
        if (-not (Test-Path $file)) {
            $failures += "Required file missing: $file"
        }
    }
    
    # Check environment variables
    foreach ($envVar in $script:PreDeploymentChecks.RequiredEnvVars) {
        Write-Log -Level Info -Message "Checking environment variable: $envVar..."
        if (-not (Test-EnvVariable $envVar)) {
            $failures += "Required environment variable missing: $envVar"
        }
    }
    
    # Check DigitalOcean authentication
    Write-Log -Level Info -Message "Verifying DigitalOcean authentication..."
    try {
        $null = Invoke-Expression "doctl account get" 2>&1
    } catch {
        $failures += "DigitalOcean authentication failed. Please check your API token."
    }
    
    # Check database connection string
    Write-Log -Level Info -Message "Validating database connection string..."
    if (-not (Test-DatabaseConnection)) {
        $failures += "Database connection validation failed"
    }
    
    # Check SSL certificate configuration
    Write-Log -Level Info -Message "Checking SSL certificate configuration..."
    if (-not (Test-SSLConfiguration)) {
        $failures += "SSL certificate configuration is invalid"
    }
    
    Stop-TimedOperation $timer
    
    if ($failures.Count -gt 0) {
        foreach ($failure in $failures) {
            Write-Log -Level Error -Message "Validation Error: $failure"
        }
        if ($StopOnFailure) {
            throw "Pre-deployment validation failed with $($failures.Count) errors"
        }
        return $false
    }
    
    Write-Log -Level Info -Message "Pre-deployment validation completed successfully"
    return $true
}

function Test-PostDeploymentHealth {
    param(
        [string]$AppUrl,
        [switch]$StopOnFailure
    )
    
    Write-Log -Level Info -Message "Starting post-deployment health checks..."
    $timer = Start-TimedOperation "PostDeploymentValidation"
    $failures = @()
    
    # Check endpoints
    foreach ($endpoint in $script:PostDeploymentChecks.Endpoints) {
        Write-Log -Level Info -Message "Testing endpoint: $($endpoint.Path)..."
        try {
            $response = Invoke-WebRequest -Uri "$AppUrl$($endpoint.Path)" -Method $endpoint.Method
            
            # Check status code
            if ($response.StatusCode -ne $endpoint.ExpectedStatus) {
                $failures += "Endpoint $($endpoint.Path) returned status $($response.StatusCode), expected $($endpoint.ExpectedStatus)"
            }
            
            # Check content if specified
            if ($endpoint.ContentCheck -and -not (& $endpoint.ContentCheck $response.Content)) {
                $failures += "Content validation failed for endpoint $($endpoint.Path)"
            }
            
            # Log response time metric
            $responseTime = $response.Headers["X-Response-Time"]
            if ($responseTime -and [int]$responseTime -gt $script:PostDeploymentChecks.MetricThresholds.ResponseTime) {
                Write-Log -Level Warning -Message "High response time ($responseTime ms) for endpoint $($endpoint.Path)"
            }
            
            Write-MetricLog -MetricName "Endpoint.ResponseTime" -Value $responseTime -Unit "ms" -Tags @{
                Endpoint = $endpoint.Path
                Method = $endpoint.Method
            }
        } catch {
            $failures += "Failed to test endpoint $($endpoint.Path): $_"
        }
    }
    
    # Check database connectivity and basic queries
    Write-Log -Level Info -Message "Performing database health checks..."
    foreach ($query in $script:PostDeploymentChecks.DatabaseChecks) {
        try {
            if (-not (Test-DatabaseQuery $query)) {
                $failures += "Database query failed: $query"
            }
        } catch {
            $failures += "Database check failed: $_"
        }
    }
    
    # Check resource usage
    Write-Log -Level Info -Message "Checking resource usage..."
    $metrics = Get-ResourceMetrics
    
    if ($metrics.CPUUsage -gt $script:PostDeploymentChecks.MetricThresholds.CPUUsage) {
        Write-Log -Level Warning -Message "High CPU usage: $($metrics.CPUUsage)%"
    }
    
    if ($metrics.MemoryUsage -gt $script:PostDeploymentChecks.MetricThresholds.MemoryUsage) {
        Write-Log -Level Warning -Message "High memory usage: $($metrics.MemoryUsage)%"
    }
    
    if ($metrics.DiskUsage -gt $script:PostDeploymentChecks.MetricThresholds.DiskUsage) {
        Write-Log -Level Warning -Message "High disk usage: $($metrics.DiskUsage)%"
    }
    
    # Log all metrics
    Write-MetricLog -MetricName "Resource.CPU" -Value $metrics.CPUUsage -Unit "percent"
    Write-MetricLog -MetricName "Resource.Memory" -Value $metrics.MemoryUsage -Unit "percent"
    Write-MetricLog -MetricName "Resource.Disk" -Value $metrics.DiskUsage -Unit "percent"
    
    Stop-TimedOperation $timer
    
    if ($failures.Count -gt 0) {
        foreach ($failure in $failures) {
            Write-Log -Level Error -Message "Verification Error: $failure"
        }
        if ($StopOnFailure) {
            throw "Post-deployment verification failed with $($failures.Count) errors"
        }
        return $false
    }
    
    Write-Log -Level Info -Message "Post-deployment verification completed successfully"
    return $true
}

# Helper Functions
function Test-VersionRequirement {
    param(
        [string]$InstalledVersion,
        [string]$RequiredVersion
    )
    
    $installed = [version]$InstalledVersion
    $required = [version]$RequiredVersion
    return $installed -ge $required
}

function Test-EnvVariable {
    param(
        [string]$Name
    )
    
    $value = [Environment]::GetEnvironmentVariable($Name)
    return -not [string]::IsNullOrWhiteSpace($value)
}

function Test-DatabaseConnection {
    try {
        $config = Get-DeploymentConfig
        $connectionString = "Server=$($config.DB_HOST);Database=$($config.DB_NAME);User Id=$($config.DB_USER);Password=$($config.DB_PASSWORD)"
        # Add your database connection test logic here
        return $true
    } catch {
        Write-Log -Level Error -Message "Database connection test failed: $_"
        return $false
    }
}

function Test-DatabaseQuery {
    param(
        [string]$Query
    )
    
    try {
        # Add your database query test logic here
        return $true
    } catch {
        Write-Log -Level Error -Message "Database query test failed: $_"
        return $false
    }
}

function Test-SSLConfiguration {
    try {
        $config = Get-DeploymentConfig
        # Add your SSL configuration test logic here
        return $true
    } catch {
        Write-Log -Level Error -Message "SSL configuration test failed: $_"
        return $false
    }
}

function Get-ResourceMetrics {
    try {
        # Add your resource metrics collection logic here
        # This is a placeholder that returns mock data
        return @{
            CPUUsage = 30
            MemoryUsage = 45
            DiskUsage = 60
        }
    } catch {
        Write-Log -Level Error -Message "Failed to collect resource metrics: $_"
        throw
    }
}

Export-ModuleMember -Function Test-PreDeploymentRequirements, Test-PostDeploymentHealth
