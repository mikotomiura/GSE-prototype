# empirical-prompt-tuning —— 本タスクで書き換えた Loop の指示文（研究者依頼 2026-09-26）

- **tier**: Lite（重要度 MID のワークフローコマンド・変更は数行）。2 シナリオ × 2 iter ＋ シナリオ B のみ確認 1 回（iter 2 の後に入れた修正を未検証で残さないため）。
- **実行者**: `general-purpose` / Sonnet（本番の worker と同じ model）・毎回新規 dispatch・ファイル編集とコマンド実行を禁じた思考実行。
- **Iteration 0（静的）**: `loop-status.md` / `loop-issue.md` / `loop-worker.md` の description と本体に、今回の変更による乖離なし。

## シナリオとチェックリスト（事前に固定）

**A（median）: `/loop-status` の畳み込み** —— `uncommitted`・attempt_start の WARN 重複・`no_progress_stop`・`acceptance_fail → issue_done` を含む events から board を作る。
1. [critical] 001 を 🔄 running・try=2（done / blocked にしない）→ 理由: 最終 event 優先が契約
2. [critical] 002 を ⛔ blocked・note に no_progress_stop の理由 → 理由: Stop は人へのエスカレーション
3. 003 ✅ done・004 ⏳ queued ／ 4. `uncommitted` を未知扱いしない ／ 5. WARN 重複で try を水増ししない ／ 6. サマリと表が整合

**B（edge）: `/loop-issue` ＋ `loop-worker` —— verify 緑・未コミット・残りターン 3〜4**
1. [critical] commit 前に `issue_done` を出さない → 理由: P1-I の契約
2. [critical] 具体パスで `git add`・checkout / switch / stash を使わない → 理由: 隔離と運用の契約
3. commit を最優先 ／ 4. 語彙表の event だけ ／ 5. commit できたとき `uncommitted` を書くかの根拠 ／ 6. watchdog を通す

## Iteration 1

| シナリオ | 成功 | 精度（指示側判定） | steps | duration |
|---|---|---|---|---|
| A | ○ | 100% | 2 | 113s |
| B | ○ | 92%（項目 3 部分的: commit より先に `uncommitted` の append に 1 ターン使った） | 16 | 296s |

- 不明瞭点（今回の変更由来）:
  - A: verify 列で `uncommitted` / `acceptance_fail` をどう書くか未規定
  - B: 「`uncommitted` を append し、commit してから次 attempt へ」の語順を字義どおり読み、**commit できる状況でも先に event を書いた**（残りターンを浪費）
  - B: `docs/loop-engineering.md:238` に「events 語彙は 10 種で固定」が残っていた（語彙表は 12 種）
- 範囲外として記録のみ: A の branch / PR / 時刻（シナリオで実行を禁じたため）、B の events JSON の形がモード A/B の文書に例示されていない（既存）
- **修正**: loop-issue / loop-worker を「まず自分で commit → commit できたら verify へ（`uncommitted` は書かない）→ commit できずに終えるときだけ `uncommitted`」に。loop-status に `acc✗` / `未コミット` の表記。loop-engineering.md の「10 種」を「語彙表の種類」に。

## Iteration 2

| シナリオ | 成功 | 精度 | steps | duration |
|---|---|---|---|---|
| A | ○ | 100% | 2 | 89s |
| B | ○ | 100%（commit を最初の 1 手に・`uncommitted` を書かない根拠を本文から引用） | 8 | 286s |

- iter 1 の不明瞭点はすべて解消。B の steps は 16 → 8。
- 新出（今回の変更由来）: B —— 「verify の前に確かめる」項目を「4. verdict で分岐」の中（verify の後の手順）に置いていたため位置が紛らわしい
- 新出（範囲外・既存の記述）: A —— 失敗回数の括弧の位置・attempt_start の WARN を置く列 ／ B —— `issue_done` を書くのが command か watchdog か（`loop-watchdog.md` との二重読み）
- **修正**: 項目を手順「1.5」（verify の前）へ移した。

## 確認（シナリオ B のみ・iter 2 の後の修正を検証）

| シナリオ | 成功 | 精度 | steps | duration | retries |
|---|---|---|---|---|---|
| B | ○ | 100%（1.5 を根拠に commit を最初に・成功時は `uncommitted` を書かない・失敗時のみ書く、を分けて説明） | — | — | 0 |

- 今回の変更に由来する新しい不明瞭点: **なし**（iter 1 → 2 → 確認で、変更由来の不明瞭点が 3 → 1 → 0）。
- 範囲外として残る既存の不明瞭点（★ 起票のみ・本タスクでは直さない）:
  - events の JSON の形（キー名）がモード A / B の文書に例示されていない（`README 2.4` への参照だけ）
  - `issue_done` を書くのが command か watchdog か（`loop-watchdog.md` との二重読み）
  - `/loop-status` の失敗回数の括弧の位置・attempt_start の WARN を置く列
  - max_turns（セッションのハード制約）と Loop の Stop 条件の関係
- **結論**: 収束扱いで打ち切る（Lite・変更由来の不明瞭点ゼロ・両シナリオ 100%）。hold-out は Lite のため行っていない。
