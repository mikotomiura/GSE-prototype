# 次セッション — IME 論文: Discussion の仕上げ（観測可能性の段落・書字研究の尺度・数字を §6 に寄せる）と断りの重複を寄せる → 点検 → attack-me round 2 を回すか → M12

> 作成: 2026-10-06（G-GEAR）。研究者が Discussion の見立てを聞き、残りの問い 8 つに答えた後（判断 200）。前の引き継ぎ `next-session-ime-paper-manuscript-4.md` の §2 の 1 は、この判断で方針がすべて決まった。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 188〜200**、読み直しの資料 `reading-results-discussion.md`（§B・§C）、Mac の下書き `discussion-outline-draft.md`、`attack-me/manuscript-ime-observation/round-1/verdict.md`、外枠 `papers/ime-observation/manuscript/outline.md`、凍結した事前登録、`experiment/deviations.md`（D1〜D12）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（PR #313 が main に merge 済みか・枝 docs/ime-manuscript-handoff-5 に判断 200 と本メモがある）。⚠️ main は別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/docs/ime-manuscript-handoff-5 から枝を切る（判断 200 を含むため）。
.steering/_handoff/next-session-ime-paper-manuscript-5.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 188〜200、reading-results-discussion.md（§B・§C）、discussion-outline-draft.md、outline.md、凍結した事前登録、deviations.md（D1〜D12）。
⚠️ 結果の解釈・Discussion・結論は研究者のもの（Springer Nature "the argument, interpretation, and conclusions must be author-led"）。判断 200 で研究者が決めた方向だけを英語にする。新しい解釈の文は日本語で研究者に見せて採るかを聞く（判断 198 の作法）。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない。評価の語を使わない（外枠 57 行・登録 §6.1）。
⚠️ 公開物（papers/）は学術的な英語・GSE への言及なし・内部の番号を書かない（D の番号は可）。_style_check.py を repo 直下から papers/ime-observation で回す。新しい行は 120 字以内。
⚠️ 判断の番号は 201〜、逸脱は D13。研究者に決めてもらうことは AskUserQuestion（推奨と理由を添える）。
⚠️ 文献: 有料の本文は使わない（無料の版を OpenAlex などで確かめる）。引用は本文の該当箇所を一次で確かめてから（citation-ssot・docs/references.md に append-only で登録してから references.bib）。探索はサブエージェント・references.md への追記はメインが直列（/literature-review の Step 2）。
Skill: verify-before-claiming・citation-ssot・subagent-delegation・git-workflow（round 2 を回すなら attack-me）。応答は日本語。コミットは git add パス指定。
⚠️ heredoc（cat も）・python -c・sed にバックスラッシュを含めない → 置換は Edit か、Write で書いたスクリプトで。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。PYTHON=python bash papers/ime-observation/manuscript/build.sh ~/tools/sn-template/sn-article-template <原稿の外の出力先> [--submission]。読む用の PDF は ~/ime-paper-build/。
```

## §1 状態（2026-10-06）

- ✅ PR #312（main `78aeacdb`）・PR #313（Discussion 5 段落・D12 の層ごとの範囲と変化・AI 宣言・判断 195〜199）。
- ✅ 判断 200（研究者の答え・8 問とも推奨どおり）: 観測可能性の段落を足す／書字研究の尺度を文献で並べる／プライバシーは結論に残す／Discussion の数字は §6 に寄せる／断りは資料 §C の案どおり／長さの目安は置かない／§A は今のまま／OSF の名前は研究者が直す。
- Codex の台帳: 2026-10-06 は 244,646 / 8 回（日付が変わっていれば 0 から）。

## §2 やること

1. **Discussion の仕上げ**（`sections/discussion.tex`）:
   - (a) **数字を §6 に寄せる**: ¶1・¶5 で §6 に既にある値（gt_obs のプール・層ごとの範囲・D12 の外れた数と範囲）は「Section~\ref{sec:results-detection}」などの参照に。§6 に無い値（予測との比較の dwell の限界と中央絶対差・層の「どれでもない」の値・D12 の層ごとの変化）だけ残す。D12 の段落は含意だけに。
   - (b) **観測可能性の段落を足す**（研究者の例: macOS は変換を知らせる公開の接点が無くキーから推すしかない → 一致の天井は実装でなく規則が決める〔予測とロガーの差は数 ms〕。Windows は窓を見るので構成概念の差が残る）。§3・§14 の第 1 段落の言い回しに揃える（「documented interfaces examined that do not depend on the application」の限定を落とさない）。下書きを日本語で研究者に見せて採るかを聞く。
   - (c) **書字研究の尺度**: 無料で読める文献を 1〜2 本探す（例: キーストローク研究のポーズの閾値・バーストの定義など。⚠️ 探す前に問いを固める: 「書字研究が使う時間の尺度（ms〜s）」）→ 本文で尺度を確かめる → citation-ssot で登録 → 判定せずに 1〜2 文（キー行の時刻 1〜2 ms・dwell の差の広がり・その尺度を並べる）。文を日本語で研究者に見せる。
2. **断りの重複を寄せる**（資料 §C の表の案どおり）: 定義と理由は方法の節に 1 回、結果・推奨・限界は 1 句か節の参照、要旨・結論・推奨 (a)(c) は残す。Discussion の断り（算術で組み合わせない・検証していない）も見る。削った語数を報告する（`_count_abstract.py` は要旨を変えたときだけ）。
3. **点検**: `build.sh --submission`・文体の検査・code-reviewer ∥ security-checker・/cross-review 2 巡（Codex の台帳を先に見る）→ PR → CI → merge。
4. **原稿の attack-me round 2 を回すか**を研究者に問う（推奨: この仕上げの後に、同じ立場・同じ接地で 1 回）。
5. **M12**（`next-session-ime-paper-manuscript-2.md` §2 の 3 と `-4.md` §2 の 3 の注意: 公開の repo は履歴なしで作る・commit `115cd5ff` の参照をどう扱うか）。
6. 投稿の前: 投稿規程の語数の上限を一次で確かめる（判断 200 の 6）・カバーレター・タイトル頁（repo の外で記入）。

## §3 気をつけること

- ⚠️ メインは判断 198 で Mac の下書きの筋のうち 3 つ（観測可能性・書字研究・プライバシー）を落として書いた（判断 200 で研究者に開示）。筋を採ったら、下書きの全項目と突き合わせてから書く。
- ⚠️ 予測の層は 4 つで、登録が列挙した S10 の Tab と live on の 2 回目の Return/Escape には層が無い（判断 199）。
- ⚠️ 表の道具を直したら selftest と使い捨ての変異（scratchpad）。Python の版で浮動小数の `sum()` が変わる（`math.fsum`）。
- ⚠️ レビューの依頼では `experiment/runs/` と `sealed/` を読まないと名指す。
