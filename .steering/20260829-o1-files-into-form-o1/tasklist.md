# タスクリスト

## 実装
- [x] ⚠️ `.gitignore` を先に直す（`Form_O1/` → `Form_O1/Drive関連情報.md`）
- [x] `git mv` で 5 本を移動（★ 全部 `R` = rename として記録された）
- [x] 参照の一括置換（22 ファイル）
- [x] ★ 構造的な 2 か所を手で修正（テストの G1 パス / ゲートの fixture）
- [x] ★ ゲートに「git に追跡されているか」の検査を追加

## テスト
- [x] ⚠️ **移動直後に壊れることを確認**（ゲート 13/1 → **9/3** / ビルダー検査クラッシュ）
- [x] `check-o1-release-readiness.sh` → **通過 14 / 未達 1**（★ 検査が 1 本増えた）
- [x] `--selftest` → **29/29**（22 → 28 → 29）
- [x] `node Form_O1/o1_submit_guard_test.cjs` → **44 ケース**緑
- [x] `node Form_O1/o1_form_builder_test.cjs` → **96 ケース**緑
- [x] `bash Form_O1/o1_form_builder_mutation_test.sh` → **25 変異すべて赤**
- [x] `make-common-app-zip.sh --selftest` → **17/17**
- [x] `cargo test --features package --workspace` → **564 passed**
- [x] ⚠️ `git ls-files Form_O1/` で **5 本が追跡**・手控えのみ無視を確認
- [x] ⚠️ 残存参照ゼロを確認（★ `requirement.md` の「背景」記述を除く）

## レビュー
- [x] code-reviewer ＋ security-checker（並列）→ ⚠️ **両者が同じ HIGH を独立に検出**
- [x] ⚠️★★★ **秘密の露出寸前を修正**（`Form_O1/o1_submit.json`・→ design.md）
  - [x] `.gitignore` を **deny-by-default ＋ 名前列挙**へ
  - [x] ゲートに「提出設定が git に入っていないか」を追加（★ 陽性を実物で撃って確認）
  - [x] 追跡検査を**ディスク走査**へ（★ `!` 行の足し忘れを捕まえる・実測で赤を確認）
  - [x] selftest の陰性対照を「**存在するのに未追跡**」へ強化（★ 旧版は実在しないパスでも通った）
  - [x] `scripts/secrets-filter.sh` の既知リストに `Form_O1/*.cjs` を追記
- [x] ★ 先行既存の問題を起票: **T-15**（G1 の配布 URL ＋ secret）/ T-16 / T-17 / T-18 / T-19 / T-20
- [ ] `/cross-review`（Codex）

## 完了処理
- [ ] git commit
