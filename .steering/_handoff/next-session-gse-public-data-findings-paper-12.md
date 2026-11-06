# 次のセッション —— 公開データの知見の論文 1: 推定器の切り出しの後（公開 repo の組み立て・round 3 の要否）

> 作成: 2026-11-06。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-11.md` の §2 の 2 は済んだ。研究者が決めた順は (2) 切り出し → (3) 公開 repo → (4) attack-me round 3。

## §1 状態

- 著者への問い合わせ（前の §2 の 1）: 研究者が送った（2026-11-06）。返事待ち。返事で推定の行・取り置きの id の一覧の扱いを決め、考察の Materials と限界を直す。
- 推定器と replay の切り出し（前の §2 の 2）: 済み。e20b63b0（push 済み）。記録は `.steering/20261106-estimator-replay-extract/`（判断 1〜4）。
  - crate: `papers/public-data-findings/kit/estimator/`。GSE 24767c7e の `analysis/` の OS 非依存の部分を逐語で写し、gse-replay を引数なしと `--features`（`--set`・`--feature-config`・`--pole`）に縮めた。自前の `[workspace]`・GSE の CI の外・MIT OR Apache-2.0・版 0.1.40（`--features` の出力に版が出るので変えない）。
  - 元との関係: `provenance/manifest.json`（種別 file / trimmed / excerpt / cut / lock / new）と `provenance/check_provenance.py`（`--self`・`--upstream <gse-checkout>`・`--write`）・`provenance/replay.rs.diff`。
  - 門: `gate/run-gate.sh <cs1|cs1-variants|coauthor|klicke>`。論文の計算のスクリプト（書き換えない）に `gate/compare-replay.sh` を replay として挟み、旧（`~/gse-public-data/klicke/bin/gse-replay`・SHA-256 26cae610…33bb3）と新の stdout・終了コード・stderr を比べる。結果は不一致 0（CS1 2019 は 3,723 呼び出し・中間 1,078/1,078、`--set` 変種 3 つは 4,304・3×1,076、CoAuthor は 2,357・書き手 43/43、KLiCKe は 9,984・4,992/4,992）。件数だけが `gate/results/`。陽性対照（係数を 1 か所変えた版で不一致）は README に。
  - 新しい版の一致の証拠は呼び出しごとの比べだけ。中間物の一致は「論文と同じパイプラインとデータで同じ呼び出しをした」裏づけ（README に書いた）。`--feature-config` と `--pole` は門を通していない。

## §2 やること（研究者に順を確かめてから）

1. 公開 repo の中身（前の §2 の 3）を repo の外に組む。/start-task で別のタスクとして始める。
   - 入れるもの: `kit/estimator/` 一式（`target/` を除く）、評価と探索のコード、変換、係数の表、README（英語と日本語版・図つき。手本は Affective-Tactility-Works-public）。
   - 入れないもの: 書き手ごとの値・推定の行・取り置きの id の一覧（CS1 の約束・著者の返事待ち）、入力のフック・logger・介入・O1、データそのもの。
   - crate を写したら、写した先でも `cargo test --locked` と `check_provenance.py --self` を通す（`--upstream` は GSE の checkout が要る）。README の「GSE commit 24767c7e」は公開物として通じるか（GSE 本体が非公開であること）を書き方で考える。
   - GitHub の repo の作成と Zenodo の公開は、押す前に研究者に確かめる。公開したら要旨の置き字を DOI に。
2. attack-me round 3 を回すか（前の §2 の 4）。推移は major 2 回。止める理由は E と公開だったので、公開 repo ができてから回すのが筋。回すなら同じ panel・Codex あり・既知の未決は round 2 の tmp/codex-input.md の 18 件を組み直し、推定器の公開で閉じた件を外す。
3. 著者の返事が来たら、その扱いを先にする。

## §3 気をつけること

- 凍結した文書と manifest を書き換えない。推定器の係数を「学んだ」と書かない。書き手ごとの値を repo に出さない・外部の LLM に送らない。取り置きは開けない（一覧は除外にだけ使う）。
- 外枠 v6（outline.md）は書き換えない（草稿が新しい版）。
- `.codex/budget.json` は台帳で未ステージのまま（巻き戻さない）。2026-11-06 の使用は約 58.7 万トークン（上限 80 万）。
- 門を回し直すなら: ディスクの空きは約 9 GiB しかない。並列 7 ではディスクが埋まり、基準の版ごと落ちた。並列 4（`JOBS=4`）で回し、`GATE_WORK` は repo の外（スクラッチ）に置く（repo の中なら門が 2 で止まる）。全部で 4 時間半ほど（CS1 約 45 分・変種 約 2 時間 15 分・CoAuthor 約 2 分・KLiCKe 約 10 分）。
- 返答とファイルは日本語、記号（絵文字・★・⚠）を控える。未決は AskUserQuestion で日本語で聞く。/cross-review は Codex を加える。
