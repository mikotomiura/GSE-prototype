# 次セッション — IME 論文: 原稿を書き始める（BRM・10 月末投稿）

> 作成: 2026-10-04（G-GEAR・投稿計画を見直したセッションの最後に）。研究者の選択で、**BRM に 10 月末に投稿**し、原稿は**計測と並行で今から書く**（判断 145）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 1・6・15・21・145・146**）・`design.md` §5（論文の節構成）・`paper-suggest.md`（題の候補）と、凍結した事前登録 `papers/ime-observation/experiment/preregistration.md`（macOS の節と Windows の追補 §10）・`experiment/deviations.md`（D1〜D5）・`experiment/notes.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 枝 origin/docs/ime-submission-plan の記録（判断 144・145）が main に入ったかを確かめる。入っていなければ、その枝から作業ブランチを切る。
.steering/_handoff/next-session-ime-paper-writing.md を読んで §2 から始めてください。
一次は decisions.md の判断 1・6・15・21・145・146、design.md §5、凍結した事前登録（§10 を含む）、deviations.md、notes.md。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし（memory）。原稿は papers/ime-observation/manuscript/ に置く（判断 21・書き出しで公開される）。
⚠️ 理論・手法・先行研究に依拠する文は citation-ssot（docs/references.md の [Pn]/[Vn]・append-only）。
⚠️ 凍結のタグ（ime-observation-prereg-macos / -windows）のコードと事前登録は変えない。
⚠️ 封印（sealed/）は開けない。生ログの中身・キーコードを原稿や外部の LLM に出さない。
Skill: citation-ssot・verify-before-claiming・attack-me（外枠を書いた後）・git-workflow。
応答は日本語。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-04 の終わり）

- **計測**: M4（Mac）は最後の run が **10-05 10 時ごろ**に終わる（研究者）。M7 は Windows のセルが 10-04 13:03 に完了（2925 / 2925・`data.windows.md`）、残りは Windows の E3（`idle` → `working`）で明日・明後日に終わる見込み。→ 結果は 10-05〜06 にそろう。
- **事前登録**: macOS `https://osf.io/9nh7r`（10-02）・Windows の追補 `https://osf.io/4jwzn`（10-03）。逸脱 D1〜D5（`deviations.md`）。
- **投稿先**: BRM（判断 1）。**購読モデルなら費用 0** を 10-04 に一次で確認（"no APC charges apply"・判断 145）。⚠️ 採択後に購読モデルを選ぶ（OA は APC $4,090）。CHI 2027 Posters は取り下げ済み。
- **題**: T1 *Observing Japanese IME conversion without recording text: Observability limits, a cross-platform logger, and a synthetic-input validation*（判断 15・E2 が強ければ T4 へ変えてよい）。
- **節構成**: `design.md` §5（12 節・Recommendations for researchers を含む）。BRM の規程（2026-09-28 確認）: Open Practices Statement を References の直前・Declarations 節（該当しない見出しも置いて "Not applicable"）・要旨 250 語以内・APA 第 7 版・本文の分量の上限は無い。
- **主張の範囲**: 判断 6（精度評価が主・本文を再構成できないことの定量・TSF で観測できないことの論証・実行コスト）。⚠️ E2 の結果が「一部は漏れる」でも**そのまま報告する**。
  ★ **判断 146（研究者の選択）: 合成入力の記録一式を 5 つ目の貢献「データセット」として加える**（正解の参照ログ付き・macOS 2 セル＋Windows 1 セル・語句のコーパス）。主張の芯は精度評価のまま。⚠️ 「人の書字のデータ」「自然な入力のベンチマーク」とは書かない。使い道は判断 146 の (a)〜(c) の範囲で書く。
- `papers/ime-observation/manuscript/` は**まだ無い**（`README.md` は `manuscript/` を公開物の一部として挙げている・ライセンスは CC BY 4.0）。

## §2 やること（判断 145 の日程）

1. **外枠**（〜10-05）: `papers/ime-observation/manuscript/outline.md`（英語）に、節構成（★ データセットの節か厚い Availability の節を足す・判断 146）と**主張 ↔ 根拠の対応表**（★ 貢献 5 のデータセットの行も）（各主張 → 事前登録の節・問い・結果ファイル `experiment/results/*.json`・図表）を書く（判断 21）。⚠️ 公開物なので、内部の判断番号・`.steering/` のパス・GSE の語を書かない。内部の対応は `.steering/` 側に別に持つ。
2. **attack-me（外枠）**: Skill の「原稿の外枠を書いた後」。外枠の段階で主張の骨格を攻撃させる（4 本とも Opus・`paper-reviewer`）。
3. **手法の節**（結果を待たない）: 凍結した事前登録と追補 §10 から書く（system・reference input field・executor・plans・ground-truth rules・delivery checks・analysis）。逸脱 D1〜D5 は手法の中か専用の節で報告する（事前登録 §8 のとおり）。
4. 原稿の形式を決める（研究者に聞く）: LaTeX（Springer の雛形）か Word か。⚠️ Springer の Editorial Manager の実測（memory: EMSE）では、別添のタイトル頁が必須・2 つ目の `.tex` は補助ファイルにできない（埋め込む）・Zenodo のリンクは Invalid（GitHub を使う）。BRM でも同じかは投稿の前に確かめる。
5. ★ データセットの準備（判断 146・M12 の枠 10-23〜27）: Datasheets for Datasets の形の説明書（Gebru らを citation-ssot で登録）・Zenodo のデータセットの記録と DOI・較正パイロットの生ログを含めるかの判断（M2 の残り）。
6. 10-05〜07 に結果がそろったら（M8・M10 は別の作業）結果の節へ。以降は判断 145 の表（10-08〜17 全体 → 10-18〜22 attack-me → 10-23〜27 M12 → 10-28〜31 投稿）。
7. 出荷: 枝は `docs/*`。⚠️ **PR は Mac の計測が終わるまで出さない**（Mac の CI は self-hosted runner で、測定中の run と重なる・研究者の指示 10-04）。

## §3 気をつけること

- ⚠️ **判断の番号の衝突**: Mac・Surface・G-GEAR のセッションが並行で `decisions.md` に追記している。2026-10-03 に「判断 135」が 2 つの枝で別の中身になった（判断 144）。→ 追記の前に `git fetch` して main の最後の番号を見る。merge の前にもう一度突き合わせ、ぶつかったら番号を付け直す。
- ⚠️ M12 の申し送り（判断 145）: 凍結のタグが 2 つ（macOS の一覧 `29b183ba…`・98 ファイル／Windows の一覧 `f61af353…`・108 ファイル）。公開 repo で両方の一覧を計算し直せる形を M12 の前に決める。
- ⚠️ 原稿で結果の数を書くときは `experiment/results/` の JSON から写し、手で丸めない（再現性・reproducibility-discipline）。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。
