
function PromptForPath() {
    Write-Host "Unable to locate the .env file. Please enter the path where repositories are commonly cloned:"
    $userInput = Read-Host
    return $userInput
}


# Function to load environment variables from a .env file
function LoadEnvironmentVariables($filePath) {
    Get-Content $filePath | ForEach-Object {
        $keyValue = $_ -split '=', 2
        $key = $keyValue[0].Trim()
        $value = $keyValue[1].Trim()
        Set-Item -Path "env:$key" -Value $value
    }
}

# Load environment variables from .env file
$envFilePath = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) ".env"

if (Test-Path $envFilePath) {
    LoadEnvironmentVariables $envFilePath
    $repoParentPath = $env:REPO_PARENT_PATH
}
else {
    $repoParentPath = PromptForPath
}

# Function to check for .git folder and perform a git pull
function GitPullIfRepo($path) {
    $gitPath = Join-Path $path ".git"
    if (Test-Path $gitPath -PathType Container) {
        Write-Host "Pulling changes in repository at $path"
        Set-Location $path
        git pull
    }
}

# Recursively search for .git folders and perform git pull
function UpdateRepositories($path) {
    Get-ChildItem $path | Where-Object { $_.PSIsContainer } | ForEach-Object {
        GitPullIfRepo $_.FullName
        UpdateRepositories $_.FullName
    }
}

# Execute the update function
UpdateRepositories $repoParentPath
