<#
.SYNOPSIS
    GSE セッション NDJSON を一括で gse-dataset に同期する (Windows)。

.DESCRIPTION
    処理:
      1. fallback ディレクトリの未同期 NDJSON を raw/P000/ にコピー
      2. raw 内で metrics 未生成のファイルに sync-session.ps1 -NoCommit を実行
      3. まとめて 1 commit + push

.PARAMETER FallbackDir
    セッション NDJSON の fallback ディレクトリ。
    省略時は $env:USERPROFILE\Documents\GSE-sessions

.PARAMETER DatasetRoot
    gse-dataset リポジトリのルート (default: env $GSE_DATASET、未設定なら C:\gse-dataset)

.PARAMETER ParticipantId
    被験者 ID (default: env $GSE_PID、未設定なら P000)

.PARAMETER NoCommit
    指定時は Step 3 の commit/push をスキップ (dry-run)

.EXAMPLE
    pwsh -NoProfile -File scripts\sync-all.ps1

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\sync-all.ps1 -NoCommit

.NOTES
    関連: scripts/sync-session.ps1、docs/development-guidelines.md §10.2
    Exit codes: 0=OK, 1=cargo fail, 3=git fail
#>
#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$FallbackDir = $(if ($env:USERPROFILE) { "$env:USERPROFILE\Documents\GSE-sessions" } else { '' }),
    [string]$DatasetRoot = $(if ($env:GSE_DATASET) { $env:GSE_DATASET } else { 'C:\gse-dataset' }),
    [string]$ParticipantId = $(if ($env:GSE_PID) { $env:GSE_PID } else { 'P000' }),
    [string]$RepoRoot = $(if ($env:GSE_PROTOTYPE_ROOT) { $env:GSE_PROTOTYPE_ROOT } else { 'C:\GSE-prototype' }),
    [switch]$NoCommit
)

$EXIT_OK           = 0
$EXIT_CARGO        = 1
$EXIT_GIT          = 3
$EXIT_PRECONDITION = 4

function Write-Step([string]$Message) { Write-Host "[sync-all] $Message" -ForegroundColor Cyan }

# PS 5.1 quirk: pre-access variables (see docs/development-guidelines.md §10.2.1)
Write-Host "[sync-all] repo root: $RepoRoot" -ForegroundColor DarkGray
Write-Host "[sync-all] dataset root: $DatasetRoot" -ForegroundColor DarkGray

# === 前提チェック ===
if (-not (Test-Path -LiteralPath $DatasetRoot)) {
    Write-Warning "gse-dataset not found at $DatasetRoot — set GSE_DATASET env or clone the repo"
    exit $EXIT_PRECONDITION
}

$rawDir     = "$DatasetRoot\raw\$ParticipantId"
$metricsDir = "$DatasetRoot\metrics\$ParticipantId\windows"
$syncScript = "$RepoRoot\scripts\sync-session.ps1"

if (-not (Test-Path -LiteralPath $syncScript)) {
    Write-Warning "sync-session.ps1 not found at $syncScript"
    exit $EXIT_PRECONDITION
}

# ディレクトリ作成
foreach ($d in @($rawDir, $metricsDir)) {
    if (-not (Test-Path -LiteralPath $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
    }
}

# === Step 1: fallback → raw コピー (重複スキップ) ===
$copied = 0
if ($FallbackDir -and (Test-Path -LiteralPath $FallbackDir)) {
    Write-Step "Step 1/3: copying unsynced NDJSON from $FallbackDir"
    $fallbackFiles = Get-ChildItem -Path $FallbackDir -Filter 'gse_*.ndjson' -File -ErrorAction SilentlyContinue
    foreach ($f in $fallbackFiles) {
        $destPath = "$rawDir\$($f.Name)"
        if (-not (Test-Path -LiteralPath $destPath)) {
            Copy-Item -LiteralPath $f.FullName -Destination $destPath
            Write-Host "  copied: $($f.Name)"
            $copied++
        }
    }
    Write-Step "Step 1/3 OK ($copied files copied)"
} else {
    Write-Step "Step 1/3: fallback dir not found ($FallbackDir) — skipping"
}

# === Step 2: metrics 未生成ファイルを検出して sync-session 実行 ===
$processed = 0
$failed    = 0
Write-Step "Step 2/3: generating metrics for unprocessed sessions"
$rawFiles = Get-ChildItem -Path $rawDir -Filter 'gse_*.ndjson' -File -ErrorAction SilentlyContinue
foreach ($f in $rawFiles) {
    $basename    = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    $metricsFile = "$metricsDir\$basename.metrics.json"
    if (Test-Path -LiteralPath $metricsFile) {
        Write-Host "  skip (already has metrics): $basename"
        continue
    }
    Write-Host "  processing: $basename"
    # 現在のホストと同じ PowerShell で子プロセスを起動
    $psExe = "$PSHOME\powershell.exe"
    if (Test-Path "$PSHOME\pwsh.exe") { $psExe = "$PSHOME\pwsh.exe" }
    & $psExe -NoProfile -ExecutionPolicy Bypass -File $syncScript `
        -SessionPath $f.FullName `
        -DatasetRoot $DatasetRoot `
        -ParticipantId $ParticipantId `
        -RepoRoot $RepoRoot `
        -NoCommit
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "  FAILED: $basename (exit $LASTEXITCODE)"
        $failed++
    } else {
        $processed++
    }
}
Write-Step "Step 2/3 done ($processed processed, $failed failed)"

if ($failed -gt 0) {
    Write-Warning "$failed files failed — aborting before commit"
    exit $EXIT_CARGO
}

if ($processed -eq 0 -and $copied -eq 0) {
    Write-Host "[sync-all] nothing to sync" -ForegroundColor Green
    exit $EXIT_OK
}

# === Step 3: git commit + push ===
if ($NoCommit) {
    Write-Step "Step 3/3 skipped (-NoCommit)"
    Write-Host "[sync-all] done (dry-run): $processed metrics generated, $copied files copied" -ForegroundColor Green
    exit $EXIT_OK
}

Write-Step "Step 3/3: committing to $DatasetRoot"
Push-Location -LiteralPath $DatasetRoot
try {
    & git add "raw/$ParticipantId/" "metrics/$ParticipantId/"
    if ($LASTEXITCODE -ne 0) { exit $EXIT_GIT }

    $date        = Get-Date -Format 'yyyy-MM-dd'
    $pidLower    = $ParticipantId.ToLower()
    $total       = $copied + $processed
    $commitMsg   = "data($pidLower-windows): batch sync $date ($total files)"
    & git commit -m $commitMsg
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "git commit failed (maybe nothing to commit?)"
        exit $EXIT_GIT
    }

    & git push origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "git push failed. Try: cd $DatasetRoot; git push origin main"
        exit $EXIT_GIT
    }
} finally {
    Pop-Location
}
Write-Host "[sync-all] done: $processed metrics generated, $copied files copied, committed and pushed" -ForegroundColor Green
exit $EXIT_OK
