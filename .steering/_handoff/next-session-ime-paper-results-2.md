# 次セッション — IME 論文: 閉じた集合（D8）と macOS の解析を回し、結果の節を書く → 出荷（BRM・10 月末投稿）

> 作成: 2026-10-05（G-GEAR・前の引き継ぎ `next-session-ime-paper-results.md` の §2 の 0〜3 を済ませたセッションの最後）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 145〜156**、
> `manuscript-map.md`、公開物 `papers/ime-observation/manuscript/`（`outline.md`・`sections/*.tex`・`tools/results_tables.py`・`generated/`・`BUILD.md`）、
> 凍結した事前登録・`deviations.md`（**D1〜D9**）・`data.md`・`data.windows.md`・`env.md`・`experiment/results/`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 枝 origin/docs/ime-manuscript-outline から続ける（main に入っていなければその枝で）。
.steering/_handoff/next-session-ime-paper-results-2.md を読んで §2 から始めてください。
一次は decisions.md の判断 145〜156、outline.md、sections/*.tex、tools/results_tables.py、凍結した事前登録、deviations.md（D1〜D9）、data.md・data.windows.md・env.md、experiment/results/。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue・Y）を書かない（D の番号は公開の逸脱なので書いてよい）。_style_check.py を必ず回す（.tex / .bib も対象）。
⚠️ 結果の値は tools/results_tables.py で generated/ に生成し、本文は \rv{<key>} で読む（手で写さない）。要旨と結論は外枠の「Rule for the abstract」。結果を見てから規則を変えない。
⚠️ 理論・手法・先行研究に依拠する文は citation-ssot（docs/references.md の [Pn]/[Vn]・append-only・次は [V236]）。公開物は著者と年で引く。
⚠️ 判断の次の番号は 157、逸脱の次は D10。他の枝が足していないか着手時に必ず見る（MSYS_NO_PATHCONV=1 git show <ref>:<path>）。
⚠️ 凍結のタグのコードと事前登録は変えない（D8 の closed_set.py の --skip-scenario だけが例外で、既定の出力は凍結と同じ）。封印（sealed/）は開けない。生ログ・キーコードを原稿や外部の LLM に出さない。
Skill: citation-ssot・verify-before-claiming・subagent-delegation・reproducibility-discipline・git-workflow（attack-me は原稿の段で）。
LaTeX: G-GEAR は MiKTeX 25.12（ユーザー領域）と雛形 C:\Users\johnd\tools\sn-template\sn-article-template（公開物の外）。組むのは manuscript/build.sh（BUILD.md）。
応答は日本語。コミットは git add パス指定（-A 禁止）。heredoc にバックスラッシュを含めない（Write / Edit を使う・sed の置換文字列も同じ）。
```

## §1 状態（2026-10-05 夕 JST）

- 枝 `docs/ime-manuscript-outline`（push 済み・PR は出していない＝判断 155-3「結果の節の後に出す」）。このセッションのコミット: LaTeX `1fdf8018`（判断 154）・D8 / D9 `14c85e6e`（判断 155）・結果の生成の道具 `4239d07e`（判断 156）。
- ✅ **GSE 本体の訂正**（前の引き継ぎ §2 の 0）: PR #305 を merge（`2e881e23`・main の CI 緑）。記録は `.steering/20261005-macos-ax-marked-text-correction/`（worktree `C:/wt/macos-ax-correction`・枝は消していない）。⚠️ 研究者に渡す 4 点は同じ記録の decisions.md 判断 2（ADR-036 の (a) にアプリしだいの通知を入れるか・`workspace-behavior-observation.md` の分類・kit の照合を凍結の commit に固定して上流の `ime_compose.rs` のコメントを直すか・`data-privacy` の凍結表）。
- ✅ **LaTeX**（§2 の 1）: `main.pdf` 38 頁・エラー 0・未定義の参照は `fig:components`・`sec:availability`・`sec:limitations`・`sec:results-attempts` だけ。`supplement.pdf`（文書の一覧＋層ごとの検出）。雛形は CC BY に入れられない（LPPL・LaTeX の基本と一緒にしか配れない）→ `BUILD.md` に取得の手順。
- ✅ **研究者の判断**（§2 の 3）: D8 = 閉じた集合は S12 の試行をすべて外す（3 セルとも・`closed_set.py --skip-scenario S12`）。D9 = Windows の run が別々の夜でない。01:51 の開始は D7 で済み。⚠️ 寄託（OSF）は研究者の作業のまま。
- ✅ **結果の生成の道具**（§2 の 2 の前半）: `manuscript/tools/results_tables.py` → `generated/`（値・表 8・表 9・補遺の層の表）。Windows の値は判断 156。
- ❌ **まだ**: 閉じた集合（3 セル）・macOS の問 1〜4・E3 の結果ファイル（`e3_<system>.txt`）がリポジトリに無い → 要旨の (iii) 推奨と (iv) CPU、表 7・10・11・12 はまだ生成できない。

## §2 やること

1. **計測の機械で回す（このメモを持って Surface と Mac で）**:
   - **Windows（Surface）**: `experiment/runs/windows-msime-tsf-2`（gitignore・書庫 `f2287a74…cd06` を展開済み）で、§10.7 の閉じた集合の命令に `--skip-scenario S12` を足して回す。`kit/e2/closed_set.py` だけ commit `14c85e6e` 以降のもの、他は Windows のタグ `ime-observation-prereg-windows` の書き出し。出力 `experiment/results/windows/e2_closed_set_windows-msime-tsf.json` の `skipped_scenarios` が `{"S12": 225}`・各 K の `n` が 2,700（全ブロックが採点されたとき）であることを確かめる。
   - **Windows の E3**: `summarize_e3.py` の標準出力（idle と working の両方）を `experiment/results/windows/e3_windows.txt` に置く（notes.md の表の名前）。
   - **macOS（Mac）**: macOS のタグから `run.sh`（問 1〜3）と §6.8 の開いた集合・閉じた集合（閉じた集合は `--skip-scenario S12` と commit `14c85e6e` 以降の `closed_set.py`）。`e3_macos.txt` も置く。⚠️ ON の閉じた集合の `n` は 2,925、OFF は 2,700。
   - いずれも結果を commit したら G-GEAR か同じ機械で `python3 manuscript/tools/results_tables.py --results experiment/results --out manuscript/generated` を回し、`--check` が緑になるまで。
2. **道具を広げる**: 閉じた集合（表 11・要旨の (iii)＝推奨は macOS の 2 セルから・Windows は但し書き・登録の判定規則 §6.8 をコードで写す）、E3（表 12・要旨の (iv)＝条件ごとの CPU の平均・区間なし・系どうしを比べない）、届き方（表 7・RF1・KT1 は `e1_delivery.json`）、L2（表 10・`e1_l2.json` の `agreement`・`mixture_bias`）、開いた集合。⚠️ 新しい値ごとに selftest と変異を足す（memory「Acceptance self-test」）。
3. **結果の節を書く**（`sections/results-*.tex`・外枠の §6〜§9 の順: まず RF1〔基準が何を確かめたか〕→ 問 1・2 → 問 3 → 問 4 → 問 5）。値はすべて `\rv{}` と生成した表。評価の語を使わない（登録 §6.1）。⚠️ 要旨・結論は全セルがそろってから。macOS のセルが 1 つでも欠けたら推奨しない（判断 150-5）。
4. **Mac で**: AppKit と C の Accessibility の定数の数と `TextInputSources.h` を macOS 27.0.1 の SDK のヘッダで確かめる（外枠の Open items）。★ 判断 154 の WebKit の発火の経路（`AXObjectCache.cpp` 3692〜3719 行・`PlatformHave.h`）を §3 の文と [V206] の注に足すかも決める。
5. **Surface で**（研究者か Surface のセッション）: (a) Windows の試行 2 の間に計測機で何が動いていたか → `data.windows.md` と外枠 §5.2。(b) `data.windows.md` の §10.8 の点検の計画の SHA-256 を全桁に。
6. **出荷**: 結果の節と D8・D9 の後に、この枝の完了時レビュー（code-reviewer ∥ security-checker ＋ /cross-review〔パス限定・`run-codex-review.sh -- <paths>`〕）→ git-workflow ルール 6。⚠️ Codex の前に origin/main の `.codex/budget.json` も見る（memory「台帳はブランチごと」・2026-10-05 は main の台帳で 132,139 / 300,000 まで使った）。⚠️ この枝は `kit/e2/closed_set.py` を変えたので、完了時レビューに含める。
7. 結果の節の後: 原稿の attack-me（stage `manuscript`・判断 145 の 10-18〜22）。外枠の round 1・2 の引き継ぎ（`verdict.md` の Y1〜Y44 と採否）と、判断 151〜156 を渡す。

## §3 気をつけること

- ⚠️ **番号の衝突**: Mac・Surface・G-GEAR が並行で `decisions.md` と `deviations.md` に追記する。追記の前に `git fetch` して他の枝の最後の番号を見る。
- ⚠️ `OSF` の 2 つの登録の著者は `references.bib` で `TODO` のまま（研究者の名の書き方を確かめてから）。
- ⚠️ 雛形の APA の書式は 3 人以上の著者の最後の前に "&" を出さない・会議録の DOI を出さない（`.bst` は変えない・DOI は note に書いた）。
- ⚠️ git-bash の heredoc と sed の置換文字列でバックスラッシュが壊れた（このセッションで 3 回）。LaTeX の文字列を含む置換は Edit か、Write で書いた Python で行う。
- ⚠️ サブエージェントの記録ファイル（`tasks/*.output`）は読まない。報告は届いた本文から使い、一次で裏取りする（このセッションのレビュー 3 本の指摘は全部真だった）。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。
