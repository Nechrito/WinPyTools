Write-Host "This script will move your Python installation from a local path to a global path."
Write-Host "This is useful if you want to use Python in a global context (e.g., in a Jenkins build)."
Write-Host "This script will also update the PATH environment variable to point to the new Python installation."
Write-Host "---"
Write-Host "NOTE: This script MUST be run as an administrator."
Write-Host "---"

# Prompt the user for the source and target directories
$sourcePath = Read-Host -Prompt 'Enter the source path of your Python installation (e.g., C:\Users\phili\AppData\Local\Programs\Python\Python311)'
$targetPath = Read-Host -Prompt 'Enter the target path where you want to move the Python installation (e.g., C:\Python311)'

# Move the Python installation
try {
    # Move the Python installation
    Move-Item -Path $sourcePath -Destination $targetPath

    # Update the PATH environment variable
    $oldPythonPath = $sourcePath + '\;'
    $oldPythonScriptsPath = $sourcePath + '\Scripts\;'
    $newPythonPath = $targetPath + '\;'
    $newPythonScriptsPath = $targetPath + '\Scripts\;'

    # Get the current PATH
    $oldPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

    # Replace old paths with new paths
    $newPath = $oldPath.Replace($oldPythonPath, $newPythonPath).Replace($oldPythonScriptsPath, $newPythonScriptsPath)

    # Set the updated PATH
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
   
    Write-Host "Python installation moved and PATH updated successfully."
} catch {
    Write-Host "Error: Failed to move Python installation and update PATH. Please check the source and target paths and try again." -ForegroundColor Red
}

Read-Host -Prompt 'Press Enter to close...'