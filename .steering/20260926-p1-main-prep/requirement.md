# D. P1 本体の準備 —— 凍結値で 3 極を回し解析する「器とテスト」

## 背景

- 研究者と合意した順番（2026-09-26）: A（Loop 基盤・完了）→ B（事前宣言 v1.1・完了 PR #227）→ **D（本タスク）** → O1 / G1 の収集中に C ＋ 研究案。
- 事前宣言 `docs/preregistration-p1-episode.md` **v1.1**（凍結 JSON `src-tauri/prereg/p1-episode.json` = `1.0.0`）は凍結済みである。
  実行側の道具（`gse-replay --features --pole …`・`scripts/run-features-all-poles.sh`・`scripts/check_prereg_parity.py`）も揃っている。
- ⚠️ ただし **`--features` の出力を読むコードは repo に 1 本も無い**（2026-09-26 実測: `pole_applicable` / `prereg_version` を参照するのは `run-features-all-poles.sh` と `replay.rs` だけ）。
  → v1.1 が定めた**読み方の規則**（冒頭 (3)(5)・(1) の retrospective 注意）は、**検査も実装も無い**（前タスク `design.md` 末尾「検査が届かないもの」）。
- ⚠️ **P1 はまだ回せない**（研究者回答 2026-09-26: **G1・O1 とも収集未開始**）。事前宣言 §2.2 は探索を「WP1（O1 natural-work discovery）の内側でのみ」とする。
- ⚠️ **G2 はまだ計算できない** —— G2 は「recovery risk の上下界の幅が介入判断を反転させるか」（`personalization-and-online-learning.md:1174`）で、
  recovery の推定器も介入判断も未実装。→ 上下界の規則は **任意のスカラー量に対する汎用の結合器**として作る。

## ゴール

**実データに 1 度も触れずに**、P1 の実データが届いた日に次を 1 コマンドずつで回せる状態にする:

1. `--features` の 3 極出力を参加者ごとに読み、**PG-1 に渡す「参加者ごとの episode 数の分布」だけ**を出す
   （⚠️ 転帰・予測成績・`restart`・`ime_overlap`・`T1a` を**構造的に**読まない）
2. v1.1 の読み方の規則 (a)〜(e) を**テストで固定した**コードとして持つ
3. §2 の探索（27 通り ＋ OFAT 4）を回す**器**と、grouped nested CV の**選択器**を持つ
   （⚠️ PG-1 の値・転帰ラベルが無ければ**拒否**する。推測で埋めない）
4. episode 表を DuckDB に載せる（repo の外・共有しない）
5. 再現の雛形（seed / 入力の commit / `HMM_VERSION` / lockfile の刻印）と 1 コマンド再現
6. 起票 P1-G / P1-A と #8（`feat` 行 0 本の `T1a`）を閉じる

## スコープ

### 含むもの
- Python（`scripts/`・stdlib ＋ 既存の dev 依存 duckdb のみ）: 軸ごとの上下界の結合器 ／ 特徴出力の読み込み ＋ PG-1 分布集計 ／ episode DB ／ 探索格子の実行器 ／ nested CV 選択器 ／ 再現の雛形
- Rust: P1-G（`--feature-config` の `id` / `version` の検証）／ P1-A（凍結既定で restop が測れる fixture とテスト）／ #8（`feat` 行 0 本で `T1a` を `null`）
- ADR-030 **補訂 3**（#8 の裁定・P1-F の裁定を記録。本文は書き換えない）
- `docs/glossary.md` への用語追加・`docs/verification-runbook.md` への手順追加

### 含まないもの（Out）
- ⚠️ **実データ（NDJSON・metrics・`--features` の出力）を開く・集計する・試しに 1 本回す**
- ⚠️ PG-1 の**値**を決める・PG-1 を通す（WP1 の yield の直後の研究者判断）
- ⚠️ 凍結文書 v1.1・凍結 JSON を書き換える（値を変えるなら v1.2 として別タスク）
- ⚠️ 転帰（ADR-029 D3 の競合リスク 4 択）の**定義**・recovery 推定器・G2 の中身
- ⚠️ `gse-replay` の CLI に `q`→`warmup_count` の連動を持たせる（P1-F は「CLI を変えない」と裁定）
- ⚠️ metrics.json・probe ラベル・survey との結合（episode 表と sessions.csv まで）
- ⚠️ ADR-030 D9（壁時計の非単調性）・E1（連結の実装形）
- ⚠️ `experiments/<日付>-…/` の実体を作る（P1 を始める日に作る）・O1 の実験 dir（`left-observation-decomposition`・別タスク）
- ⚠️ C トラック（`.steering/20260921-media-expression-theory-audit/`）

## 受け入れ条件

- [ ] issue 001〜009 の acceptance がすべて exit 0（merge 前にメインが clean な checkout で回す）
- [ ] `cargo test --manifest-path src-tauri/Cargo.toml --workspace` 緑 ／ clippy `-D warnings` 緑
- [ ] `python -m unittest discover -s scripts/tests -t . -p "test_p1_*.py"` 緑・**skip 0**（duckdb を入れた状態）
- [ ] `bash scripts/check-tests-are-wired.sh` exit 0（新しいテストが CI に配線されている）
- [ ] `python scripts/check_prereg_parity.py` exit 0 ／ `git diff main -- src-tauri/prereg/ docs/preregistration-p1-episode.md` が空
- [ ] ゴールデン再生（`minimal.ndjson` snapshot）緑・`HMM_VERSION` 不変
- [ ] 通し検査: repo の**合成 fixture**（`src-tauri/tests/fixtures/*.ndjson`）を参加者レイアウトに並べ、3 極 → PG-1 分布 → episode DB → 格子（偽 replay）→ 選択器（合成 PG-1・合成ラベル）が端から端まで通る
- [ ] `/cross-review` 2 巡・code-reviewer ＋ security-checker 並列

## 関連ドキュメント

- `docs/preregistration-p1-episode.md`（v1.1・**全文**）／ `src-tauri/prereg/p1-episode.json`
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md`（補訂 1・補訂 2）
- `docs/architecture/personalization-and-online-learning.md` §8.2 / §10 / G2 の表
- `.steering/20260921-p1-prereg-cli-poles/decisions.md`（起票 P1-A / P1-F / P1-G）
- `.steering/20260926-prereg-p1-episode-v1-1/design.md`（検査が届かないもの）
- `docs/loop-engineering.md` ／ `reproducibility-discipline` Skill ／ `docs/experiment-tracking.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 判断分岐は grill（研究者との 5 往復）で閉じた。設計の自由度は各 issue の内部実装に限られ、Loop の verify で機械的に検出・再試行できる。
- Loop: **分解する**（モード C を想定）。分解後は `/clear` して別セッションで実行する。
