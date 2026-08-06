# 次セッション開始プロンプト — G1 自動提出の**実装**（第 2 版）

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-07 に **同意の確定・GAS の実測・設計 (`/reimagine`) まで完了**した。
★ **残っているのは実装だけ**（`tasklist.md §3` 以降）。
⚠️ ★ 第 1 版（Q-1〜Q-4 待ちの版）は**もう有効ではない**。git 履歴に残っている。

---

===

## §0 このセッションでやること

`.steering/20260806-g1-auto-submit-on-block-end/` の **`tasklist.md §3` 実装**を進める。

★ **最初に読むもの（この順）**:

1. `design.md` — ★ **採用済みの v2（収束型）**。⚠️ **ここが実装の契約である**
2. `decisions.md` — D-1〜D-6（確定）＋「まだ決めていないこと」#1/#2/#3/#5
3. `gas-measurements.md` — ★ **実測値。⚠️ 推測で上書きしない**
4. `incident-20260807-g1c-rebuild.md` — ⚠️ ★ **同じ穴を掘らないために必ず読む**
5. `requirement.md` の受け入れ条件

⚠️ ★ **`/reimagine` は適用済み（1 回目・v2 採用）。もう一度回さない。**
`design-v1.md`（却下案）と `design-comparison.md` に経緯がある。★ **v1 に戻さない。**

---

## §1 ★ 設計の核（`design.md` の要約。⚠️ これを崩さない）

★ **イベント駆動にしない。収束型にする。**

```
毎回、ディスクの状態を突き合わせて「足りない仕事」だけをする:

  ① 閉じ終わった NDJSON   … session_end を持つ、いま書いていないファイル
  ② それに対応する .age    … 無ければ作る（匿名化 → 暗号化）
  ③ それに対応する .sent   … 無ければ送る（成功したら .sent を置く）

  未送信 N 件 = ② が在って ③ が無いものの数   ← ★ 別カウンタを持たない
```

- ★ **ブロック終了 / アプリ起動は「ヒント」にすぎない。** 取りこぼしても次の機会に収束する。
- ★ **再送という特別処理を作らない**（`.sent` が無ければ送る、それだけ）。
- ★ **永続カウンタを作らない**（ズレるため。実際 `G1_BLOCKS_STARTED` は再起動でリセットされる）。
- ⚠️ ★ **ブロック中に走らせない。**
- ★ 置き場所は **`gse-submit`（`package` feature）**。⚠️ **盲検アプリ本体に `age` も HTTP も載せない。**
- ★ **CSP を 1 文字も触らない**（Rust の別プロセスから送るため）。

## §2 ★ 実測済み（**再調査しない**）

| 何 | 実測値 |
|---|---|
| GAS への POST | 匿名 `curl`（Cookie 無し）で **300 KB / 1.45 s / 200**。50 MB でも 200 = **上限未到達** |
| ⚠️ 302 | POST は **302 を返す** → ★ **リダイレクト追従が必須**。メソッドを強制すると **405** |
| ⚠️★ ヘッダ | GAS の `e` は `contextPath/parameter/parameters/queryString/contentLength/postData` の **6 キーだけ**。★ **ヘッダも IP も取れない** → 認証は**本文**に入れる（⚠️ クエリに置かない） |
| 研究者が見える記録 | 実行数ページの **6 列だけ**（導入/関数/種類/開始時間/期間/ステータス）。★ `console.log` 本文は出ない（陽性対照つきで確認）。Cloud ログは開けない |
| → 帰結 | ★ **送信の成否は送信先から追えない。** `.sent` が唯一の真実源 → **未送信件数の表示は必須の安全装置** |
| `find_latest_session_ndjson` | 本番の呼び出しは `submit.rs:222` の **1 箇所だけ** |
| 匿名化 | `packaging.rs` に集約。★ **`vk` が漏れないテストが既にある**（新経路でも使える） |
| `g1-block-ended` | emit は `lib.rs:2246` の **1 箇所**。その場に `block_log_tx` と `app_handle` がある |
| ★ 閉じたファイルのパス | ブロック終了時点では**まだローテートしていない** → **`current_path()` がそれ**（`lib.rs:860`） |
| `age` の隔離 | `gse-package`/`gse-unpack`/`gse-submit` が `required-features = ["package"]` |
| ⚠️ Rotate 失敗時の作法 | **触った状態を全部巻き戻して `Err`**（`lib.rs:1477-1490`）。★ **自動提出もこの厳しさに合わせる** |

## §3 ⚠️★ 実装前に閉じる 3 件

1. ★ **「× で閉じてもプロセスが残る」** — `lib.rs` が `overlay` という 2 つ目の窓を作り、
   Tauri は全窓が閉じたときに終了するので **overlay が残る限りプロセスが死なない**
   （`CloseRequested`/`ExitRequested` の処理が無い）。
   ⚠️ ★ **「アプリ起動時」がヒントの 1 つなので、起動の定義がこれに依存する。**
2. ⚠️ ★ **GAS の実行時間は `DriveApp` 保存込みで未実測**（`gas-measurements.md §3`）。
   ★ 本番 `doPost` を書いたら測る。**推測で埋めない。**
3. ⚠️ ★ **`data-privacy` ルール 3-1**（オプトイン UI・デフォルト OFF）との整合。
   同意は紙＋G1-C（8 項目目）で取り、アプリ側は「G1 マーカーが無ければ送信経路が無い」＝既定 OFF。
   ★ **この読み替えでよいかを `security-checker` に明示的に問う**（`decisions.md` 未確定 #5）。
   満たさないと判断されたら **G1 スタート画面に確認チェックを 1 つ足す**（縮退案）。

## §4 制約（厳守）

- ★★ `preregistration.md §3.1/§3.2/§3.4/§3.5/§3.6` を変更しない
- ★ `§5.4-2` の客観検証（probe 行 0）は**何があっても残す**
- ★ **通常運用（マーカー無し起動）を 1 ピクセルも変えない。** ID 欄も送信も **G1 モード限定**
- ★ **送るのは `.age` だけ。** 生 NDJSON を送る経路を作らない。★ **送信後も `.age` を消さない**
- ⚠️ ★ `ime_state` の session ゲートには触らない（`20260805` **R-9**・**蒸し返さない**）
- ⚠️ ★ **`schema_dto.rs` を変えない**（ブロック番号を `session_meta` に足す案は
  schema drift と gse-dataset 整合まで波及するので**却下済み**。manifest 側で持つ）
- **PII**: 実名・メール・セッション日時 / NDJSON ファイル名を成果物に出さない
- ★ Rust は `rust-standards` / `architecture-rules`、外部送信なので **`data-privacy` を先に読む**

## §5 ⚠️ 環境の罠（★ 先に読む）

| 罠 | 中身 |
|---|---|
| ⚠️★★ `~/.cargo/bin/cargo` が壊れている | rustup shim が dangling。実体は **`~/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo`**（1.97.1）。★ **PATH に足さないと `run.sh` の cargo ゲートが「飛ばした」と言って素通りする** |
| repo 直下の `cargo test --workspace` は空振り | `Cargo.toml` は `src-tauri/`。`cd src-tauri` か `--manifest-path` |
| `run.sh` は未コミット変更で RED | `src-tauri/` `src/` に未コミット変更があると FAIL。**ゲートが仕様どおり働いているだけ** |
| ⚠️★★ **Apps Script の関数セレクタは自動操作を受け付けない** | option クリックもキーボードも効かず `setupG1Forms` のまま。★ **これで事故を起こした**（`incident-…md`）。⚠️ **自動で実行しようとしない。人に依頼する** |
| ⚠️★ Apps Script の保存 | 「変更が保存されていません」表示のまま**保存が通っていない**ことがある。★ **リロードして実体のハッシュで確かめる** |

## §6 終わり方

- `bash run.sh` が **GREEN (rc=0)**（★ cargo ゲートが "N / N 本" で**実際に走った**ことを確認）
- `cargo test --workspace` / `--features package` / golden / `emit_schema` byte-equal / `npx tsc --noEmit`
- ★ **検査を足したら、その場でわざと壊して赤を実測する**（後回しにしない）
- `code-reviewer` ＋ **`security-checker`** を並列（★ 外部送信なので security 必須。§3-3 を明示的に問う）
- 最後に `/cross-review`（★ 予算は**その場で計算する**。⚠️ **メモの数字を根拠にしない**）

## §7 ★ 研究者にお願いしている宿題（未完）

1. ⚠️ **Apps Script で `checkConsentFormParity()` を 1 回実行**（読み取り専用）。
   ★ `✅ G1-C はコードと一致している（同意項目 8 件・既存回答 3 件）` が出れば確定。
   ⚠️ ★ **`migrateConsentForm()` は実行不要**（事故で走った `setupG1Forms` が結果的に
   同じ状態にしたため、いま走らせても挿入 0 件）。
2. `docs/win-g1-measured-tests`（3 コミット）が **未 push**。
   ⚠️ ★ 本セッションで `git push` が **2 回とも権限で拒否**された。★ **PR は出せていない。**
3. ⚠️ 消えた G1-C 回答 1 件分を Phase1 ロスター / 受付メール控えから再構成できるかは **未確認**。
