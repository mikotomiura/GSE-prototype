# 次セッション開始プロンプト — G1 の自動提出を作る

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-06 に P-1 Windows 回の結果と W-1〜W-8 の実測を受け取り、
⚠️★★ **提出 (`.age`) が 1 本も作られない**という設計の穴が確定した。
★ タスクは起票済み (`.steering/20260806-g1-auto-submit-on-block-end/`)。**実装は未着手。**

---

===

## §0 このセッションでやること

`.steering/20260806-g1-auto-submit-on-block-end/` を進める。
★ **最初に `requirement.md` / `decisions.md` / `consent-draft.md` / `tasklist.md` を読む。**

⚠️ ★ **`/reimagine` 適用 = Yes**（設計承認の前に一度破棄して作り直す）。

### ★ いちばん先に確認すること

⚠️★★ **`consent-draft.md` §5 の Q-1〜Q-4 に研究者の判断が出ているか。**
出ていなければ**そこで聞く**。★ 同意の範囲を超える実装を先に作ってはいけない
（`§3.6` が事後除外を禁じているのと同じ構造で、**止められるのは実施前だけ**）。

---

## §1 何が決まっていて、何が決まっていないか

### ✅ 決まっている（研究者判断 2026-08-06・`decisions.md` D-1〜D-3）

| # | 決定 |
|---|---|
| D-1 | **ネットワークで自動送信する**（ローカル生成だけで止めない） |
| D-2 | 送信先は **GAS Web App → 研究者の Drive**。⚠️ Dropbox 直は**却下**（配布バイナリにトークンを埋めることになる） |
| D-3 | 失敗時は**ローカルに貯めて自動再送**＋未送信件数を画面に出す。単位は**ブロック終了ごとに 1 本** |
| — | 参加者 ID は **起動時にアプリの画面で 1 回入力**（`g1.mode` に書く案は不採用） |

### ⚠️ 決まっていない（★ 設計フェーズで閉じる）

1. **送信の実行主体**（Tauri 本体 / `gse-submit` / 3 つ目のバイナリ）— ★ §2 の実測が効く
2. **ブロック番号の採り方** — ⚠️ 再起動で数え直しになる
3. **共有シークレットの置き場所** — `pubkey.txt` と同じ配布同梱でよいか（security-checker に掛ける）
4. `consent-draft.md` §5 の **Q-1〜Q-4**

---

## §2 ★ 2026-08-06 に済ませた調査（**再調査しない**）

⚠️ ★ 以下は**コードを読んで確かめたもの**である。推測は含まない。

| 何 | 実測 |
|---|---|
| ★ `find_latest_session_ndjson` の**本番**呼び出し元 | **`src-tauri/src/bin/submit.rs:222` の 1 箇所だけ**（他は `packaging.rs` のテスト）→ ★ **`--input` 追加は影響範囲が小さい** |
| `package_session` の呼び出し元 | `submit.rs` と `bin/package.rs` の 2 箇所 |
| 匿名化 (`vk`→`category`) | `packaging.rs` に集約済み。★ **`vk` が漏れないことのテストが既にある**（`packaging.rs` の `assert!(!…contains("\"vk\""))`）→ 新経路でも同じ資産が使える |
| ⚠️★★ **HTTP を出す手段** | **1 つも入っていない**（`reqwest` / `tauri-plugin-http` / `ureq` / `hyper` すべて `Cargo.toml` に無し）→ ★ **依存を足す判断が要る** |
| ⚠️★★ **CSP** | `default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'`。★ **`connect-src` が無い** |
| ★★ **CSP と設計問い 1 の関係** | ⚠️ **CSP は webview しか縛らない。** → ★ **Rust 側から送れば CSP を 1 文字も触らずに済む**。フロントから `fetch` すると CSP 改訂が要る。★ これは設計問い 1 への**強い入力**である |
| ローテートの形 | `lib.rs` が `logger::next_session_path()` で新パスを作り `LogEntry::Rotate { new_path }` を send する。★ **「閉じたばかりのファイル」のパスは呼び出し側が知っている**（`current_path()`）→ 取得は容易 |
| ⚠️ Rotate 失敗時の作法 | channel 満杯で送れなければ **触った状態を全部巻き戻して `Err` を返す**（cross-review HIGH）。★ **自動提出もこの厳しさに合わせる**（黙って進まない） |
| ★ `.age` のサイズ | mac 実測で NDJSON **233,115 B → `.age` 243,459 B**（**+4.4%**）。Windows の 4 本は 151〜213 KB → ★ **`.age` は概ね 160〜225 KB**。base64 なら +33% で **約 300 KB/本** |
| ⚠️ GAS の上限 | ★ **未実測。** POST サイズ・実行時間・**実行ログに何が残るか (Q-3)** を測る。**推測で埋めない** |

### ⚠️★ 同じタスクで決着させる 1 件

★ **「× で閉じてもプロセスが残る」**。原因はコードで確認済み:
`lib.rs` が実行時に **`overlay` という 2 つ目の窓**を作り、Tauri は**全窓が閉じたとき**に終了するので
**overlay が残る限りプロセスは死なない**（`CloseRequested` / `ExitRequested` の処理は無い）。
→ ★ **再送キューがいつ回るかがこれに依存する**ので、自動提出の設計と一緒に決める。

---

## §3 制約（厳守）

- ★★ `preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` を変更しない
- ★ **`§5.4-2` の客観検証（probe 行 0）は何があっても残す**
- ★ **通常運用（マーカー無し起動）を 1 ピクセルも変えない。** ID 欄も送信も **G1 モード限定**
- ★ **送るのは `.age` だけ。** 生 NDJSON を送る経路を作らない
- ⚠️ ★ **`ime_state` の session ゲートには触らない**（`20260805` の `decisions.md` **R-9**・**蒸し返さない**）
- **PII**: 実名・メール・セッション日時 / NDJSON ファイル名を成果物に出さない
- ⚠️ 本リポジトリは一時 public にする運用がある
- ★ Rust を書くなら `rust-standards` / `architecture-rules`、外部送信なので **`data-privacy` を必ず先に読む**

## §4 ⚠️ 環境の罠（★ 先に読む）

| 罠 | 中身 |
|---|---|
| ⚠️★★ **`~/.cargo/bin/cargo` が動かない** | rustup の shim が dangling（`rustup` 本体が `~/.cargo/bin/` に無い）。`ls` ではリンクが見えるので気づきにくい。★ 実体は **`~/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo`**（1.97.1）。⚠️ ★ これを PATH に足さないと **`run.sh` の cargo ゲート 4 本が「飛ばした」と言って素通りする** |
| ★ **repo 直下の `cargo test --workspace` は空振り** | `Cargo.toml` は `src-tauri/`。`cd src-tauri` か `--manifest-path src-tauri/Cargo.toml`（`docs/agent-shared.md` に明記済み） |
| ★ `run.sh` は未コミット変更で RED | `[FAIL] src-tauri/ または src/ に未コミットの変更がある`。**ゲートが仕様どおり働いているだけ** |

## §5 終わり方

- `bash run.sh` が **GREEN (rc=0)**（★ cargo ゲートが "N / N 本" で**実際に走った**ことを確認）
- `cargo test --workspace` / `--features package` / golden / `emit_schema` byte-equal / `npx tsc --noEmit`
- ★ **検査を足したら、その場でわざと壊して赤を実測する**（後回しにしない）
- `code-reviewer` ＋ **`security-checker`** を並列（★ 外部送信なので security 必須）
- 最後に `/cross-review`（★ 予算は**その場で計算する**。⚠️ **メモの数字を根拠にしない**）

## §6 ★ 未 push のブランチがある

`docs/win-g1-measured-tests` に **3 コミット**（`test(g1)` / `docs(experiments)` / `docs(steering)`）。
★ **push も PR も出していない。** 研究者判断で PR にするか、次の作業に含めるかを決める。
