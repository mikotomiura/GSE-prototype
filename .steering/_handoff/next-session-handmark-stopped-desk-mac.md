# 引き継ぎ（Mac）: 手跡の止まりの層（ADR-056）—— 本人の記録での机上の確かめ

作成 2026-11-22（G-GEAR・Windows）。前のセッションは PR-b の道具（出力の口・重ね描き・検定）を作り、合成の対照で確かめ、研究者が条件を固定した（判断 13・14）。本人の段 1 の記録・割付の表・回 1 の venv は Mac にあるので、本人の記録で回すのはこの Mac のセッションで行う（判断 14）。
応答と記録は日本語で書く。★・⚠️ などの記号を多用しない（研究者の指摘）。

## 0. 始める前に

- 枝は `feature/handmark-stopped-state-prototype`。Mac では worktree を新しく作ってこの枝を取る（並行のセッションがあるかもしれない・`git add -A` は使わない）。`git fetch` してから、origin の先端（この引き継ぎを入れたコミット）と揃っているかを見る。
- 先に読むもの: `.steering/20261121-handmark-stopped-state-prototype/decisions.md`（判断 9〜14）・`experiments/20261121-handmark-stopped-desk/conditions.md`（固定済み・変えない）・`notes.md`・`results/controls_report.md`。`.claude/skills/reproducibility-discipline/SKILL.md`。
- 条件は固定してある。変えたくなったら、記録を開く前か後かを書き、新しい版として残す（黙って変えない）。

## 1. 準備（Mac）

1. `cd src-tauri && cargo build --bin gse-replay --bin gse-handmark-table`（debug）。
2. `experiments/20261121-handmark-stopped-desk/` と `experiments/20261115-handmark-leak-desk/` の両方で `npm ci --ignore-scripts`（`overlay.mjs` は漏れの道具の `pixels.mjs` を借りる）。
3. venv は回 1 と同じ `~/gse-venvs/handmark-desk`（numpy 2.5.2）。
4. 先に `bash run.sh selftest`。時間があれば `bash run.sh controls`（12 分ほど・Windows での結果 `results/controls/` と判定が同じになるかを見る。数値は機械で少し違いうる）。

## 2. 回す

```bash
cd experiments/20261121-handmark-stopped-desk
RECORDS_DIR=… TABLE_JSON=… TABLE_SHA=… UTC_OFFSET_SECS=32400 bash run.sh records
```

- 記録の場所・表の場所は回 1 と同じ（`../20261115-handmark-leak-desk/data.md` の「本人の記録」・表の SHA-256 `e19e51c9…20da`）。削除の台帳は既定で記録の場所の `redaction_ledger.jsonl`。
- 9 版 × (i)〜(iii) × 3 層と、9 版の漏れの検査を回す。数時間かかりうる。結果は `results/records/<回>/`（`elapsed_*.json`・`leak_*.json`・`report.md`・`inputs.json`・`capabilities.json`）と `results/records/runs.txt`。
- Claude が読むのは `results/records/<回>/` の集計だけ。記録・中間（WORK）は開かない。

## 3. 結果を書く

- `report.md` と JSON の一次を読んでから、decisions.md に新しい判断（15 から）として書く。推測で書かない。必ず止まりの数・日の数・帰無の平均と SD・95% 点を添える（判断 9）。
- 上回った件があれば、W・形をまたいで揃うか、基層だけ・止まりの層だけの層の分けでどちらが運んだかを添える（conditions.md E5・E6）。27 件は補正していないので、1〜2 件は偶然でも上回りうる。
- (iii) で最終の画と基層だけの画の両方が上回ったら、研究者に確かめる（基層の位相も有限の窓の平滑に置き換えるか、残すか・E8）。黙って消したり残したりしない。
- 漏れの検査は 9 版の主の判定を表にする。「満たさない」の版があれば、研究者に伝えて、その版を候補から外すかを決めてもらう。
- `data.md` に日の範囲（最初と最後の日付）と回の番号を、`env.md` に Mac の版を足す。
- `results/records/` をコミットする（明示のパスで）。

## 4. その後（完了処理）

- /cross-review を 2 巡回す（1 巡目は矛盾、2 巡目は足した規則の境界条件）。範囲は PR-a と PR-b の差分 `bd557a6b..HEAD`。Codex にはコードの差分だけを渡す。`results/records/` の数値・記録は含めない（パスで絞る）。
- PR を 1 本にするか、PR-a と PR-b に分けるかを研究者に確かめる（判断 9 の分け方）。
- /finish-task から出荷のフローに進む。
- 次のタスクの引き継ぎを書く: 研究者自身の試しと手動の確かめ、値の確定、ADR-056 の「決めずに残すもの」1。どれも段 1 の期間の外で行う。起動は `GSE_DEBUG=1` と `GSE_HANDMARK_STOPPED=form=band;rise_ms=2000;window_s=20;strength=0.5`。

## 5. してはいけないこと

- 止まりの長さ・経過時間・残り時間・累計を、見た目でも数字でも返さない。推定の出力を手跡に入れない（ADR-025 D1・ADR-048 D2・ADR-047 D2・ADR-056）。
- 研究者自身に止まりの層を画面で見せない（段 1 の期間の外で行う・判断 5・12）。机上の描き直しは晒しにならない。
- 本人の記録・NDJSON・results の数値を外部の LLM（Codex を含む）に送らない。
- 回 2（12-09 以降）で使う机上の道具の、切っているときの出力を変えない。再生の決定性（`to_bits` の一致）を壊さない。
- `git add -A`・`git add <dir>` を使わない。`.codex/budget.json` を `git checkout --` で戻さない。権限を自分で広げない。
- 事実を断定する前は `verify-before-claiming`、サブエージェントに渡す前は `subagent-delegation` を読む。

## 6. 道具の要点（PR-b で足したもの）

- `gse-replay --handmark-windows … --stopped <cfg>`: 窓の行に `b_stopped`（9 列）を足す。ヘッダに `stopped`・`b_stopped_names`・`live_lag_ms` を足す（切っているときは何も足さない）。
  - `--stopped-frames <path>`（`--frames` と同じ順の止まりの層のコマ）
  - `--stopped-stops <path>`（止まりの一覧）
  - `--stopped-queries <q> --stopped-query-frames <path>`（指定した時刻のコマ）
- `desk.rs`: `build_with`・`stream_samples_stopped`・`stop_episodes`・`all_stops`・`render_queries`・`prepared_segments`・`pause_events`・`b_stopped_features`。
- 実験: `scripts/synth_stops.py`・`queries.py`・`overlay.mjs`・`elapsed.py`・`leak_prime.py`・`selftest.py`・`report.py`。
