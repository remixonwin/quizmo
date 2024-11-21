# Check if WSL is installed
$wslCheck = wsl --status
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing WSL..."
    wsl --install
} else {
    Write-Host "WSL is already installed"
}

# Check if Docker Desktop is installed
$dockerCheck = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCheck) {
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop/"
    Write-Host "After installation, make sure to enable WSL 2 integration in Docker Desktop settings"
    Start-Process "https://www.docker.com/products/docker-desktop/"
} else {
    Write-Host "Docker is already installed"
}

# Check if doctl (DigitalOcean CLI) is installed
$doctlCheck = Get-Command doctl -ErrorAction SilentlyContinue
if (-not $doctlCheck) {
    Write-Host "Installing doctl..."
    winget install --id DigitalOcean.doctl
} else {
    Write-Host "doctl is already installed"
}

Write-Host "Setup complete! Please restart your computer if you installed WSL."
