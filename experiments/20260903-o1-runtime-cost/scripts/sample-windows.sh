#!/usr/bin/env bash
# Windows (git-bash): GSE のプロセスを INTERVAL 秒ごとにサンプルする。
# ⚠️★★★ プロセス名以外は 1 つも記録しない。
set -euo pipefail
DURATION_S="$1"; INTERVAL_S="$2"
# ⚠️★★ PowerShell の中で ' を使わない (bash の '...' と衝突するため " に統一)。
read -r -d '' PS <<'PWSH' || true
$p = Get-Process -Name "gse-next" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $p) { "0`t0`t0`t0" } else {
  # ★ Get-Counter は「全コアに対する %」を返すので、コア数で割って 1 コア相当に揃えない
  #   (⚠️ macOS の top は 1 コア = 100% なので、比較するときに注意する)。
  $c = (Get-Counter -Counter ("\Process(" + $p.ProcessName + ")\% Processor Time") -ErrorAction SilentlyContinue).CounterSamples[0].CookedValue
  if ($null -eq $c) { $c = 0 }
  # ⚠️ 列 6 (rss_alt_kb) = PrivateMemorySize64。★ macOS 側の対照と対になる (env.md)。
  ("{0}`t{1}`t{2}`t{3}" -f [math]::Round($c,2), [int]($p.WorkingSet64/1024), $p.Threads.Count, [int]($p.PrivateMemorySize64/1024))
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
  [ -n "$row" ] || row=$'0\t0\t0\t0'
  # ⚠️ PowerShell は "cpu<TAB>ws<TAB>th<TAB>priv" を返す。★ battery を 5 列目に差し込む。
  cpu=$(printf '%s' "$row" | cut -f1); ws=$(printf '%s' "$row" | cut -f2)
  th=$(printf '%s' "$row" | cut -f3); priv=$(printf '%s' "$row" | cut -f4)
  # ⚠️★★★ **8 列で出す。** ★ 2026-09-04 に `run.sh` のヘッダが 8 列
  #   (`energy_impact` / `ref_energy_impact`) になったのに、⚠️ 本スクリプトは
  #   **6 列のままだった** —— そのまま 8 時間回すと集計は必ず DataInsufficient になる
  #   (★ 2026-09-05 に Windows へ渡す直前の点検で発見。macOS 側で踏んだのと同型の欠陥)。
  #
  # ⚠️★★ 7・8 列目は **空**にする（★ `0` ではない）。
  #   ★ Windows には macOS の「エネルギー影響」(`top -stats power`) に相当する
  #   **プロセス単位の公開指標が無い**。→ ★ **空 = 「この OS では測れない」**、
  #   ⚠️ `0` = 「測って 0 だった」。★ この 2 つを混ぜると、集計が
  #   「測定器が壊れている」と誤報告する (`summarize.py` の `energy_report`)。
  printf '%s\t%s\t%s\t%s\t%s\t%s\t\t\n' "$now" "$cpu" "$ws" "$th" "${batt:-}" "$priv"
  sleep "$INTERVAL_S"
done
