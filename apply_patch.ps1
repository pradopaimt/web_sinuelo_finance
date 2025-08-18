Param(
  [string]$File = "index.html",
  [string]$Patch = "patch.json",
  [switch]$Backup
)

if ($Backup) { Copy-Item $File "$File.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')" }

$json = Get-Content $Patch -Raw | ConvertFrom-Json
$content = Get-Content $File -Raw

foreach ($edit in $json.edits) {
  $pattern   = $edit.find
  $replace   = $edit.replace
  $multiple  = $edit.multiple

  $regex = New-Object System.Text.RegularExpressions.Regex(
    $pattern,
    [System.Text.RegularExpressions.RegexOptions]::Singleline -bor `
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor `
    [System.Text.RegularExpressions.RegexOptions]::Compiled,
    [TimeSpan]::FromSeconds(10) # timeout maior
  )

  if ($multiple) {
    $content = $regex.Replace($content, $replace)
  } else {
    $content = $regex.Replace($content, $replace, 1)
  }
}

Set-Content $File $content -Encoding utf8
Write-Host "Patch aplicado em $File com sucesso."
