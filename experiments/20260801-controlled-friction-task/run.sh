#!/usr/bin/env bash
# G1 統制タスク実験 — 実行スクリプト（★ 未実装のスタブ）
#
# 本実験は「設計のみ」であり、実施は Phase1 完了＋研究者承認による凍結解除後。
# 誤って走らせて「実施済み」と誤認されるのを防ぐため、明示的に停止する。
set -euo pipefail

cat <<'MSG'
[G1] この実験は設計のみで、まだ実装・実施されていません。

実施前に必要な作業（experiments/20260801-controlled-friction-task/README.md §5）:
  1. 課題文の作成（LO 資料 1 本 / HI 資料 3 本 × 必要セット数）
  2. §3 判定基準の事前登録（G1 は凍結済み preregistration-v0.3 に含まれない新規ゲート）
  3. 倫理・同意手続き
  4. Tier 0/1 特徴量の実装（FS-B に必要・schema_dto.rs は凍結対象）
  5. 本スクリプトと解析スクリプトの実装

判定基準は config.json に凍結済みです。データを見てから変更しないでください。
MSG
exit 2
