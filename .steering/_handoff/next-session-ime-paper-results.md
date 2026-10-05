# 次セッション — IME 論文: 結果の節（表は JSON から生成）→ 出荷の判断（BRM・10 月末投稿）

> 作成: 2026-10-05（G-GEAR・結果を待たない節〔§2・§3・§4・§10〕を書き、main の M4 と Windows の解析を取り込んだセッションの最後）。前の引き継ぎ `next-session-ime-paper-sections.md` の §2 の 1 はこのセッションで済んだ（2 の Surface の 2 件は残り、3 の結果の節はこのメモの §2）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 145〜153**、`manuscript-map.md`、公開物 `papers/ime-observation/manuscript/outline.md`・`sections/*.tex`・`references.bib`、凍結した事前登録（§10 を含む）・`deviations.md`（**D1〜D7**）・`data.md`・`data.windows.md`・`env.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 枝 origin/docs/ime-manuscript-outline から続ける（main に入っていなければその枝で）。
.steering/_handoff/next-session-ime-paper-results.md を読んで §2 から始めてください。
一次は decisions.md の判断 145〜153、manuscript-map.md、outline.md、sections/*.tex、凍結した事前登録、deviations.md（D1〜D7）、data.md・data.windows.md・env.md、experiment/results/。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue・Y）を書かない。_style_check.py を必ず回す（.tex / .bib も対象）。
⚠️ 結果の値は結果の JSON からスクリプトで写す（手で写さない・丸めない）。要旨と結論は外枠の「Rule for the abstract」（判断 150・事前登録 §6.1）のとおり。結果を見てから規則を変えない。
⚠️ 理論・手法・先行研究に依拠する文は citation-ssot（docs/references.md の [Pn]/[Vn]・append-only・次は [V236]）。公開物は著者と年で引く。
⚠️ 逸脱の次の番号は D8（D6 = macOS の晩・D7 = Windows の試行の数え方・判断 152）。他の枝が足していないか着手時に必ず見る。
⚠️ 凍結のタグのコードと事前登録は変えない。封印（sealed/）は開けない。生ログ・キーコードを原稿や外部の LLM に出さない。
Skill: citation-ssot・verify-before-claiming・subagent-delegation・reproducibility-discipline・git-workflow（attack-me は原稿の段で）。
§2 の 0（GSE 本体の訂正）は main から別の枝で行う（論文の枝に混ぜない・判断 151-2）。
応答は日本語。コミットは git add パス指定（-A 禁止）。heredoc にバックスラッシュを含めない（Write / Edit を使う）。
```

## §1 状態（2026-10-05 11 時台 JST）

- 枝 `docs/ime-manuscript-outline`（push 済み）。このセッションのコミット: 4 節の草稿 `ee54bcbe`・main の取り込み `745a551f`（PR #297 の M4・PR #304 の Windows の解析）・書誌 [V192]〜[V235] `4e5e5184`・照合の反映 `b836e9c0`（＋ 補遺の文書一覧・引き継ぎ）。
- **原稿の節**: `related.tex`（§2・Table 1）・`observability.tex`（§3・Table 2）・`logger.tex`（§4・Table 3・4）・`method.tex`（§5）・`recoverability.tex`（§8 の手法）・`cost.tex`（§9 の手法）・`dataset.tex`（§10・Table 13）。補遺 `supplement/observability-documents.tex`（31 件）。⚠️ **未コンパイル**（この機械に LaTeX が無い）。未定義のラベル: `fig:components`・`sec:availability`・`sec:limitations`・`sec:results-attempts`。引用キーは 67 / 67 が書誌にある。
- ★ **判断 151**: macOS の AppKit の Accessibility にも変換中の範囲の属性と開始・終了の通知があり、WebKit が出す → §3 と貢献 1 は「アプリが用意する経路は両 OS にある・ロガーはアプリを問わない経路だけを使う」の対称の形。事前登録 §1.1 の言い方は文書が支えるより広い、と原稿の注に書いた。
- ★ **判断 153**: 独立の照合（Opus）の指摘 17 件はすべて真で直した（AppKit の定数は 131・18・42 など）。
- **計測**: macOS（M4）は ON・OFF・E3 idle・E3 working とも完走・打ち切り 0（`data.md`・`env.md`・逸脱 D6）。⚠️ **macOS の解析（問 1〜4）はまだ回っていない**（Mac で macOS のタグから `run.sh`）。Windows（M7）は問 1〜3 と問 4 の開いた集合の結果が `experiment/results/windows/` にある（PR #304）。⚠️ **問 4 の閉じた集合は凍結のコードの欠陥で止まっている**（`next-session-ime-paper-m7-windows.md` §2.11: S12 のコーパスの句が数えられ K = 100 のおとりが足りない・**macOS も S12 の候補が 72 で同じ欠陥に当たるおそれ**）→ 研究者が逸脱として直し方を決める待ち。
- 判断の番号: このセッションで 151〜153 を使った（10-05 11 時の時点で他の枝は最大 146）。

## §2 やること

0. **最初に片づける小さな別作業 —— GSE 本体の「macOS は公開 API が存在しない」を一次に戻す**（判断 151-2）。⚠️ **論文の枝には混ぜない**: `main` から別の枝（例 `docs/macos-ax-marked-text-correction`）を切り、`/start-task` で `.steering/` を作る（並行セッションがあれば `git worktree`）。
   - 一次: (1) Apple の AppKit の Accessibility の定数に `textInputMarkedRangeAttribute`（変換中の範囲）と `NSAccessibilityTextInputMarkingSessionBegan` / `…Ended`（変換の開始・終了）がある（macOS 10.6 から・説明なし・`docs/references.md` [V224]・[V225]）。(2) WebKit のソース（[V206]・commit `1a5a134d`）が変換の開始・終了を 2 つの通知に写し、変換中の範囲を位置と長さで返す。(3) 内部の調査メモ `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §7.5 の「135 個でゼロ」は C の定数だけを数えていた（AppKit は属性 131・パラメータ付き 18・通知 42）。
   - 手順: 消費者を grep で洗う（`公開 API が存在しない`・`公開 API が無い`・`no public interface` などを `docs/`・`.claude/`・`.steering/`・`src-tauri/src/` で。⚠️ 凍結物の事前登録は変えない）→ `docs/agent-shared.md` の技術的制約 7 の末尾（★ Codex も読む共通文書なので最小の変更）と調査メモ §3.2・§7.5・§7.6 を「アプリを問わない公開の経路は見つかっていない。アプリが用意する Accessibility の経路はあり、WebKit は出す（AppKit の NSTextView が出すかは未確認）」に直す。⚠️ 設計の結論（打鍵から推す）は変えない —— 変えるかは研究者。
   - 完了時: `python scripts/check_citations.py`・code-reviewer ∥ security-checker ＋ /cross-review（パス限定）→ 出荷フロー（git-workflow ルール 6）。
1. **LaTeX を入れてコンパイルする**（研究者の許可 2026-10-05）: G-GEAR に TeX の配布（例: `winget` で MiKTeX か TeX Live）を入れ、Springer Nature の雛形（`sn-jnl.cls`・`sn-apa.bst` ほか）を**公開物の外**に取得する（⚠️ 雛形のライセンスが CC BY 4.0 の公開物に入れられるかは未決〔判断 147 (b)〕→ 取得の手順だけを `manuscript/` に書く）。`main.tex` をコンパイルし、未定義のラベル（`fig:components`・`sec:availability`・`sec:limitations`・`sec:results-attempts`）以外の警告と、表の幅・`longtable`（補遺）・書誌の出力（APA）を直す。
2. **結果の節の道具**: `manuscript/` に、結果の JSON（`experiment/results/` と `results/windows/`・`notes.md` が名指すファイル）から表と本文の値を生成する道具を作る（手で写さない）。まず Windows の結果で作り、macOS の結果が来たら同じ道具で足す。要旨と結論は外枠の「Rule for the abstract」（層は 30 試行以上・外した層の数・範囲と carry-over の割合・`all_trials`・Windows は別の構成概念・CPU は系ごと）。
3. **研究者の判断待ち（他の枝で起票済み）を確かめてから書く**: 問 4 の閉じた集合の欠陥の直し方（逸脱 D8〜）、Windows の run の晩の扱い（`method.tex` の \tbd「The timing of the Windows runs, as recorded.」）、01:51 の開始の扱い（D7 で済んでいるか照合）、寄託。
4. **Mac で**: AppKit と C の Accessibility の定数の数と `TextInputSources.h` を macOS 27.0.1 の SDK のヘッダで確かめる（外枠の Open items）。
5. **Surface で**（研究者か Surface のセッション）: (a) Windows の試行 2 の間に計測機で何が動いていたか → `data.windows.md` と外枠 §5.2（macOS は `env.md` に CI の負荷が書かれた）。(b) `data.windows.md` の §10.8 の点検の計画の SHA-256 を全桁に。
6. **出荷の判断**: Mac と Windows の計測は終わったので、この枝の PR を出せる状態か研究者に確かめる。出すなら完了時レビュー（code-reviewer ∥ security-checker ＋ /cross-review〔パス限定・`run-codex-review.sh -- <paths>`〕）→ git-workflow ルール 6。⚠️ Codex の前に origin/main の `.codex/budget.json` も見る（memory「台帳はブランチごと」）。
7. 結果の節の後: 原稿の attack-me（stage `manuscript`・判断 145 の 10-18〜22）。外枠の round 1・2 の引き継ぎ（`verdict.md` の Y1〜Y44 と採否）と、このセッションの判断 151〜153 を渡す。

## §3 気をつけること

- ⚠️ **判断・逸脱の番号の衝突**: Mac・Surface・G-GEAR が並行で `decisions.md` と `deviations.md` に追記する。追記の前に `git fetch` して他の枝の最後の番号を見る（git-bash では `MSYS_NO_PATHCONV=1` を付けないと `git show <ref>:<path>` が壊れる）。このセッションでは逸脱 D6 が衝突した（判断 152）。
- ⚠️ 文書の取得と写しの台帳（`gen_refs.py` など）は scratchpad にあり、次のセッションでは消えている。書誌と写しの URL は `docs/references.md` [V206]〜[V235] と `references.bib` の注に残してある。
- ⚠️ サブエージェントの記録ファイル（`tasks/*.output`）は読まない。報告は届いた本文から使う。照合や道具集めの報告は一次で裏取りしてから反映する（このセッションでは道具集めの報告の「ScriptLog は入手できない」が不正確だった）。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。
