$ErrorActionPreference = 'Stop'

$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$stateFile = Join-Path $toolsDir 'installDir.txt'
if (-not (Test-Path $stateFile)) {
    throw "Install dir not found in $stateFile. Cannot uninstall."
}

$installDir = Get-Content $stateFile
$uninstaller = Join-Path $installDir 'maintenancetool.exe'
if (-not (Test-Path $uninstaller)) {
    throw "Uninstaller not found in $uninstaller. Cannot uninstall."
}

Write-Host "Running Vulkan SDK uninstaller from $uninstaller..."
& $uninstaller purge --confirm-command --accept-messages
