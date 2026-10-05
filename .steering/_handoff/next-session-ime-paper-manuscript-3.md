# 次セッション — IME 論文: macOS の探索的な dwell の分位点（Mac）→ 研究者が結果と考察を読んで直す（Discussion を含む）→ attack-me round 2 を回すか → M12

> 作成: 2026-10-06（G-GEAR）。原稿の attack-me round 1（major）→ 研究者の採否（判断 188）→ 直し → 作業中の点検と /cross-review 2 巡（判断 189）まで済ませたセッションの最後。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 188・189**（と 145・146・150・167・175・181〜187）、`attack-me/manuscript-ime-observation/round-1/verdict.md`（§3 の Z1〜Z49・§7 の採否・§8 の対応）、外枠 `papers/ime-observation/manuscript/outline.md`、凍結した事前登録、`experiment/deviations.md`（D1〜D11）・`data.md`・`data.windows.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（この枝 docs/ime-manuscript-attack-me が main に merge 済みかを見る）。⚠️ main は別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る。
.steering/_handoff/next-session-ime-paper-manuscript-3.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 188・189、verdict.md（round-1）の §8、outline.md、凍結した事前登録、deviations.md（D1〜D11）。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。封印（sealed/）は寄託のためだけに開ける（解析しない）。生ログ・キーコードを原稿や外部の LLM に出さない。experiment/runs/ は git に入れない。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない。値を見た後で表の道具の規則を変えない（変えるなら研究者に聞く）。評価の語を使わない（登録 §6.1）。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・issue）を書かない（D の番号は書いてよい）。_style_check.py を repo 直下から papers/ime-observation で回す。
⚠️ 判断の番号は 190〜、逸脱は D12（他の枝が足していないか着手時に MSYS_NO_PATHCONV=1 git show で見る）。
⚠️ 研究者に決めてもらうことは AskUserQuestion で聞く（推奨と理由を添える）。問いの前提は一次で確かめてから書く（判断 188-4 で「既存の対の値から計算できる」と誤って書き、問い直した）。
⚠️ 結果と考察・Discussion の解釈は研究者のもの（Springer Nature の方針 "the argument, interpretation, and conclusions must be author-led"・"Writing results or discussion independently" は AI に不可）。Claude は事実と対応を日本語で渡し、研究者の解釈を英語にする。
Skill: verify-before-claiming・citation-ssot・reproducibility-discipline・subagent-delegation・git-workflow（attack-me round 2 を回すなら attack-me）。応答は日本語。コミットは git add パス指定（-A もディレクトリ指定もしない）。
⚠️ heredoc（cat も）・python -c・sed にバックスラッシュを含めない（2026-10-06 も 3 回壊れた）→ 置換は Edit か、Write で書いたスクリプトで。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。PYTHON=python bash papers/ime-observation/manuscript/build.sh ~/tools/sn-template/sn-article-template <原稿の外の出力先> [--submission]。⚠️ 出力先は papers/ime-observation の外（中は拒む）。頁の確認は pdftoppm -r 60 -f N -l N -png。
```

## §1 状態（2026-10-06・枝 `docs/ime-manuscript-attack-me`）

- ✅ **原稿の attack-me round 1**: 記録 `attack-me/manuscript-ime-observation/round-1/`。立場は外枠と同じ 3 つ、接地は 7 本＋統計の方法論 2 本（Giavarina 2015・Koo & Li 2016）。R1・R2・R3 とも **major**。捏造 0・注入 0・偽陽性 0。
- ✅ **研究者の採否（判断 188）**: 直す一覧を全部承認。要旨は登録 §6.1 の規則を保ち、範囲の端を決めた場面を添える。ICC の恒等的な 0 は値なし（逸脱 **D11**）。dwell の分位点の限界を探索的に。キーワードを外し、問 4 の大きさを結論と §8 に。Discussion は研究者の解釈を元に。公開しないタイトル頁と投稿用の組版。計測の run はすべて Claude Code が起動した（AI 宣言に書いた）。
- ✅ **直し（`verdict.md` §8）**: 本文・表の道具（`cell_name`・参照の文間の SD・D11・探索的な dwell の読み込み・負のゼロ）・`kit/analysis/explore_dwell_quantiles.py`（新規）・補遺の来歴の表と探索的な dwell の表・`build.sh --submission`・`submission/title-page.tex`（住所と電話は空欄・記入は repo の外）。
- ✅ **点検（判断 189）**: code-reviewer（HIGH 3・MEDIUM 4・LOW 9）・security-checker（LOW 4）・/cross-review 2 巡（Codex 3 回・111,404 tokens）の指摘をすべて一次で確かめて直した。表の道具の selftest 162 件・変異 17 本すべて赤。探索的なスクリプトの selftest 0 failed・変異 4 本すべて赤。
- `build.sh --submission`: main・main-submission・補遺ともエラー 0・未定義の参照 0・**生成されていない値は macOS の探索的な 8 個**（§2 の 1 で埋まる）・overfull は main 1（§4 の頁の 2.1 pt・見た目は問題なし）・要旨 248 語・文体 違反 0。
- ⚠️ **見つけたこと**: OSF の 2 つの登録の貢献者のプロフィール名が「Mikto Miura」（研究者に確かめてもらう）。`experiment/env.md` の「Analysis machine」と Windows の lock file の行が「(to be filled in)」のまま（M12 の前に埋める）。

## §2 やること

0. **PR の CI と merge**（この枝を出したセッションが済ませていれば飛ばす）。main の CI を確かめる。
1. **Mac で: macOS の 2 セルの探索的な dwell の分位点**（判断 188-4・原稿の `\rv` の 8 個）。
   - ⚠️ **凍結タグのままでは macOS の解析は止まる**（逸脱 D10 の欠陥）。`data.md` の「Analysis of the macOS cells」と同じく、macOS の凍結タグの書き出し（`git archive ime-observation-prereg-macos papers/ime-observation`）の `kit/analysis/match.py` を commit `115cd5ff` のもの（D10 の第 1 の変更・合成の run で結果はタグとバイト一致）に差し替えた写しを `--code` に渡す。
   - run のディレクトリは書庫（`~/ime-m4/deposit/`）を展開したもの（`run.json`・`obs.jsonl`・`plan.jsonl` の SHA-256 を `data.md` と照らす）。⚠️ 書庫は消さない（M12 で使う）。
   - セルごとに（`<cell>` は `macos-standard-live-on` と `macos-standard-live-off`）:
     `python <repo>/papers/ime-observation/kit/analysis/explore_dwell_quantiles.py --code <写し>/papers/ime-observation --run <run> --config <写し>/papers/ime-observation/experiment/config.json --seed 20260929 --seed-file <写し>/papers/ime-observation/experiment/SEED --prereg <写し>/papers/ime-observation/experiment/preregistration.md --registered <repo>/papers/ime-observation/experiment/results/e1_l1.json --scratch <空のディレクトリ・papers/ime-observation の外> --out <repo>/papers/ime-observation/experiment/results/exploratory/dwell_quantiles_<cell>.json`
   - スクリプトは、照合の出力の SHA-256 が登録の `e1_l1.json` の記録と一致する対だけを使い、速さごとの dwell の数値を登録と照合する（合わなければ止まる）。止まったら原因を見て研究者に報告する（値を合わせに行かない）。
   - その後 `manuscript/tools/results_tables.py --results ../experiment/results --out generated` → `build.sh` で「生成されていない値 0」を確かめる。`data.md` に実行の記録（機械・Python の版・命令・出力の SHA-256）を足す。
2. **表の道具に Windows の 2 つの定義の差の大きさ（Z40・R1）**: 結果のファイルは `cells/<cell>/all/` と `windows_def/` の両方を持つ。定義ごとの会話の数とプールした recall・precision を値に足し、§6「The two definitions」で引く（selftest と変異）。
3. ★ **研究者が結果と考察を読んで直す段**（判断 185・186・188-6）:
   - 結果（§6〜9）・推奨（§12）・限界（§13）・結論（§14）について、節ごとに「主張 ↔ 根拠（登録の節・結果のファイル・表）」の対応を日本語で渡す。
   - **Discussion（§10・今は `\tbd` の枠だけ）**: 不一致の出どころの事実（予測による分解・規則が予測した不一致〔S6・S10〕と予測しなかった不一致・Windows の分割〔S2・S8〕・dwell の裾・KT1 と物理の経路の 8 ms）を日本語で渡し、**研究者の解釈を受けて**英語にする。
   - 断りの重複（Z10: 「別の構成概念」「プライバシーの基準ではない」「外部の装置で測っていない」「プールした Wilson は下限」）を、研究者の読み直しと一緒に 1 か所に寄せる。
   - ⚠️ AI 宣言の "The interpretation of the results is the author's" は、この段を済ませて初めて事実になる。
4. **原稿の attack-me round 2 を回すか**を研究者に問う（推奨: 研究者の読み直しと Discussion の後に、同じ立場・同じ接地で 1 回。引き継ぎは round 1 の各役の指摘と対応）。
5. **M12**（前の引き継ぎ `next-session-ime-paper-manuscript-2.md` §2 の 3 のとおり）: Zenodo の下書きと DOI の予約（公開は研究者に確かめる）・datasheet（`dataset.tex` の `\tbd{written at deposit}`）・GitHub の公開 repo・`\tbd`（DOI・URL・外枠の commit・表 1 の版・試行の表の「at deposit」）・`references.bib` の `dataset`・`release` の DOI。⚠️ 公開 repo には `experiment/results/exploratory/` と `kit/analysis/explore_dwell_quantiles.py` も入る。
6. 外枠の Open items の残り（入力方式を通したテキスト入力の評価の文献・凍結の書き出しの一覧を公開 repo から計算し直す形・§10.8 の点検の計画の SHA-256 の全桁）・`env.md` の空欄・OSF のプロフィール名。
7. 投稿の前: カバーレター・投稿規程の読み直し・要旨を変えたら `_count_abstract.py`・`build.sh --submission` の版とタイトル頁（repo の外で記入）を ScholarOne に。

## §3 気をつけること

- ⚠️ `explore_dwell_quantiles.py` を直したら、出力に記録したスクリプトの SHA-256 がずれる → 直した後に出力を作り直す（2026-10-06 に 3 回やり直した）。
- ⚠️ 表の道具や探索的なスクリプトを直したら selftest と使い捨ての変異（scratchpad）。確かめは例外で落ちない形に（2026-10-06 も 2 本が例外で落ちて FAIL に数えられなかった）・変異は直すたびに当たるか確かめる（2 本が当たらなくなっていた）。
- ⚠️ Codex の台帳: 2026-10-06 は 111,404 / 3 回。回す前に origin/main の台帳も見る・merge のときは和。
- ⚠️ code-reviewer の grep が `experiment/runs/windows-msime-tsf-2/plan.jsonl`（合成入力の計画・git の外）に当たった。レビューの依頼では `experiment/runs/` を読まないと名指す。
