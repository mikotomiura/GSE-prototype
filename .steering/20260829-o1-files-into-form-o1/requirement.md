# O1 のファイルを `Form_O1/` へ移す

## 背景

★ O1 (R3-a) のファイル 5 本が **`Form_G1/` の中にある**:

```
Form_G1/GSE_O1_Submit.gs
Form_G1/GSE_O1_Form_Builder.gs
Form_G1/o1_submit_guard_test.cjs
Form_G1/o1_form_builder_test.cjs
Form_G1/o1_form_builder_mutation_test.sh
```

⚠️ ディレクトリ名と中身が食い違っており、★ **「G1 のものだと思って触る」事故の温床**である
(2026-08-07 に `setupG1Forms` の誤実行で G1-C の全設問が消えた事故と同じ型の危険)。
★ `Form_O1/` は既にあるが、⚠️ いまは研究者のローカル手控え 1 本しか入っていない。

## ゴール

★ O1 のファイルを `Form_O1/` に移し、⚠️ **全ての参照を追随させて機械検査を緑のまま保つ**。

## スコープ

### 含むもの
- `git mv` による 5 本の移動 (★ 履歴を保つ)
- ⚠️★★★ **`.gitignore` の `Form_O1/` を先に直す** (→ 下記の罠 1)
- 参照の更新: ゲート / `run.sh` / `make-common-app-zip.sh` / テスト 2 本 / 変異テスト /
  `.gs` のヘッダ / `submission.rs` の doc / docs / `.steering/` / 引き継ぎ

### 含まないもの
- ⚠️ `Form_G1/` に残る **G1 のファイルは 1 つも触らない** (★ G1 は実施中)
- ⚠️ O1 のファイルの**中身の変更** (★ 参照パスの表記を除く)

## ⚠️★★★ 事前に分かっている罠 (一次資料で確認済み)

1. **`.gitignore:84` に `Form_O1/` がある。**
   ⚠️ そのまま移すと **O1 のソースが丸ごと git から消える** (★ 追跡外になり、push しても届かない)。
   → ★ 無視するのは **`Form_O1/Drive関連情報.md` だけ**に変える。
2. **`o1_form_builder_test.cjs:22` が `path.join(__dirname, "GSE_G1_Form_Builder.gs")`** で
   ⚠️ **G1 のビルダーを読んでいる** (★ 拒否リストの突き合わせ)。
   → ★ 移すと `__dirname` が `Form_O1/` になるので **`REPO/Form_G1/…` へ書き換える**。
3. **ゲートの `--selftest` は `$fix/w/Form_G1/` へ写している** (★ `build()`)。
   → ⚠️ `Form_O1/` を作って写す側も直さないと、selftest が**空回りする**。

## 受け入れ条件

- [ ] ⚠️★★★ `git status` / `git ls-files` で **5 本が追跡されている** (★ 無視されていない)
- [ ] `bash scripts/check-o1-release-readiness.sh` が **通過 13 / 未達 1** のまま
- [ ] `--selftest` が **28/28** のまま
- [ ] `node Form_O1/o1_submit_guard_test.cjs` (44) / `o1_form_builder_test.cjs` (96) が緑
- [ ] `bash Form_O1/o1_form_builder_mutation_test.sh` が **25 変異すべて赤**
- [ ] `make-common-app-zip.sh --selftest` が **17/17**
- [ ] `cd src-tauri && cargo test --features package --workspace` が緑
- [ ] ⚠️ `Form_G1/` に **O1 のファイルが 1 本も残っていない**
- [ ] ⚠️ repo 全体に **`Form_G1/GSE_O1` / `Form_G1/o1_` を指す記述が残っていない**
