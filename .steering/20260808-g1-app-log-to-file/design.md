# 設計 — アプリのログをファイルに残す

## 0. 先に一次資料で確かめたこと（★ 記憶で書かない）

| 確かめたこと | どこで | 結果 |
|---|---|---|
| いま RUST_LOG は効いているか | `src-tauri/Cargo.toml:110` + tracing-subscriber 0.3.22 の `[features]` | ★ **効いていない**。`env-filter` は **default features に無い** |
| ならば既定の閾値は何か | `tracing-subscriber-0.3.22/src/fmt/mod.rs:349` | `DEFAULT_MAX_LEVEL = LevelFilter::INFO`。★ **`debug!` は今も 1 行も出ていない** |
| `MakeWriter` を tee できるか | 同 `src/fmt/writer.rs:455` (`MakeWriterExt::and` → `Tee`) / `:279` (`with_max_level`) | できる。★ **layer / registry を組まなくてよい** |
| ファイルに直接書けるか | 同 `src/fmt/writer.rs:704` (`impl MakeWriter for std::fs::File`) | 書ける。⚠️ **ただし同期 I/O**（後述で不採用） |
| 提出物に混ざらないか | `src-tauri/src/reconcile.rs:189` | 収束器は `*.ndjson` しか拾わない。★ `.log` を同じフォルダに置いても安全 |
| 終了時に被験者へ見せられるか | `src-tauri/src/lib.rs:1838-1849` | 終了時に**セッションフォルダを開いている**。★ 同じフォルダに置けば目に入る |

## 1. どこに書くか

`~/Documents/GSE-sessions/gse-app.log`（= **セッション NDJSON と同じフォルダ**）。
`GSE_DATASET` 設定時は `$GSE_DATASET/raw/<PID>/gse-app.log`。

★ 理由: (a) 被験者が既に知っているフォルダである、(b) 終了時に自動で開かれる、
(c) 収束器は `.ndjson` しか見ないので提出物に混ざらない。

`logger.rs` の `default_log_path()` からディレクトリ解決を `session_log_dir()` として切り出し、
`app_log_path()` はそれを使う。⚠️ **ログ出力は `default_log_path()` 側に残す**
（`app_log_path()` は subscriber の設置**前**に呼ばれるので、そこで `info!` しても消える）。

## 2. どう書くか — ⚠️★ 同期 I/O にしない

`impl MakeWriter for File` を使えば 3 行で済むが、**採らない**。

⚠️ `hook_macos.rs:428` に `tracing::warn!("InputEvent dropped (channel full)")` がある。
これは **CGEventTap のコールバックの中**である。channel が詰まると打鍵ごとに発火しうるので、
そこにファイル I/O を置くと `hook-constraints`（コールバック内はブロッキング禁止）を破る。

→ `logger.rs` の `LogChannel` と**同じ形**にする（新しい依存を足さない）:

```
tracing の fmt レイヤ
   └ Tee ─┬→ stdout               (開発時。従来どおり)
          └→ AppLogMaker
                └ bounded(256) crossbeam channel   ← try_send。★ 詰まったら捨てる
                      └ 書き込みスレッド → gse-app.log へ append + flush
```

- `AppLogWriter` は 1 イベント分を `Vec<u8>` に貯め、**Drop で 1 回 `try_send`** する
  （行が途中で割れない）。
- `try_send` なので**呼び出し側は絶対に待たない**。溢れたら捨てる
  （★ 捨てた件数は次に書けたときに 1 行出す。黙って捨てない）。
- ⚠️ 新しい crate は足さない。`tracing-appender` は Cargo.lock にも registry cache にも
  無く、配布ビルドの依存を増やす。`crossbeam-channel` は既存依存（`Cargo.toml:98`）。

## 3. 無限に伸びないようにする

書き込みスレッドが自分でバイト数を数え、`MAX_BYTES`（2 MiB）を超えたら
`gse-app.log` → `gse-app.log.1` に rename して開き直す（**世代は 1 つだけ**、上限 ~4 MiB）。

★ 世代交代を書き込みスレッド 1 本の中だけで行うので、ロックも競合も無い。

## 4. プライバシー（`data-privacy`）

- ★ ファイル側の writer に **`.with_max_level(Level::INFO)`** を付ける。
  今は既定が INFO なので冗長だが、⚠️ **将来 `env-filter` を足した誰かが
  `RUST_LOG=debug` でキーコード (`hook_macos.rs:518` の `VK=0x..`) をディスクに
  落とすのを構造で防ぐ**（運用の注意ではなく型で止める）。
- ルール 1 の「文字内容」は元から `tracing` に流れていない（177 箇所を grep 済み）。
- ルール 2（外部送信禁止）: ★ **ローカル保存のみ**。送信は今回やらない。

## 5. 壊れたときの落ち方

ファイルを開けない（ホームが読取専用など）→ ★ **stdout だけで起動を続ける**。
起動を止めない。開けなかったことは stdout 側に `warn!` で出す。

## 6. テスト戦略

`applog.rs` に単体テスト（★ すべて `tempfile` で実ファイルを触る。偽物を作らない）:

| # | 何を確かめるか | ★ 赤を先に見る |
|---|---|---|
| T1 | 送った行が**実ファイルに現れる** | パスを間違えたら赤 |
| T2 | 追記である（既存の中身を消さない） | `truncate(true)` にしたら赤 |
| T3 | `MAX_BYTES` 超で `.1` へ回り、新しいファイルが小さくなる | 上限判定を消したら赤 |
| T4 | channel 満杯で**呼び出し側が待たない**（`try_send` が返る） | `send` にしたら固まる |
| T5 | 捨てた件数が次の行に出る | 黙って捨てたら赤 |

⚠️ ★ **単体テストが緑でも「`.app` で落ちる」ことの証明にはならない**
（今回直しているバグがまさにそれ）。→ **実バイナリを走らせてファイルを見る**まで受け入れない。

## 7. 同じ機会に入れる follow-up

`writing-pad.html` の `beforeunload`:

```js
// 現状: 未入力なら警告しない → ★ 開始直後に閉じるとブロックが黙って消える
if (pad.value.length === 0) return;
// 変更後:
if (!started && pad.value.length === 0) return;
```

`build_task_pages.py:420` が `"beforeunload"` を検査に入れているので、
生成済み `pages/blockNN.html` も**作り直して**差分を出す。
