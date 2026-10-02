# carryover-audit — round 2 からの引き継ぎ（意図の監査役）

作成: 2026-10-02（メイン）。あなた（意図の監査役）の round 2 の指摘 19 件（1-a〜1-d・2-a〜2-f・3-a〜3-i）と、round 2 であなたが「部分的に解消」と判定した round 1 の指摘 5 件について、メインの裏取り・研究者の採否（判断 108〜110）・対応（判断 111 と事前登録の節）・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい食い違い**を探してほしい。round 2 で「解消」と判定した指摘は引き継がない（変わっていない節は round 2 の判定のまま）。

## 版の変化（round 2 の版 `384712ee` → 今の版 `abc5d7f9`）

- 節番号は変わっていない。round 2 の行番号は使えない（本文は 9,326 語から 11,217 語に増えた）。変わった節とコードの関数は context-A の「round 2 から変わった箇所」。
- 意図の資料に判断 108〜111 が増えた（context-B）。判断 108 が判断 99 の「問 3 の主は全試行」を、判断 109 が判断 102 の「1 秒のビンを推奨に残す」を改めた。

## A. round 2 の指摘

裏取りの判定は、メインが対象物・公開物・コードで確かめた結果。3-f を除いてすべて「真」。

### 1-a パイロットの生ログを公開する約束が消えている
- 研究者の採否（判断 110 の X6）: 約束を戻し、封印したセッション行は預けるときだけ開け、解析しない。
- 対応: §3.1 の第 1 段落（「The raw logs of its runs that meet the criteria set out there are deposited with the measurement data. The observation logs of the pilot are deposited whole, so their sealed session rows (section 2.5) are unsealed after the measurement only to be deposited; they are not analysed, not even in an exploratory analysis.」）。
- **未解決**: 預ける基準そのものは、まだ `pilot-macos.md` の "Raw logs" に書いていない（測定機での残りの作業）。

### 1-b §7 に E2 の区間の限界が無い
- 対応: §7 の新しい項「Intervals that treat trials as independent」・§6.8 の最後の段落（依存の向きを直し、ブロックで再標本した区間を記述として並べる）。

### 1-c 判断 106 の「限界と今後の課題」が §7 に届いていない
- 対応: §7 の「One input method, one machine, one system version」の項（「Only the standard Japanese input method of the system is measured, in its two live-conversion settings, in the reference input field; other input methods and applications are outside this study (section 1.3).」）。

### 1-d 判断 107 の 1 の 3 点が本文に無い
- 対応: 予測のセッションも重なり最大で割り当てる → §4.5（「like the ground-truth sessions, each is assigned to the trial it overlaps most」）／試行ごとの表は範囲の外の試行を除く → §6.7（「the trials outside the scope are left out」）／`dwell_fraction` の分母は変えない → §6.4（「the duration of a text, the denominator of the fraction of time spent converting, does not change」）。

### 2-a §7「The primary estimates of questions 1 and 2 describe the sessions the observer is specified to report」が §6.4 と合わない
- 対応: §7 の打ち切りの範囲の項を書き直した（「The primary scope sets aside the trials whose presses went into a session that is cut off; the other disagreements that the observer's rules predict stay in the primary estimates (section 6.4).」）・§6.4 の Comparisons の最後（「The primary scope therefore sets aside only the cut-off; the other disagreements that the rules predict remain in the primary estimates.」）。

### 2-b §1.1「For every key press」
- 対応: §1.1（「For every key press it receives, other than the input-mode keys, … (on macOS the keys F13 to F19 and the modifier keys produce no row either)」）。

### 2-c §7「a conversion exists only as the calls …」
- 対応: §7 の基準の項（「because an application sees a conversion only through these calls」）。

### 2-d `kit/refinput-macos/README.md`「trials are independent of one another」
- 対応: README（「therefore given no left context from the text of an earlier trial. Trials are not independent in every respect: the input method keeps its own state, including what it has learned, across trials.」）。

### 2-e `notes.md` の問いがはい／いいえの形
- 対応: `notes.md` の表の問いを how completely / how closely / how did / how much の形にした。

### 2-f 題の「the input method's own calls」
- 対応: 題を「… and a reference input field (macOS cells)」に。

### 3-a・3-b §6.4 の範囲の数と比較の組がコードと合わない
- 対応: §6.4 の Scopes の最後の段落（問 1 は 3 範囲・問 2 は `under_limit` と `all_trials`〔`over_limit` は §6.6 の Cut-off だけ〕・問 3 は `under_limit`〔主〕と `all_trials`〔副〕）と Comparisons（問 1・2 は 3 つの比較・問 3 は `gt_obs` だけ）。
- ⚠️ 問 3 の主は判断 108 で `under_limit` に変わった（判断 99・107 の 1 の「L2 は `all_trials` が主」を改めた）。コードは `pipeline.py` の `PRIMARY`・`L2_SCOPES`・`PRIMARY_NOTE`。

### 3-c 層 closing key in reading の説明が S12 のかな配列で誤り
- 対応: §4.5（「the trial sends the minus, comma or period key, which closes a session under the observer's rules (in Romaji input these keys type a long-vowel mark, a comma and a full stop; in the kana layout of S12 they type ho, ne and ru)」）・§3.1（「113 trials send the minus, comma or period key (76 of them are S12 trials …)」）・§6.4・`spec_predict.py` の冒頭の docstring とコメント。

### 3-d §8「may not change any other existing file」と Windows の手順の置き場が食い違う
- 研究者の採否（判断 110 の X7）: 追補は既存のファイルの Windows の部分も変えてよい。macOS の部分が変わらないことは 2 つの凍結のタグの差で示し、macOS の解析は macOS のタグから回す。
- 対応: §8（Windows の部分を列挙: `gt_rules.json` の Windows のブロック・2 つの手順書の `os.windows`・`generate_plan.py` の `_PROFILES["windows"]`。「The macOS plans are generated, and the macOS analysis is run, from the macOS freezing tag, also after the addendum」）・`notes.md` の同じ段落。

### 3-e 時計のずれで対にならなくなる長さが公開物どうしで違う（66 ms と 370 ms）
- 対応: `pilot-macos.md` の Clocks（22 ms だけなら約 66 ms、回収の遅れを足すと約 370 ms）・§6.9・`notes.md`（区間の長さが違うときの言い方も直した。round 1 の 1-2 の残り）。

### 3-f context-B の「約 3 割」と事前登録の 40%
- 裏取り: 意図の側の古さ（対象物は直さない）。今回の context-B は、判断 111 の 2 の新しい定義の値（447 / 1,050）に直した。

### 3-g §6.7「A text mixes the scenarios of its block about equally」
- 対応: §6.7（「The plan orders the trials of a block by the seed and does not balance the scenarios within a text, so a text mixes the scenarios about equally only in expectation」）。

### 3-h `gt_rules.json` の `_note`「together with both trials」
- 対応: `_note` を「together with every trial it overlaps」に（凍結のハッシュに入る。凍結の前なので値の変化は問題にならない）。

### 3-i §6.4 の over_limit の文は、持ち越しのとき誤り
- 研究者の採否（判断 108 の X2）: `long` を「打ち切られたセッションに打鍵が 1 つでも入った試行」に広げ、持ち越しを受けた層を「前の試行で始まったセッションに打鍵が入った試行」に定義し直す。
- 対応: §4.5・§6.4 の `over_limit` の文（「a letter or digit pressed after the cut-off opens a fresh session …, whose row is a row of the trial in which that press falls」）・§3.1・§3.3 の数を計算し直した（判断 111 の 1・2）。

## B. round 2 で「部分的に解消」と判定した round 1 の指摘

### 1-2（部分的に解消と判定）「a third of its length」は長さが同じときだけ → 上の 3-e と同じ箇所で直した（§6.9・`notes.md`・`pilot-macos.md`）。
### 1-4（部分的に解消と判定）一致の限界・kappa・ICC に「その幅で言えること」が無い
- 対応: §3.3 の連続量の精度の最後（「No width is predicted for the limits of agreement, kappa and the ICC, because it depends on the values estimated; they are read through the intervals reported with them.」）。§3.3 の割合の精度の文は、判断 110 の直す一覧（X8）で書き直した（「this does not guarantee that 0.95 and 0.90 are told apart」など）。
### 1-5（部分的に解消と判定）E3 `working` の 8 時間の後の計画の残り
- 対応: §6.10（「the runner plays the whole plan, about 11.9 hours, and the samples are those of the first eight hours」）。
### 3-2（部分的に解消と判定）追補の範囲と Windows の手順書 → 上の 3-d。
### 3-8（部分的に解消と判定）§1.2 の「Every … continuous estimate is reported with an interval」は言い過ぎ
- 研究者の採否（判断 108 の X5）: 問 3 の偏り・一致の限界・混合の偏りには区間を足す。
- 対応: §1.2（区間を付けるもの: 問 1〜3 の一致の推定と問 4 の正解率・誤り率／付けないもの: F1・数・問 4 の平均順位・§6.3・§6.9・§6.10 の記述の値）・§6.1・§6.7。
