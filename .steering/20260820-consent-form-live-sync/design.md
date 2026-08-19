# 設計 — 実フォームへの反映手順

## なぜこの手順か（★ 既存の安全機構に乗る）

`GSE_G1_Form_Builder.gs` は 2026-08-07 の事故を受けて、既に必要な機構を持っている:

| 機構 | 役割 |
|---|---|
| 固定 ID 方式（`FormApp.create` を使わない） | 実行しても**フォーム ID が変わらない**＝配った URL が死なない |
| `ALLOW_REBUILD_WITH_RESPONSES = false` | 回答があるフォームの作り直しを **fail-closed で止める** |
| `migrateConsentForm()` | ★ `clearForm()` を呼ばない。説明文更新＋不足設問の挿入のみ |
| `checkConsentFormParity()` | 読み取り専用。実フォームを読んでコードと突き合わせる |

★ **新しい仕組みを作らない。** `migrateConsentForm()` を使う（README 126–127 行の指示どおり）。

## 手順

1. **公開 viewform を読む**（読み取り専用）— 実際に古いかを確定する
2. **デプロイ済みコードを退避**して repo 正本と `diff` — 上書きが他の変更を巻き込まないか確認
3. repo 正本を貼り付けて保存 → ★ **リロードして読み戻し**、byte-equal を確認
4. `checkConsentFormParity()` を実行（読み取り専用）— 現状の不一致を記録
5. `migrateConsentForm()` を実行 — 説明文を更新
6. ★ **公開 viewform を再度読む** — GAS の自己申告ではなく、被験者が見る側で確認

## ⚠️ この作業の危険源（実測記録あり）

★ **関数セレクタの表示は信用できない**（memory `gas-live-state-vs-code`）。
2026-08-07 は、選択したはずと違う関数（`buildConsentForm`）が走り、`clearForm()` が
同意回答 3 件の設問紐付けを壊した。⚠️ **Forms に回答の版履歴は無い。取り返しがつかない。**

→ 本タスクの対策:
- ★ **実行の直前に毎回セレクタを拡大して読む**（本タスクで実際に 2 回、選択が反映されていなかった）
- ★ 実行後は**実行ログでどの関数が走ったか**を確認する（表示ではなく結果で見る）
- ★ 回答が 6 件あるので `ALLOW_REBUILD_WITH_RESPONSES = false` のガードが**実際に効く状態**である
  ことを、`checkConsentFormParity()` の「既存回答 6 件」で確認してから進める

## 検証戦略（★ どちら側を見ているか）

⚠️ `checkConsentFormParity()` は **Apps Script プロジェクトのコード** と実フォームを比べる。
★ repo とプロジェクトがズレていると、**両方が古いまま ✅ になる**（memory
`name-lookup-only-works-within-one-source` の「鏡どうしを比べる」型）。
→ ★ 先に **repo → プロジェクト** を byte-equal にしてから parity を回す。
→ ★ 最後は **公開 viewform の本文**を読む（プロジェクトを介さない外部からの確認）。
