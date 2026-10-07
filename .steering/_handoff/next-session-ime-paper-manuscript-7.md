# 次セッション — IME 論文: round 3 を回すかを研究者に → M12（Zenodo・datasheet・公開 repo・`\tbd`）→ 投稿の前の確かめ

> ⚠️★ **2026-10-07 に `next-session-ime-paper-manuscript-10.md` で置き換えた**（§2 の 1 は判断 206、2 は判断 207〜220 で済み。3〜5 は -10 へ移した）。次のセッションは -10 を読む。以下は記録。
> 作成: 2026-10-06 夕方（G-GEAR）。原稿の attack-me round 2（minor）の採否と直し（判断 204）と、プレプリントの置き場所の決定（判断 205）の後。PR #315 は merge 済み（`96c4032e`）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 204**（と追記）、`attack-me/manuscript-ime-observation/round-2/verdict.md`（§3 の Y 番号・§7 の採否・§8 の対応）、外枠 `papers/ime-observation/manuscript/outline.md`、凍結した事前登録、`experiment/deviations.md`（D1〜D12）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（枝 docs/ime-attack-me-round-2 の PR が main に merge 済みか・判断 204 が main にあるか）。⚠️ main は別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る。
.steering/_handoff/next-session-ime-paper-manuscript-7.md を読んで §2 を上から実行してください。
一次は decisions.md の判断 204（追記を含む）、attack-me/manuscript-ime-observation/round-2/verdict.md、outline.md、凍結した事前登録、deviations.md（D1〜D12）。
Skill: git-workflow・verify-before-claiming・citation-ssot（DOI を足すとき）・subagent-delegation・browser-verification（Zenodo を Chrome で見るとき）。応答は日本語。コミットは git add パス指定。
⚠️ 結果の解釈・Discussion・結論は研究者のもの。新しい解釈の文は日本語で研究者に見せて採るかを聞く（判断 204 で直した Discussion と AI 宣言は研究者が採った）。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。
⚠️ 結果の値は \rv{<key>} と生成した表で読み、手で写さない。層を名指す・値を比べる文は手で書き、生成した値と照らす（§5 の Reproducibility にそう書いた）。評価の語を使わない。公開物（papers/）は学術的な英語・GSE への言及なし・内部の番号を書かない（D の番号は可）。_style_check.py を repo 直下から papers/ime-observation で回す。新しい行は 120 字以内（★ 枝の全体を origin/main と比べて測る。head で切らない）。
⚠️ 判断の番号は 205〜、逸脱は D13。
⚠️ heredoc（python -c・sed も）でバックスラッシュを 2 本重ねない（python に渡ると \t がタブになる・判断 204 で 3 か所壊した）→ 置換は Edit か、Write で書いたスクリプトで。cat の heredoc の 1 本のバックスラッシュは通る。git show <ref>:<path> は MSYS_NO_PATHCONV=1。
LaTeX（G-GEAR）: PATH="$HOME/AppData/Local/Programs/MiKTeX/miktex/bin/x64:$PATH"。PYTHON=python bash papers/ime-observation/manuscript/build.sh ~/tools/sn-template/sn-article-template ~/ime-paper-build [--submission]。頁を画像で見るときは PyMuPDF（fitz）で PNG にして Read。
```

## §1 状態（2026-10-06 夕方）

- ✅ 原稿の attack-me round 2: 有効 3/3 とも **minor**。捏造 0・注入 0・偽陽性 1。編集者の判定は minor revision。研究者は 8 問とも推奨どおり（判断 204）。
- ✅ 直した（`4aeb9ed4`・`a8204d3e`・`a7ee74cb`・`ad710425`・`cd22a8ab`）。
  - Discussion: ¶1 を値と範囲の文に。値を §6 へ移した。規則の文を「主の範囲で・参照に対して会話をどう区切るか」に。探索的の標識を付け、尺度の段落を直した（Conijn 2019 p. 2362 を含む）。
  - 方法・限界・宣言: D11 と D12 の段階ときっかけ。D11 は表に登録の値を並べる。
  - そのほか: 表の道具の生成（§7 の数・問 4 の句・層の名前）、表 4 のポインタの行、タイトル頁の頁番号、README。
  - 点検（security 0・code MEDIUM 5・LOW 10）と /cross-review の 2 巡（3 回・92,792 tokens）の指摘を、一次で確かめて直した。
- ✅ 研究者が、直した Discussion の全文（日本語の訳）と AI 宣言の直しを「このまま採る」を選んだ。
- Codex の台帳: 2026-10-06 は 390,628 / 13 回（日付が変わっていれば 0 から）。上限 300,000（一時的に 420,000 にし、回した後に戻した・`_comment_2026_10_06_raise_2`）。
- attack-me の `round-1/tmp/`・`round-2/tmp/`（接地の原本と本文・応答の raw）は残してある（git の外）。研究者が round 3 を回さないと決めたら消す（Skill: 最後の round の採否が決まったら消す）。

## §2 やること

1. **round 3 を回すかを研究者に問う**（AskUserQuestion・推奨と理由）。推奨: 回さない。理由は 3 つ。
   - round 2 は 3 人とも minor で、その指摘は直した。
   - 同じ立場・同じ接地の 3 回目は効きが小さい。
   - 投稿先の査読が次の検証になる。

   回さないなら、`round-1/tmp/` と `round-2/tmp/` を消して閉じる（`panel.md` の URL と SHA-256 から取り直せる）。
2. **M12**（`next-session-ime-paper-manuscript-2.md` §2 の 3 と `-4.md` §2 の 3 の注意）:
   - Zenodo の下書きと DOI の予約（公開は研究者に確かめる）
   - datasheet
   - GitHub の公開 repo（**履歴なしで作る**・commit `115cd5ff` の 5 か所の参照を、公開側のタグか SHA-256 に揃えるかを決める）
   - `\tbd`（18 か所: DOI・URL・外枠の commit・表 1 の版・試行の表の「at deposit」・datasheet・bib の 2 件）
   - `references.bib` の `dataset`・`release`

   ⚠️ 書庫は Mac の `~/ime-m4/deposit/` と Surface の `~/ime-m7/deposit/`（G-GEAR の `Downloads` にあるのは Windows の 1 本だけ）→ macOS 側は Mac で。⚠️ 凍結の表の書き出しの一覧の SHA-256（round 1 の Z37・監査役の 1-7）は M12 で。
3. **プレプリント**（判断 205）: M12 で `\tbd` を埋めた後、BRM に出す版と同じものを **PsyArXiv** に出す（ライセンスは推奨 CC BY 4.0 を研究者に確かめる・分野の選び方と OSF の事前登録の project とのつなぎ方もそのとき決める）。⚠️ PsyArXiv はほぼ撤回できない。⚠️ 事前の審査で止まったら Zenodo に切り替える（研究者に確かめる）。同じ原稿にプレプリントの DOI を 2 つ付けない。投稿のときにプレプリントの DOI とライセンスを申告し、掲載が決まったらプレプリントに掲載版の DOI と URL を足す（Springer の方針）。
4. **投稿の前**:
   - 投稿規程（BRM・ScholarOne）の語数の上限を一次で確かめる。round 2 の取得（2026-10-06）では、規程のページに上限は無かった（"word limit" などの語なし）。ScholarOne の画面でも確かめる。
   - カバーレター。
   - タイトル頁（repo の外で記入・右上の頁番号は付けた）。
   - 要旨を変えたら `_count_abstract.py` で 250 語以内にする（今は 248 語）。
   - 図 1（AI が描画のコードを書いた図）の説明文に AI の開示が要るかを編集部に確かめる（出版社の方針の "visual content" の適用範囲は規程から読めない・round 2 の Y39）。
5. 研究者に残っていること: OSF のプロフィール名「Mikto Miura」を直す（判断 200 の 8・PsyArXiv の著者名にも出るので、プレプリントの前に）。

## §3 気をつけること

- ⚠️ 値の置き場所（判断 204-3）: Discussion で読む値は §6 にあり、Discussion は参照する。例外は 2 つ: ¶3 のキー行の遅れ（「数 ms」の代わりの値）と、尺度の段落（並べることが目的）。
- ⚠️ D11 は登録の値（0.000）を横に並べる（登録 §8）。表の道具の `icc_text()` と `values.json` の `registered`。
- ⚠️ 層を名指す・値を比べる文は手で書いている（§5 の Reproducibility）。結果ファイルが変わったら、手で確かめ直す。「S12 の中速・高速と長い試行の S8」「同じ最低の層（高速の S6 と S10）」「範囲の両端は両定義で同じ」「層『どれでもない』ではすべて互いに対」「1 文だけ違う層は live on の mid と fast」が該当する。
- ⚠️ `number_word()` は 0 と 1 で本文の型が崩れる（"In none further strata" など）。値が変わったら文を見直す。
- ⚠️ 投稿用の組版（main-submission）の overfull 1 は書誌の WebKit の項目のパスの中（未対応）。
