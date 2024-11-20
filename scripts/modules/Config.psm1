# Configuration Module
using module .\Logging.psm1

# Default configuration values
$script:Config = @{
    DOMAIN_NAME = "quizmo.me"
    APP_NAME = "mn-dmv-quiz"
    REGION = "nyc"
    DOCTL_VERSION = "1.101.0"
    ENVIRONMENT = "production"
}

# Function to get configuration value
function Get-ConfigValue {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Key
    )
    
    if ($script:Config.ContainsKey($Key)) {
        return $script:Config[$Key]
    }
    
    Write-LogError "Configuration key not found: $Key"
    throw "Configuration key not found: $Key"
}

# Function to set configuration value
function Set-ConfigValue {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Key,
        
        [Parameter(Mandatory = $true)]
        [string]$Value
    )
    
    $script:Config[$Key] = $Value
}

# Export functions
Export-ModuleMember -Function Get-ConfigValue, Set-ConfigValue
