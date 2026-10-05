# 次セッション — IME 論文: 研究者の読み直しの答えを英語にする（Discussion・直し・断りを寄せる）→ attack-me round 2 を回すか → M12

> 作成: 2026-10-06（G-GEAR）。macOS の探索的な dwell〔判断 190・Mac〕・`math.fsum`〔判断 191〕・逸脱 D12〔判断 192〕・読み直しの資料〔判断 193〕・点検と /cross-review 2 巡〔判断 194〕まで済ませ、PR #312 を出したセッションの最後。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 188〜194**、読み直しの資料 `reading-results-discussion.md`、`attack-me/manuscript-ime-observation/round-1/verdict.md`（§3・§7・§8）、外枠 `papers/ime-observation/manuscript/outline.md`、凍結した事前登録、`experiment/deviations.md`（D1〜D12）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（PR #312 が main に merge 済みか）。⚠️ main は別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る。
.steering/_handoff/next-session-ime-paper-manuscript-4.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 188〜194、reading-results-discussion.md、verdict.md（round-1）、outline.md、凍結した事前登録、deviations.md（D1〜D12）。
⚠️ 結果の解釈・Discussion・結論は研究者のもの（Springer Nature "the argument, interpretation, and conclusions must be author-led"）。研究者の答え（日本語）を英語にするだけ。研究者の答えが無い論点を Claude が埋めない。選択肢の形で解釈を差し出さない（問いは事実と論点だけ）。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。experiment/runs/ は git に入れない。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない。値を見た後で表の道具の規則を変えない（変えるなら研究者に聞く）。評価の語を使わない（登録 §6.1）。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・記号や口語なし・内部の番号（判断・M・Z・issue）を書かない（D の番号は書いてよい）。_style_check.py（.steering/20260927-ime-observation-paper-eval-design/issues/）を repo 直下から papers/ime-observation で回す。
⚠️ 判断の番号は 195〜、逸脱は D13（他の枝が足していないか着手時に MSYS_NO_PATHCONV=1 git show で見る）。
⚠️ 研究者に決めてもらうことは AskUserQuestion で聞く（推奨と理由を添える）。問いの前提は一次で確かめてから書く（判断 192: 判断 188 の承認は登録 §5 の「報告しない」に気づく前だった）。
Skill: verify-before-claiming・citation-ssot（Discussion で新しい文献を引くなら）・subagent-delegation・git-workflow（round 2 を回すなら attack-me）。応答は日本語。コミットは git add パス指定。
⚠️ heredoc（cat も）・python -c・sed にバックスラッシュを含めない（2026-10-06 も 2 回壊れた）→ 置換は Edit か、Write で書いたスクリプトで。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。PYTHON=python bash papers/ime-observation/manuscript/build.sh ~/tools/sn-template/sn-article-template <原稿の外の出力先> [--submission]。読む用の PDF は ~/ime-paper-build/ に置いている。
```

## §1 状態（2026-10-06・枝 `docs/ime-macos-dwell-quantiles`・PR #312）

- ✅ 引き継ぎ manuscript-3 の §2 の 0〜2: PR #311 は merge 済み。macOS の探索的な dwell（判断 190・Mac）。G-GEAR で通しのビルド（生成されていない値 0）。`values.json` の最後の桁が Python の版で変わる問題を `math.fsum` で直した（判断 191）。
- ✅ **逸脱 D12**（判断 192）: 登録 §5 は共通の定義（`all`）の結果を「報告しない」と書いていた → 研究者の選択で D12。§6「The two definitions」に外れた参照の会話（26 / 2,306・全試行 28 / 2,923）と共通の定義の recall・precision・**統合の率**（0.001 → 0.009・研究者の選択〔判断 194〕）。補遺に両定義の表（`generated/detection-definitions.tex`）。
- ✅ **読み直しの資料**（判断 193）: `.steering/20260927-ime-observation-paper-eval-design/reading-results-discussion.md`。§A 主張 ↔ 根拠（§6〜9・12〜14）・§B Discussion の事実 F1〜F8 と問い 7 つ・§C 断りの重複 7 種。Mac の下書き `discussion-outline-draft.md`（Claude の提案）の取り違え 2 点を §B.3 に。
- ✅ 点検（判断 194）: code-reviewer（MEDIUM 1・LOW 3・資料 2）・security-checker（LOW 1）・/cross-review 2 巡（Codex 48,136 tokens・今日の台帳 159,540 / 5 回）。selftest 173 件・変異 14 本と前の 17 本すべて赤。
- ⏳ **研究者の答え待ち**: 資料の §A（各行をそのまま／弱める／削る）・§B.4（Discussion の問い 7 つ）・§C（断りの置き場所）。OSF のプロフィール名「Mikto Miura」の確認。

## §2 やること

0. **PR #312 の CI と merge**（この枝を出したセッションが済ませていれば飛ばす）。main の CI を確かめる。
1. **研究者の答えを英語にする**（答えが来ていれば）:
   - §A の直し → 該当の節。`\rv` と生成した表で読む。
   - §10 Discussion（`sections/discussion.tex` の `\tbd` の枠）→ 研究者の解釈から書く。新しい文献（例: 書字研究のポーズの尺度）を引くなら citation-ssot で `docs/references.md` に登録してから `references.bib` に。
   - §C → 断りを 1 か所に寄せ、他は 1 句か節の参照に（要旨・結論・推奨のどれを単独で読まれる場所として残すかは研究者の答えに従う）。
   - その後: `build.sh --submission`・要旨を変えたら `_count_abstract.py`・文体の検査・code-reviewer ∥ security-checker・/cross-review。
   - ⚠️ AI 宣言の "The interpretation of the results is the author's" は、この段を済ませて初めて事実になる。
2. **原稿の attack-me round 2 を回すか**を研究者に問う（推奨: 読み直しと Discussion の後に、同じ立場・同じ接地で 1 回。引き継ぎは round 1 の各役の指摘と対応）。
3. **M12**（`next-session-ime-paper-manuscript-2.md` §2 の 3 のとおり）: Zenodo の下書きと DOI の予約（公開は研究者に確かめる）・datasheet・GitHub の公開 repo・`\tbd`（DOI・URL・外枠の commit・表 1 の版・試行の表の「at deposit」）・`references.bib` の `dataset`・`release`。
   - ⚠️ 公開 repo には `experiment/results/exploratory/`・`kit/analysis/explore_dwell_quantiles.py`・`generated/detection-definitions.tex` も入る。
   - ⚠️ **公開の repo は履歴なしで作る**（security-checker LOW・判断 194）: `papers/` は非公開の作業 repo の commit `115cd5ff` を 5 か所で参照している（`data.md` 53・`data.windows.md` 106・`deviations.md` 243・`supplement/provenance.tex` 21・33）。履歴ごと出すと作業 repo のコミットメッセージ（判断番号を含む）が出る。参照を公開側のタグか `match.py` の SHA-256 に揃えるかを公開時に決める。
4. 外枠の Open items の残り・`env.md` の空欄・OSF のプロフィール名。
5. 投稿の前: カバーレター・投稿規程の読み直し・タイトル頁（repo の外で記入）を ScholarOne に。

## §3 気をつけること

- ⚠️ Python の版で浮動小数の `sum()` の結果が変わる（3.12〜）。表の道具に浮動小数の和を足すときは `math.fsum`（判断 191）。Mac（3.14）と G-GEAR（3.11）の両方で `--check` が通ることを前提にしている。
- ⚠️ 表の道具を直したら selftest と使い捨ての変異（scratchpad）。確かめは例外で落ちない形に。変異は直すたびに当たるか確かめる。
- ⚠️ 補遺に表を足すときは横向き（landscape）にすると頁が送られて空く。縦の表で、推定値と区間を `\newline` で 2 行に（判断 192）。
- ⚠️ Codex の台帳: 2026-10-06 は 159,540 / 5 回（PR #311 の 3 回を含む）。回す前に origin/main の台帳も見る・merge のときは和。
- ⚠️ レビューの依頼では `experiment/runs/` と `sealed/` を読まないと名指す。
