$ErrorActionPreference = 'Stop';

$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$sdk_version = "1.4.363.0" # Not using ChocolateyPackageVersion, since it's normalized.

# Get install directory. Either specified in package params or default.
$pp = Get-PackageParameters
if ($pp.InstallDir) {
  $installDir = $pp.InstallDir
} else {
  $installDir = "C:\VulkanSDK\$sdk_version"
}
$stateFile = Join-Path $toolsDir 'installDir.txt'
$installDir | Out-File $stateFile -Encoding ASCII # persist for uninstaller

$packageArgs = @{
  packageName   = $env:ChocolateyPackageName
  unzipLocation = $toolsDir
  fileType      = 'exe'
  url           = "https://sdk.lunarg.com/sdk/download/$sdk_version/windows/vulkansdk-windows-X64-$sdk_version.exe"
  softwareName  = 'VulkanSDK*'
  checksum      = '94A82D378F7A5E3E54C9DB7D2FB7016AF136E14AC0A18DBF0F2F67A36352D141'
  checksumType  = 'sha256'
  silentArgs    = "install --accept-licenses --confirm-command --accept-messages --root=$installDir"
  validExitCodes= @(0)
}

Install-ChocolateyPackage @packageArgs
