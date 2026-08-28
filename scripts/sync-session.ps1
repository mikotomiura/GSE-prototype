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
    被験者 ID の明示指定 (任意)。下記の解決順で使われる。
    PowerShell 自動変数 $PID と衝突するため $ParticipantId 命名。

    参加者 ID 解決順 (raw 構造を真実源とし logger Part 2 の自動生成 ID に追従):
      1. パス導出: SessionPath が .../raw/<PID>/gse_*.ndjson なら親ディレクトリ名 <PID>
      2. -ParticipantId / env $GSE_PID (allowlist 通過時)
      3. ~/.gse/participant_id (logger の永続化先、allowlist 通過時)
      4. P000 (最終 fallback)
    詳細: .steering/20260619-sync-auto-participant-id/decisions.md

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
    Exit codes: 0=OK, 1=cargo fail, 2=schema fail, 3=git fail, 4=O1 セッションを弾いた
#>
#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$SessionPath,

    [string]$OutputDir,
    [string]$DatasetRoot = $(if ($env:GSE_DATASET) { $env:GSE_DATASET } else { 'C:\gse-dataset' }),
    # 既定は env $GSE_PID または空。空のまま P000 へ即決せず、本体で永続化値 fallback を通す。
    [string]$ParticipantId = $(if ($env:GSE_PID) { $env:GSE_PID } else { '' }),
    [string]$RepoRoot = $(if ($env:GSE_PROTOTYPE_ROOT) { $env:GSE_PROTOTYPE_ROOT } else { 'C:\GSE-prototype' }),
    [switch]$NoCommit
)

$EXIT_OK     = 0
$EXIT_CARGO  = 1
$EXIT_SCHEMA = 2
$EXIT_GIT    = 3
$EXIT_O1     = 4   # ★ O1 セッションを弾いた

function Write-Step([string]$Message) { Write-Host "[sync-session] $Message" -ForegroundColor Cyan }

# === 参加者 ID ヘルパー (logger is_valid_participant_id と挙動を一致させる) ===
# allowlist: ASCII 英数字 + _ + - のみ・長さ 1..=64、かつ Windows 予約デバイス名を拒否
# (大小無視)。logger.rs:918-942 と完全一致。
$script:GseReservedIds = @('CON','PRN','AUX','NUL',
    'COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9',
    'LPT1','LPT2','LPT3','LPT4','LPT5','LPT6','LPT7','LPT8','LPT9')

function Test-ValidParticipantId([string]$Id) {
    if ([string]::IsNullOrEmpty($Id)) { return $false }
    # \A..\z で末尾改行も許さない (PS の ^..$ は末尾 \n を許すため logger と挙動が乖離する)。
    if (-not [regex]::IsMatch($Id, '\A[A-Za-z0-9_-]{1,64}\z')) { return $false }
    if ($script:GseReservedIds -contains $Id.ToUpperInvariant()) { return $false }
    return $true
}

function Get-PidFromPath([string]$Path) {
    # .../raw/<PID>/gse_*.ndjson の <PID> を返す。祖父名が厳密に 'raw' のときのみ。
    $parent = Split-Path -Leaf (Split-Path -Parent $Path)
    $grand  = Split-Path -Leaf (Split-Path -Parent (Split-Path -Parent $Path))
    if ($grand -eq 'raw' -and (Test-ValidParticipantId $parent)) { return $parent }
    return $null
}

function Get-PersistedParticipantId {
    # logger の永続化先 ~/.gse/participant_id を読む (基点 USERPROFILE → HOME)。
    $base = if ($env:USERPROFILE) { $env:USERPROFILE } elseif ($env:HOME) { $env:HOME } else { $null }
    if (-not $base) { return $null }
    # §10.2.1: Join-Path 空返し回避のため文字列結合で組む
    $f = "$base\.gse\participant_id"
    if (-not (Test-Path -LiteralPath $f)) { return $null }
    try {
        $raw = (Get-Content -LiteralPath $f -Raw -ErrorAction Stop).Trim()
    } catch { return $null }
    if (Test-ValidParticipantId $raw) { return $raw }
    return $null
}

# === 前提チェック ===
if (-not (Test-Path -LiteralPath $SessionPath)) {
    Write-Warning "session not found: $SessionPath"
    exit $EXIT_CARGO
}

# === ⚠️★★★ O1 (R3-a) を gse-dataset へ出さないガード ==========================
#
# ★ なぜ止めるのか (docs/o1-deletion-ledger.md §4):
#   ⚠️ gse-dataset の metrics/ は git で追跡され push されている (2026-08-28 に 34 件を実測)。
#   ★ O1 の同意文書は「あとから『この時間帯を消して』と言える」と約束している。
#   → ⚠️★★★ 一度 push すると、その削除は **git 履歴の書き換え**になる。
#     ★ 「消せます」と言った約束を、実務上守れない形にしてしまう。
#
# ⚠️ ★ 弾く根拠を 2 本持つ (片方だけだとすり抜ける)。sync-session.sh と**同じ規則**:
#   1. ファイル名が gse_o1_ で始まる (logger.rs: session_file_name)
#   2. ★ meta 行に o1_mode がある (reconcile.rs が O1 判定の第 1 の根拠にしているもの)
#
# ⚠️★ **両方の実装を同時に直すこと。** 片方だけ直すと、もう片方の OS から漏れる。
$o1Why = $null
if ([System.IO.Path]::GetFileName($SessionPath) -like 'gse_o1_*') {
    $o1Why = 'ファイル名が gse_o1_ で始まる'
} else {
    try {
        # ⚠️ ★ meta 行は 1 行目とは限らないので先頭 20 行を見る。
        $head = Get-Content -LiteralPath $SessionPath -TotalCount 20 -ErrorAction Stop
        if ($head -match '"o1_mode"') { $o1Why = 'meta 行に o1_mode がある' }
    } catch {
        # ★ 読めないファイルはここでは判定しない (下流の cargo が正しいエラーを出す)。
    }
}
if ($o1Why) {
    Write-Warning "O1 のセッションは gse-dataset に同期しません ($o1Why)"
    Write-Warning "  ★ 理由: metrics/ は追跡・push されるため、あとからの削除要求が"
    Write-Warning "     **git 履歴の書き換え**になります (docs/o1-deletion-ledger.md §4)。"
    Write-Warning "  ★ O1 の記録は自動提出 (reconcile) で研究者へ届きます。ここを通す必要はありません。"
    Write-Warning "  ⚠️ どうしても必要なら、先に台帳 §4 の運用規則を読み、同意文書を改訂してください。"
    exit $EXIT_O1
}

# === 参加者 ID 解決 (パス導出 → -ParticipantId/GSE_PID → 永続化 → P000) ===
$pidSource = ''
$derivedPid = Get-PidFromPath $SessionPath
if ($derivedPid) {
    $ParticipantId = $derivedPid; $pidSource = 'raw-path'
} elseif ($ParticipantId -and (Test-ValidParticipantId $ParticipantId)) {
    $pidSource = 'GSE_PID'
} else {
    $persistedPid = Get-PersistedParticipantId
    if ($persistedPid) { $ParticipantId = $persistedPid; $pidSource = 'persisted' }
    else { $ParticipantId = 'P000'; $pidSource = 'default' }
}
Write-Step "participant id: $ParticipantId (source: $pidSource)"

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
