# タスクリスト — O1 のフォーム類 (C-4) ＋ 配布物の o1.mode (C-5)

★ 単一の真実源は `bash scripts/check-o1-release-readiness.sh`。
⚠️ 本ファイルではなくゲートを信じること（★ 2026-08-27 / 08-28 に古い記述による誤報が 2 回起きている）。

## ゲートの推移（★ 実測）

| いつ | 通過 / 未達 | selftest |
|---|---|---|
| セッション開始時 | **8 / 6** | 18 / 18 |
| セッション終了時 | ★ **12 / 2** | ★ **22 / 22** |

⚠️ **残る 2 件は意図的に残した**（引き継ぎ §2 #3 / #1・研究者判断で別タスク）:
- ❌ O1 で liveness の閾値が G1 と同じ（マウスのみ 2 分で誤警告）
- ❌ 送信 timeout が 180 秒固定のまま（★ 1 日ぶんが入りきるか**未実測**）

## C-4 O1 のフォーム類

- [x] `Form_O1/GSE_O1_Form_Builder.gs` を新規作成（⚠️ G1 の `.gs` は **1 バイトも変えていない**）
  - [x] **O1-C 参加登録＝説明・同意**（★ 同意の正本）— 同意 11 項目 ＋ 氏名 / メール / P-ID / OS
  - [x] **O1-S 終了後アンケート** — 受容性・負担（ADR-014 D8）＋ 宣言 UI の使い勝手（研究者判断 2）
  - [x] P-ID 採番（★ **Phase1 ロスターただ 1 つ**から・冪等）
  - [x] 受付メール（★ 参加者 ID / アプリ入手 / **自動起動** / 3 点セット。⚠️ 課題ページの話は 0 文字）
  - [x] ★ `checkO1FormConfig()`（読み取り専用の配備前チェック）
  - [x] ★ `migrateO1ConsentForm()`（★ 回答を保ったまま更新する経路）
- [x] ⚠️★★★ **G1 のフォームを壊さない 3 段**
  - [x] 段 1: 別プロジェクトに貼る（配備手順に明記）
  - [x] 段 2: `o1AssertNotG1Form_` が G1 の 3 フォーム ID を**拒否**（★ `openById` より**前**）
  - [x] 段 3: `o1AssertSafeToRebuild_` が回答のあるフォームを守る（既定 fail-closed）
- [x] `Form_O1/o1_form_builder_test.cjs` → ★ **89 ケース全通過**（★ レビュー後に 10 件追加）
- [x] `Form_O1/o1_form_builder_mutation_test.sh` → ★ **25 変異すべて赤**（★ レビュー指摘のガードにも変異を追加）
  - [x] ⚠️ 変異テストが**検査の穴を 1 件見つけた**（★ `installO1ConsentTrigger` の検査が
        「G1 フォームが存在しない」で緑になっていた）→ 検査を直した
  - [x] ⚠️ **効いていない変異を 1 件見つけた**（★ 置換後に後続行の連結が生き残っていた）→ 変異を直した
- [x] ★ 実装のバグを 1 件発見・修正: `o1NextParticipantId_` の `last > 1`
      （⚠️ **1 行だけのロスターで既存 P-ID を見落とし、同じ ID を再発番する**）

## C-5 配布物に o1.mode を入れる

- [x] `dist-readme-macos-o1.txt` / `dist-readme-windows-o1.txt`（⚠️ **【ドラフト・未承認】**）
  - [x] ★ 自動起動の手順（研究者判断 1）: mac = ログイン項目 / Win = `shell:startup` へショートカット
  - [x] ★ 3 点セット（印 / すぐ止める / 時間帯を指定して削除）と 48 時間の猶予
  - [x] ⚠️ G1 の 4 語（Gatekeeper 経路は同じなので必要）を保持
- [x] `launch-o1-windows.bat`（⚠️ ★ **G1 と挙動が 3 か所ちがう**: 殺さない / `pause` を置かない / 読み上げない）
- [x] `make-common-app-zip.sh --mode g1|o1`
  - [x] ⚠️★★★ **既定 g1 の経路は不変**（★ 削除行はすべて `${LABEL}` かモード分岐の同値に置換）
  - [x] マーカーは **literal で 2 行**（★ 変数にするとゲートの grep から見えなくなる）
  - [x] ★ マーカーの**取り違え検査**（片方が入っていたらもう片方が無いこと）
  - [x] `--selftest` → ★ **14 / 14**（⚠️ macOS 不要の範囲のみ）
- [ ] ⚠️★★★ **macOS 実機での実行は未実施**（`ditto` / `hdiutil` / `codesign` は本機に無い）
- [ ] ⚠️★★ **被験者向け文面は未承認**（★ 研究者の承認が要る）

## ★ 追加でやったこと（★ ゲートが赤で保持していた 2 件）

- [x] **保管上限の確定**（研究者判断 3）→ `docs/o1-deletion-ledger.md` §5 ＋ マーカを `set` に
  - [x] `.age` **2 年** / 復号済み平文 **解析完了後 30 日** / `metrics.json` **論文発表後 5 年**
  - [x] ★ 同意文書 §5 とフォームの `O1_RETENTION_*` にも同じ値を入れた（★ 3 か所と明記）
- [x] **`sync-session.*` の O1 ガード**（⚠️ 通すと削除が git 履歴の書き換えになる）
  - [x] `.sh` / `.ps1` の**両方**を同じ規則で（名前 `gse_o1_` ＋ `meta` の `o1_mode`）→ exit 4
  - [x] `scripts/sync_session_o1_guard_test.sh` → ★ **11 / 11**（★ 陽性対照つき・両実装を実行）
- [x] **ゲートの検査を実体化**（★ 旧版は「ファイルがある」「語が出てくる」しか見ていなかった）
  - [x] フォームビルダー → ガード検査の**実行**に差し替え
  - [x] sync ガード → **弾くことを示すテスト**を要求
  - [x] selftest を再構成（★ 緑になった 3 件を「壊すと赤」側へ移し、片側破壊の検査を両方向に）

## 検証（★ 実行した結果）

- [x] `node Form_O1/o1_form_builder_test.cjs` → **96 / 96**
- [x] `bash Form_O1/o1_form_builder_mutation_test.sh` → **25 変異すべて赤**
- [x] `bash scripts/sync_session_o1_guard_test.sh` → **13 / 13**（★ `.ps1` も実行済み）
- [x] `bash make-common-app-zip.sh --selftest` → **14 / 14**
- [x] `bash -n` — `make-common-app-zip.sh` / `run.sh` / `sync-session.sh` / `check-o1-release-readiness.sh`
- [x] ★ G1 非回帰: `guard_test` 4 / `submit_guard_test` 33 / `o1_submit_guard_test` 44 /
      `run_sheet_migration_test` 緑 / `materials_autosend_test` 緑
- [x] `cargo test --features package --workspace` → ★ **597 passed / 0 failed**（10 バイナリ・exit 0）
      —— ⚠️ 引き継ぎ §3 の「未実行」を**閉じた**
- [x] `bash scripts/check-o1-release-readiness.sh` → **通過 12 / 未達 2**
- [x] `--selftest` → **22 / 22**
- [x] code-reviewer ＋ security-checker（★ 並列）→ ⚠️ **HIGH 4 / MEDIUM 8 / LOW 6**
      → ★ **HIGH 4 件・MEDIUM 8 件を修正**（★ 詳細は `decisions.md` 判断 R）
  - [x] ⚠️★★★ 他人の P-ID を名乗れる欠陥（security HIGH）→ 照合順を変え `conflict` で止める
  - [x] ⚠️★★★ P-ID 列が空の行で 1 人に 2 つの ID ができる（code HIGH）→ ★ 自分で再現して修正
  - [x] ⚠️★★★ `--mode o1` が G1 の配布物を消す（code HIGH）→ 自分のモードだけ消す
  - [x] ⚠️★★★ 設定不備でもトリガを張る（code HIGH）→ fail-closed
  - [x] ⚠️★★ アンケートが**動機を尋ねていた**（★ 同意 §4 違反）→ 設問と検査の両方を直した
  - [x] ⚠️★★ `grep -q` の **SIGPIPE fail-open**（★ 400KB で実測）→ `grep -c` ＋ 陰性対照
  - [x] ⚠️★★ `GmailApp` が **Gmail 全体のスコープ**を要求する → コードから削除
- [x] ★ **CI 緑**（run `33143273205` / 2026-08-28・★ 研究者の承認を得て push した）
      - ✅ `check (gse-win-selfhosted, x86_64-pc-windows-msvc)` 10m3s
      - ✅ `check (gse-mac-selfhosted, aarch64-apple-darwin)` 8m19s
      - ✅ `frontend-check` 21s ／ ✅ `decide-win-runner` 12s
      - ⚠️ `build-macos` / `build-windows` / `release` は **skipped**（★ `v*` タグ push 用のジョブ）
      - ⚠️ ★ 本コミットは Rust を 1 行も変えていないので、CI が見たのは**非回帰**である
- [x] `/cross-review`（Codex 系統）→ ⚠️ **高 1 / 中 2 / 低 1**（★ Claude の 2 エージェントが見落とした分）
      → ★ 高・中の 3 件を修正、低 1 件は**境界をテストで固定**（詳細は `decisions.md` 判断 X）

## ⚠️ 外界に触っていないこと（★ 明示する）

- ⚠️ **Apps Script への貼り付け・スクリプトプロパティ設定・デプロイ・トリガ設置は 1 つもしていない**
- ⚠️ **Google フォームを 1 本も作っていない / 開いていない**（`FORM_ID_O1_*` は空のまま）
- ⚠️ **メールを 1 通も送っていない**（`MailApp` はテストのスタブのみ）
- ⚠️ **Drive を 1 バイトも変更していない**
- ⚠️ **gse-dataset に何も push していない**
