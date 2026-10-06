# 次セッション（Mac）— IME 論文 M12: `conditions.txt` の SHA-256 を記録し、macOS の書庫と標本を G-GEAR へ移す

> ✅ 済み（2026-10-07・判断 216・枝 `docs/ime-m12-mac-conditions`）: §2 の 1〜6。7 のうち 13 ファイルは Drive の `mac/` で移し済み。**残りは計測の書庫 2 つ**（`macos-standard-live-on-1.zip` `77bd8a8e…`・`-off-1.zip` `e1cdf2e8…`）を、測った機械の `~/ime-m4/deposit/` から Drive の `mac/` へ研究者が手で上げること。

> 作成: 2026-10-06 夜（G-GEAR・判断 215 の後）。`next-session-ime-paper-manuscript-9.md` の §2.1 の残りを、機械ごとの引き継ぎに分けたもの（研究者の求め）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 214・215**、`papers/ime-observation/experiment/data.md`（Deposits・Deposit procedure・question 5 の段落・2026-10-06 の節）、`papers/ime-observation/kit/export/deposit.internal.{json,py}`（寄託の一覧と照合の道具・docstring が仕様）。状態は着手時に `git fetch` で測り直す。
> 並行: Surface（`next-session-ime-paper-m12-surface.md`）と同時に進めてよい。G-GEAR（`next-session-ime-paper-m12-ggear.md`）は両方の後。

## §0 打ち込む用

```
git fetch → origin/docs/ime-m12-deposit-prep から枝 docs/ime-m12-mac-conditions を切る（main ではない）。
.steering/_handoff/next-session-ime-paper-m12-mac.md を読んで §2 を実行してください。
一次は decisions.md の判断 214・215、experiment/data.md、kit/export/deposit.internal.json と deposit.internal.py の docstring。
Skill: git-workflow・verify-before-claiming・data-privacy（書庫・標本を扱うとき）。応答は日本語。コミットは git add パス指定。
⚠️ 判断の番号は 216（Surface が 217 を使う。番号を詰めない）。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。ログ（obs / oracle / gt / plan）は開かない。生ログ・キーコードを外部の LLM に出さない。
⚠️ heredoc でバックスラッシュを重ねない（python に渡ると壊れる）→ 置換は Edit か、Write で書いたスクリプトで。
⚠️ PR は出さない（枝を push するだけ。G-GEAR が Surface の枝と合わせて 1 本の PR にする）。
```

## §1 状態（2026-10-06 夜・G-GEAR で測った）

- ✅ 判断 214（Mac）: 書庫 9 つ（`macos-e3-working-1.zip`・パイロット 8）を `~/ime-m4/deposit/`（パイロットは `pilot/`）に、標本 4 ファイルを `~/ime-m4/deposit/e3-samples/` に束ねた。SHA-256 と `git_commit` は `data.md`。
- ✅ 判断 215（G-GEAR）: 寄託は **1 ファイルずつ**（研究者の選択）。一覧 `kit/export/deposit.internal.json` と、照合して Zenodo の下書きに上げる道具 `kit/export/deposit.internal.py`（internal・書き出されない）を作った。G-GEAR で照合すると、記録・datasheet・共有ファイルは通り、欠けは Mac と Surface の書庫だけ。
- ⚠️ **穴 1 つ**: `conditions.txt`（`idle`・`working`）の SHA-256 が `data.md` に無い（判断 214 は `samples.tsv` だけ既存の値と照らした）。一覧では `macos-e3-idle-conditions.txt`・`macos-e3-working-conditions.txt` が `sha256: null`（保留）。測った機械で読むのが筋なので Mac で記録する。
- ⚠️ G-GEAR に macOS の書庫はまだ 1 つも無い（計測の 2 つ `macos-standard-live-on-1`・`-off-1` も）。

## §2 やること

1. **`conditions.txt` の SHA-256 を記録する**。`~/ime-m4/deposit/e3-samples/` の 2 つの `conditions.txt`（どちらが `idle` でどちらが `working` かは、束ねたときの元の run ディレクトリで確かめる。⚠️ 中身の確かめは判断 214 で済んでいる）の SHA-256 を `shasum -a 256` で取り、`data.md` に書く。
   - ★ 書き方（道具の照合の条件・docstring の 2）: **1 行に SHA-256 は 1 つだけ**、その行に**条件の語（`idle` か `working`）**と**語 `conditions`** を入れる。もう一方の条件の語は同じ行に書かない。例: ``The `conditions.txt` of the `idle` condition has the SHA-256 `<64 桁>`.`` を 1 行、`working` も 1 行。置き場所は 2026-10-06 の節の最後の段落（"The runtime samples are the files of …"）の後。
   - `samples.tsv` の 2 行（`data.md` の question 5 の段落・`f2fc37ef…`・`32fb0782…`）は変えない。
2. **一覧を埋める**: `kit/export/deposit.internal.json` の `macos-e3-idle-conditions.txt` と `macos-e3-working-conditions.txt` の `sha256` に 1 の値を入れる（ほかの項目は触らない。Windows の項目は Surface が埋める）。
3. **macOS の計測の書庫 2 つを探す**（2026-10-05 に測った機械で `--pack` 済み・SHA-256 は `data.md` の Deposits: `77bd8a8e…`・`e1cdf2e8…`）。見つけたら `~/ime-m4/deposit/` に写す（名前は何でもよい。道具は SHA-256 で探す）。
4. **道具で照合する**（Mac の python3 で。3.9 でも動く作り）:
   - `python3 -I papers/ime-observation/kit/export/deposit.internal.py --selftest` → `deposit selftest ok`（Mac ではシンボリックリンクのテストと、大文字に変えたパスの token を作業ツリーの中と見抜くテストが走る。後者は Windows では原理的に差が出ず、G-GEAR では確かめられなかった・判断 215）
   - `python3 -I papers/ime-observation/kit/export/deposit.internal.py --from ~/ime-m4/deposit --allow-pending`
   - ★ 期待: `macos-*` の 15 ファイル（計測 2・working 1・標本 4・パイロット 8）がすべて `ok`、FAIL は **`windows-*` の MISSING だけ**（Windows の書庫と標本は Mac に無い）。記録・datasheet の表・一覧の形の FAIL が 1 つでも出たら止まって原因を一次で確かめる。`unlisted` が出たら、それが何かを確かめる（`.DS_Store` などは無視される）。
   - `bash papers/ime-observation/kit/check.sh`（作業ツリー・34 本）
5. **記録**: `decisions.md` に判断 216（2 つの SHA-256・計測の書庫の在処〔パスは書かず「測った機械の …」〕・照合の結果）、`tasklist.md` の M12 に 1 行、本ファイルの冒頭に「✅ 済み」を書く。文体の検査 `python3 .steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py`（引数なしで `papers/ime-observation` 全体）→ 違反 0。
6. **コミット → push**（`git add` はパス指定: `papers/ime-observation/experiment/data.md`・`papers/ime-observation/kit/export/deposit.internal.json`・`.steering/20260927-ime-observation-paper-eval-design/{decisions,tasklist}.md`・本ファイル）。`git push -u origin docs/ime-m12-mac-conditions`。PR は出さない。
7. **研究者が移す**: macOS の 15 ファイル（計測 2・`macos-e3-working-1.zip`・パイロット 8・標本 4）を G-GEAR の **`C:/ime-deposit/`**（新しく作る・⚠️ OneDrive の下に置かない —— 道具は再解析ポイントを辿らない）へ。Windows の書庫と同じ道で。

## §3 気をつけること

- ⚠️ `--pack` を回し直さない（判断 214 の書庫の SHA-256 が記録にある。束ね直すとバイトは同じはずだが、確かめの手間が増える）。
- ⚠️ 書庫・ログを開かない。標本（`samples.tsv`・`conditions.txt`）は判断 214 で目と検索で確かめ済み。ここでは SHA-256 を取るだけ。
- ⚠️ `--remote` / `--upload` は Mac で回さない（token は G-GEAR だけ・Mac では `--token-file` が要る作り）。
- ⚠️ 研究者のメールアドレスを外部の LLM に送らない（/cross-review は G-GEAR でまとめて回す）。
