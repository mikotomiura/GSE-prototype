# 次セッション — IME 論文: 研究者の読み直しの残り（§A の各段落・§C の断りの重複・§B.4 の 5〜7）を英語にする → attack-me round 2 を回すか → M12

> 作成: 2026-10-06（G-GEAR）。更新: 同日、Discussion を書いて研究者が採った後（判断 195〜199・PR #313 の枝 `docs/ime-manuscript-handoff-4`）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 188〜199**、読み直しの資料 `reading-results-discussion.md`、`attack-me/manuscript-ime-observation/round-1/verdict.md`（§3・§7・§8）、外枠 `papers/ime-observation/manuscript/outline.md`、凍結した事前登録、`experiment/deviations.md`（D1〜D12）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（PR #313 が main に merge 済みか）。⚠️ main は別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る。
.steering/_handoff/next-session-ime-paper-manuscript-4.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 188〜199、reading-results-discussion.md、verdict.md（round-1）、outline.md、凍結した事前登録、deviations.md（D1〜D12）。
⚠️ 結果の解釈・Discussion・結論は研究者のもの（Springer Nature "the argument, interpretation, and conclusions must be author-led"）。研究者の答え（日本語）を英語にするだけ。研究者の答えが無い論点を Claude が埋めない。解釈の文は研究者に日本語で見せて採るかを聞く（判断 198）。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。experiment/runs/ は git に入れない。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない（足りない値は表の道具に足す: selftest と変異）。値を見た後で表の道具の規則を変えない（変えるなら研究者に聞く）。評価の語を使わない（外枠 57 行・登録 §6.1）。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・Z・issue）を書かない（D の番号は書いてよい）。_style_check.py（.steering/20260927-ime-observation-paper-eval-design/issues/）を repo 直下から papers/ime-observation で回す。新しい行は 120 字以内。
⚠️ 判断の番号は 200〜、逸脱は D13（他の枝が足していないか着手時に MSYS_NO_PATHCONV=1 git show で見る）。
⚠️ 研究者に決めてもらうことは AskUserQuestion で聞く（推奨と理由を添える）。問いの前提は一次で確かめてから書く。
Skill: verify-before-claiming・citation-ssot（新しい文献を引くなら）・subagent-delegation・git-workflow（round 2 を回すなら attack-me）。応答は日本語。コミットは git add パス指定。
⚠️ heredoc（cat も）・python -c・sed にバックスラッシュを含めない（2026-10-06 も 2 回壊れた）→ 置換は Edit か、Write で書いたスクリプトで。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。PYTHON=python bash papers/ime-observation/manuscript/build.sh ~/tools/sn-template/sn-article-template <原稿の外の出力先> [--submission]。読む用の PDF は ~/ime-paper-build/ に置いている。
```

## §1 状態（2026-10-06）

- ✅ PR #312（main `78aeacdb`）: macOS の探索的な dwell〔判断 190〕・`math.fsum`〔191〕・逸脱 D12〔192〕・読み直しの資料〔193〕・点検〔194〕。
- ✅ 枝 `docs/ime-manuscript-handoff-4`（PR #313）:
  - 判断 195: 研究者の Discussion の方向性を事実と照らし、Codex に第二意見（consult）。★ macOS のロガーは規則を数 ms で実行していた（予測とロガーの dwell の限界 −3〜4 ms）→ 裾は規則と参照の会話の違いにある。タイマーの精度・人の打ち方は原因でない（データで言える）。live on と off は別の計画。
  - 判断 196・197: D12 に共通の定義の層ごとの範囲（値に依らず報告すると記録してから計算）→ 両定義で同じ範囲。
  - 判断 198: §10 Discussion（5 段落）を研究者の方向性から書き、研究者が採った。AI 宣言に Codex の本文のレビューと Discussion の計画への第二意見、Claude が研究者の方向性から下書きしたことを足した。
  - 判断 199: 点検（code-reviewer・security-checker・Codex 2 巡）の直し。¶2 の事実の誤り（S10 と live on の 2 回目の Return は層が無く「どれでもない」に入る）・¶1 と ¶3 の言い過ぎを直した。¶5 の最後の一文は研究者の選択で事実（範囲の内側で変わった層の数と最大の変化）に置き換えた。
  - Codex の台帳: 今日 244,646 / 8 回（PR #311 の 3 回を含む）。
- ⏳ **研究者の答え待ち**: 資料の §A（§6〜9・12〜14 の各段落をそのまま／弱める／削る）・§C（断りの重複の置き場所）・§B.4 の 5（書字研究の尺度と並べるか・新しい文献が要る）・6（結論の「テキストを記録しないログでも…分かりうる」を結論に残すか）・7（長さ）。OSF のプロフィール名「Mikto Miura」の確認。

## §2 やること

0. **PR #313 の CI と merge**（この枝を出したセッションが済ませていれば飛ばす）。main の CI を確かめる。
1. **研究者の答えを英語にする**（§A・§C・§B.4 の 5〜7）:
   - §A の直し → 該当の節。`\rv` と生成した表で読む。
   - §C → 断りを 1 か所に寄せ、他は 1 句か節の参照に（要旨・結論・推奨のどれを単独で読まれる場所として残すかは研究者の答えに従う）。⚠️ Discussion（§10）にも断りがある（3 つの比較を算術で組み合わせない・検証していない）。
   - 書字研究の尺度を並べるなら citation-ssot で `docs/references.md` に登録してから `references.bib` に。
   - その後: `build.sh --submission`・要旨を変えたら `_count_abstract.py`・文体の検査・code-reviewer ∥ security-checker・/cross-review。
2. **原稿の attack-me round 2 を回すか**を研究者に問う（推奨: §A・§C の後に、同じ立場・同じ接地で 1 回。引き継ぎは round 1 の各役の指摘と対応・判断 195〜199 の Discussion）。
3. **M12**（`next-session-ime-paper-manuscript-2.md` §2 の 3 のとおり）: Zenodo の下書きと DOI の予約（公開は研究者に確かめる）・datasheet・GitHub の公開 repo・`\tbd`（DOI・URL・外枠の commit・表 1 の版・試行の表の「at deposit」）・`references.bib` の `dataset`・`release`。
   - ⚠️ 公開 repo には `experiment/results/exploratory/`・`kit/analysis/explore_dwell_quantiles.py`・`generated/detection-definitions.tex` も入る。
   - ⚠️ **公開の repo は履歴なしで作る**（security-checker・判断 194・199）: `papers/` は非公開の作業 repo の commit `115cd5ff` を 5 か所で参照し（`data.md` 53・`data.windows.md` 106・`deviations.md` 243・`supplement/provenance.tex` 21・33）、作業 repo のコミットメッセージには判断の番号がある。参照を公開側のタグか `match.py` の SHA-256 に揃えるかを公開時に決める。
4. 外枠の Open items の残り・`env.md` の空欄・OSF のプロフィール名。
5. 投稿の前: カバーレター・投稿規程の読み直し・タイトル頁（repo の外で記入）を ScholarOne に。

## §3 気をつけること

- ⚠️ Python の版で浮動小数の `sum()` の結果が変わる（3.12〜）。表の道具に浮動小数の和を足すときは `math.fsum`（判断 191）。
- ⚠️ 表の道具を直したら selftest と使い捨ての変異（scratchpad）。確かめは例外で落ちない形に。変異は直すたびに当たるか確かめる（判断 199 でも 2 本が当たらなくなっていた）。
- ⚠️ 補遺に表を足すときは横向き（landscape）にすると頁が送られて空く。縦の表で、推定値と区間を `\newline` で 2 行に（判断 192）。
- ⚠️ 予測の層は 4 つ（持ち出し・持ち込み・読みの中の閉じるキー・どれでもない）で、登録が列挙した S10 の Tab と live on の 2 回目の Return/Escape には層が無い（判断 199）。
- ⚠️ `fmt_ms` は偶数への丸め（178.5 → 178）。
- ⚠️ Codex の台帳: 2026-10-06 は 244,646 / 8 回。回す前に origin/main の台帳も見る・merge のときは和。
- ⚠️ レビューの依頼では `experiment/runs/` と `sealed/` を読まないと名指す。
