# Installation Module
using module .\Logging.psm1
using module .\Config.psm1

function Install-Chocolatey {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Log -Level Info -Message "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        $env:Path = "$env:Path;$env:ChocolateyInstall\bin"
    }
}

function Install-RequiredTools {
    param(
        [bool]$SkipFailed = $false
    )
    
    $tools = @(
        @{Name = "git"; Command = "git --version"},
        @{Name = "python"; Command = "python --version"}
    )
    
    foreach ($tool in $tools) {
        if (-not (Get-Command $tool.Name -ErrorAction SilentlyContinue)) {
            try {
                Write-Log -Level Info -Message "Installing $($tool.Name)..."
                choco install $tool.Name -y
                refreshenv
            }
            catch {
                $errorMsg = "Failed to install $($tool.Name): $_"
                if (-not $SkipFailed) {
                    throw $errorMsg
                }
                Write-Log -Level Warning -Message $errorMsg
            }
        }
    }
}

function Install-DOCTL {
    $config = Get-DeploymentConfig
    $doctlVersion = $config.DOCTL_VERSION
    
    if (-not (Get-Command doctl -ErrorAction SilentlyContinue)) {
        Write-Log -Level Info -Message "Installing doctl version $doctlVersion..."
        
        $tempDir = Join-Path $env:TEMP "doctl"
        New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
        
        $downloadUrl = "https://github.com/digitalocean/doctl/releases/download/v$doctlVersion/doctl-$doctlVersion-windows-amd64.zip"
        $zipFile = Join-Path $tempDir "doctl.zip"
        
        try {
            Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile
            Expand-Archive -Path $zipFile -DestinationPath $tempDir -Force
            
            $doctlPath = Join-Path $env:ProgramFiles "doctl"
            New-Item -ItemType Directory -Force -Path $doctlPath | Out-Null
            Move-Item -Path (Join-Path $tempDir "doctl.exe") -Destination $doctlPath -Force
            
            if ($env:Path -notlike "*$doctlPath*") {
                [Environment]::SetEnvironmentVariable(
                    "Path",
                    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";$doctlPath",
                    "Machine"
                )
                $env:Path = "$env:Path;$doctlPath"
            }
            
            Write-Log -Level Info -Message "doctl installed successfully"
        }
        finally {
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

Export-ModuleMember -Function Install-Chocolatey, Install-RequiredTools, Install-DOCTL
