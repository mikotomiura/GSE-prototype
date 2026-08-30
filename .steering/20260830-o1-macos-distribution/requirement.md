# requirement — O1 の macOS 配布物と実機通し確認

## 背景

`.steering/_handoff/next-session-prompt-o1-macos-distribution.md` の実施。

- O1 (R3-a「ふだんの作業の長期記録」) の受け口 (`GSE_O1_Submit`) は 2026-08-29 にデプロイ済み。
- 配布スクリプト `make-common-app-zip.sh --mode o1` は実装済みだが、
  ⚠️ **macOS 実機で 1 度も通し確認していない**。
- readiness ゲートに残る唯一の赤は「送信 timeout が未実測」。

## ゴール

1. 本番設定 (`Form_O1/o1_submit.json`) で O1 配布物を作り、中身を実測で検証する。
2. ⚠️ 配布物**そのもの**から macOS 実機の通し確認を行う (`cargo run` で代用しない)。
3. 送信 timeout を実サイズで実測し、readiness の最後の赤を消す。
4. 実機と食い違う README 文言・手順を直す。

## 受け入れ条件

- [ ] `--mode o1 --tag v0.1.29 --config Form_O1/o1_submit.json` が緑で完走する
- [ ] zip 内 `g1-submit.json` が本番設定と **byte 一致**
- [ ] ⚠️ `--mode o1` が G1 の配布物を作り直していない (タイムスタンプで確認)
- [ ] README 【1】の初回セットアップが実機で **`OK:` を返す**
- [ ] O1 モードで動いていることを NDJSON の実体で確認する
- [ ] `check-o1-release-readiness.sh` が通過 18 / 未達 0 になる

## スコープ外

- G1 の配布経路 (⚠️ 既定 `--mode g1` / `TAG="v0.1.24"` は**触らない**。G1 は実施中)
- `sync-all.sh` の O1 生ログ常駐問題 (⚠️ 起票済み・`.ps1` と対で直すため Windows 作業時)
- Windows PowerShell 5.1 (Desktop) での `.ps1` ガード検証 (⚠️ macOS では不可能)

## 運用メモ

- /reimagine 適用: No
- 理由: 引き継ぎメモで手順が確定しており、設計判断の余地が無い。
  ⚠️ ただし実機で見つかった欠陥の直し方は `decisions.md` に残す。

## ★ 研究者が決めた分担 (2026-08-30)

| 項目 | 決定 |
|---|---|
| §1-D 実機通し確認 | ★ 私が可能な範囲まで自動で進め、GUI 操作のみ研究者へ都度依頼 |
| §1-E-4 送信 timeout 実測 | ✅ **実施してよい** (本番受け口へ送信) |
| §0-2 配布フォルダの中身 | ★ 私が Chrome で開いて確認する |
