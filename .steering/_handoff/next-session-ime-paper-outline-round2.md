# 次セッション — IME 論文: 外枠の attack-me round 2 → 手法の節の続き（BRM・10 月末投稿）

> 作成: 2026-10-05（G-GEAR・外枠を書いて attack-me round 1 を回したセッションの最後・コンテキストが半分を超えたため区切った）。前の引き継ぎ `next-session-ime-paper-writing.md` の §2 の 1〜4 はこのセッションで済んだ（外枠・round 1・手法の節の草稿・形式 = LaTeX）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 145〜149**、`manuscript-map.md`（内部の対応）、`attack-me/outline-ime-manuscript/round-1/verdict.md`、公開物 `papers/ime-observation/manuscript/outline.md`・`sections/method.tex`、凍結した事前登録（§10 を含む）・`deviations.md`（D1〜D6）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 枝 origin/docs/ime-manuscript-outline（このセッションの作業・push 済みか確かめる）から続ける。main に入っていなければその枝で。
.steering/_handoff/next-session-ime-paper-outline-round2.md を読んで §2 から始めてください。
一次は decisions.md の判断 145〜149、manuscript-map.md、attack-me/outline-ime-manuscript/round-1/verdict.md、outline.md、method.tex、凍結した事前登録、deviations.md。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue）を書かない。_style_check.py を必ず回す（.tex / .bib も対象になった・判断 148）。
⚠️ 理論・手法・先行研究に依拠する文は citation-ssot（docs/references.md の [Pn]/[Vn]・append-only）。公開物は著者と年で引く（判断 76）。
⚠️ 凍結のタグ（ime-observation-prereg-macos / -windows）のコードと事前登録は変えない。封印（sealed/）は開けない。生ログ・キーコードを原稿や外部の LLM に出さない。
⚠️ この G-GEAR には封印物（C:/ime-pilot-win/runs/*/sealed/）と Zenodo のトークンがある → attack-me を起動する前に研究者に知らせる。
Skill: attack-me（round 2）・citation-ssot・verify-before-claiming・subagent-delegation・git-workflow。
応答は日本語。コミットは git add パス指定（-A 禁止）。PR は Mac の計測が終わるまで出さない（push だけ）。
```

## §1 状態（2026-10-05 未明）

- 枝 `docs/ime-manuscript-outline`（`docs/ime-submission-plan` から切った）。コミット: 外枠 `08e50a54`・規程の照合 `6f0af22b`・round 1 の記録 `fd195671`・手法の節 `66f4a158`・round 1 の直し `9463fae6`（＋ 引き継ぎのコミット）。
- **外枠**（`papers/ime-observation/manuscript/outline.md`・6,984 語・主張 31 行）: round 1（major・有効 3/3・捏造 0・注入 0）の直しを全部反映済み。研究者の選択（判断 149）: §11 は閾値の無い 5 種・D6 と §10.8 の公開・題は **"Logging Japanese IME conversion without recording text: …" に固定**・要旨の規則・利用者の道具は足さない・キー行の時刻は登録済みの値だけ。
- **手法の節**（`sections/method.tex`・約 5,300 語・LaTeX）: 草稿あり。⚠️ **未コンパイル**（この機械に LaTeX も pandoc も無い）。後の節のラベル（`sec:logger`・`sec:dataset`・`sec:limitations`・`sec:results-attempts`・`sec:availability`・`sec:cost`・`fig:components`）はまだ無い。
- **投稿規程**は 2026-10-04 に原文（curl）で照合済み: 投稿は **ScholarOne**（EMSE の Editorial Manager の実測は当たらない可能性）・Open Practices は References の直前・Declarations の見出しは原文の一覧。
- 新しく登録した書誌: [V190] Sudachi・[V191] 青空文庫。
- 計測: M4（Mac）の最後の run は 10-05 10 時ごろに終わる。M7 の Windows の E3 は 10-05〜06。→ M8・M10（解析）は別の作業。

## §2 やること

1. **attack-me round 2（外枠）**: `attack-me/outline-ime-manuscript/round-2/` に **引き継ぎ 4 本（`carryover-R1.md`〜`R3.md`・`carryover-audit.md`）は書いてある**。残り: `context-A.md`（対象物の commit を最新に・一覧は round 1 と同じ ＋ 必要なら `kit/logger/src/` の単体テストのファイルを足すか判断）・`context-B.md`（★ round 1 の監査で、メインが書いた「入力方式自身のセッション」「どの測度を信頼してよいか」「結果に基づいて」が事前登録と食い違っていた → 事前登録の言い方に直す）・`panel.md`（同じ立場・同じ接地の 9 本。`tmp/` は消えているので取り直す: URL と SHA-256 は round 1 の `panel.md`）・規程の抜粋は round ごとに取り直す（curl・cookie）・依頼文 4 本（round 1 の `brief-*.md` に「引き継ぎを読む」を足す）。→ 4 本を並列（`paper-reviewer`・Opus）→ 保存の検査 → 裏取り → `verdict.md` → 研究者に採否。
2. 手法の節の残り: 問 4（漏洩）・問 5（実行コスト）の手法は §8・§9 の冒頭に（凍結の §6.8・§6.10・§10.7・§10.9 から）。
3. 結果を待たない節: §3（観測可能性・★ 方法を先に・MS / Apple の一次文書を取得して `docs/references.md` に登録・macOS の Accessibility の定数は計測の版で数え直す）・§4（ロガー・Table 3・Table 4）・§2（比較表 Table 1・Inputlog は版ごとに一次で）・§10（データセット・Datasheets for Datasets〔Gebru ら・登録〕）。
4. 題を Logging に揃える（`README.md`・`CITATION.cff`・`.zenodo.json`・`kit/` の題の文字列・凍結のタグは変えない・書き出しの前）。`kit/logger/README.md` 41〜42 行の古い一文（"not implemented"）も書き出しの前に直す。
5. `data.windows.md` の §10.8 の点検の計画の SHA-256 を全桁に（Surface の点検の run `~/ime-m7/runs/verify-m7` の manifest から・研究者か Surface のセッション）。
6. 10-05〜07 に結果がそろったら結果の節へ（表は JSON から生成する道具を `manuscript/` に作る・手で写さない）。以降は判断 145 の表。

## §3 気をつけること

- ⚠️ **判断の番号の衝突**: Mac・Surface・G-GEAR が並行で `decisions.md` に追記している。このセッションで 147〜149 を使った（10-05 未明の時点で他の枝は 143 まで）。追記の前に `git fetch` して他の枝の最後の番号を見る。merge の前にもう一度突き合わせる。
- ⚠️ heredoc にバックスラッシュを含めると化ける（このセッションで 2 回）→ Windows のパスや `\n` を含むものは Write / Edit で書く。
- ⚠️ attack-me の応答は `tmp/<名>.raw.md` に置き、`scripts/secrets-filter.sh` と絶対パスの突き合わせ（scratchpad に書いた `check_paths.py` と同じ形）を通してから写す。接地の引用は空白・合字・行末のハイフンを正規化して照合する（`check_quotes.py` と同じ形・そのままの grep だと 0 件に見える）。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。
