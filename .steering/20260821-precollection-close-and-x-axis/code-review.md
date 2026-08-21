# レビュー結果 (2026-08-21)

## ① Codex (`/cross-review` — パス限定: `src-tauri/src/{g1.rs,input/liveness.rs,lib.rs}`)

⚠️ 引き継ぎ §5-6 に従い **パス限定**で回した
(`scripts/run-codex-review.sh -- <paths>`)。★ exit 0・fail-closed に引っかからず完走。

| # | 重要度 | 指摘 | ★ 対応 |
|---|---|---|---|
| 1 | 中 | `BLOCK_TRANSITION` を保持したまま重い処理に入る可能性。「最大 1500 ms」がコード上保証されているか | ★ **保証されている**（`let deadline = Instant::now() + Duration::from_millis(1500);` で有界。⚠️ `emit` / `recv_timeout(5s)` / 自動提出は**すべてロックの外**へ出してある）。→ ★ **対応不要**だが、`design.md` に検算を明記した |
| 2 | 中 | ⚠️★★ **呼び出し側が `== Superseded` でしか中止していない。** 将来 `decide_block_end` の分類が増えると**新しい枝が黙って「閉じてよい」側へ倒れる** | ★ **採用・修正した。** `!= EndBlock` なら中止する **fail-closed** に変更（`lib.rs`）。⚠️ ログにも判定結果 (`{:?}`) を出すようにした |
| 3 | 低 | ソース走査テストが脆く、設計保証にはならない | ★ **採用（文書化）。** テストの docstring に「**回帰検知であって設計保証ではない**」「壊れたときは *テストが古い* と断じる前に不変条件を目で確かめる」と明記 |
| 4 | 低 | ⚠️ 純関数テスト中心で、`Rotate` / `BlockEnd` の**実際の並び**を見る統合テストが無い | ★ **採用・テストを足した。** `logger::tests::a_rotate_before_block_end_moves_session_end_into_the_new_file` —— **順序が逆転したときに何が壊れるか**（`Rotate` が `block_closed` を false に戻すので `BlockEnd` が**新ファイル**へ `session_end` を書く）を固定した。⚠️ これが赤くなったら `BLOCK_TRANSITION` の前提が変わったということである |

> Codex の総評: 「セキュリティ上の新規懸念は、この diff からは特に見当たりません。」

### ⚠️ #4 について — なぜ「並行統合テスト」ではなくこの形にしたか

Codex は「ログ sender を差し替えた**並行**テスト」を提案したが、★ 採らなかった:

- ⚠️ 自動終了スレッドの本体は `lib.rs` の `thread::spawn` クロージャに**インライン**で、
  テスト可能な関数として取り出すには**構造変更**が要る。
  → ★ 研究者決定 #2「**T-0 / T-1 が緑になった時点で計器の作業は終了**」の線を越える。
- ⚠️ スレッドのタイミング依存なので、**並行テストは緑でも交錯を通っていない**ことがありうる
  （★ 空振りする回帰テストになる）。
- ★ 代わりに「**順序が逆転したときの帰結**」を logger 単体で決定的に固定した ——
  ⚠️ **こちらは必ず走る。**

## ② Claude `security-checker`

⚠️ CRITICAL なし。★ 指摘はすべて **T-2 で新規に書いた Python / テンプレート**側であった
（src-tauri 側は「問題なし」と根拠つきで判定された）。

| # | 重要度 | 指摘 | ★ 対応 |
|---|---|---|---|
| **H-1** | **HIGH** | ⚠️★★★ **`--json` が参加者 ID ＋ セッション開始時刻をファイルへ書き出し、それが `.gitignore` に掛からない。** 実データのファイル名は `P010_gse_20260629_073659.ndjson` ＝ **擬似 ID ＋ 秒精度の時刻そのもの**。`run.sh` がそれを `results/capabilities.json` へ保存し、⚠️ `.gitignore` は `results/*.json` を塞いでいない（「集計 JSON はコミット可」と明記）。★ **本 repo は一時 public にする運用がある** → 「各参加者がいつ打鍵していたか」の全リストが公開されうる | ★ **採用・発生源で直した。** `as_dict()` は**不可逆な `file_id`（sha256 8 桁）だけ**を出す。実名は `render()`（**端末表示**）にのみ出し、`--json` 指定時は本文を **stderr** へ回す。⚠️ `.gitignore` に足す対処は**採らない** —— テンプレはコピーされるので**新ディレクトリごとに漏れる**。★ **実データで検算**: `--json` の stdout に `gse_` は **0 件**、stderr に実名 4 件 |
| **M-1** | MEDIUM | ⚠️ `collect_paths` が存在しない入力を**黙って捨てる** → 残りだけで判定して exit 0。★ **コホートが揃っていることを担保するゲートが、コホートの縮小を検知できない** | ★ **採用。** `MissingInputError` を追加し **fail-closed**（CLI は `EXIT_USAGE`）。self-test ⑪ と単体テスト 2 本で固定 |
| **M-2** | MEDIUM | ⚠️ 空入力時の例外メッセージが「**すべての要求行種が読める**」になる（`summary()` の `bad` が空になるため）。★ `except ... as e: log(str(e))` した解析が**入力ゼロの失敗を緑として記録する** —— 本ゲートが防ぐはずの誤読が、**ゲート自身のエラーパス**に残っていた | ★ **採用。** 空入力専用の文言を返す。self-test ⑬ と単体テストで**文言**まで assert |
| **M-3** | MEDIUM | ⚠️ `start_session` は同期 `#[tauri::command]` ＝ メインスレッドで、新たに最大 1500 ms 待ちうる（イベントループ停止 →「応答なし」表示）。★ ただし **データ欠落は起きない**（キーボードフックは専用スレッド ＋ 自前 `PeekMessageW` ループ） | ⚠️ **直さない** → `blockers.md` **N-3**。★ 排他を外すと HIGH 相当の破損が戻るので**残す**。⚠️ `async` 化は**通常運用のスレッド挙動を変える**ので研究者決定 #2 の線を越える |
| **L-1** | LOW | `read_file` の例外未処理。⚠️ 不正 UTF-8 で `UnicodeDecodeError`、`PermissionError` では例外文に**絶対パス**（ユーザ名と参加者 ID を含む）が出る | ★ **採用。** `errors="replace"`（不正バイトは `malformed_lines` に数えて判定は続行）＋ `except OSError` で **`path.name` だけ**を出して fail-closed |
| **L-2** | LOW | `run.sh` のリダイレクトが先に開くため、ゲート失敗時に `results/capabilities.json` が **0 バイトで残る** → 次に読む人が「宣言 0 件」と誤読 | ★ **採用。** 一時ファイルへ書いて `mv` する |
| L-3 | LOW | 巨大 1 行 NDJSON のメモリ | ⚠️ **対応しない**（入力は自前データで信頼境界の内側。★ レビュア自身が「DoS 経路として現実的でない」と判定） |
| L-4 | — | シンボリックリンク | ★ **問題なし**（`Path.rglob` は既定でリンク**ディレクトリ**を辿らない・確認事項として記載） |

### ★ 「問題なし」と根拠つきで判定された項目

- **デッドロック**: 起きない。①臨界区間の保持は**有界**（`ANALYSIS_IDLE` は 1500 ms deadline、
  `try_recv` / `try_send` は非ブロッキング、`recv_timeout(5s)` は `drop` の**後**）
  ②待つ側の `start_session` は最外で取り、**待機中に他のロックを 1 つも持たない**
  ③自動終了スレッドは `log` / `latest_feat` / `intervention` を取らない
  ④取得点は 2 箇所だけで `g1.rs` のソース走査テストが位置関係を固定
- **`BLOCK_TRANSITION` の poison 処理**: 安全。★ 守っているのが `()` で**不変条件を持つデータが無い**。
  ⚠️ poison で諦める設計にすると 1 回の panic 以降**恒久的に開始不能**になるため、現在の選択が安全側
- **`run.sh` のシェル安全性**: `set -euo pipefail` / `${GSE_DATASET:?}` / 全展開 quote 済み /
  `eval` なし → **インジェクション経路なし**
- **CI**: 追加 2 ステップは `secrets` を参照せず `permissions` も増やさない。
  ★ **生ログを CI に持ち込んでいない**（`--self-test` と単体テストのみ）
- **NDJSON の混入**: 新規ファイルに `.ndjson` / `.log` は 1 つも無い。
  `t0-result.md` は `P999`（研究者自身のテスト）の値のみ
- **依存**: `Cargo.toml` / `Cargo.lock` / `package.json` を **1 行も変更していない**
  → 新規サプライチェーン面積ゼロ

## ③ Claude `code-reviewer`

⚠️★★★ **本レビューが本セッションで最も価値があった** —— ★ 私の所見 C の修正が
**狙った誤帰属をほぼ閉じていない**ことを、実トレースで示した。

### HIGH

| # | 指摘 | ★ 対応 |
|---|---|---|
| **H-1** | ⚠️★★★ **所見 C の修正が効いていない。** `step()` が `starved_ms` を 0 に落とすのは**打鍵が届いた tick か非計測の tick だけ**。★ `RotateForRestart` は「開始する」ボタンの**マウス押下**なので、⚠️ **エポックの tick では `starved_ms` は 0 ではなく増え続けている**。→ 抑止が効くのは「打鍵がエポックと**同一 tick** に来た」場合だけで、★ **1 tick ずれて同じ誤帰属が起きる**（tick N: `prev=8000 → 9000` 抑止で計上なし ／ tick N+1: `prev=9000, now=0` で **9000 ms が新窓へ計上**）。⚠️ しかも私のテストは `now_starved_ms` に **0 を手で渡していた**ので**配線を検証していなかった** | ★ **採用・直した。** `liveness::reset_starvation_at_new_block` を追加し、エポックで**累積そのものを 0 に戻す**（＝ 通常のブロック境界で `session_active=false` により起きていることと同じ形に揃える）。⚠️ **`peak_starved_ms` は戻さない** —— 戻すと復帰行の `starved_ms` が 0 になり「**何秒落ちていたか**」という測った量が消える（★ 誤帰属ではなく**嘘**になる）。テストは **`step` → `reset` → `carried` → `tick` の鎖を実際に回す**形に作り直し、⚠️ **対照**（エポックが無ければ同じ入力で 9000 ms を数える）も置いて空振りを防いだ |
| **H-2** | ⚠️ `RotateForRestart` の **`Rotate` 送信失敗**で `SESSION_META_RECORDED` が巻き戻らない。→ 次の押下が `RetryAfterMetaFailure` に落ち、★ `Ok(())` を返すのに**ログを 1 行も書かない**ので、フロントが `record_session_meta` へ進み ⚠️★★★ **旧ファイルに 2 本目の `session_meta`** が入る（`protocol.md §1` の破れ） | ★ **採用・直した。** `swap(false)` で旧値を控え、失敗枝で復元する（`session_active` を枝ごとに戻しているのと同じ形）。⚠️ **pre-existing だが、同じ関数の同じ失敗クラス**（ブロック境界の破れ）であり **1 行**で閉じるので、収集開始前に閉じた |

### MEDIUM

| # | 指摘 | ★ 対応 |
|---|---|---|
| M-a | ⚠️★★ **ソース走査テストが「照合」を固定していない。** ★ **変異実測**: ロック配置を壊す **5 変異はすべて赤**になったが、⚠️ `Superseded` の再照合を潰す変異（`== Superseded` → `== NotStarted`）は**緑のまま**。設計は「排他と**照合**の両方が要る」と言っているのに、固定されていたのは排他だけ | ★ **採用。** 再照合に専用の needle（`let current_start_ms = SESSION_START_MS.load(...)`）を与え、`acquire[1] < recheck[0] < block_end[0]` を追加 |
| M-b | ⚠️ `peak_starved_ms` がブロック境界で引き直されない → `RotateForRestart` 後の最初の `hook_health` が**前ブロックのピーク**を申告する | ⚠️ **意図的に直さない。** ★ 戻すと復帰行が `starved_ms: 0` になり、**測った量が消える**（H-1 の対応で理由を明記）。⚠️ 誤帰属より**嘘**のほうが悪い。→ `liveness.rs` の doc と専用テストで「戻さない」ことを**固定**した |
| M-c | `capabilities_gate.py`: 入力 0 本の例外文が「すべての要求行種が読める」になる | ★ **採用**（security-checker M-2 と同一。修正済み） |
| M-d | `collect_paths` が存在しないパスを黙って捨てる | ★ **採用**（security-checker M-1 と同一。修正済み） |
| M-e | ⚠️ `--allow-undecidable` が **Python API では警告が 1 行も出ない**（docstring の「警告に落とす」が未実装） | ★ **採用。** `preflight()` が stderr に「**判定不能を明示的に受け入れました**／`notes.md` の結論は『判定不能』と書くこと」を必ず出す。テストで固定 |
| M-f | `judge([], ...)` が `StopIteration`（公開関数として素の例外） | ★ **採用。** 空なら空の `Report` を返す。テスト追加 |
| M-g | `read_file` の例外未処理（不正 UTF-8 / 権限エラー） | ★ **採用**（security-checker L-1 と同一。修正済み） |
| M-h | `now` を排他取得の**前**に採っている（最大 ~1.5 秒古い値で判定・ログ） | ★ **採用。** ロック取得後に採り直す |

### LOW

| # | 指摘 | ★ 対応 |
|---|---|---|
| L-a | `acquire.len()==2` を **binding 文字列**で数えているので `let _g = lock_block_transition();` が素通り | ★ **採用。** `lock_block_transition();` の**呼び出し回数**で数える |
| L-b | `spawn_duplicate_instance_check` が排他の**中**にある | ⚠️ **直さない。** ★ 中身は `thread::spawn` のみで**ブロックしない**（レビュア自身「無害」と判定）。⚠️ 動かすと押下時の順序が変わるので、収集開始前に触る価値が無い |
| L-c | ⚠️ docs 5 ファイルが `lib.rs:2923/2924` を「`hook_health` の間引き」として参照しているが、そこは既に別のコードであり**本 diff が更にずらした** | ★ **採用。** **11 箇所**を行番号から**式・シンボル名**へ張り替えた（`if health == prev_health && !rehook { continue; }` / `Thresholds::default()` / `reported_starved_ms`）。⚠️ 行番号でアンカーしない |
| L-d | `run.sh` は `python`、CI は `python3` | ★ **採用。** `command -v python3 \|\| command -v python` の順で解決（`PYTHON` env で上書き可） |
| L-e | `MIXED` 出力にどのファイルがどの群かが無い | ★ **部分対応。** 混在時、端末表示に**旧ビルドのファイル名 ＋ `file_id`** を列挙する（⚠️ JSON には出さない・security H-1） |
| L-f | `--require meta` が `DECLARATION_BUG` になる（`meta` はどの群にも載らない設計） | ★ **採用。** `EXIT_USAGE` で理由つきに断る。テスト追加 |
| L-g | ローカル clippy(1.94) は 29 error だが**すべて既存コード**、本 diff の追加行は 0 件 | ★ **対応不要**（本機の clippy でも本 diff 起因の警告は 0 件を確認） |

### ★ レビュアが「正しい」と検証した点

- **ロック順序の論証は成立**。`start_session` は `BLOCK_TRANSITION` を**他のロックを 1 つも持たない状態**で待つので循環は構造的に作れない
- **FIFO の根拠も成立**: `BlockEnd`(`log_tx_g1`) と `Rotate`(`guard.tx`) は**同一 channel の clone** なので、臨界区間で送信順を固定すれば受信順が固定される
- **交錯 2 方向は閉じている**。第 3 の経路 `RetryAfterMetaFailure` は `Rotate` を 1 通も送らずに返るので不変条件は保たれる
- **ソース走査テストは実測で非空振り**（ロック配置の 5 変異すべてが赤）
- ★ 「通常運用への影響を**唯一の例外**として正直に文書化した」姿勢 ——
  ⚠️ 逐語「**実際にはその例外の記述も不正確（HIGH-1）だが、隠さずに書いたからこそ検証できた**」

---

## ④ ★ 本ラウンドで足したテスト（★ すべて実際に走ったことを確認済み）

| テスト | 何を固定するか |
|---|---|
| `liveness::restart_epoch_does_not_leak_starvation_on_the_next_tick` | ⚠️★★★ **H-1 の本命**。再押下（マウス）の**次の tick**で打鍵しても漏れない |
| `liveness::the_same_sequence_is_counted_when_no_block_boundary_happens` | ⚠️ **対照**（★ これが無いと上は「常に None」でも緑になる） |
| `liveness::resetting_at_the_epoch_does_not_touch_the_peak` | ★ **ピークは戻さない**という判断を値で固定 |
| `logger::a_rotate_before_block_end_moves_session_end_into_the_new_file` | ★ 順序が逆転したときの**帰結**（Codex 4） |
| `g1::block_transition_is_held_across_the_whole_block_boundary`（拡張） | ★ 排他 ＋ **照合**の位置関係（M-a） |
| `test_capabilities_gate.PrivacyTests` × 3 | ⚠️★★★ JSON にファイル名を出さない（security H-1） |
| `test_capabilities_gate.FailClosedTests` × 4 | ⚠️ 入力欠落・空入力・不正バイト（security M-1/M-2/L-1） |
| `test_capabilities_gate.PublicApiEdgeTests` × 3 | ⚠️ 空コホート・`--require meta`・無音の `--allow-undecidable`（M-e/M-f/L-f） |

## ⑤ ★ 最終検証

| 検査 | 結果 |
|---|---|
| `cargo test --workspace` | ★ **468 passed / 0 failed**（438 + 29 + 1） |
| ゴールデン | ★ **6 本 byte-equal** |
| `HMM_VERSION` | ★ **0.4.0 据え置き** |
| `emit_schema` vs `schema/current.json` | ★ **byte-equal**（記録仕様を変えていない） |
| schema parity（`gse-dataset` 突合） | ★ **exit 0**（⚠️ `\| tail` にパイプせずリダイレクトして確認） |
| `cargo fmt --check` / clippy | ★ clean / **本 diff 起因の警告 0 件** |
| Python | ★ **83 tests OK** |
| `capabilities_gate --self-test` / `check_vignettes --self-test` | ★ 両方 exit 0 |
| `check_citations.py` | ★ 違反なし |
