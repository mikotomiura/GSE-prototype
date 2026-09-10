# tasklist

## §3-2 計測用バイナリの作り直し（★ 最優先）
- [x] 現状を機械で見る（`check-measurement-binary.sh` → rc=3 を再現）
- [x] 計測を止める（sampler stop・途中結果を `_aborted-*` へ退避）
- [x] `npx tauri build ...`（★ 成功・13:02）
- [x] ⚠️ 差し替え**前**にゲート（★ ①②緑・③は未差し替えなので赤＝設計どおり）
- [x] 旧 app 退避 → 差し替え → GSE 再起動（⚠️ `open -a` では起動せず・直接実行で起動 → D5）
- [x] ⚠️ **再度**ゲート → ✅ **rc=0**

## §2 macOS 8h 再測
- [x] `calibrate-cpu.sh` で計器を校正（★ top -l 3 = 100.1 / ⚠️ top -l 2 = 22.3）
- [x] `GSE_COST_LABEL=with-gse-20260910-macos-8h-v0133` で run.sh 開始（★ 13:05〜21:05）
- [ ] （8h 後）`summarize.py`

## §5 ブランチ棚卸し
- [x] ⚠️ 救出**不要**と判明（★ 4 件とも main に差分ゼロで存在 → D1）
- [ ] 救出後に削除の可否を研究者へ提示（⚠️ 削除は私からはやらない）

## §3 スリープ跨ぎ
- [x] ★ 1 回目を実行 → ⚠️★★★ **不成立**（★ 蓋を 16 分閉じたが **Mac が寝なかった** → D8）
- [x] ⚠️ 検出器の壊れ **3 件**を塞ぐ（★ pmset の陽性対照 / shell 差 / 自己参照 → D8）
- [x] ★ `check-can-sleep.sh`（寝かせる**前**のゲート）と単独手順 `sleep-test-runbook.md` を用意
- [ ] ⚠️★★★ **やり直し** —— ★ Claude Code を終了し、Safari の再生を止めてから閉じる

## ⚠️★★★ 新規: v0.1.33 の SIGSEGV（★ D9）
- [x] ★ クラッシュを一次資料で特定（`cg_event_tap_callback_internal` / EXC_BAD_ACCESS）
- [x] ★ 機序の**仮説**を立てる（⚠️ `remove_source` が 1265 行中 **0 件** ＝ stale source 由来の UAF 疑い）
- [ ] ⚠️ **再現していない**（★ tap 失効を繰り返し起こす必要がある）
- [ ] ⚠️ **修正していない**（★ hook コードなので `hook-constraints` を読んでから・要承認）
- [ ] ⚠️ **被験者影響の判断**（★ 無言で収集が止まる → 研究者判断）

## §4 G-GEAR 取り込み（案 C）
- [ ] ⚠️ 未着手（★ 時間が余れば）
