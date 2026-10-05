# 次セッション — IME 論文: 結果を待たない節（§3・§4・§2・§10）→ 結果の節（BRM・10 月末投稿）

> 作成: 2026-10-05（G-GEAR・外枠の attack-me round 2 を閉じたセッションの最後）。前の引き継ぎ `next-session-ime-paper-outline-round2.md` の §2 は、1（round 2）・2（問 4・問 5 の手法）・4（題を揃える）が済んだ。残りは 3・5・6。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 145〜150**、`manuscript-map.md`、`attack-me/outline-ime-manuscript/round-2/verdict.md`、公開物 `papers/ime-observation/manuscript/outline.md`・`sections/*.tex`、凍結した事前登録（§10 を含む）・`deviations.md`（D1〜D6）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 枝 origin/docs/ime-manuscript-outline から続ける（main に入っていなければその枝で）。
.steering/_handoff/next-session-ime-paper-sections.md を読んで §2 から始めてください。
一次は decisions.md の判断 145〜150、manuscript-map.md、attack-me/outline-ime-manuscript/round-2/verdict.md、outline.md、sections/*.tex、凍結した事前登録、deviations.md。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue・Y）を書かない。_style_check.py を必ず回す（.tex / .bib も対象）。
⚠️ 理論・手法・先行研究に依拠する文は citation-ssot（docs/references.md の [Pn]/[Vn]・append-only）。公開物は著者と年で引く（判断 76）。
⚠️ 外枠の規則（要旨は事前登録 §6.1 に従う・層は 30 試行以上・推奨 (d) は 2 段・macOS のセルが欠けたら推奨しない）は判断 150 で固定した。結果を見てから変えない。
⚠️ 凍結のタグ（ime-observation-prereg-macos / -windows）のコードと事前登録は変えない。封印（sealed/）は開けない。生ログ・キーコードを原稿や外部の LLM に出さない。
Skill: citation-ssot・verify-before-claiming・subagent-delegation・git-workflow（attack-me は原稿の段で）。
応答は日本語。コミットは git add パス指定（-A 禁止）。PR は Mac の計測が終わるまで出さない（push だけ）。
```

## §1 状態（2026-10-05 01 時台）

- 枝 `docs/ime-manuscript-outline`（push 済み）。このセッションのコミット: round 2 の準備 `ce9e44a9`・問 4 / 問 5 の手法 `730edd64`・round 2 の記録 `328c6322`・題の統一 `10bb1304`・round 2 の直し `ffd315a4`（＋ この引き継ぎ）。
- **外枠**（`outline.md`・約 9,200 語・主張 31 行・表 13）: round 2（major・R1 major / R2 minor / R3 major・捏造 0・注入 0）の直しを全部反映済み（判断 150）。★ **外枠の round 3 は回さない** → 原稿の attack-me（stage `manuscript`・判断 145 の 10-18〜22）に、外枠の round 1・2 の引き継ぎ（`verdict.md` の Y1〜Y44 と採否）を渡す。
- **手法**: `sections/method.tex`（§5）・`sections/recoverability.tex`（§8 の手法・near-chance の表）・`sections/cost.tex`（§9 の手法）。結果は `\tbd`。⚠️ **未コンパイル**（この機械に LaTeX も pandoc も無い）。まだ無いラベル: `sec:logger`・`sec:dataset`・`sec:limitations`・`sec:results-attempts`・`sec:availability`・`fig:components`。
- ★ ソースで確かめたこと（判断 150）: **macOS も解放の行を書く**（`driver_macos.rs`）。解析と攻撃は押下の行だけ。KT1 の定義は凍結の `delivery.py` 62〜76 行。Windows の安全弁は `main.rs` 273 行・テスト 777 行。
- 判断の番号: このセッションで 150 を使った（10-05 01 時の時点で他の枝は最大 146）。

## §2 やること

1. **結果を待たない節**（外枠の §3・§4・§2・§10 の箇条どおりに LaTeX で書く）:
   - §3 観測可能性: ★ 方法を先に（調べたインタフェースの選び方・文書の URL・**アーカイブの写し**・取得日・版・基準）。MS / Apple の一次文書を取得して `docs/references.md` に登録（内部の出どころは `manuscript-map.md` §2 の OB 行）。macOS の Accessibility の定数は計測の版で数え直す。観察から来た文（隠蔽・ウィンドウ一覧の時機）は系と版を付けて「観察」と書く。
   - §4 ロガー・Table 3・Table 4（測度 × OS: 計算できるか・一致を推定したか・理由）。
   - §2 比較表 Table 1（CyWrite・GenoGraphiX-Log・Inputlog〔言語別版は別の行〕・ScriptLog・Translog-II・Hylog・このロガー。版と確かめた日付つき。Plant・Pinet・Bridges・Monaco・Gebru は citation-ssot で登録してから引く）。
   - §10 データセット（Datasheets for Datasets の形・FORMATS.md を寄託に含める・コーパスの取り扱いの条件・起動ごとの寄託の有無）。
2. **Surface で調べること**（研究者か Surface のセッション）: (a) Windows の試行 2 の間に計測機で何が動いていたか（判断 150-6・外枠の Open items）→ `data.windows.md` と外枠 §5.2。(b) `data.windows.md` の §10.8 の点検の計画の SHA-256 を全桁に。
3. 10-05〜07 に結果がそろったら結果の節へ（表は JSON から生成する道具を `manuscript/` に作る・手で写さない）。要旨と結論は外枠の「Rule for the abstract」のとおり。以降は判断 145 の表。

## §3 気をつけること

- ⚠️ **判断の番号の衝突**: Mac・Surface・G-GEAR が並行で `decisions.md` に追記する。追記の前に `git fetch` して他の枝の最後の番号を見る（git-bash では `MSYS_NO_PATHCONV=1` を付けないと `git show <ref>:<path>` が壊れる）。
- ⚠️ heredoc にバックスラッシュを含めない（Windows のパスは Write / Edit で書く）。
- ⚠️ サブエージェントの記録ファイル（`tasks/*.output`）は 0 バイトだった。attack-me の応答を保存するときは、届いた本文から `tmp/*.raw.md` に書く。検査の道具（`check_paths.py`・`check_quotes.py`）は scratchpad にあり、次のセッションでは消えている → 作り直す（陰性対照で確かめる）。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。
