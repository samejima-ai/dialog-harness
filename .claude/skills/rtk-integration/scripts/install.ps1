# rtk-integration install script (Windows native / Windows PowerShell 5.1+ and PowerShell 7+)
# Installs rtk v0.37.1, configures PATH, runs `rtk init -g --auto-patch` (non-interactive), and applies cross-skill patches.

$ErrorActionPreference = 'Stop'
$RtkVersion = '0.37.1'
$ZipName = 'rtk-x86_64-pc-windows-msvc.zip'
$DownloadUrl = "https://github.com/rtk-ai/rtk/releases/download/v$RtkVersion/$ZipName"
# SHA256 of the published zip on GitHub Releases (rtk v0.37.1). Maintainer must
# update this when bumping $RtkVersion. Source: release page checksum file
# (https://github.com/rtk-ai/rtk/releases/download/v$RtkVersion/checksums.txt).
# An empty value disables verification only if $env:RTK_SKIP_VERIFY -eq '1'.
# Update protocol (when bumping $RtkVersion): see references/sha-update-protocol.md
$ExpectedSha256 = '3b9f207e8ea360d744649760788cbcf7d6ce62d8ccb8677aa3c8d1513a9d2cc2'
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

# Step 1: Precondition checks
Write-Step 'Checking preconditions...'
$IsWindowsHost = if ($null -ne $PSVersionTable.Platform) { $IsWindows } else { $true }
if (-not $IsWindowsHost) {
    Write-Error 'This installer supports Windows native only.'
    exit 1
}

# Step 2: Download and extract rtk binary
Write-Step "Downloading rtk v$RtkVersion..."
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
$ZipPath = Join-Path $env:TEMP $ZipName
# -UseBasicParsing is required and accepted on Windows PowerShell 5.1, and is
# a no-op accepted alias on PowerShell 7+ when present. Conditionally pass it
# only on 5.x to remain compatible with both shells.
$IwrArgs = @{ Uri = $DownloadUrl; OutFile = $ZipPath }
if ($PSVersionTable.PSVersion.Major -lt 6) {
    $IwrArgs['UseBasicParsing'] = $true
}
Invoke-WebRequest @IwrArgs

# Step 2.1: Verify integrity (SHA256). Pinned to a known-good hash to prevent
# tampering (MITM via proxy, compromised mirror, etc.).
if ([string]::IsNullOrEmpty($ExpectedSha256)) {
    if ($env:RTK_SKIP_VERIFY -ne '1') {
        Remove-Item $ZipPath -ErrorAction SilentlyContinue
        Write-Error 'ExpectedSha256 is empty. Set the constant in this script or run with RTK_SKIP_VERIFY=1 to bypass (not recommended).'
        exit 1
    }
    Write-Step 'WARNING: skipping SHA256 verification (RTK_SKIP_VERIFY=1).'
} else {
    Write-Step 'Verifying SHA256...'
    $ActualSha256 = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToUpperInvariant()
    $Expected = $ExpectedSha256.ToUpperInvariant()
    if ($ActualSha256 -ne $Expected) {
        Remove-Item $ZipPath -ErrorAction SilentlyContinue
        Write-Error "SHA256 mismatch for ${ZipName}: expected $Expected, got $ActualSha256. Refusing to install."
        exit 1
    }
    Write-Step 'SHA256 OK.'
}

Write-Step "Extracting to $InstallDir..."
Expand-Archive -Path $ZipPath -DestinationPath $InstallDir -Force
Remove-Item $ZipPath

# Locate rtk.exe within extracted tree (zip may have subfolder)
$RtkExe = Get-ChildItem -Path $InstallDir -Recurse -Filter 'rtk.exe' | Select-Object -First 1
if (-not $RtkExe) {
    Write-Error 'rtk.exe not found after extraction.'
    exit 1
}
$RtkBinDir = $RtkExe.DirectoryName

# Step 3: Add to User PATH
Write-Step "Adding $RtkBinDir to User PATH..."
$CurrentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($CurrentPath -notlike "*$RtkBinDir*") {
    $NewPath = if ([string]::IsNullOrEmpty($CurrentPath)) { $RtkBinDir } else { "$CurrentPath;$RtkBinDir" }
    [Environment]::SetEnvironmentVariable('Path', $NewPath, 'User')
    Write-Step 'PATH updated. New terminals will pick this up.'
} else {
    Write-Step 'PATH already contains rtk bin directory.'
}
$env:Path = "$env:Path;$RtkBinDir"

# Step 4: Run `rtk init -g`
Write-Step 'Running rtk init -g (global hook activation)...'
& "$RtkBinDir\rtk.exe" init -g --auto-patch
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'rtk init -g returned non-zero. Check output above.'
}

# Step 5: Apply cross-skill patches
Write-Step 'Applying cross-skill patches...'
$PatchBlock = @'

<!-- rtk-integration: begin -->
## rtk 未導入検知（rtk-integration スキルが提供）

スキル起動直後、セッション初回のみ以下を実行する:

1. `rtk --version` を実行
2. コマンドが存在しない、または exit code が非ゼロの場合、以下を 1 回だけ通知する:

   > **rtk 未導入**: `/rtk-integration` を呼ぶと Claude Code の Bash 出力が 60-90% 圧縮されます（git/test/build/lint 対象、Windows native）。

3. 導入済み、またはセッション内で既に通知済みの場合は沈黙する

この検知は通知のみであり、自動導入や設定ファイル編集は一切行わない。
<!-- rtk-integration: end -->
'@

$MarkerBegin = '<!-- rtk-integration: begin -->'
$MarkerEnd = '<!-- rtk-integration: end -->'

foreach ($skill in $TargetSkills) {
    $SkillFile = Join-Path $SkillsDir "$skill\SKILL.md"
    if (-not (Test-Path $SkillFile)) {
        Write-Warning "Skill file not found: $SkillFile (skipping)"
        continue
    }
    $Content = Get-Content -Path $SkillFile -Raw
    if ($Content -match [regex]::Escape($MarkerBegin)) {
        Write-Step "Patch already applied: $skill"
        continue
    }
    $Content = $Content.TrimEnd() + "`r`n" + $PatchBlock + "`r`n"
    Set-Content -Path $SkillFile -Value $Content -NoNewline
    Write-Step "Patched: $skill"
}

# Step 6: Verification
Write-Step 'Verifying installation...'
& "$RtkBinDir\rtk.exe" --version
& "$RtkBinDir\rtk.exe" init --show

Write-Step 'rtk-integration install complete.'
Write-Step 'Open a new terminal to pick up PATH changes.'
