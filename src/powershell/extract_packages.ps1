# Find all .py files
$pyFiles = Get-ChildItem -Path . -Recurse -Include *.py

# Initialize an empty list to store unique package names
$uniquePackages = @()

# Loop through each .py file
foreach ($file in $pyFiles) {
    # Get the content of the file
    $content = Get-Content $file.FullName

    # Extract package names from import statements
    $imports = $content -match "^import\s+([\w_]+)|^from\s+([\w_]+)\s+import"

    # Loop through the matches and add unique package names to the list
    foreach ($import in $imports) {
        $packageName = ($import -split '\s+')[1]
        if ($uniquePackages -notcontains $packageName) {
            $uniquePackages += $packageName
        }
    }
}

# Write unique package names to requirements.txt
$uniquePackages | Out-File -FilePath requirements.txt
