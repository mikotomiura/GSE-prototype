# 設計判断

## D-1: ログの出力先は「セッション NDJSON と同じフォルダ」

**決定**: `~/Documents/GSE-sessions/gse-app.log`（`GSE_DATASET` 有りなら `raw/<PID>/`）。

**理由**:
- 研究者が NDJSON を見に行く場所と同じ。探す場所を増やさない。
- 収束器 (`reconcile.rs:189`) は `*.ndjson` だけを拾うので、⚠️ **提出物には混ざらない**
  （実装で確認 → `app_log_is_not_picked_up_as_a_session_file` テストで固定）。

**却下案**: `~/.gse/` に置く
→ ★ 被験者にも研究者にも見えない隠しフォルダ。取り寄せの説明が増える。

**⚠️ 積み残し**: 被験者向け `README_先に読む.txt` は **このフォルダに触れていない**
（`dist-readme-macos.txt` を grep して確認）。★ ログを取り寄せるときは場所を伝える必要がある。

## D-2: 同期 I/O にしない（bounded channel + 書き込みスレッド）

**決定**: `impl MakeWriter for std::fs::File`（3 行で済む）を**使わない**。
`crossbeam-channel` の bounded(256) + `try_send` + 専用スレッド。

**理由**: `hook_macos.rs:428` の `tracing::warn!("InputEvent dropped (channel full)")` は
**CGEventTap のコールバックの中**にある。channel が詰まると打鍵ごとに発火しうるので、
そこでファイル I/O をすると `hook-constraints`（コールバック内ブロッキング禁止）を破る。

**却下案**: `tracing-appender` を足す
→ Cargo.lock にも registry cache にも無い。配布ビルドの依存を増やす。
`crossbeam-channel` は既存依存で、`logger.rs` の `LogChannel` と同じ形にできる。

**⚠️ 代償**: 溢れたら**捨てる**。★ 黙って捨てないよう、捨てた件数を次の行に出す。

## D-3: ファイル側の閾値を INFO に固定する

**決定**: `.with_max_level(Level::INFO)` をファイル側 writer に付ける。

**理由**: いま `env-filter` feature は入っておらず既定閾値も INFO
（`tracing-subscriber` の `Subscriber::DEFAULT_MAX_LEVEL` を一次資料で確認）なので**冗長**である。
それでも書くのは、⚠️ 将来 `RUST_LOG` を効くようにした誰かが
`hook_macos.rs:518` のキーコード (`VK=0x..`) を `debug!` 経由でディスクへ落とすのを
**構造で止める**ため（`data-privacy` ルール 1 を運用の注意に頼らない）。

★ この防波堤は統合テストで**壊して赤を見た**（`with_max_level` を外すと `VK=0x41` が
ファイルに現れて赤くなる）。

## D-4: `app_log_path()` は参加者 ID を解決しない（`GSE_DATASET` 無しのとき）

**決定**: `GSE_DATASET` が無い経路では `fallback_log_dir()` を直接使い、
`resolve_participant_id()` を**呼ばない**。

**理由**: この関数は **`tracing` の購読者を設置する前**に呼ばれる。
`resolve_participant_id()` には「新しい ID を生成 → `~/.gse/participant_id` へ永続化 →
`info!` で記録」という副作用があり、★ **先に呼ぶとその 1 行がどこにも出ないまま消える**。
`GSE_DATASET` 無しでは保存先が ID に依存しないので、副作用ごと後続の
`default_log_path()`（購読者の設置後）に任せる。

⚠️ `GSE_DATASET` 有り（開発機）では初回の `info!` が失われるが、開発機には端末がある。

## D-5: ログの外部送信はしない

**決定**: ローカル保存のみ。`data-privacy` ルール 2 の判断が要るので今回はやらない。

**⚠️ 帰結**: 研究者がログを見るには**被験者に送ってもらう**必要がある。
★ ログには `resolved_log_dir` などでホームパス（= 実名を含みうる）が入る。
`redact_home_path` は自動提出の詳細行にしか掛かっていない。取り寄せ運用を決めるときに再検討する。

## D-6: 後片付けで見つけた「残ったプロセス」は止めた

**決定**: `~/Desktop/G1_実施用_macOS` の削除承認に含まれるものとして、そこから動いていた
`gse-next`（PID 84943・3 時間・CPU 157 分）を SIGTERM で止めた。

**理由**: プロセスが動いたままフォルダを消しても、⚠️ 実体は unlink されたまま動き続けて
記録を書き続ける（消したことにならない）。

**⚠️ 消していないもの**: `~/Documents/GSE-sessions/*.ndjson` 3 本（承認外）。
★ うち `gse_20260808_060459.ndjson` は被験者の実施ではなく**研究者の通常作業 3 時間ぶん**である。
詳細は `cleanup-record.md`。

**★ 副産物の発見**: `windows-verification.md §4-1`（× で閉じてもプロセスが残る）は
Windows でしか観測されていなかったが、**macOS でも起きる**ことが実例で分かった。
原因（overlay 窓が残る限り Tauri は終了しない）はプラットフォーム非依存である。
