$ErrorActionPreference = 'Stop';

$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$sdk_version = "1.4.357.0" # Not using ChocolateyPackageVersion, since it's normalized.

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
  checksum      = '81F474711E9042F4CD22B31B2F7A8870DB2E428B21586FB43DD80150BE97310D'
  checksumType  = 'sha256'
  silentArgs    = "install --accept-licenses --confirm-command --accept-messages --root=$installDir"
  validExitCodes= @(0)
}

Install-ChocolateyPackage @packageArgs
