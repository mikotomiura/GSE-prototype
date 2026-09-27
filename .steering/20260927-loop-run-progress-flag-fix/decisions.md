# 重要な設計判断

## 判断 1: 不具合 1 は `progressed` の継続条件を削除する（案 A）

- **判断日時**: 2026-09-27
- **背景**: `while` が「バッチで `issue_done` が出たか」だけを見ていたので、「このバッチは失敗した」と「ほかに試せる issue が無い」を区別できていなかった。
- **選択肢**:
  - A: 継続条件を「`deps_met` が真の issue が `remaining` に残っているか」にする。
  - B: 失敗した issue を `remaining` に残し、成功した issue だけを外す（再試行を防ぐガードが別に要る）。
- **採用**: A
- **理由**: 「試せる issue が無ければ抜ける」判定は、既存の `[ -n "$batch" ] || break` がもう持っている。なので案 A は `progressed` を消すだけで実現できる。バッチの issue は成否に関わらず `remaining` から外れるので、ループを 1 周するたびに `remaining` は 1 件以上減る。そのため**同じ issue は再試行されず**、**ループは必ず終わる**（周回数は多くても issue 数まで）。案 B では、同じ run の中で失敗した issue を再試行するという新しい挙動が入る。
- **トレードオフ**: 失敗した issue を同じ run で再試行しない（従来どおり）。
- **影響範囲**: `scripts/loop-run.sh` の DAG 実行ループだけ。
- **見直しタイミング**: 同じ run の中で失敗した issue を自動で再試行したくなったとき。

## 判断 2: 不具合 2（依存先の成果物が base に無い）は docs に書くだけにする

- **判断日時**: 2026-09-27
- **背景**: `deps_met` は events の `issue_done` しか見ない。各 issue は base から切った別の worktree で動くため、依存先の成果物は base に入っていない。
- **選択肢**:
  - A: `docs/loop-engineering.md` に運用手順を書く（コードは変えない）。
  - B: `loop-run.sh` が依存先の `loop/*` ブランチを base に自動でマージする。
- **採用**: A
- **理由**: B は無人で base ブランチを書き換えることになり、今回の範囲（progress フラグ）を超える。人が merge ゲートを握るという既存の境界とも衝突する。
- **トレードオフ**: 波（ウェーブ）の間の手動マージは、引き続き人の仕事になる。
- **影響範囲**: `docs/loop-engineering.md`
- **見直しタイミング**: 依存 chain が長い task で、手動マージが律速になったとき。

## 判断 3: 検証は stub ハーネスと変異テストで行う（本物の claude では回さない）

- **判断日時**: 2026-09-27
- **背景**: 引き継ぎメモは「bash の単体テストが無いので実地で回す」としていた。しかし実際には `scripts/loop-run-guard-test.sh` があり、一時 repo と `claude` stub で本物の `loop-run.sh` を回している（一次資料で確認）。
- **採用**: `loop-run-guard-test.sh` に回帰テストを足し、旧実装で赤・新実装で緑・変異で赤の 3 点を確かめる。
- **理由**: 修正したのは bash の制御フローだけで、claude の振る舞いには依存しない。stub なら「失敗する issue」を決定的に作れる。

## 判断 4: 境界侵害と token_ceiling 超過のときだけ run 全体を止める（1 巡目レビュー後）

- **判断日時**: 2026-09-27
- **背景**: security-checker から MEDIUM の指摘を受けた。旧実装では parallel=1 のとき「どれか 1 本の失敗でループを抜ける」挙動が、境界侵害（ブランチ逸脱・履歴の差し替え・deny を保証できない）に対しても**偶然** fail-closed として効いていた。判断 1 の修正でこれが消えたので、逸脱した worker の後でも次の issue が spawn されうる。
- **選択肢**:
  - A: 何もしない（issue 単位の blocked だけ）。
  - B: 境界侵害（`ensure_branch` / `ensure_deny` の blocked）だけで run を中止する。通常の失敗では止めない。
  - C: 旧実装に戻す（どの失敗でも止める）。これは不具合 1 そのもの。
- **採用**: B。あわせて token_ceiling もバッチを組む前に見る（security-checker LOW）。
- **理由**: 「通常の失敗」と「隔離が崩れた」は性質が違う。後者の後に spawn を続けると、base に残ったものから切りうる。
- **実装**: `run_issue` はバックグラウンドのサブシェルで動き変数を親へ返せないので、`$WORK_TMP/boundary-breach` というファイルで伝える（`mark_boundary_breach`）。
- **テスト**: P3（逸脱の後は 002 / 004 を spawn しない）と M-bnd（印を無効化すると赤）。P4（token_ceiling=0 で worktree 0 本）は、事前検査を外すと赤になることをその場で確認した（スイートには変異を入れていない）。

## 判断 5: 「--issues なしの再実行で done が再 spawn される」は docs に書くだけにする

- **背景**: cross-review（Claude 側）の MEDIUM 指摘。一次で確認したところ、`is_done` は `deps_met` の中でしか使われていなかった（事実）。ただし既存の挙動で、今回の diff より前からある。
- **採用**: `docs/loop-engineering.md` に明記し、2 波目以降は `--issues` で未完の id だけを渡すよう書いた。コードは変えない（`done` を外すと後続の `deps_met` が壊れる、という既存の判断に触れるため。次に loop-run.sh を触るときの候補）。

## 判断 6: 最終 code-reviewer 指摘への対応（2 巡目）

- **MEDIUM 1**（最終 attempt の verify / watchdog 中の逸脱に印が付かない）→ `run_issue` を薄いラッパーにし、本体（`run_issue_body`）が失敗で抜けたら**出口の外側で 1 回だけ** `ensure_branch` を見る。出口を 1 つずつ塞ぐ案は、出口が 4 つ以上あって塞ぎ漏れが出やすいので採らなかった。本体は worktree とアンカーを `$WORK_TMP/wt-<id>` に残す（サブシェルなので変数では渡せない）。P3c で固定した。
- **MEDIUM 2**（中止したことが report と終了コードに出ない）→ report に「run を中止した理由」節を出す。**境界侵害は exit 3**。**token_ceiling は exit 0**（予定された予算の停止で、人が介入すべき異常ではないため）。
- **LOW** → 印を書けなかったら log を 1 行残す／P3b（履歴の入れ替え経路）／P5（`grep -F`）／docs に parallel>1 の注意を追記。
  - `ensure_deny` の経路は動作テストしていない（M-bnd は関数全体の変異なので、呼び出し 1 行を消しただけでは赤にならない）。→ 未対応として残す。
  - `tokens_used` が空のときの fail-open は、既存の :713 と同じ型なので対象外にした。
- ⚠️ 途中で「`run_issue_body` の `trap … RETURN` が関数を抜けても残り、`set -u` で落ちる」と考えて解除を入れた。しかし実測（functrace 無しの bash では、後の関数に引き継がれない）で**誤り**と分かったので取り除いた。
