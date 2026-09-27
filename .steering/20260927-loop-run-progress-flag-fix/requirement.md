# loop-run-progress-flag-fix

## 背景

`scripts/loop-run.sh`（モード C の無人オーケストレータ）の DAG 実行ループは、
`while` を続けるかどうかを `progressed`（そのバッチで `issue_done` が 1 件でも出たか）だけで決めていた。
`parallel=1` のとき、バッチが無関係な issue の失敗 1 件だけで終わると `progressed=0` でループを抜け、
依存を満たしているのにまだ試していない issue まで、末尾で `blocked（依存 issue が未完のため未実行）` にされた。
2026-09-27 に `.steering/20260927-precondition8-t3-and-consent/` で実測した
（issue 005 は Dependencies なしなのに 2 回とも blocked になり、worktree は一度も作られなかった。
同じディレクトリの blockers.md §1 に記録）。

あわせて、依存の DAG 判定（events の `issue_done`）と、依存先の成果物が base ブランチへマージされていることは
別物なのに、その運用手順が SSOT に書かれていなかった（同じ blockers.md の §2）。

## ゴール

- 依存を満たした issue は、同じ run の中で無関係な issue が失敗しても**必ず 1 回試される**。
- 同じ issue を同じ run の中で**再試行しない**。ループは**必ず終わる**。
- 失敗した issue に依存する issue は、従来どおり `blocked` にする。
- 「依存先の成果物を要する issue は、依存先を base にマージしてから spawn する」を
  `docs/loop-engineering.md` に書く。

## スコープ

### 含むもの
- `scripts/loop-run.sh` の DAG 実行ループ（`progressed` の扱い）
- `scripts/loop-run-guard-test.sh` への回帰テスト追加（stub ハーネス）と、変異テスト
- `docs/loop-engineering.md` への是正の記録と運用手順

### 含まないもの
- 依存先の自動マージ（不具合 2 のコードでの修正。無人で base を書き換えることになるため）
- `loop-spawn.sh` / `loop-worktree-deny.sh` など、ほかの Loop 基盤ファイル
- `ensure_branch` / `permission_denials` など、この不具合と関係のない既存機構

## 受け入れ条件

- [ ] 新しいテスト（失敗する 001・独立した 002・001 に依存する 003）が、旧実装で赤・新実装で緑になる
- [ ] 002 が `issue_done` になり、003 が `blocked` になり、001 の `attempt_start` 数が `max_attempts` を超えない
- [ ] `progressed` 条件を戻す変異でテストが赤になる
- [ ] `bash scripts/loop-run-guard-test.sh` が全件合格する（exit 0）
- [ ] `docs/loop-engineering.md` に是正と、依存先を base にマージする手順が書かれている

## 関連ドキュメント

- `.steering/20260927-precondition8-t3-and-consent/blockers.md` §1・§2
- `.steering/_handoff/next-session-loop-run-progress-flag-bug.md`
- `docs/loop-engineering.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 直し方は 2 案だけで、一次のコードを読むと案 A が「条件を 1 つ消すだけ」に帰着し、自明だったため（grill で確定）。
