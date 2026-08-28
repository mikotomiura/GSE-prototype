# O1 ゲートの残り 2 件 ＋ 配備準備

## 背景

`scripts/check-o1-release-readiness.sh` が **通過 12 / 未達 2** で赤い（2026-08-28 実測）。
⚠️ このゲートが緑になるまで被験者を 1 人も走らせない、という契約になっている。

未達の 2 件と、前セッションで起票だけされた欠陥がある:

- **A-1** O1 の liveness 閾値が G1 と同じ（★ マウスのみ 2 分で「⚠ 計測できていません」が出る。
  ⚠️ O1 の宣言 4 択には「デザイン・映像・制作作業」があり、そこでは**常態**になる）
- **A-2** 送信 timeout が `from_secs(180)` 固定（★ 1 日ぶんが入りきるか**未実測**）
- **E-1** 削除後の案内が O1 で**逆を指している**（★ 案内に従うほど消せない状態に留まる）
- **F-12** `reconcile` の 34 テストが **CI で走っていない**（⚠️ 48 時間の猶予を守る当の機構）

## ゴール

★ AI だけで閉じられる範囲を**全部**閉じ、⚠️ 研究者の手作業に依存する分は
**何が残っているかを機械（ゲート）に持たせた状態**で引き渡す。

## スコープ

### 含むもの
- E-1 RecordingControls の O1 分岐漏れの修正
- A-1 O1 の liveness トレイ警告の切り離し（★ 研究者判断: トレイだけ 30 分）
- A-2 **ゲートの検査を「実測の記録があるか」に変える**（⚠️ 数字の書き換えでは緑にしない）
- F-12 CI に `--features package` を足す
- E-4 launcher の UTF-8 BOM / E-5 selftest-dump の二重管理
- E-2 / E-3（G1 側）の起票
- B-1 / B-2 の配備手順に、研究者から渡された Drive ID を差し込む

### 含まないもの
- ⚠️ **フォームの作成そのもの**（研究者判断 2026-08-28:「いまはやらない」）
- ⚠️ Apps Script への貼り付け・デプロイ・トリガ設置（★ 自動操作が効かないことを実測済み）
- ⚠️ `reconcile.rs` の timeout の**値の変更**（★ 実測が先。B-1 に依存する）
- ⚠️ macOS 実機での配布物（→ 別の引き継ぎ）
- ⚠️ B-4 削除 UI の実機クリック（★ 研究者が操作する）

## 受け入れ条件

- [ ] `bash scripts/check-o1-release-readiness.sh` の未達が **2 → 1** になる（★ A-1 が緑）
- [ ] ⚠️ A-2 は**赤のまま**だが、★ 「数字を書き換えるだけ」では緑にならないことを selftest が示す
- [ ] `--selftest` が全件通過し、★ **件数が増えている**（22 → 27）
- [ ] `cd src-tauri && cargo test --features package --workspace` が緑
- [ ] `npm run build`（tsc）が緑
- [ ] CI の `cargo test` に `--features package` が入っている

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-o1-gate-closeout-and-deployment.md`（★ 本タスクの上流）
- `src-tauri/src/input/liveness.rs`（★ 閾値の一次資料）
- `Form_O1/GSE_O1_Submit.gs` / `Form_O1/GSE_O1_Form_Builder.gs`（★ 配備手順の一次資料）
- `docs/o1-deletion-ledger.md`
