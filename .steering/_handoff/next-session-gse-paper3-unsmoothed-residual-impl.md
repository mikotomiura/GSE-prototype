# 引き継ぎ —— 論文 3 の平滑の無い記号と擬似残差の試験の実装（Mac）

> 作成: 2026-11-07（Mac）。このメモを一次資料にしない。一次は `experiments/20261107-unsmoothed-residual-check/conditions.md`（条件）と `.steering/20261107-gse-paper3-unsmoothed-residual-check/`（判断 1〜6・`design.md` は採った v2）。worktree は `/Users/johnd/GSE-prototype-paper3`（枝 `docs/gse-paper3-per-person-learning`・未 push）。

## 0 入口の文（新しいセッションで `/model sonnet` の後に打ち込む）

```
/Users/johnd/GSE-prototype-paper3/.steering/_handoff/next-session-gse-paper3-unsmoothed-residual-impl.md を読み、experiments/20261107-unsmoothed-residual-check/conditions.md のとおりに実装し、合成の門と変異まで通してください（worktree /Users/johnd/GSE-prototype-paper3）。条件を変えるときは実データを見る前に判断として書き、条件の末尾に足してください。決めることは AskUserQuestion で聞いてください。push と PR は私が確かめてから。
```

## 1 ここまでに済んだこと

- 判断 1〜5（AskUserQuestion）: 列は o・u・n、残差は軸ごとの乱数化した分位の擬似残差、範囲は論文の主の表と同じ、読みの形は向きと大きさの比。
- 判断 6（/reimagine）: v2 を採った。u・n の規則は公開の kit の `variants.py`、記号器は `last_raw` を残すだけ、tau-extend の数式のコードは読み込んで SHA-256 で固定、当てはめ（npz・repo の外）と残差の 2 段、実行は n → o → u。
- 条件と SEED のコミット: efa38fbf（コードより前）。

## 2 実装でやること（`tasklist.md` の「実装」「テスト」）

1. kit: `symbolizer.py` の tick に `self.last_raw = (x_raw, y_raw)`（返す行は変えない）。`variants.py`・README の節・selftest。conformance がそのまま通ること（P-KIT）。
2. `build_variants.py`（Mac）: 生データから新しい中間と P-U の門（全行・外れた行の数だけ）。生データと今の中間の場所は tau-extend の `run.sh` の変数を見る。
3. `fit.py`（乱数の並べは tau-extend の `em_writer` と同じ・作らない k・折り目・hmm6・hmm10 の番は乱数だけ捨てる・P-SAME で tau-extend の `em_writer` と照らす）・`residual.py`・`report.py`・`repro_check.py`・`run.sh`・`mutate.sh`・`selftest.py`。
4. Mac の合成で時間を測り、見積もりを条件の末尾の「条件の後の変更」に足す。
5. code-reviewer と /cross-review（Codex には既知の未決の一覧を添える）。
6. HP Z2 で回す引き継ぎを書く（研究者が回す・n → o → u・o の後に P-REPRO）。

## 3 守ること

- tau-extend と構造の試験（`/Users/johnd/GSE-prototype-structure-deficit`）のディレクトリ・条件・コードを変えない。
- 書き手ごとの値・npz を人が開かない。summary は集計値だけ。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない。
- 公開物（`papers/`）に GSE の名前・内部のパス・番号を書かない（`papers/README.md`）。
- 決めることは AskUserQuestion で 1 問ずつ。返答は日本語。記号を多用しない。
