# 次セッション — IME 論文: 原稿の attack-me（stage `manuscript`）→ 研究者が結果と考察を読んで直す → M12（Zenodo・GitHub の公開 repo）

> 作成: 2026-10-05 夜（G-GEAR）。図 1〜5〔判断 181〕・要旨と残りの節〔判断 182〕・完了時レビュー〔判断 183・184〕・表紙と Declarations と AI Declaration〔判断 185〜187〕を書き、**PR #309 を merge した**（merge コミット `ab7851db`）セッションの最後。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 145・146・150・167・175・181〜187**、
> 外枠 `papers/ime-observation/manuscript/outline.md`（Rule for the abstract・Claims and evidence・Open items）、凍結した事前登録（§6.1・§7・§10.11）・`deviations.md`（D1〜D10）・`data.md`・`data.windows.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → origin/main から新しい作業ブランチを切る（例: docs/ime-manuscript-attack-me）。⚠️ main は別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。
.steering/_handoff/next-session-ime-paper-manuscript-2.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 145・146・150・167・175・181〜187、outline.md、凍結した事前登録、deviations.md（D1〜D10）、manuscript/tools/results_tables.py。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。封印（sealed/）は寄託のためだけに開ける（解析しない）。生ログ・キーコードを原稿や外部の LLM に出さない。experiment/runs/ は git に入れない。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない。値を見た後で表の道具の規則を変えない（変えるなら研究者に聞く）。評価の語を使わない（登録 §6.1）。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue）を書かない（D の番号は書いてよい）。_style_check.py を repo 直下から papers/ime-observation で回す。
⚠️ 判断の番号は 188〜、逸脱は D11（他の枝が足していないか着手時に MSYS_NO_PATHCONV=1 git show で見る）。
⚠️ Zenodo: 下書きと DOI の予約は Claude が進めてよい・公開は都度研究者に確かめる・token は表示も委譲もしない（memory「Zenodo token」）。
⚠️ 研究者に決めてもらうことは AskUserQuestion で聞く（推奨と理由を添える）。
Skill: attack-me・verify-before-claiming・citation-ssot・reproducibility-discipline・subagent-delegation・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。
⚠️ heredoc（cat も）・python -c・sed にバックスラッシュを含めない（2026-10-05 に 6 回以上壊れた）→ 置換は Edit か、Write で書いたスクリプトで。追記した記録は grep でバックスラッシュの残り方を確かめる。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。雛形は ~/tools/sn-template/sn-article-template。PYTHON=python bash papers/ime-observation/manuscript/build.sh <雛形> <原稿の外の出力先>。頁の確認は pdftoppm -r 100 -f N -l N -png（MiKTeX に入っている）。
```

## §1 状態（2026-10-05 夜・PR #309 merge 後）

- ✅ **PR #309**（判断 181〜187）を merge（`ab7851db`）。⚠️ main の CI（run `37316167205`）は merge の時点で走っていた —— §2 の 0 で結果を確かめる。
- ✅ **図 1〜5**（判断 181）: pgfplots。図 2〜5 は `results_tables.py` が `generated/fig-*.tex` を生成（`--check` の対象）。図 1 は手書きの `figures/components.tex`。⚠️ sn-jnl の `\scriptsize`（9pt）は `\footnotesize`（7pt）より大きい → 図の小さい字は `\footnotesize`。図 2 は横向きの頁。
- ✅ **要旨（249 語）と §1・§11〜13・Declarations・Open Practices Statement**（判断 182）。要旨は規則どおり (iv) CPU → (ii) `dwell_ms` の偏りを本文へ回した。手法の節に D10。語数は `.steering/20260927-ime-observation-paper-eval-design/issues/_count_abstract.py`（`\rv` を展開して数える）。
- ✅ **表紙と Declarations**（判断 185）: Mikoto Miura（ORCID は文字のリンク・雛形に ORCID の画像が無いため）・Independent researcher, Hiroshima, Japan・メール。住所と電話は投稿システム（ScholarOne）だけ。Funding なし・利益相反なし・単著（CRediT の役割すべて）。
- ✅ **AI Declaration と図の題の断り**（判断 185〜187・Springer Nature の「AI use in manuscript preparation」）: Claude（Opus 4.6〜5.5・Sonnet 4.6〜5.5・Haiku 4.5・2026 年 2〜10 月）と Codex（コードのレビュー）の使い道をすべて。コードの確認は「テストと道具のレビュー」、設計と設定は「Claude の提案を著者が選び・確かめ・承認」、データは「言語モデルが値を作っても変えてもいない」と記録どおりに書いた。
- ✅ **レビュー**: code-reviewer 2 回・security-checker・Codex 3 回（2 巡＋追加分）。指摘はすべて一次で確かめて直すか理由を記録した。selftest 137 件・変異 25 本（scratchpad の使い捨て `mutate_figs.py`・判断 181〜186 に一覧）。
- ✅ **M12 の 4 点を研究者が決めた**（判断 183）: E3 の標本は Zenodo のデータに／working の観測ログも寄託／較正パイロットの生ログを別の区分で含める／コードの DOI は GitHub と Zenodo の連携。
- `build.sh`: main・補遺ともエラー 0・未定義の参照 0・生成されていない値 0・overfull は main 0・補遺 160（以前から）。
- Codex の台帳: 2026-10-05 は 333,672 / 9 回（上限は 300,000 に戻してある）。
- Mac の self-hosted runner: 研究者が空けて空き 27 GiB（2026-10-05 13:15）。

### 研究者が覆せる判断（未確認）

- ★ **要旨に全試行の範囲の「外した層の数」を入れていない**（判断 183 の 5）: 語数のため。規則 (i) の「with the number of strata left out」は主の範囲に付くと読んだ。結論と結果の節には入れた。
- ★ **「全試行の範囲」の読み (B)**（判断 175）。
- 図の作り方（pgfplots・30 試行未満は白抜き・対数軸の下端）（判断 181・183）。
- 値から手で書いた語（結果のファイルが変われば手で直す）: 要旨の「neither … none … nor」、§11 (c) と §13 の「neither granularity … in either macOS cell」、判断 174 の一覧。

## §2 やること

0. **main の CI**: run `37316167205`（merge コミット `ab7851db`）の結果を `gh run view 37316167205` で確かめる。赤なら 1 回だけ原因を見て研究者に報告（git-workflow ルール 6）。
1. **原稿の attack-me**（stage `manuscript`・判断 145 の 10-18〜22 の枠を前倒し）: Skill `attack-me` の手順で、査読者 3 人＋意図の監査役（`paper-reviewer`・Opus）。外枠の round 1・2 の引き継ぎ（`.steering/20260927-ime-observation-paper-eval-design/attack-me/outline-ime-manuscript/round-1/`・`round-2/` の verdict と指摘の一覧）を渡す（判断 150-4）。⚠️ 渡すのは組んだ PDF ではなく `.tex` と生成物（値は `generated/values.tex`）。指摘は一次で裏取りしてから、採否を AskUserQuestion で研究者に聞く（査読の結果は研究の証拠ではない）。
2. ★ **研究者が結果と考察を読んで直す段**（判断 185・186・Springer Nature の規程「the argument, interpretation, and conclusions must be author-led」）: attack-me の直しの後、投稿の前に、結果（§6〜9）・推奨・限界・結論を研究者が読み、主張と解釈を自分のものとして直す。Claude は節ごとに「主張 ↔ 根拠（登録の節・結果のファイル・表）」の対応を日本語で添えて渡す。⚠️ AI Declaration の「The interpretation of the results is the author's, and the author is accountable」はこの段を済ませて初めて事実になる。
3. **M12**（判断 145・146・167・183）:
   - Zenodo のデータセットの記録を**下書き**で作り DOI を予約（公開は研究者に確かめる）。中身は外枠 DS1・`dataset.tex` の表 13＋判断 183 の 4 点。寄託の前に各 run を `kit/analysis/pipeline.py --pack` と `--check-deposit` に通す（`data.md` の寄託の手順）。書庫は Mac の `~/ime-m4/deposit/`・Surface の `~/ime-m7/deposit/`（G-GEAR の `Downloads` に同じ SHA の写し）。
   - datasheet（Gebru らの形・`dataset.tex` が約束している）を書く。⚠️ Claude が書いたら AI Declaration の使い道に足す。
   - GitHub の公開 repo: 最初の commit は macOS の凍結の書き出し（判断 131・一覧の SHA-256 `29b183ba…`）、Windows の凍結の書き出しの一覧（`f61af353…`）も公開物から計算し直せる形にする（判断 145 の申し送り・外枠 Open items）。リリースと Zenodo の連携は研究者の GitHub アカウントで。
   - 予約した DOI・repo の URL・外枠を固定した公開 commit を原稿の `\tbd` に入れる（`declarations.tex` の Availability と Code availability と Open Practices・`dataset.tex`・`related.tex` の表 1「This logger」の版・`results-agreement.tex` の試行の表の「at deposit」）。⚠️ BRM はデータの引用を書誌に求める → `references.bib` にデータセットの項目（citation-ssot）。
   - `dataset.tex` の「`\tbd{confirmed at deposit}`」（working の観測ログ）を寄託の後に外す。
4. **外枠の Open items の残り**: 入力方式を通したテキスト入力の評価の文献を §2 に置くか（一次で確かめる）・凍結の書き出しの一覧を公開 repo から計算し直す形・§10.8 の点検の計画の SHA-256 の全桁（Surface の manifest から）・Windows の計測機で何が動いていたか（Surface）・観察可能性の文書の一覧を補遺に。
5. 投稿の前: カバーレター（判断 145 の 10-23〜27）・投稿規程を読み直す（BRM は ScholarOne・memory）・要旨を変えたら `_count_abstract.py` で 250 語以内を確かめる。

## §3 気をつけること

- ⚠️ 表の道具を直したら selftest と変異（scratchpad の使い捨て・狙った確認で赤になることを FAIL の名前で確かめる）。2026-10-05 も 2 本が「例外で落ちて FAIL に数えられない」「前の直しで行が変わって当たらない」で空振りした → 確認は例外で落ちない形に、変異は直しのたびに当たるか確かめる。
- ⚠️ `run-codex-review.sh` は 1 回で 2〜3 万トークン。ガードは「残り < 30,000」で止まる（OpenAI 側の制限ではなく repo の台帳）。上限は研究者の 2026-10-01 の指示で必要に応じて上げてよい（`tokens_used` は触らず理由をコメントに・回した後は戻す）。台帳はブランチごとに記帳される —— 回す前に origin/main の台帳も見る・merge のときは和。
- ⚠️ CI の macOS は self-hosted runner の空きが 8 GiB 未満だと「Disk guard」で止まる（15 GiB 未満で掃除）。赤ならまず空きを見る。⚠️ Mac の `~/ime-m4/deposit/` は M12 の書庫なので消さない。
- ⚠️ 雛形 sn-jnl: `\orcid` は `Orcidlogo.eps` を読むが同梱されていない（`main.tex` で `\orcidlogo` を文字に置き換えた）。`\scriptsize` > `\footnotesize`。
