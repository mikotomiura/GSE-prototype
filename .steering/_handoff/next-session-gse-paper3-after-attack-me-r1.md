# 引き継ぎ —— 論文 3 の attack-me round 1 の後（Mac）

> 作成: 2026-11-07（Mac）。このメモを一次資料にしない。一次は `.steering/20261107-gse-paper3-per-person-learning/decisions.md`（判断 1〜13）と `attack-me/outline-paper3/round-1/verdict.md`。worktree は `/Users/johnd/GSE-prototype-paper3`（枝 `docs/gse-paper3-per-person-learning`・τ の枝の上に origin/main を merge 済み・未 push）。

## 0 入口の文（次のセッションで最初に打ち込む・順に 1 つずつ）

1. 文献の調べ（判断 12）:

```
/Users/johnd/GSE-prototype-paper3/.steering/_handoff/next-session-gse-paper3-after-attack-me-r1.md を読み、論文 3 の文献の調べを /literature-review で 1 ラウンド回してください（worktree /Users/johnd/GSE-prototype-paper3）。決めることは AskUserQuestion で聞いてください。push と PR は私が確かめてから。
```

2. 新しい小さな試験（判断 11）: 文献の調べの後で、同じ形の入口の文で「§3 の試験を /start-task から」と頼む。
3. 外枠の直しと round 2: 文献の調べと試験の条件が済んだ後。

## 1 ここまでに済んだこと

- paper-write Step 0〜5 の計画: 投稿先 UMUAI（購読モデル・APC なし）・英語・MacTeX・本文 7,000 語・図表 4（判断 3〜4・`paper-write/venue-fit.md`・`length-log.md`）。外枠は `papers/per-person-learning/manuscript/outline.md`。
- 文献のラウンド 1 回（[V386]〜[V400]・`docs/literature/20261107-per-person-gain-comparison-baselines.md`）。
- 記号化の書き直し（`papers/per-person-learning/kit/symbols/`・作業記録 `.steering/20261107-gse-paper3-symbol-reimpl/`）: 元の replay と、合成 300 本・CoAuthor 1,157 セッション・CS1 2021 の 177 課題で記号と x・y の bit まで一致。/cross-review 2 巡。
- attack-me outline round 1: major revision（R1〜R3・Codex が major、編集者は「直してから回す」）。

## 2 文献の調べ（判断 12）で探すこと

- 多水準・混合 HMM（個人ごとの遷移・放出を集団分布へ縮める）。少なくとも Aarts & Haslbeck 2025（PsyArXiv・doi:10.31234/osf.io/y2u5s_v2・前のラウンドで本文未取得）。論文 3 の「τ で共通へ縮める MAP」がその特殊な場合に当たるかを確かめる。
- 階層モデル・経験ベイズの部分的なプール（縮小の強さを他人で選ぶこと、分散成分が 0〔完全なプール〕に張り付く問題・Chung ほか 2013 Psychometrika・本文未取得）。
- キーボードの言語モデルの個人化（全体のモデルと個人のモデルの補間・微調整を予測の尤度で比べる系統）。R2 が挙げたが一次は未確認。
- 前のラウンドの「やり残し」: Pardos & Heffernan 2010・Yudelson 2016 の本文、[V392] Ferrari の Chrome での照合、[V398] Stoye の雑誌版。
- 既にある文献は入れ直さず番号だけ挙げる（memory「文献のラウンドで既存の文献を入れ直さない」）。Saeb 2017 は [V98] で登録済み（外枠に引く）。

## 3 新しい小さな試験（判断 11）

- 目的: 査読者が求めた 2 点。(1) 短距離の依存が記号化の作り（30 秒窓・指数平滑・1 Hz・休止の秒も記号を出す）から来る分を見分ける対照（平滑の無い記号・例えば raw_x・raw_y の量子化か、窓の重ならない記号）。(2) 尤度以外のモデル検査（擬似残差の自己相関など）。
- やり方: /start-task → 条件と SEED をコードより前にコミット → 設計は /reimagine で比べる → 合成の門 → 本計算は職場の PC（HP Z2）。G-GEAR は 11 月ふさがり。
- 公開の記号化の kit（`papers/per-person-learning/kit/symbols/`）の記号器は x・y と平滑前の値を持つので、平滑の無い列を作る足場に使える（元の replay との一致は確かめ済み）。
- 並行の「構造の足りなさの試験」（`/Users/johnd/GSE-prototype-structure-deficit`・枝 `exp/gse-structure-deficit-test`）は別のセッションのもの。条件・コードを変えない。結果は論文 3 に入れる（判断 11 で引き継ぎの「入れない」を改めた）。あちらは記号の順の並べ替えの対照と、量子化 3 通り（記号 10・26・50）・構造 6 つ。平滑の無い記号と残差の検査は入っていない。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない（D2・D6）。書き手ごとの値と npz は開かない。

## 4 外枠の直し（verdict の「直す順」1〜14 を参照）

- 中心: 手順（C3）と実例（C1）の 2 つ。C2 は根拠の段へ（判断 10）。
- 一次で確かめた事実（verdict §3）: 共通は対象の書き手を除く（conditions D2）／r1 は各 +0.5 の擬似度数の 1 次のマルコフで ar1 の τ = 0 と一致／系列のモデルに本人の切片は無い（outline の "with a person-level intercept" は誤り）／hmm3 にも τ 他人の行がある（構造だけの比べを主表で示せる）／ar1 の τ 他人の行がプールだけの比べになる。
- CS1 の "exactly zero" → 「他人で選ぶと全員で共通のモデル（τ = ∞）が選ばれた」。"pooled limit" と呼ばない（∞ は有限の τ の列の極限ではない）。
- take-home と C1 の Evidence は CoAuthor に限る（CS1 の hmm3 は一貫して勝たない）。
- 当てはめのコードも公開 repo に入れる（判断 13）。
- round 2 は同じ立場・同じ接地の文献で、役ごとの carryover を渡す。Codex には既知の未決の一覧を添える（memory）。

## 5 守ること

- push と PR は研究者が確かめてから。τ の 3 本の枝の PR はまだ出ていない（`next-session-gse-tau-trio-pr-then-paper3.md`）。この枝はその上に載っている。
- 決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。報告を地の文の問いで終えない。
- 公開物（`papers/`）に GSE の名前・内部のパス・番号を書かない（`papers/README.md`）。
- attack-me の本文の照合は件数だけを出す（round 1 で本文の 1 行が文脈に印字された逸脱あり）。
- 返答は日本語。記号を多用しない。
