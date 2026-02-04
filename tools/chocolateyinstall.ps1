$ErrorActionPreference = 'Stop';

$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$sdk_version = "1.4.341.0" # Not using ChocolateyPackageVersion, since it's normalized.

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
  checksum      = '5072AC63F0B00BC8C132BC0052BAC0456F61983BD9D5DD50F614E190472DB875'
  checksumType  = 'sha256'
  silentArgs    = "install --accept-licenses --confirm-command --accept-messages --root=$installDir"
  validExitCodes= @(0)
}

Install-ChocolateyPackage @packageArgs
