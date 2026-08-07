# タスクリスト

⚠️ ★ **`/reimagine` 適用 = Yes**。設計 (§2) を承認する前に一度破棄して作り直す。

## 0. 準備

- [x] ★ `data-privacy` Skill を読む（**外部送信を足すので必須**）
      → ⚠️ ★ **ルール 3 との緊張が 1 件出た**（`decisions.md` の「まだ決めていないこと」#5）
- [x] ★ `browser-verification` Skill を読む（GAS を実機で触るため）
- [x] `architecture-rules` / `rust-standards` / `typescript-standards` を読む
- [ ] `.steering/20260805-g1-app-mode-and-log-rotation/decisions.md` R-7 / R-8 / **R-9** を読む
      （★ R-9 は「蒸し返さない」ことの確認）
- [ ] `experiments/.../consent.md` §3 と `participant-guide.md` を読む（★ 何を約束済みか）
- [x] ⚠️ 環境: `~/.rustup/toolchains/stable-aarch64-apple-darwin/bin` を PATH に足す
      （`requirement.md` 環境メモ。★ 足さないと `run.sh` の cargo ゲートが飛ぶ）

## 1. 調査

- [x] `packaging.rs` の匿名化がどこで `vk` → `category` に落としているかを読む
      → `anonymize_ndjson` に委譲。★ 新経路 (`package_session_as`) も**同じ 1 本**を通る
- [x] `find_latest_session_ndjson` の呼び出し元をすべて洗う → 本番は `submit.rs` の **1 箇所だけ**。
      `resolve_input` に切り出し、★ **指定なしの経路は 1 バイトも変えていない**
- [x] ⚠️ ★ **この問いを捨てた。** 収束型ではパスを渡さない (`design.md` §1)。
      渡す設計だと ★ 渡し忘れが「書きかけを包む」形になるので、
      **`session_end` を持つファイルだけを拾う**構造にした (`reconcile::closed_sessions`)
- [x] Tauri 2.0 で HTTP を出す経路と CSP → ★ **どちらも使わない**。送信は Rust の別プロセス
      (`gse-submit --reconcile`) なので **CSP を 1 文字も触らない** (D-7)
- [x] ⚠️ GAS Web App の **POST サイズ上限**を実測する → `gas-measurements.md` §2
      （★ 300 KB は 1.45 s で通過。**50 MB まで通ったところで打ち切り＝上限は未到達**）
- [ ] ⚠️ GAS の**実行時間上限** → ★ **未実測のまま。** 測る関数 (`measureSaveTiming()`) は
      用意した。⚠️ ★ **研究者が Apps Script で 1 回実行する必要がある**
      (セレクタが自動操作を受け付けないため)
- [x] ⚠️★ **Q-3**: GAS の実行ログに**接続元・日時が何まで残るか**を実測する
      → `gas-measurements.md` §1（★ **陽性対照つき**。⚠️ Google 社内の記録は確認不能と明記）
- [x] ★ 「× で閉じてもプロセスが残る」→ ★ **D-10 で決着（直さない）**。
      `CloseRequested`/`ExitRequested` が無いことを grep で確認したうえで、
      ★ **依存しない設計にした**（収束型 + D-9 の合図で最後のブロックもその場で送る）

## 2. 設計

- [x] design.md を書く（送信の実行主体・キューの形・ブロック番号の採り方）
- [x] ★ **`/reimagine`**: requirement.md だけを見て v2 案を作り、2 案を比較して採用を決める
      → ★ **v2（収束型）を採用**（研究者判断 2026-08-07）。`design-v1.md` / `design-comparison.md`
- [x] decisions.md の「まだ決めていないこと」のうち **#1 送信の実行主体 / #2 ブロック番号 /
      #3 シークレットの置き場所** を design.md で閉じた（★ #3 は security-checker の確認待ち）
- [x] ⚠️ ★ **#5 `data-privacy` ルール 3-1 との整合**を security-checker に明示的に問うた（§5 に結果）
- [x] ★ `consent.md` の**文案**を出す → `consent-draft.md`（★ 実装より先）
- [x] ⚠️ ★ 研究者が `consent-draft.md` §5 の **Q-1〜Q-4** を判断する
      → ★ **Q-1 / Q-2 / Q-4 = 研究者判断（D-4 / D-5 / D-6）**、**Q-3 = 実測で確定**
- [x] ★ `consent.md` / `Form_G1/README.md` / `protocol.md §4.1-1` ＋ `GSE_G1_Form_Builder.gs` を
      **同時に**直した（★ **4 箇所**。同意項目は 8 つに）
- [ ] ⚠️★ **研究者が Apps Script で `checkConsentFormParity()` を 1 回実行**（読み取り専用）。
      ★ `✅ G1-C はコードと一致している` を確認する。
      ⚠️ **`migrateConsentForm()` は実行不要**（事故で走った `setupG1Forms` が結果的に
      同じ状態にしたため、いま走らせても挿入 0 件）

## 3. 実装

- [x] **B**: `gse-submit` に `--input <path>` を追加（★ ゼロ引数の既定挙動は不変）
- [x] **A**: G1 モード時のスタート画面に参加者 ID 欄。妥当な ID まで「開始する」を無効化
      ★ **バックエンドにも gate を置いた** (`start_session` → `g1_start_gate`。二重 gate)
- [x] **A**: ID の永続化と次回起動時の復元（`~/.gse/g1_participant_id`。
      ⚠️ ★ logger が自動生成する `~/.gse/participant_id` とは**別ファイル**にした）
- [x] **C**: ブロック自動終了時に収束器を起こす（★ **パスを指定しない**。D-9 の合図を待ってから）
- [x] **D**: 送信 + 失敗時のローカル保持 + 再送 → ★ **「再送」という処理は無い**
      （`.sent` が無ければ送る、それだけ）
- [x] **E**: スタート画面の「未送信 N 件」（★ 0 件なら何も出さない）＋ 自動提出の失敗表示
- [x] **G**: GAS Web App (`doPost`) の**実装**（`Form_G1/GSE_G1_Submit.gs`）
      ⚠️ ★ **配備は未実施**（研究者が手で行う。セレクタが自動操作を受け付けない）

## 4. テスト（★ 足したら、その場でわざと壊して赤を実測する）

- [x] `--input` の単体テスト（存在しないパス / 別ディレクトリ / 既定との共存）★ 破壊で赤を実測
- [x] ★ **匿名化の実測**: `reconcile::tests::generated_age_is_anonymized` が**復号して**確認
- [x] ★ ID 未入力で開始できないこと → `submission::tests::start_gate_blocks_g1_without_valid_id`
      ★ ゲートを常時 Ok にして**赤を実測**。⚠️ **UI の disabled はテストしていない**
      (フロントのテスト基盤がこの repo に無い)
- [x] ★ 送信失敗 → ローカル保持 → 再送 の一巡（`FailUploader` で実測。
      ⚠️ ★ **実エンドポイントには投げていない**）
- [x] ★ **通常運用（マーカー無し）で画面も挙動も変わらない**非回帰
      （`g1_start_gate` の非回帰テスト / UI は `g1Mode !== null` で全て包んだ / golden 4 本緑）
- [x] `cargo test --workspace` (286) / `--features package` (301 + bin 7 + 2)
- [x] `gse-replay --snapshot` golden 4 本緑 / `emit_schema` byte-equal / `npx tsc --noEmit` 緑
- [x] `bash run.sh` GREEN（★ cargo ゲートが "2 / 2 本" で**実際に走った**ことを確認）
      ＋ ★ 受け口ガード検査 (16 ケース) を `run.sh §4` に接続し、**7 種の破壊で赤を実測**

## 5. レビュー

- [x] `code-reviewer` と **`security-checker`** を並列起動（★ 外部送信なので security 必須）
- [x] HIGH 指摘への対応（HIGH 4 / MEDIUM 5 / LOW 5 を反映。`notes.md §8-3c`・`decisions.md` D-12〜D-16）
      - ★ **data-privacy ルール 3-1 の判定**: security-checker は
        「読み替え自体は成立する（マーカー＋設定ファイルの **2 つの独立したスイッチ**が
        両方揃わないと送信経路が存在しない = チェックボックスの既定 OFF より構造的に強い）。
        ただし **送信対象がその同意の範囲を超えていた**」→ ★ **範囲を絞って解消**
      - ★ ⚠️ **security-checker の MEDIUM-4（macOS 隔離の破れ）は実測で否定した**
        （`notes.md §8-3d`・陽性対照つき）
- [x] ⚠️★ `/cross-review` — **実施した（2026-08-07）**。★ Codex のレビュー本文が返ったことを
      目で確認している（`rc=0` だけを根拠にしていない）。
      - ★ **対象**: `reconcile.rs` + `submission.rs` + `GSE_G1_Submit.gs`（**1,890 insertions**・
        `manual_approval_threshold_lines` = 2,000 の内側）。
        ⚠️ `Cargo.lock` / `docs/` / `.steering/` / `experiments/` は送っていない。
      - ⚠️★★ **踏んだ罠 1**: `run-codex-review.sh` は `git diff`（未ステージ）しか見ないため、
        **コミット済みの本タスクは対象ゼロで rc=0** になる。
        → ★ wrapper に **範囲指定の引数**を足した（`git diff "$@"`）。
        ⚠️ 引数を渡したのに差分が空なら **exit 1** にした（rc=0 での誤読を塞ぐ）。
      - ⚠️★★ **踏んだ罠 2**: `secrets-filter.sh` が **rc=2（fail-closed）**でブロックした。
        ★ 一次資料まで降りて確認したところ **実体のある機密はゼロ**（`let secret = v` という
        変数束縛と、「`.gs` に `SHARED_SECRET` を書くな」という注意書きの 2 行だけ。
        フィルタ出力は入力と **byte-equal** = 1 バイトも伏せていない）。
        → ★ **研究者の明示承認**を得て、wrapper の `--ack-filtered`（既定は fail-closed のまま）で
        1 回だけ通した。⚠️ 自動では絶対に付けない旨を wrapper の先頭に書いた。
      - ★ **結果**: ⚠️ **Codex だけが見つけた穴が 1 件あった**（D-17）。
        Claude 側レビュー 2 本（code-reviewer / security-checker）は見落としていた。
        | # | Codex の指摘 | 判定 | 対応 |
        |---|---|---|---|
        | 1 | 受け口の名前検査が **同秒ローテートの連番 (`_2`)** を弾く | ⚠️★ **採用（実在）** | D-17。regex 修正＋両側に検査（破壊して赤を実測） |
        | 2 | 壊れた base64 が `server error` に丸まる | ★ 採用 | D-18。専用の理由を返す＋発火するテスト |
        | 3 | `age_for_stem` が participant を見ない | ★ **却下** | D-19。安全側に倒れる／絞ると二重送信が出る |
        | 4 | `is_closed_g1_session` の文字列一致が脆い | ★ **却下** | D-20。emit_schema ＋ golden が形を固定している |
        | 5 | `.ok` を付けた後に `.age` が消えた場合の再収束テストが無い | ★ 却下 | 消えた `.age` は**新しいブロック番号**で包み直されるので `.ok` は一致しない（`next_block_number` は max+1）。孤児 `.ok` は無害 |
      - ★ 重複報告はゼロだった（Claude 側で潰した 7 件と 1 件も重ならない）。
- [x] ⚠️★★ **2 周目**: 上の修正そのものを `security-checker` ＋ Codex に掛けた
      → ★ **レビュー基盤に足した仕掛けが新しい穴になっていた**（`decisions.md` **D-21**）。
      - ⚠️ `secrets-filter` は「大文字小文字無視」と**書いてあるだけ**で、
        `"secret": "…"`（★ `g1-submit.json` そのものの形）が **rc=0 で素通り**していた
      - ⚠️★ wrapper の引数が素通しで `git diff --no-index` が書け、
        **`.gitignore` した `g1-submit.json` に到達できた**（実測）
      - → 両方塞ぎ、`scripts/secrets-filter-test.sh`（17）と
        `scripts/run-codex-review-test.sh`（7）で**壊して赤を実測**した
      - ★ Codex の `ROOT` 未定義指摘は**誤検知**（差分の外で定義済み）
- [x] ~~⚠️★ `/cross-review` — 未実施~~（★ 以下は前セッションの skip 理由。経緯として残す）
      - ★ **予算はその場で計算した**（⚠️ メモの数字は使っていない）:
        - 全体差分 = **25 files / 4,395 insertions / 181 deletions = 4,576 行**
        - `.codex/budget.json` の `manual_approval_threshold_lines` = **2,000** → ★ **超過**
        - `diff_size_threshold_lines` = 500 → 超過 / `per_invocation_max` = 30,000 tokens
        - `today.date` は `2026-08-06` で**古い**（本日は 2026-08-08 なので日次カウンタはリセット扱い）
      - ★ そこで**新規コードの中核 3 ファイルだけ**に絞ったスライスを用意した
        （`reconcile.rs` + `submission.rs` + `GSE_G1_Submit.gs` = **1,890 insertions**・閾値内）
      - ⚠️★★ **skip 理由**: そのスライスでの `/cross-review` 起動が
        **本セッションの権限チェックで拒否された**（`codex` / `jq` は存在するので不在ではない。
        ⚠️ セッション後半は `Bash` / `Agent` / `Skill` の多くが同様に拒否されている）。
        → ★ **Claude 単独（`code-reviewer` ＋ `security-checker`）へ縮退した。**
      - ★ **次セッションでの再実行を推奨**（コマンド）:
        ```
        git diff docs/win-g1-measured-tests..HEAD -- \
          src-tauri/src/reconcile.rs src-tauri/src/submission.rs Form_G1/GSE_G1_Submit.gs
        ```
        ⚠️ Cargo.lock / docs / .steering / experiments は**送らない**（差分が閾値を超えるため）

## 6. ドキュメント

- [x] `consent.md` §3 は 8cb36f2 で記載済み。★ **実施前の停止条件を実態に合わせて更新**
      （コードは入った / ⚠️ **受け口の配備と通し確認が未実施**）
- [x] `participant-guide.md` / `protocol.md §4b.2`（提出の手作業を落とし、ID 入力と
      未送信件数の確認を足した）＋ 配布物一覧に `g1-submit.json` を追加
- [x] `docs/architecture.md` §4.13（収束型自動提出）＋ §6 の外部連携表に 1 行
- [x] `experiments/.../notes.md` §8（★ 実測したことだけ）＋ `gas-measurements.md §3` の未実測を明示

## 7. 完了処理

- [x] decisions.md に D-7〜D-11 を追記し、未確定 #1/#2/#3 を閉じた（残るは #5）
- [x] `/finish-task`（2026-08-07）
      - schema parity check: **skip**（★ `schema_dto.rs` / `schema/current.json` は触っていない）
      - `cargo test --workspace` **289** / `--features package` **311** + bin 23/7/2
      - golden 4 本 byte-equal / `emit_schema` byte-equal / `npx tsc --noEmit` 緑
      - `bash run.sh` **GREEN**（★ cargo ゲートが "2 / 2 本" で実走・受け口ガード **33 ケース**）
- [ ] ⚠️★ **push と PR** — ★ 研究者の判断待ち（前セッションは権限で拒否された）
