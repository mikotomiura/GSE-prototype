# 重要な設計判断

> grill（2026-09-26・研究者と）で確定した分岐。すべて「推奨案」が採用された。

## 判断 1: 単発タスクとして進める（Loop に分解しない）

- **判断日時**: 2026-09-26（研究者裁定）
- **背景**: 直す対象が `loop-spawn.sh` / `loop-run.sh` そのもの。
- **選択肢**: A: 単発タスク（/fix-bug・設計 Opus・実装 Sonnet subagent）／ B: Loop に分解して回す
- **採用**: A
- **理由**: B は P1-J / P1-K が未是正の spawn で worktree を切ることになり、直している最中の道具で自分を回す循環になる。
- **トレードオフ**: Loop の実地試験は本タスクでは行わない（次の Loop 実行＝ D で初めて実地に乗る）。
- **影響範囲**: 本タスクの進め方全体。
- **見直しタイミング**: なし。

## 判断 2: P1-H は範囲外（起票のまま残す）

- **判断日時**: 2026-09-26（研究者裁定）
- **選択肢**: A: 外す ／ B: 入れる（config に回帰 acceptance 一覧・Allowed Files 運用と組）
- **採用**: A
- **理由**: 設計が重く、判断 22（前タスク）の運用＝メインが全 acceptance を正しい終了コードで回す、で当面補える。引き継ぎメモ §4 の優先順とも一致。
- **トレードオフ**: Loop の verify は引き続き他の門の破損を見ない。
- **見直しタイミング**: 次に Loop を回して、メインの独立検証でだけ見つかる破損が再発したとき。

## 判断 3: P1-J —— ローカルと `origin/<base>` を祖先関係で分ける

- **判断日時**: 2026-09-26（研究者裁定）
- **選択肢**: A: 一致 → origin ／ ローカル先行 → ローカル ／ ローカル遅れ → origin（現行どおり）／ 分岐 → fail-closed ／ B: 食い違えば一律 fail-closed
- **採用**: A
- **理由**: 事故の型（push 前にローカルで merge → 古い origin から切られた）はローカル先行であり、そこはローカルが正しい。ローカル遅れは fetch した最新を採るのが従来の意図（stale local base を避ける）。どちらが正しいか決められないのは分岐だけなので、そこだけ止める。B は無人モードで止まる回数が増える。
- **トレードオフ**: ローカル先行時は「未 push のコミットを含む worktree」ができる（PR には push が必要なのは従来どおり）。
- **影響範囲**: `loop-spawn.sh` の start 決定（fetch 後）と provenance 表示。
- **見直しタイミング**: 分岐による停止が頻発したとき。

## 判断 4: P1-B —— パス限定 allow が実測で効かなければ許可を広げない

- **判断日時**: 2026-09-26（研究者裁定）
- **選択肢**: A: 広げずに記録（worker は自己検証できないまま・メインが補う）／ B: `Bash(bash:*)` まで広げる
- **採用**: A
- **理由**: 許可の拡大は後戻りしにくく、効かないことを記録すれば次の判断材料になる。
  （補足として示した事実: `cargo run` / `cargo test` は build.rs 経由で既に任意コードを実行できるので B の追加リスクは小さい —— それでも A を採った。）
- **影響範囲**: `.steering/_template/loop-config.json` の `allowed_tools`・`docs/loop-engineering.md`。
- **見直しタイミング**: Claude Code の permission rule の仕様が変わったとき。

## 判断 5: P1-I —— 未コミット／コミット 0 件の verify 緑は「失敗 attempt（`uncommitted`）」

- **判断日時**: 2026-09-26（研究者裁定）
- **選択肢**: A: 失敗 attempt として次へ（新しい種別 `uncommitted`）／ B: その場で `blocked` ／ C: loop-run が自動コミット
- **採用**: A
- **理由**: 実例（005 / 008）は worker が `max_turns` で切れただけで、中身は正しかった。次の attempt の worker がコミットすれば進める。B は無人モードで後続が止まる。C は worker が意図しないファイル（生成物・一時ファイル）も入りうる。
- **トレードオフ**: events 語彙が 1 つ増える → `docs/loop-engineering.md` の語彙表・`/loop-status` の board 解釈・fingerprint / no-progress 判定との関係を揃える必要がある。
- **影響範囲**: `loop-run.sh` の `run_issue`、`docs/loop-engineering.md`、`/loop-status`。
- **見直しタイミング**: `uncommitted` が同じ issue で連続し no-progress で止まる事例が出たとき。

## 判断 6: P1-K —— spawn を mkdir ロックで直列化し、失敗時の残骸ブランチを片づける

- **判断日時**: 2026-09-26（研究者裁定）
- **選択肢**: A: `loop-spawn.sh` 自身でロック直列化（mode A / C の両方に効く）／ B: ロックエラー検知でリトライ
- **採用**: A
- **理由**: B は git のエラー文言に依存する。A は原因（同時実行）を消す。git-bash に `flock` が無い前提で `mkdir` を使う。
- **トレードオフ**: ロックの残骸（異常終了）への対処が要る（stale 判定）。
- **影響範囲**: `loop-spawn.sh`。
- **見直しタイミング**: なし。

## 判断 7: P1-D —— 装飾を剥がして拾い、拾えない 3 桁数字は WARN して続行

- **判断日時**: 2026-09-26（研究者裁定）
- **選択肢**: A: WARN して続行 ／ B: preflight で die
- **採用**: A
- **理由**: 散文中の言及（「issue 004 の merge 後に…」）は正当にありうる。黙らないことが要点で、止めることではない。
- **影響範囲**: `loop-run.sh` の `issue_deps_raw` / `preflight_dag`。

## 判断 8: P1-B —— `Bash(bash .steering/**/*-acceptance.sh)` を入れる（★ 境界ではないと明記）

- **判断日時**: 2026-09-26（研究者裁定・判断 4 の前提が実測で変わったため再裁定）
- **背景**: 実測（design.md P1-B 表・`claude 2.1.282`）で、途中に `*` を置く形（`:*` / ` *`）と前方一致 `Bash(bash .steering/:*)` は**効かず**、
  `**` 形式 `Bash(bash .steering/**/*-acceptance.sh)` だけが効いた。陰性対照（他スクリプト・引数付き・`&&` の後半）は拒否。
  ⚠️ ただし `bash .steering/../esc-acceptance.sh` は通り、worker は `Write` で任意の `*-acceptance.sh` を作れる → **権限上は `Bash(bash:*)` と同等**。
- **選択肢**: A: 入れる（利便のための許可であり境界ではないと明記）／ B: 入れずに記録
- **採用**: A
- **理由**: 境界は元から `ensure_branch`・必須 deny・人の merge ゲートであり、`cargo run` / `cargo test` が build.rs 経由で任意コードを実行できる状況は変わらない。
  得るもの（worker が acceptance の欠陥を自分で見つけられる）が大きい（前タスクで `--exact`・jq 欠陥により 5 attempt を失った）。
- **トレードオフ**: worker が acceptance を書き換えて自分で緑にすることはできる → ★ ただし Loop の verify は **main 側**の acceptance を走らせるので合否には効かない（既存の守り）。
- **影響範囲**: `.steering/_template/loop-config.json` の `allowed_tools`、`loop-config.README.md`、`docs/loop-engineering.md`。
- **見直しタイミング**: Claude Code の permission rule の照合規則が変わったとき（★ 実測をやり直す）。
