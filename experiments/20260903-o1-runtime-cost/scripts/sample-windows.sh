#!/usr/bin/env bash
# Windows (git-bash): GSE のプロセスを INTERVAL 秒ごとにサンプルする。
# ⚠️★★★ プロセス名以外は 1 つも記録しない。
set -euo pipefail
DURATION_S="$1"; INTERVAL_S="$2"
# ⚠️★★ PowerShell の中で ' を使わない (bash の '...' と衝突するため " に統一)。
read -r -d '' PS <<'PWSH' || true
$p = Get-Process -Name "gse-next" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $p) { "0`t0`t0" } else {
  # ★ Get-Counter は「全コアに対する %」を返すので、コア数で割って 1 コア相当に揃えない
  #   (⚠️ macOS の top は 1 コア = 100% なので、比較するときに注意する)。
  $c = (Get-Counter -Counter ("\Process(" + $p.ProcessName + ")\% Processor Time") -ErrorAction SilentlyContinue).CounterSamples[0].CookedValue
  if ($null -eq $c) { $c = 0 }
  ("{0}`t{1}`t{2}" -f [math]::Round($c,2), [int]($p.WorkingSet64/1024), $p.Threads.Count)
}
PWSH
read -r -d '' PSB <<'PWSH' || true
$b = Get-CimInstance -ClassName Win32_Battery -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $b) { "" } else { $b.EstimatedChargeRemaining }
PWSH
end=$(( $(date +%s) + DURATION_S ))
while [ "$(date +%s)" -lt "$end" ]; do
  now=$(date +%s)
  row=$(powershell.exe -NoProfile -NonInteractive -Command "$PS" 2>/dev/null | tr -d '\r' | tail -1 || true)
  batt=$(powershell.exe -NoProfile -NonInteractive -Command "$PSB" 2>/dev/null | tr -d '\r' | tail -1 || true)
  [ -n "$row" ] || row=$'0\t0\t0'
  printf '%s\t%s\t%s\n' "$now" "$row" "${batt:-}"
  sleep "$INTERVAL_S"
done
