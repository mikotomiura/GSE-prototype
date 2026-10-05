# 次セッション — IME 論文: 原稿の attack-me（stage `manuscript`）→ M12（Zenodo・GitHub の公開 repo）

> 作成: 2026-10-05 夜（G-GEAR・図 1〜5〔判断 181〕、要旨と残りの節〔判断 182〕、完了時レビュー〔判断 183・184〕、PR を出したセッションの最後）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 145・146・150・167・175・181〜187**、
> 外枠 `papers/ime-observation/manuscript/outline.md`（Rule for the abstract・Claims and evidence・Open items）、凍結した事前登録（§6.1・§7・§10.11）・`deviations.md`（D1〜D10）・`data.md`・`data.windows.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → この枝（docs/ime-manuscript-outline）の PR の状態を gh pr view で確かめる（merge 済みなら main から新しい枝を切る）。
.steering/_handoff/next-session-ime-paper-manuscript-2.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 145・146・150・167・175・181〜187、outline.md、凍結した事前登録、deviations.md（D1〜D10）、manuscript/tools/results_tables.py。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。封印（sealed/）は寄託のためだけに開ける（解析しない）。生ログ・キーコードを原稿や外部の LLM に出さない。experiment/runs/ は git に入れない。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない。値を見た後で表の道具の規則を変えない（変えるなら研究者に聞く）。評価の語を使わない（登録 §6.1）。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue）を書かない（D の番号は書いてよい）。_style_check.py を repo 直下から papers/ime-observation で回す。
⚠️ 判断の番号は 188〜、逸脱は D11（他の枝が足していないか着手時に MSYS_NO_PATHCONV=1 git show で見る）。
⚠️ Zenodo: 下書きと DOI の予約は Claude が進めてよい・公開は都度研究者に確かめる・token は表示も委譲もしない（memory「Zenodo token」）。
Skill: attack-me・verify-before-claiming・citation-ssot・reproducibility-discipline・subagent-delegation・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。
⚠️ heredoc・python -c・sed にバックスラッシュを含めない（このセッションで 6 回以上壊れた）→ 置換は Edit か、Write で書いたスクリプトで。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。雛形は ~/tools/sn-template/sn-article-template。PYTHON=python bash manuscript/build.sh <雛形> <原稿の外の出力先>。頁の確認は pdftoppm -r 100 -f N -l N -png（MiKTeX に入っている）。
```

## §1 状態（2026-10-05 夜）

- ✅ **図 1〜5**（判断 181）: pgfplots。図 2〜5 は `results_tables.py` が `generated/fig-*.tex` を生成（`--check` の対象）。図 1 は `figures/components.tex`。⚠️ sn-jnl の `\scriptsize`（9pt）は `\footnotesize`（7pt）より大きい → 図の小さい字は `\footnotesize`。図 2 は横向きの頁。
- ✅ **要旨（249 語）と §1・§11〜13・Declarations・Open Practices Statement**（判断 182）。要旨は規則どおり (iv) CPU → (ii) `dwell_ms` の偏りを本文へ回した。手法の節に D10。
- ✅ **完了時レビュー**（判断 183・184）: code-reviewer（HIGH 0）・security-checker（LOW 1）・Codex 2 巡（今日の台帳 310,956 / 8 回）。指摘はすべて一次で確かめ、直すか理由を記録した。selftest 135 件・変異 24 本（scratchpad の使い捨て）。
- ✅ **M12 の 4 点を研究者が決めた**（判断 183）: E3 の標本は Zenodo のデータに／working の観測ログも寄託／較正パイロットの生ログを別の区分で含める／コードの DOI は GitHub と Zenodo の連携。
- `build.sh`: main・補遺ともエラー 0・未定義の参照 0・生成されていない値 0・overfull は main 1（以前から）・補遺 160（以前から）。

### 研究者が覆せる判断（未確認）

- ★ **要旨に全試行の範囲の「外した層の数」を入れていない**（判断 183 の 5）: 語数（249）のため。規則 (i) の「with the number of strata left out」は主の範囲に付くと読んだ。結論と結果の節には入れた。
- ★ **「全試行の範囲」の読み (B)**（判断 175）。
- 値から手で書いた語（結果のファイルが変われば手で直す）: 要旨の「neither … none … nor」、§11 (c) と §13 の「neither granularity … in either macOS cell」、判断 174 の一覧。

## §2 やること

0. **PR の状態**: CI が緑なら merge・main の CI を確かめる（git-workflow ルール 6）。赤なら 1 回だけ原因を見て報告。
1. **原稿の attack-me**（stage `manuscript`・判断 145 の 10-18〜22 の枠を前倒し）: Skill `attack-me` の手順で、査読者 3 人＋意図の監査役（`paper-reviewer`・Opus）。外枠の round 1・2 の引き継ぎ（`.steering/.../attack-me/outline-ime-manuscript/round-1/`・`round-2/` の verdict と指摘の一覧）を渡す（判断 150-4）。⚠️ 渡すのは組んだ PDF ではなく `.tex` と生成物（値は `generated/values.tex`）。指摘は一次で裏取りしてから研究者に採否を聞く（査読の結果は研究の証拠ではない）。
2. ✅ **表紙・Funding・利益相反・貢献**は判断 185 で埋めた（単著・Independent researcher, Hiroshima, Japan・資金なし・利益相反なし・住所と電話は投稿システムだけ）。AI Declaration と図の題の断りも入れた。
   ★ **研究者が結果と考察を読んで直す段**（判断 185・Springer Nature の規程「the argument, interpretation, and conclusions must be author-led」）: attack-me の直しの後、投稿の前に、結果（§6〜9）・推奨・限界・結論を研究者が読み、主張と解釈を自分のものとして直す。Claude は節ごとに「主張 ↔ 根拠（登録の節・結果のファイル・表）」の対応を日本語で添えて渡す。⚠️ AI Declaration の「The interpretation of the results is the author's, and the author is accountable」はこの段を済ませて初めて事実になる（判断 186 で、コードの確認は「テストと道具のレビュー」、設計と設定は「Claude の提案を著者が選び・確かめ・承認」と記録どおりに直した）。datasheet を Claude が書いたら、宣言の使い道に足す。
3. **M12**（判断 145・146・167・183）:
   - Zenodo のデータセットの記録を**下書き**で作り DOI を予約（公開は研究者に確かめる）。中身は外枠 DS1・`dataset.tex` の表 13＋判断 183 の 4 点。寄託の前に各 run を `kit/analysis/pipeline.py --pack` と `--check-deposit` に通す（`data.md` の寄託の手順）。書庫は Mac の `~/ime-m4/deposit/`・Surface の `~/ime-m7/deposit/`（G-GEAR の `Downloads` に同じ SHA の写し）。
   - GitHub の公開 repo: 最初の commit は macOS の凍結の書き出し（判断 131・一覧の SHA-256 `29b183ba…`）、Windows の凍結の書き出しの一覧（`f61af353…`）も公開物から計算し直せる形にする（判断 145 の申し送り・外枠 Open items）。リリースと Zenodo の連携は研究者の GitHub アカウントで。
   - 予約した DOI・repo の URL・外枠を固定した公開 commit を原稿の `\tbd` に入れる（`declarations.tex`・`dataset.tex`・`related.tex` の表 1「This logger」の版）。⚠️ BRM はデータの引用を書誌に求める → `references.bib` にデータセットの項目（citation-ssot）。
   - `dataset.tex` の「`\tbd{confirmed at deposit}`」（working の観測ログ）を寄託の後に外す。
4. **外枠の Open items の残り**: 入力方式を通したテキスト入力の評価の文献を §2 に置くか（一次で確かめる）・凍結の書き出しの一覧を公開 repo から計算し直す形・§10.8 の点検の計画の SHA-256 の全桁（Surface の manifest から）・Windows の計測機で何が動いていたか（Surface）・観察可能性の文書の一覧を補遺に。
5. 投稿の前: カバーレター（判断 145 の 10-23〜27）・投稿規程を読み直す（BRM は ScholarOne・memory）。

## §3 気をつけること

- ⚠️ 表の道具を直したら selftest と変異（狙った確認で赤になることを FAIL の名前で確かめる）。このセッションでも 2 本が「例外で落ちて FAIL に数えられない」「行が変わって当たらない」で空振りした。
- ⚠️ `run-codex-review.sh` は 1 回で 2〜3 万トークン。ガードは「残り < 30,000」で止まる。台帳はブランチごとに記帳される —— 回す前に origin/main の台帳も見る・merge のときは和。
- ⚠️ 要旨の語数は scratchpad の `count_abstract.py`（`\rv` を `generated/values.json` で展開して空白で数える）で数えた。次のセッションで要旨を変えるなら同じ数え方を作り直す（250 語以内）。
