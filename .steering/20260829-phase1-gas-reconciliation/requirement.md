# requirement — Phase1 の GAS を repo に取り込み、O1 に足りない機能を洗い出す

作成日: 2026-08-29 / モデル: Opus
引き継ぎ元: `.steering/_handoff/next-session-prompt-phase1-gas-reconciliation.md`

## 背景

⚠️★★★ **Apps Script が唯一のコピーだった。**

`.steering/20260829-o1-roster-guards/decisions.md` G-2 で判明したとおり、Phase1 の
Apps Script プロジェクト `GSE_検証フォーム(事前・事後)_Phase1` は repo より **1,100 行以上**
先行しており、`git log --all -S "sendReminders"` が空＝**一度もコミットされたことが無い**。
→ repo 版を GAS に貼れば稼働中の機能が消えるため、G-2 で「触らない」と決めて本タスクへ分離した。

本タスクは **GAS → repo の一方向の取り込み**を行い、そのうえで
「Phase1 にあって O1 / G1 に無い機能」を棚卸しして研究者判断を仰ぐ。

## ゴール（★ Done は exit code / 実測で言える形）

- [x] G1. GAS 上の全文が `Form_Phase1/GSE_Phase1_Form_Builder.gs` に入り、
      **repo と GAS が SHA-256 で一致**する（`monaco.getValue()` のハッシュで実測）
- [x] G2. 取り込んだコードの**秘密・PII 直書き**を検査し、見つかったものを起票する
- [x] G3. **T-25**（Phase1 の集計を凍結）を実装する
- [ ] G4. T-25 を GAS へ貼り戻し、★ 再度 SHA 一致を確認する（⚠️ **研究者の承認が要る**）
- [x] G5. **機能の棚卸し表**（Phase1 / G1 / O1）が `design.md` にある
- [x] G6. `bash scripts/check-o1-release-readiness.sh` が **通過 16 / 未達 1** のまま（悪化させない）

## スコープ外（★ 触らない）

- ⚠️★★★ **`Form_G1/` は 1 バイトも触らない**（G1 実施中）。読み取り（ハッシュ比較・関数一覧）のみ可。
- O1 のフォーム / トリガ（2026-08-29 に配備完了。触ると被験者に影響する）
- 配布 zip（→ `next-session-prompt-o1-macos-distribution.md`）
- ⚠️ **リマインダーを O1 に実装すること**。★ 送るか否かは研究者判断であり、
  本タスクは**表を作って提案するところまで**（引き継ぎ §4 の明示指示）。

## 運用メモ

- /reimagine 適用: **No**
- 理由: 実装ではなく「差分を読んで正本を決める」作業であり、方式の選択肢が無い
  （GAS が唯一のコピーなので取り込み方向は一意）。T-25 の実装も `decisions.md` G-1 で
  方式が確定済み。⚠️ ただし G-1 の想定より GAS が先行していたため、**実装形は D-1 で更新**した。
