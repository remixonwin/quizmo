# Logging Module

# Log configuration
$script:LogConfig = @{
    LogLevel = 'Info'  # Possible values: Debug, Info, Warning, Error
    MaxLogSize = 10MB  # Maximum size of log file before rotation
    MaxLogFiles = 5    # Number of log files to keep
    IncludeTimestamp = $true
    IncludeSource = $true
    IncludeThread = $true
    LogFormat = "[{timestamp}] [{level}] [{source}] [{thread}] {message}"
}

# Initialize log paths
$script:LogFile = Join-Path $PSScriptRoot "../../logs/deployment.log"
$script:ErrorLogFile = Join-Path $PSScriptRoot "../../logs/deployment_error.log"
$script:DebugLogFile = Join-Path $PSScriptRoot "../../logs/deployment_debug.log"
$script:MetricsLogFile = Join-Path $PSScriptRoot "../../logs/deployment_metrics.log"

# Create logs directory if it doesn't exist
$logsDir = Join-Path $PSScriptRoot "../../logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

function Write-Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [ValidateSet('Debug', 'Info', 'Warning', 'Error', 'Metric')]
        [string]$Level = 'Info',
        [string]$Source = $MyInvocation.ScriptName,
        [hashtable]$MetricData,
        [switch]$NoConsole
    )
    
    # Check if we should log this level
    $levelPriority = @{
        Debug = 0
        Info = 1
        Warning = 2
        Error = 3
        Metric = 4
    }
    
    if ($levelPriority[$Level] -lt $levelPriority[$script:LogConfig.LogLevel]) {
        return
    }
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $thread = [System.Threading.Thread]::CurrentThread.ManagedThreadId
    
    # Format the log message
    $logMessage = $script:LogConfig.LogFormat
    $logMessage = $logMessage.Replace('{timestamp}', $timestamp)
    $logMessage = $logMessage.Replace('{level}', $Level)
    $logMessage = $logMessage.Replace('{source}', $Source)
    $logMessage = $logMessage.Replace('{thread}', $thread)
    $logMessage = $logMessage.Replace('{message}', $Message)
    
    # Add metric data if provided
    if ($MetricData) {
        $metricJson = $MetricData | ConvertTo-Json -Compress
        $logMessage += " | Metrics: $metricJson"
    }
    
    # Write to console with color (unless NoConsole is specified)
    if (-not $NoConsole) {
        switch ($Level) {
            'Debug'   { Write-Host $logMessage -ForegroundColor Gray }
            'Info'    { Write-Host $logMessage -ForegroundColor Green }
            'Warning' { Write-Host $logMessage -ForegroundColor Yellow }
            'Error'   { Write-Host $logMessage -ForegroundColor Red }
            'Metric'  { Write-Host $logMessage -ForegroundColor Cyan }
        }
    }
    
    # Rotate logs if needed
    foreach ($logFile in @($script:LogFile, $script:ErrorLogFile, $script:DebugLogFile, $script:MetricsLogFile)) {
        if (Test-Path $logFile) {
            $fileInfo = Get-Item $logFile
            if ($fileInfo.Length -gt $script:LogConfig.MaxLogSize) {
                Rotate-Logs $logFile
            }
        }
    }
    
    # Write to appropriate log file
    switch ($Level) {
        'Debug'   { Add-Content -Path $script:DebugLogFile -Value $logMessage }
        'Error'   { Add-Content -Path $script:ErrorLogFile -Value $logMessage }
        'Metric'  { Add-Content -Path $script:MetricsLogFile -Value $logMessage }
        Default   { Add-Content -Path $script:LogFile -Value $logMessage }
    }
}

function Write-MetricLog {
    param(
        [Parameter(Mandatory=$true)]
        [string]$MetricName,
        [Parameter(Mandatory=$true)]
        [double]$Value,
        [string]$Unit = "",
        [hashtable]$Tags = @{},
        [string]$Source = $MyInvocation.ScriptName
    )
    
    $metricData = @{
        Name = $MetricName
        Value = $Value
        Unit = $Unit
        Tags = $Tags
        Timestamp = [DateTime]::UtcNow.ToString('o')
    }
    
    Write-Log -Level Metric -Message "Metric: $MetricName = $Value$Unit" -Source $Source -MetricData $metricData
}

function Write-DebugLog {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [string]$Source = $MyInvocation.ScriptName
    )
    
    Write-Log -Level Debug -Message $Message -Source $Source
}

function Rotate-Logs {
    param(
        [string]$LogFile
    )
    
    for ($i = $script:LogConfig.MaxLogFiles - 1; $i -ge 0; $i--) {
        $currentFile = if ($i -eq 0) { $LogFile } else { "$LogFile.$i" }
        $nextFile = "$LogFile.$($i + 1)"
        
        if (Test-Path $currentFile) {
            if ($i -eq ($script:LogConfig.MaxLogFiles - 1)) {
                Remove-Item $currentFile -Force
            }
            else {
                Move-Item $currentFile $nextFile -Force
            }
        }
    }
}

function Set-LogLevel {
    param(
        [ValidateSet('Debug', 'Info', 'Warning', 'Error')]
        [string]$Level
    )
    
    $script:LogConfig.LogLevel = $Level
    Write-Log -Level Info -Message "Log level set to: $Level"
}

function Get-LogPath {
    return $script:LogFile
}

function Get-ErrorLogPath {
    return $script:ErrorLogFile
}

function Get-DebugLogPath {
    return $script:DebugLogFile
}

function Get-MetricsLogPath {
    return $script:MetricsLogFile
}

# Performance metrics tracking
function Start-TimedOperation {
    param(
        [Parameter(Mandatory=$true)]
        [string]$OperationName
    )
    
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    return @{
        Name = $OperationName
        Timer = $timer
        StartTime = Get-Date
    }
}

function Stop-TimedOperation {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Operation
    )
    
    $Operation.Timer.Stop()
    $duration = $Operation.Timer.Elapsed.TotalSeconds
    
    Write-MetricLog -MetricName "Operation.Duration" -Value $duration -Unit "seconds" -Tags @{
        Operation = $Operation.Name
        StartTime = $Operation.StartTime.ToString('o')
    }
    
    return $duration
}

Export-ModuleMember -Function Write-Log, Write-MetricLog, Write-DebugLog, Set-LogLevel, 
                              Get-LogPath, Get-ErrorLogPath, Get-DebugLogPath, Get-MetricsLogPath,
                              Start-TimedOperation, Stop-TimedOperation
