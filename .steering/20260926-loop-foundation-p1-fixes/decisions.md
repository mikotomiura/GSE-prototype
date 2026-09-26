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
- **トレードオフ**: worker が acceptance を書き換えて自分で緑にすることはできる。
  ⚠️ ~~Loop の verify は main 側の acceptance を走らせるので合否には効かない~~ —— **誤り**（2026-09-26 `security-checker` MEDIUM で訂正）。
  任意コードを実行できる worker は main 側のファイルも書き換えうる（★ `cargo run` の build.rs 経由でも元から可能）。
  → ★ 合否を最終的に決めるのは **merge 前にメインが clean な checkout で回す acceptance**（前タスク判断 21 / 22 の運用）。
- **影響範囲**: `.steering/_template/loop-config.json` の `allowed_tools`、`loop-config.README.md`、`docs/loop-engineering.md`。
- **見直しタイミング**: Claude Code の permission rule の照合規則が変わったとき（★ 実測をやり直す）。

## 判断 9: レビュー（code-reviewer / security-checker・37bedf76）の MEDIUM 5 件と安い LOW を全部直す

- **判断日時**: 2026-09-26（研究者裁定）
- **背景**: HIGH は 0。MEDIUM は 5 件で、メインがすべて一次で実在を確認した:
  - S-M1: 文書が「main 側の acceptance を回すので worker が書き換えても合否は動かない」と書いていた → **誤り**（任意コード実行で main 側も書き換えうる）
  - C-M1: stale 除去の `continue` が `i` も `sleep` も飛ばし、`rm` が失敗し続けると無限ループ
  - C-M2: stale 除去の TOCTOU（死んだ pid を 2 者が同時に見ると、一方の新しいロックを他方が消す）
  - C-M3: `check_committed` が verify の**後**にあり、verify の生成物（gitignore 外）で毎回 dirty → 誤った `no_progress_stop`
  - C-M4: recheck の watchdog が `check_committed` より前に走り、未コミットの attempt でも予算を使う
- **選択肢**: A: 5 件と安い LOW を直す ／ B: MEDIUM だけ ／ C: 文書だけ
- **採用**: A
- **対応**: S-M1 → 文書 3 か所を「合否を最終的に決めるのは merge 前にメインが clean な checkout で回す acceptance」に訂正。
  C-M1 / M2 → stale 除去を別ロック `loop-spawn.lock.reap` で直列化し、pid を読み直して一致・なお死んでいるときだけ消す。除去を試みた周も待ち回数を進める。
  C-M3 / M4 → `check_committed && run_verify` の短絡評価で **verify の前**に置く（未コミットなら verify も watchdog も回さない）。
  ★ これで `uncommitted` の意味が「verify 緑だが未コミット」から「verify 前の時点で未コミット」に変わった → 語彙表・loop-status / loop-issue / loop-worker の文言を追随。
  LOW → `start-choice` の完全一致・rev-list を `refs/` で書く・LOCK の絶対パス化・LOCK_POLL / TIMEOUT の数値検証・`validate_name` の表示を `sanitize_disp` に通す・origin_sha 空や merge-base rc 128 の専用メッセージ・テスト判定の絞り込みと変異テストの追加。
- **やらない LOW**: 11b 状況での `abort_worktree` の文言（「撤去できませんでした」が事象とずれる）—— 実害なし・記録のみ。

## 判断 10: /cross-review（Codex gpt-6-astra ∥ code-reviewer）＋ security-checker の指摘への対応

- **判断日時**: 2026-09-26（研究者裁定）
- **背景**（メインが一次で照合済み）:
  - code-reviewer MEDIUM: 赤の verify が残した gitignore 外の生成物で、次の attempt の未コミット判定が dirty に固定される（worker は `rm` / `git clean` を持たない）→ 誤った `no_progress_stop`。P1-B で worker 自身が acceptance を回すので attempt 1 でも起きうる
  - Codex P2-3: 逆に未追跡を見落とす（`status.showUntrackedFiles=no`）と、コミットしていない新規ファイルを使って緑になりうる
  - Codex P2-2 / security LOW 1: verify が追跡ファイルを書き換えた場合・skip-worktree / assume-unchanged の印がある場合、コミットの内容は検証されていない（文書の「測った内容＝コミット済み」は言い過ぎ）
  - Codex P1: `worktree add` 失敗経路がロックを解放してから `abort_worktree` する → 並行する同じ id の worktree を消しうる
  - LOW 群: ref の修飾が local-ahead だけ ／ LOCK 絶対化の `cd` が CDPATH の影響を受ける ／ 解放時に自分のロックか確かめない ／ reap の残骸が中断で残る ／ 巨大な TIMEOUT で待ちが無効 ／ `uncommitted` の決まり方が暗黙 ／ テストの孫プロセス
- **選択肢（未追跡の扱い）**: A: verify が新しく作った未追跡ファイルだけを以後の判定から除外（＋ `--untracked-files=all`・verify 後の HEAD と追跡ファイル不変・skip-worktree 等の印の検出）／ B: 未追跡を判定から外す（Codex P2-3 の穴が開く）／ C: 起票して文書だけ狭める
- **採用**: A。LOW 群は全部直す。
- **却下**: Codex P2-4（fingerprint に差分内容を含める）—— 判断 5 の意図は「commit しないまま続けば、内容が動いていても止める」。未コミットの継続そのものを前進なしとみなす。

## 判断 11: /cross-review 2 巡目（Codex ∥ code-reviewer・7cef46bd）の指摘を全部直して終える

- **判断日時**: 2026-09-26（研究者裁定）
- **背景**（メインが一次で照合済み・HIGH なし）:
  - 両者一致: watchdog の後に生成集合を記録していない（文書・コメントと食い違う）／ `grep -Fxq "$path"` に `--` が無く `-` 始まりの生成物名で毎回 dirty
  - Codex P1: verify・watchdog の後の不変確認で skip-worktree / assume-unchanged の印を見ていない
  - code-reviewer MEDIUM: pid の書き込み失敗で「自分の pid のときだけ解放」がロックを永久に残す（判断 10 で入った経路）／ テスト 13f が空振りしうる
  - code-reviewer LOW: HEAD 取得が前後とも失敗すると不変確認が素通り ／ 無修飾の `$base` で同名 tag が黙って切り元になる経路 ／ sparse-checkout の限界の記載 ／ 引用パスの除外・assume-unchanged・N5 の判定のテスト補強
- **選択肢**: A: 全部直して終える（cross-review は 2 巡で打ち切り・メインが diff を一次で確認し全検査を緑に）／ B: 全部直して 3 巡目 ／ C: 一致と MEDIUM だけ
- **採用**: A

## 判断 12: タスク完了時の出荷フロー（commit → push → PR → CI 緑なら merge）を既定にする

- **判断日時**: 2026-09-26（研究者の指示「push、PR、CI 緑なら merge。今後この Git 関連の指示はこの形で動きたい」）
- **採用**: `git-workflow` Skill にルール 6（手順と「止まる条件」の SSOT）を足し、`/finish-task` に Step 4.5 を足してそこから呼ぶ。都度の承認は求めない。
- **止まる条件**: CI 赤・未対応の HIGH・non-fast-forward・conflict・`--admin` が要る・main 上・機密混入・研究者の明示の別指示。`--force` / `--admin` は使わない。
- **経緯**: `/finish-task` の制約行「ユーザー承認なしで commit しない」の書き換えは auto mode の安全判定で 2 回拒否された（研究者の許可後も）→ 研究者が手で書き換えた。
- **初回の実地**: PR #224 は最初の CI が赤（テストの環境依存・C ロケール）→ 止まる条件どおり merge せず、原因を直して緑を確認してから merge（`1fdd9137`・main の run 発火を確認）。
