# 引き継ぎ: p1-sleep-trim の残り（PR #329 / #327 の後始末と O1 草案への参照）

作成 2026-10-09（G-GEAR）。どの機でもよい。返答・記録では絵文字や記号（★・⚠️）を多用しない（研究者の指摘）。応答は日本語。

## 0. 始める前に

- `CLAUDE.md` の順に従う: 該当コマンド（`/start-task` か、steering だけの変更なら直接）→ `docs/agent-shared.md` → 該当 Skill。
- `git fetch` してから、最新の `origin/main` から作業ブランチを切る。`git add -A` / `git add <dir>` は使わず、ファイルを名指しで載せる（作業ツリーに別の未コミットの作業がある）。
- NDJSON の生ログや打鍵の内容を外部の LLM（Codex を含む）に送らない。

## 1. 何が済んでいるか

- issue #330 の前処理（`gse-replay --features` の無入力の末尾の前処理・凍結 JSON 1.1.0・事前宣言 v1.2 §6・ADR-030 補訂 4）は `feature/p1-sleep-trim` で実装した。記録は `.steering/20261008-p1-sleep-trim/`（判断 1〜8・verification.md）。
- アプリ側は #331（次に配布が要るときにまとめて入れる。O1 は v0.1.40 のまま）。

## 2. 残り

### 2-1. O1 事前登録の草案に参照を足す（PR #329 の merge の後）

> 済み（2026-10-09）: #329 と #332 が main に入った後、草案の §4 に 4-7 を足し、改訂履歴に 1 行足した。ブランチ `docs/o1-draft-idle-trim-ref` に push しただけで、PR は出していない（`.steering` だけの変更は push だけ・研究者の指示 2026-10-05）。main へは次の PR に含めて入れる。

- 草案 `.steering/20261007-o1-preregistration-draft/preregistration-draft.md` は PR #329 にだけある（main には未着）。#329 は 2026-10-08 に Windows の CI が 2 回止まった（1 回目はループの検査 `11g` の時間の検査、2 回目は 30 分の時間切れ）。変更は docs だけで、止まった理由は G-GEAR の負荷。研究者の指示は「赤は必要になったら再開」。
- #329 が main に入ったら、草案の §4（前処理の先頭に置く必須検査）に 1 行足す:
  - 4-7: P1 の stall onset と観測区間は、事前宣言 v1.2 §6 の無入力の末尾の前処理の後の値を使う。前処理なし（`--set idle_trim_max_ms=0`）を並べて報告する（2 本は真の値を挟む上下界ではない）。`provenance.idle_trim` の `dropped_feat_rows` と `spans` の本数を報告する。
  - acceptance の形は、ほかの 4-x と同じく「(1) 陽性 (2) 陰性対照」で書く（草案の §4 の表を読んでから）。

### 2-2. PR #327 の `.codex/budget.json` の競合（直すとき）

- 競合は `.codex/budget.json` だけ。台帳は合算する（`_comment_merge_2026_09_11` の規則）。
- 2026-10-08 の時点の数: 共通の起点 217,278 / 5 回、main 側 +23,156 / +1、#327 側 +35,320 / +1 → 10-08 の和は **275,754 / 7 回**。
- 注意: `feature/p1-sleep-trim` が main に入ると、main の `today` は 2026-10-09 に繰り越されている（10-08 は `history` に 240,434 / 6 回で入る）。そのときは、main の `history` の 10-08 を 275,754 / 7 回に直し、`today`（10-09）は main の値のまま残す。#327 側の `today`（10-08）は捨てて `history` の和に含める。merge の注記を `_comment_merge_...` として 1 つ足す。
- `git checkout -- .codex/budget.json` で台帳を戻さない（記帳が消える）。

### 2-3. PR #329 / #327 の CI

- どちらも Windows の check が G-GEAR の上で 30 分の上限に近い。走らせ直すときは、G-GEAR でほかに重い処理（cargo のビルドや別の CI）が走っていないときに 1 本ずつ回す。上限の余裕の話は `.steering/_handoff/next-session-win-ci-timeout-headroom.md`。

### 2-4. issue #330 の任意の項目（未着手）

- Windows のバッテリーでの長いスリープ・蓋閉じ・複数回で、寝てから記録が止まるまでが毎回 16 分前後か。macOS で複数回・長時間でもすぐ穴になるか。手順は `.steering/_handoff/next-session-windows-sleep-test.md`（PR #329 の中）。
- 試験の記録は研究者の手元（Surface の `Documents\GSE-sleeptest-20261008\`・G-GEAR の `Downloads\GSE-sleeptest-20261008-...\`）。repo に入れない。

## 3. してはいけないこと

- 事前宣言 v1.2 の値（`idle_trim_min_gap_ms` / `idle_trim_max_ms`）を、P1 の実データを見た後に変えない（変えるなら新しい版で、データを見る前に）。
- 前処理ありの結果を「補正済み」と書かない。2 本が真の値を挟むと書かない。
