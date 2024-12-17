# Define variables
$installerUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
$downloadPath = "$env:USERPROFILE\Downloads\python-3.11.0-amd64.exe"
$installPath = "C:\Python311"

try {
    # Download Python installer
    Write-Host "Downloading Python 3.11 installer..."
    Invoke-WebRequest -Uri $installerUrl -OutFile $downloadPath
    Write-Host "Python downloaded successfully."
} catch {
    Write-Host "Error: Failed to download" -ForegroundColor Red
}

try {
    # Install Python
    Write-Host "Installing Python 3.11 to $installPath..."
    Start-Process -FilePath $downloadPath -ArgumentList "/quiet InstallAllUsers=1 TargetDir=$installPath PrependPath=1" -Wait -NoNewWindow
    Write-Host "Python installed successfully."
} catch {
    Write-Host "Error: Failed to install Python." -ForegroundColor Red
}

try{
    # Remove installer
    Write-Host "Cleaning up..."
    Remove-Item $downloadPath
} catch {
    Write-Host "Error: Failed to clean up." -ForegroundColor Red
}

# try {
#     # Remove existing Python installation
#     Write-Host "Removing existing Python installation..."
#     Remove-Item -Path $installPath -Recurse -Force
#     Write-Host "Existing Python installation removed successfully."
# } catch {
#     Write-Host "Error: Failed to remove existing Python installation. Please check the source and target paths and try again." -ForegroundColor Red
# }

try {
    # Check Python installation
    Write-Host "Checking Python installation..."

    $pythonVersion = & $installPath\python.exe --version

    if ($pythonVersion -like "Python 3.11*") {
        Write-Host "Python 3.11 installation was successful!"
    } else {
        Write-Host "Python 3.11 installation failed. Please check the log for more details."
    }
} catch {
    Write-Host "Error: Failed when checking the installation." -ForegroundColor Red
}

Read-Host -Prompt 'Press Enter to close...'