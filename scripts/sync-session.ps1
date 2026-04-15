<#
.SYNOPSIS
    GSE セッション NDJSON を gse-dataset にメトリクス化して同期する (Windows)。

.DESCRIPTION
    Stage E の 3 ステップ (gse-replay --metrics → validate_schema.py → git commit/push)
    を 1 コマンド化する。macOS/Linux 側は scripts/sync-session.sh を使う (同じ I/O 契約)。

    処理:
      1. cargo run --bin gse-replay -- <session> --metrics --json → $OutputDir\<basename>.metrics.json (UTF-8 NoBOM)
      2. python $DatasetRoot\scripts\validate_schema.py <session>
      3. -NoCommit でなければ gse-dataset 側で git add/commit/push

.PARAMETER SessionPath
    入力 NDJSON (必須、位置引数)

.PARAMETER OutputDir
    metrics JSON の出力先。省略時は $DatasetRoot\metrics\<ParticipantId>\windows\

.PARAMETER DatasetRoot
    gse-dataset リポジトリのルート (default: env $GSE_DATASET、未設定なら C:\gse-dataset)

.PARAMETER ParticipantId
    被験者 ID (default: env $GSE_PID、未設定なら P000)
    PowerShell 自動変数 $PID と衝突するため $ParticipantId 命名

.PARAMETER NoCommit
    指定時は Step 3 の commit/push をスキップ (dry-run)

.EXAMPLE
    pwsh -NoProfile -File scripts\sync-session.ps1 -SessionPath C:\gse-dataset\raw\P000\gse_20260415_144120.ndjson

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\sync-session.ps1 `
        -SessionPath C:\gse-dataset\raw\P000\gse_*.ndjson -NoCommit

.NOTES
    実行ポリシー拒否時: pwsh -NoProfile -ExecutionPolicy Bypass で起動
    関連: .steering/20260415-windows-onboarding/ Stage E、docs/development-guidelines.md §10.2
    Exit codes: 0=OK, 1=cargo fail, 2=schema fail, 3=git fail
#>
#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$SessionPath,

    [string]$OutputDir,
    [string]$DatasetRoot = $(if ($env:GSE_DATASET) { $env:GSE_DATASET } else { 'C:\gse-dataset' }),
    [string]$ParticipantId = $(if ($env:GSE_PID) { $env:GSE_PID } else { 'P000' }),
    [string]$RepoRoot = $(if ($env:GSE_PROTOTYPE_ROOT) { $env:GSE_PROTOTYPE_ROOT } else { 'C:\GSE-prototype' }),
    [switch]$NoCommit
)

$EXIT_OK     = 0
$EXIT_CARGO  = 1
$EXIT_SCHEMA = 2
$EXIT_GIT    = 3

function Write-Step([string]$Message) { Write-Host "[sync-session] $Message" -ForegroundColor Cyan }

# === 前提チェック ===
if (-not (Test-Path -LiteralPath $SessionPath)) {
    Write-Warning "session not found: $SessionPath"
    exit $EXIT_CARGO
}
if (-not $OutputDir) {
    $OutputDir = Join-Path $DatasetRoot "metrics\$ParticipantId\windows"
}
if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$basename        = [System.IO.Path]::GetFileNameWithoutExtension($SessionPath)
$metricsJsonPath = Join-Path $OutputDir "$basename.metrics.json"
# ※ $PSCommandPath / $PSScriptRoot / $MyInvocation.MyCommand.Path / $env:TEMP / $env:TMP が
#    Git Bash 経由の powershell.exe 呼出で空になる事象を確認済み。path 解決は param 化して
#    呼出元または env (GSE_PROTOTYPE_ROOT) から必ず実値を受け取るようにする。

# === Step 1: gse-replay --metrics --json ===
Write-Step "Step 1/3: generating metrics JSON -> $metricsJsonPath"
# cargo stdout を変数に直接キャプチャ (一時ファイル不使用、UTF-16 BOM 問題も回避)。
# 成否判定は LASTEXITCODE ではなく「出力が妥当な JSON として parse できるか」で行う
# — PowerShell 5.1 CmdletBinding 配下で LASTEXITCODE が null 化する既知問題を回避。
# Push-Location を使って src-tauri に移動してから cargo 実行 (--manifest-path は
# 引数展開の副作用で空パスになる事象を観測したため不使用)。
# 注記: 引数直前に Write-Host で変数評価を 1 度行わないと後続で空になる PS 5.1 quirk あり。
# 注: PowerShell 5.1 で $RepoRoot を interpolation で先に 1 度アクセスしないと
# 後続の "$RepoRoot\src-tauri" が null に評価される scoping quirk があるため、
# 最初に Write-Host で値を出す (ドキュメント兼ワークアラウンド)。
Write-Host "[sync-session] repo root: $RepoRoot" -ForegroundColor DarkGray
$cargoDir = "$RepoRoot\src-tauri"
if (-not (Test-Path -LiteralPath $cargoDir)) {
    Write-Warning "src-tauri not found at $cargoDir (check -RepoRoot)"
    exit $EXIT_CARGO
}
Push-Location -LiteralPath $cargoDir
try {
    $cargoOutput = cargo run --quiet --bin gse-replay --target x86_64-pc-windows-msvc -- $SessionPath --metrics --json
} finally {
    Pop-Location
}
if (-not $cargoOutput) {
    Write-Warning "cargo run produced no stdout"
    exit $EXIT_CARGO
}
# 配列 (lines) の場合は join して 1 文字列に
if ($cargoOutput -is [array]) {
    $joinedJson = ($cargoOutput -join "`n") + "`n"
} else {
    $joinedJson = [string]$cargoOutput
}
try {
    $null = $joinedJson | ConvertFrom-Json -ErrorAction Stop
} catch {
    Write-Warning ("cargo output is not valid JSON ({0} bytes captured)" -f $joinedJson.Length)
    exit $EXIT_CARGO
}
# UTF-8 NoBOM で書き出し (LF 固定、git diff friendly)
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($metricsJsonPath, $joinedJson, $utf8NoBom)
$finalInfo = Get-Item -LiteralPath $metricsJsonPath
Write-Step ("Step 1/3 OK ({0} bytes, UTF-8 NoBOM)" -f $finalInfo.Length)

# === Step 2: validate_schema.py ===
Write-Step "Step 2/3: validating NDJSON schema"
$validateScript = Join-Path $DatasetRoot 'scripts\validate_schema.py'
if (-not (Test-Path -LiteralPath $validateScript)) {
    Write-Warning "validate_schema.py not found at $validateScript — skipping schema check"
} else {
    & python $validateScript $SessionPath
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "schema validation failed (exit $LASTEXITCODE). commit skipped."
        exit $EXIT_SCHEMA
    }
    Write-Step "Step 2/3 OK"
}

# === Step 3: git commit + push ===
if ($NoCommit) {
    Write-Step "Step 3/3 skipped (-NoCommit)"
    Write-Host "[sync-session] done (dry-run): $metricsJsonPath" -ForegroundColor Green
    exit $EXIT_OK
}

Write-Step "Step 3/3: committing to $DatasetRoot"
Push-Location -LiteralPath $DatasetRoot
try {
    & git add "metrics/$ParticipantId/"
    if ($LASTEXITCODE -ne 0) { exit $EXIT_GIT }

    $date        = Get-Date -Format 'yyyy-MM-dd'
    $pidLower    = $ParticipantId.ToLower()
    $commitMsg   = "data($pidLower-windows): session $date"
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
Write-Host "[sync-session] done: $metricsJsonPath committed and pushed" -ForegroundColor Green
exit $EXIT_OK
