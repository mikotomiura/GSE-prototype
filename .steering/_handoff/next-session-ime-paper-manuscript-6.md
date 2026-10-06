# 次セッション — IME 論文: 原稿の attack-me round 2（同じ立場・同じ接地）→ 採否を研究者に → 直す → M12

> 作成: 2026-10-06（G-GEAR）。Discussion の仕上げと断りの寄せ（判断 201〜203）の後。研究者が「round 2 は次のセッションで回す（推奨どおり）」を選んだ（判断 203）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 188〜203**、`attack-me/manuscript-ime-observation/round-1/`（`panel.md`・`verdict.md`・`review-R*.md`・`audit.md`・`carryover-*.md`）、外枠 `papers/ime-observation/manuscript/outline.md`、凍結した事前登録、`experiment/deviations.md`（D1〜D12）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（枝 docs/ime-discussion-finish の PR が main に merge 済みか・判断 201〜203 が main にあるか）。⚠️ main は別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る（merge 前なら origin/docs/ime-discussion-finish から）。
.steering/_handoff/next-session-ime-paper-manuscript-6.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 188〜203、attack-me/manuscript-ime-observation/round-1/ の panel.md・verdict.md（§3 の Z 番号・§7 の採否・§8 の対応）、outline.md、凍結した事前登録、deviations.md（D1〜D12）。
Skill: attack-me（Step 0 から）・subagent-delegation・verify-before-claiming・citation-ssot・git-workflow。応答は日本語。コミットは git add パス指定。
⚠️ 査読の結果は研究の証拠ではない。採否は研究者（AskUserQuestion・推奨と理由を添える）。指摘は一次で裏取りしてから採否に回す（引用は正規化して照合: PDF の改行・合字・頁の柱で素の grep は 0 件になる）。
⚠️ 結果の解釈・Discussion・結論は研究者のもの（Springer Nature "the argument, interpretation, and conclusions must be author-led"）。新しい解釈の文は日本語で研究者に見せて採るかを聞く。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。査読者にも experiment/runs/ と sealed/ を読ませない（依頼で名指す）。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない。評価の語を使わない（外枠 57 行・登録 §6.1）。公開物（papers/）は学術的な英語・GSE への言及なし・内部の番号を書かない（D の番号は可）。_style_check.py を repo 直下から papers/ime-observation で回す。新しい行は 120 字以内。
⚠️ 判断の番号は 204〜、逸脱は D13。
⚠️ heredoc（cat も）・python -c・sed にバックスラッシュを含めない → 置換は Edit か、Write で書いたスクリプトで。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。PYTHON=python bash papers/ime-observation/manuscript/build.sh ~/tools/sn-template/sn-article-template ~/ime-paper-build [--submission]。頁を画像で見るときは PyMuPDF（fitz）で PNG にして Read。
```

## §1 状態（2026-10-06 夜）

- ✅ 判断 201: Discussion を仕上げた（§6 にある値は参照に・観測可能性の段落・書字研究の尺度の段落〔[V162] Torrance & Conijn 2024・CC BY・p.243〕）。新しい文は研究者が日本語で採った（3 問とも推奨どおり）。
- ✅ 判断 202: 断りの重複（資料 §C の 7 種）を方法の節に寄せた（節の合計 −235 語）。§3.2 の逐語の引用符を LaTeX の形に。
- ✅ 判断 203: 点検（code-reviewer HIGH 1・MEDIUM 3・LOW 8／security LOW 1）と /cross-review 2 巡（P2 3・P3 2）をすべて一次で確かめて直した。⚠️ 観測可能性の段落の「set by its rules」は ¶1 の根拠に合わせて「set mainly by its rules」に弱めた（研究者が採った日本語より弱い・向きは同じ）。⚠️ 「almost exactly … almost the same durations」（¶1・判断 199 で入れた既存の文）は評価の語に読めるという LOW を直していない → round 2 の査読者に見せる。
- Codex の台帳: 2026-10-06 は 297,836 / 10 回（日付が変わっていれば 0 から）。上限 300,000（2 巡目のために一時的に 340,000 にし、回した後に戻した・`_comment_2026_10_06_raise`）。

## §2 やること

1. **原稿の attack-me round 2**（Skill `attack-me`・stage `manuscript`）:
   - 立場は round 1 と同じ 3 つ（R1 計時の道具の検証と方法の比較・R2 書字研究の利用者・R3 メタサイエンスとデータ管理）＋意図の監査役。接地の文献も round 1 と**同じ 9 本**（`panel.md`: 外枠から残した 7 本＋Giavarina 2015・Koo & Li 2016）。原本と本文テキストは G-GEAR の `round-1/tmp/raw/`・`tmp/sources/`（git の外・`.gitignore` の `tmp/`）—— 使う前に SHA-256 を `panel.md` の記録と照合する。⚠️ round 2 で [V162]（Torrance & Conijn 2024）を R2 の接地に足すかは Skill の「同じ stage の round 2 は同じ文献」の規則と照らして決める（足すなら理由を panel に）。
   - 渡すもの: `.tex` と生成物（値は `generated/values.tex`）。組んだ PDF ではない。round 1 の各役の指摘と対応（`review-R*.md`・`verdict.md` §3・§7・§8）、Discussion の経緯（判断 195〜203: 研究者の方向性・Codex の第二意見・点検の直し）。各役に「round 1 の自分の指摘が解消したか」を判定させる（`carryover-*.md` の形）。
   - 見てほしい点（依頼に書く）: 新しい Discussion（7 段落）の主張と根拠の距離・評価の語・§C の寄せで断りが見つからなくなった場所が無いか・D11/D12・「almost exactly」の LOW。
   - 査読者は `paper-reviewer`（Opus・Read/Grep/Glob だけ）。依頼に範囲・禁止（`experiment/runs/`・`sealed/` を読まない）・締切を書く（subagent-delegation ルール 2）。応答は届いた本文から `tmp/*.raw.md` に書く（サブエージェントの output ファイルは 0 バイト・memory）。
   - 裏取り → `verdict.md`（round 2）→ 研究者に採否（AskUserQuestion・推奨と理由）→ 直す（表の道具を直したら selftest と使い捨ての変異）→ 点検 → /cross-review 2 巡 → PR → CI → merge。
2. **M12**（`next-session-ime-paper-manuscript-2.md` §2 の 3 と `-4.md` §2 の 3 の注意）: Zenodo の下書きと DOI の予約（公開は研究者に確かめる）・datasheet・GitHub の公開 repo（**履歴なしで作る**・commit `115cd5ff` の 5 か所の参照を公開側のタグか SHA-256 に揃えるかを決める）・`\tbd`（DOI・URL・外枠の commit・表 1 の版・試行の表の「at deposit」）・`references.bib` の `dataset`・`release`。⚠️ 書庫は Mac の `~/ime-m4/deposit/` と Surface の `~/ime-m7/deposit/`（G-GEAR の `Downloads` にあるのは Windows の 1 本だけ）→ macOS 側は Mac で。
3. 投稿の前: 投稿規程（BRM・ScholarOne）の語数の上限を一次で確かめる（判断 200 の 6）・カバーレター・タイトル頁（repo の外で記入）・要旨を変えたら `_count_abstract.py` で 250 語以内。
4. 研究者に残っていること: OSF のプロフィール名「Mikto Miura」を直す（判断 200 の 8）。

## §3 気をつけること

- ⚠️ 予測の層は 4 つで、登録が列挙した S10 の Tab と live on の 2 回目の Return/Escape には層が無い（判断 199）。
- ⚠️ 断りの置き場所（判断 202）: 定義と理由は方法の節（§5.3 外部の装置・§5 の Intervals and wording・§8 の方法・§9 の方法・§3.6）。結果・限界・関連研究は 1 句か参照。要旨・結論・推奨 (a)(c) は単独で読まれるので残す。査読者が「繰り返し」を再び指摘したら、この置き方を示す。
- ⚠️ 尺度の段落は §6 の値を並べる例外（冒頭のコメントに書いた）。
- ⚠️ 表の道具を直したら selftest と使い捨ての変異（scratchpad）。Python の版で浮動小数の `sum()` が変わる（`math.fsum`）。
- ⚠️ 投稿用の組版（main-submission）の overfull 1 は書誌の WebKit の項目のパスの中（判断 202・未対応）。
