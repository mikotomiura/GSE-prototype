# 詰まりと解決

## 起票 1: macOS `secure_input` 行の実送出状況が不明（P4）

- **起票日**: 2026-09-11
- **状態**: 未解決
- **内容**: `src-tauri/src/schema_dto.rs` の doc コメントは `secure_input` 行について
  「2026-08-23 時点で送出元なし（スタブ）」と書いているが、`src-tauri/src/input/observe_macos.rs` は
  `SECURE_INPUT_AVAILABLE = true` になっている。**doc とコードが食い違っている。**
- **なぜ問題か**: ⚠️ `secure_input`（パスワード欄など macOS が入力を秘匿する状態）が
  記録されないまま O1 を配布すると、**「打鍵ゼロ」と「打鍵が見えない」が区別できないデータ**が
  本番に紛れ込む。停滞の誤判定に直結する。
- **どう処理するか**: 確認作業は 5 分程度で issue の粒度に満たないため、
  **Wave 0 完了時のチェック項目として処理する**（`decisions.md` 判断 5）。
  1. `observe_macos.rs` が実際に `secure_input` 行を送出しているかコードで確認
  2. 送出していれば `schema_dto.rs` の doc を訂正
  3. 送出していなければ `SECURE_INPUT_AVAILABLE` を `false` にするか、送出を実装する
  4. ⚠️ どちらにせよ **O1 配布前に決着させる**
- **解決**: （未）

## 起票 2: `gse-dataset` 側 `metrics.json` の後方互換

- **起票日**: 2026-09-11
- **状態**: 未解決（外部 repo のため本タスクでは確認のみ）
- **内容**: ADR-024 が `metrics.rs` の識別子を改名する（`recovery` → `pflow_exit`、
  `self_recovery_without_paste` → `pflow_exit_without_receipt` 等）。
  ⚠️ **ADR-024 自身が「`gse-dataset` 側 `metrics/P*/<os>/metrics.json` の後方互換は
  実在する懸念」と自認している。**
- **なぜ問題か**: `gse-dataset`（private repo・本機では `C:\gse-dataset`）に
  既に置かれている `metrics.json` は旧フィールド名を持つ。
  ⚠️ **schema drift check の対象外**なので、壊れても無音。
- **どう処理するか**:
  1. issue 001 の実行時に `C:\gse-dataset` の `metrics/P*/<os>/metrics.json` を確認
  2. 旧フィールド名を使っている既存ファイルがあるか、`scripts/build_analysis_db.py` が
     新旧どちらを期待するかを突き合わせる
  3. ⚠️ **外部 repo を勝手に書き換えない。** 対応が要るなら研究者にエスカレートする
- **解決**: （未）

## 起票 3: `_issue-plan.md` の自己検査で `acceptance.sh` が未作成

- **起票日**: 2026-09-11
- **状態**: 未解決
- **内容**: `issue-slicing` の締めの自己検査項目
  「**test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか**」が未実施。
- **なぜ問題か**: ⚠️ issue 002 / 003 / 005 / 006 は**何も取り込まなくても**
  `check_doc_lexicon.py` / `check_citations.py` が exit 0 になる。
  このまま無人ループに載せると「**客観に見えて無意味な緑**」を量産する
  （`docs/loop-engineering.md` が警告する failure mode そのもの）。
- **どう処理するか**: 実行セッションで各 issue に `acceptance.sh` を書く。例:
  - 002: ADR-025〜028 の 4 ファイルが存在し、README のテーブルに ADR-023〜028 の 6 行がある
  - 003: `references.md` に `[P356]` と `[V145]` が存在し、`literature/` に新規カード 3 本がある
  - 005: `mitou_submission/` の図版数が取り込み前より増えている
  - 006: 7 ファイルそれぞれに branch 側の差分が反映されている
- **解決**: （未）
