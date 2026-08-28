# タスクリスト — O1 の配備インフラ ＋ 打鍵の実機確認

## A. 打鍵の実機確認（★ 研究者がタイプ）

- [x] `cargo build --manifest-path src-tauri/Cargo.toml --bin gse-next`（exit 0）
- [x] `GSE_O1_MODE=1 GSE_DATASET=<スクラッチ>` で起動（`O1 MODE ENABLED (source=env)`）
- [x] ⚠️ 送信経路が閉じていることを**先に**確認（`g1-submit.json` 不在 ＋ `o1_consent_ack` 不在）
- [x] ★★★ **`key` 行が出る**（「開始する」を押していないのに）— **184 本**
- [x] ⚠️ **生 VK が 1 つも無い** — フィールド集合は `['category','press','t','type']` の 1 種類のみ
- [x] `category` に量子化（`alphabetic 118 / backspace 38 / space 14 / enter 10 / punctuation 2 / modifier 2`）
- [x] `feat.keys` が 0 でない（最大 70・`keys>0` が 2124/2338 行）
- [x] トレイ「GSE — 計測中」
- [x] `meta` に `"o1_mode":"env"`
- [x] ⚠️ **`hook_health.starved_ms` が 0 のまま** → ★ **成り立たなかった**（判断 A-2）
  - [x] 原因を一次資料で特定（`liveness.rs` の既知の限界・`CALLBACK_COUNT` はキーボードのみ）
  - [x] ★ 120 秒 `Down` → トレイ警告 → 生存中フックの再設置まで**実測**

## B. UI のクリック通し（★ 研究者が操作）

- [x] ⚠️ `ERR_CONNECTION_REFUSED` の原因特定と解消（debug ビルドは `devUrl` を見る → Vite 起動）
- [x] **宣言 4 択** → ローテート／新ファイルに `session_meta`（`vibe_coding`）／旧は未宣言のまま
  - [x] ★ 旧 `session_end` = 新 `session_start`（**同一値** = 隙間も重複も無い）
  - [x] ★ 副産物: `intervention_enabled: false`（O1 で介入 OFF）
- [x] **すぐ止める** → `recording_pause` 2 行／★ **停止 7.2 秒のあいだ `feat` 行 0 本**／トレイ `Stopped`
- [x] **開始前ゲート** → ★ **両方向を実測**（押す前は `O1 auto-submit` 行が 0／押した後は出る）
  - [x] ★ 副産物: `packaged:0`（48 時間の猶予が効いている）／`upload_disabled:true`（外に出ていない）
- [ ] ⚠️ **「この時間帯の記録を消す」** — ★ **未実施**（削除前ローテートが効くかは未確認）
- [ ] ⚠️ 後始末: 検証で作られた `~/.gse/o1_participant_id`（`P009`）と `o1_consent_ack` を消す

## C. 配備インフラ

- [x] **C-1 研究者判断**: O1 は **別に立てる**（新プロジェクト C ＋ 専用 Drive フォルダ ＋ 専用 secret）
  - [x] ⚠️ 前提の誤りを実測で発見（G1 の `sanitizeName_` は O1 名を **`bad name` で全弾き**）
  - [x] `Form_G1/GSE_O1_Submit.gs` を新規作成（★ G1 の `.gs` は 1 バイトも変えていない）
  - [x] `MAX_BYTES` を**実測**で決定（`.age` 5,730,783 B / 7.21h → 24h 換算 約 18 MB → 48 MB 採用）
  - [x] `Form_G1/o1_submit_guard_test.cjs`（41 ケース）＋ ★ **変異テスト 11/11 赤**
  - [x] `run.sh §4` に接続（`guard_count()` が 41 と読めることを実測）
  - [ ] ⚠️ **配備は未実施**（★ Apps Script への貼り付け・スクリプトプロパティ・デプロイは研究者）
- [x] **C-2 研究者判断**: age 公開鍵は **G1 と共用**（現行 `resources/pubkey.txt`・追加作業なし）
- [ ] **C-3** O1 用 `g1-submit.json`（endpoint ＋ secret）を配布フォルダに置く
  - [x] ★ 手順を `.gs` の配備手順に記載（⚠️ ファイル名は `g1-submit.json` のまま・中身で行き先が決まる）
  - [ ] ⚠️ 実物は受け口のデプロイ後（研究者が `/exec` URL を控えてから）
- [ ] **C-4** O1 のフォーム類（⚠️ 現在 0 件）: 参加登録（P-ID 採番・受付メール）／終了後アンケート
- [ ] **C-5** 配布物に `o1.mode` を入れる（★ 対象は `make-distribution.sh` / `make-common-app-zip.sh`）
- [ ] **C-6** 同意文書の研究責任者・所属・連絡先（⚠️ **研究者の情報待ち**）
- [ ] **C-7 (R-14)** 送信済み分の削除手順を台帳に載せる（ADR-014 D8 制約 3）

## 起票のみ（★ 本タスクでは実装しない）

- [ ] **R-15** 時計の前進で猶予が消える（研究者判断・別タスク）
- [ ] ★ **新規**: O1 で「マウスのみの作業」が 2 分続くと誤警告＋生存中フックの再設置
      （研究者判断 2026-08-28・別タスク。⚠️ **被験者を走らせる前に解消すること**）
- [ ] **F-12**（前タスクからの持ち越し）: `reconcile` の 34 テストが CI で走っていない
      （`--features package` gate。⚠️ 48 時間の猶予を守る当の機構が CI の外）

## 検証

- [x] `node Form_G1/o1_submit_guard_test.cjs` → 41/41
- [x] ★ 変異テスト 11/11 赤（ガードが空回りしていない）
- [x] ★ ケース数下限が効く（5 件に削ると exit 1）
- [x] `bash -n run.sh`（構文 OK）
- [ ] `node Form_G1/submit_guard_test.cjs`（★ G1 側の非回帰。`.gs` は触っていないが念のため）
- [ ] ⚠️ CI（★ **未実行**。走らせるまで「緑」と書かない）
- [ ] code-reviewer + security-checker（並列）／`/cross-review`
