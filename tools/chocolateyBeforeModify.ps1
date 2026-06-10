# Uninstalling in chocolateyBeforeModify.ps1 instead of chocolateyUninstall.ps1 to cover upgrades as well.
# Vulkan-SDK installer doesn't check for existing versions and installs new ones side by side, leaving the
# user with multiple versions after ugprades.
#
# The downside is if, during an upgrade, uninstallation succeeds and installation fails. Then user is left
# with no version installed and Chocolatey thinks the old version is installed. This is an edge case that
# we're willing to accept.

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
