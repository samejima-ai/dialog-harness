# rtk-integration install script (Windows native / PowerShell)
# Installs rtk v0.37.1, configures PATH, runs `rtk init -g --auto-patch` (non-interactive), and applies cross-skill patches.

$ErrorActionPreference = 'Stop'
$RtkVersion = '0.37.1'
$ZipName = 'rtk-x86_64-pc-windows-msvc.zip'
$DownloadUrl = "https://github.com/rtk-ai/rtk/releases/download/v$RtkVersion/$ZipName"
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
if (-not $IsWindows -and -not ($PSVersionTable.Platform -eq $null)) {
    Write-Error 'This installer supports Windows native only.'
    exit 1
}

# Step 2: Download and extract rtk binary
Write-Step "Downloading rtk v$RtkVersion..."
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
$ZipPath = Join-Path $env:TEMP $ZipName
Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipPath -UseBasicParsing

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
