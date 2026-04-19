# rtk-integration uninstall script (Windows native / PowerShell)
# Removes rtk binary, User PATH entry, global hooks, and cross-skill patches.

$ErrorActionPreference = 'Stop'
$InstallDir = Join-Path $env:USERPROFILE '.local\bin\rtk'
$SkillsDir = Join-Path $env:USERPROFILE '.claude\skills'
$TargetSkills = @(
    'layer0-spec-architect',
    'layer0-onboarding',
    'layer1-autonomous-dev'
)

function Write-Step($msg) {
    Write-Host "[rtk-integration] $msg"
}

# Step 1: Run `rtk init --uninstall` while binary still exists
Write-Step 'Removing rtk global hooks...'
$RtkExe = Get-ChildItem -Path $InstallDir -Recurse -Filter 'rtk.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($RtkExe) {
    try {
        & $RtkExe.FullName init --uninstall
    } catch {
        Write-Warning "rtk init --uninstall failed: $_"
    }
} else {
    Write-Warning 'rtk.exe not found; skipping hook uninstall.'
}

# Step 2: Remove cross-skill patches (marker-delimited)
Write-Step 'Removing cross-skill patches...'
$MarkerBegin = '<!-- rtk-integration: begin -->'
$MarkerEnd = '<!-- rtk-integration: end -->'
$PatchPattern = '(?s)\r?\n?' + [regex]::Escape($MarkerBegin) + '.*?' + [regex]::Escape($MarkerEnd) + '\r?\n?'

foreach ($skill in $TargetSkills) {
    $SkillFile = Join-Path $SkillsDir "$skill\SKILL.md"
    if (-not (Test-Path $SkillFile)) {
        continue
    }
    $Content = Get-Content -Path $SkillFile -Raw
    if ($Content -notmatch [regex]::Escape($MarkerBegin)) {
        continue
    }
    $NewContent = [regex]::Replace($Content, $PatchPattern, '')
    Set-Content -Path $SkillFile -Value $NewContent -NoNewline
    Write-Step "Patch removed: $skill"
}

# Step 3: Remove User PATH entry
Write-Step 'Removing rtk bin from User PATH...'
$CurrentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($CurrentPath) {
    $Parts = $CurrentPath -split ';' | Where-Object { $_ -notlike "$InstallDir*" -and $_.Trim() -ne '' }
    $NewPath = $Parts -join ';'
    [Environment]::SetEnvironmentVariable('Path', $NewPath, 'User')
}

# Step 4: Remove install directory
Write-Step "Removing $InstallDir..."
if (Test-Path $InstallDir) {
    Remove-Item -Path $InstallDir -Recurse -Force
}

Write-Step 'rtk-integration uninstall complete.'
Write-Step 'Open a new terminal for PATH changes to take effect.'
